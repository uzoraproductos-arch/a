#!/usr/bin/env python3
"""Integra a assets/js/audit-database.js la colección «expedientes»: las diez
fichas de Expedientes de Casos por Aclarar (Búsqueda Forense). Auditoría en
imágenes, en la portada, lee estas mismas fichas.

Uso:
    python3 herramientas/integrar_expedientes.py

Lee investigaciones/expedientes-asf.json (lo produce
extraer_expedientes_asf.py). Cada cifra de las fichas sale de ahí: se suman
los montos y las acciones de los informes individuales de la ASF que se
enlistan en cada ficha, o se toman del Sistema de Alertas de la SHCP. Los
textos se arman con esas mismas cifras para que no se desfasen.

También pone en DB.estados la deuda y el semáforo del Sistema de Alertas
(Cuenta Pública 2025), que sustituyen valores sin fuente.

Es idempotente: si la colección existe, la reemplaza.
"""
import json
import pathlib
import re
import sys
import unicodedata

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from integrar_ambiente import insertar  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BASE = RAIZ / 'assets' / 'js' / 'audit-database.js'
DATOS = RAIZ / 'investigaciones' / 'expedientes-asf.json'

SDA_FUENTE = 'SHCP, Sistema de Alertas, evaluación con la Cuenta Pública 2025 (publicada el 29 de junio de 2026)'
SDA_PAGINA = 'https://www.disciplinafinanciera.hacienda.gob.mx/es/DISCIPLINA_FINANCIERA/Entidades_Federativas_2025'

# (id, categoria, icono, titulo, ente, auditorias [(cp, num)], nota de alcance)
FICHAS = [
    ('tren-maya', 'megaobras', '🚅', 'Tren Maya: lo que la ASF dejó por aclarar',
     'FONATUR Tren Maya y Fondo Nacional de Fomento al Turismo',
     [(2022, n) for n in (107, 111, 112, 113, 114, 115, 116, 117, 118, 2111, 2112)] + [(2023, 145), (2024, 125), (2024, 126)]),
    ('tren-toluca', 'megaobras', '🚄', 'Tren Interurbano México-Toluca: la obra que faltaba terminar',
     'Secretaría de Infraestructura, Comunicaciones y Transportes',
     [(2022, 303), (2022, 307), (2022, 308), (2022, 329), (2023, 336), (2023, 341), (2023, 353), (2024, 338), (2024, 340), (2024, 350)]),
    ('aifa', 'megaobras', '✈️', 'Aeropuerto Felipe Ángeles: construcción y operación',
     'Secretaría de la Defensa Nacional y Aeropuerto Internacional Felipe Ángeles, S.A. de C.V.',
     [(2022, 341), (2022, 2121), (2022, 2122), (2022, 342), (2024, 9)]),
    ('cuchillo-ii', 'megaobras', '💧', 'Acueducto El Cuchillo II: agua para Monterrey',
     'Comisión Nacional del Agua',
     [(2022, 77), (2023, 101), (2024, 95)]),
    ('segalmex', 'alimentos', '🌽', 'Segalmex: las auditorías forenses más recientes',
     'Seguridad Alimentaria Mexicana (Segalmex)',
     [(2022, 2123), (2023, 400)]),
    ('dos-bocas', 'energia', '🛢️', 'Refinería Olmeca (Dos Bocas): obra y contratos',
     'Pemex Corporativo y Pemex Transformación Industrial',
     [(2022, n) for n in (215, 216, 217, 218, 219, 220, 221)] + [(2023, n) for n in (244, 246, 247, 248, 249)] + [(2024, 247)]),
    ('salud', 'salud', '🏥', 'Compra de medicamentos e IMSS-Bienestar',
     'INSABI, IMSS e IMSS-Bienestar',
     [(2022, 140), (2022, 164), (2022, 173), (2023, 191), (2024, 418), (2024, 419), (2024, 420)]),
    ('birmex', 'salud', '💊', 'Birmex: el almacén de Huehuetoca y el almacenaje privado',
     'Laboratorios de Biológicos y Reactivos de México, S.A. de C.V. (Birmex)',
     [(2023, 234)]),
    ('defensa', 'megaobras', '🛡️', 'Defensa: Tren Maya S.A. y fideicomiso militar',
     'Secretaría de la Defensa Nacional y sus empresas',
     [(2023, 371), (2024, 429), (2024, 367), (2024, 353), (2024, 356), (2024, 360)]),
]


def mdp(p):
    return '${:,.1f} mdp'.format(p / 1e6)


def plural(n, uno, varios):
    return '%s %s' % ('{:,}'.format(n), uno if n == 1 else varios)


def norm(t):
    t = unicodedata.normalize('NFD', t)
    return re.sub(r'^estado de ', '', ''.join(c for c in t if unicodedata.category(c) != 'Mn').lower())


def resumen_ficha(inf):
    tot = {'auditorias': len(inf), 'porAclarar': 0.0, 'recuperado': 0.0, 'PO': 0, 'PRAS': 0, 'acciones': 0}
    for x in inf:
        tot['porAclarar'] += x['porAclarar']
        tot['recuperado'] += x['recuperado']
        tot['PO'] += x['acciones'].get('PO', 0)
        tot['PRAS'] += x['acciones'].get('PRAS', 0)
        tot['acciones'] += sum(x['acciones'].values())
    anios = {}
    for x in inf:
        a = anios.setdefault(x['cp'], {'cp': x['cp'], 'auditorias': 0, 'porAclarar': 0.0, 'recuperado': 0.0, 'acciones': 0, 'PO': 0, 'PRAS': 0})
        a['auditorias'] += 1
        a['porAclarar'] += x['porAclarar']
        a['recuperado'] += x['recuperado']
        a['acciones'] += sum(x['acciones'].values())
        a['PO'] += x['acciones'].get('PO', 0)
        a['PRAS'] += x['acciones'].get('PRAS', 0)
    return tot, [anios[k] for k in sorted(anios)]


def hallazgo(fid, tot, anios, inf):
    por = {a['cp']: a for a in anios}
    if fid == 'tren-maya':
        t4 = next(x for x in inf if x['cp'] == 2022 and x['num'] == 114)
        a22 = por[2022]
        return ('En la Cuenta Pública 2022, con la obra en marcha, la ASF revisó la construcción de los tramos 1 a 7 y el financiamiento del proyecto: '
                'dejó %s por aclarar y promovió %s. El tramo 4, Izamal-Cancún, concentra %s: el %s del total. '
                'En las auditorías de 2023 y 2024 aquí reunidas, ya con el tren en operación, no quedaron montos por aclarar.') % (
            mdp(a22['porAclarar']), plural(a22['PO'], 'pliego de observaciones', 'pliegos de observaciones'), mdp(t4['porAclarar']),
            '{:.0f} %'.format(t4['porAclarar'] / a22['porAclarar'] * 100))
    if fid == 'segalmex':
        return ('Las dos auditorías forenses a Segalmex de las Cuentas Públicas 2022 y 2023 dejaron %s por aclarar, %s y avisos al SAT por posibles '
                'incumplimientos fiscales. Revisaron compras de bienes y servicios (2022) y la compra, venta y administración de maíz y frijol (2023).') % (
            mdp(tot['porAclarar']), plural(tot['PO'], 'pliego de observaciones', 'pliegos de observaciones'))
    if fid == 'dos-bocas':
        return ('En 2022 y 2023 la ASF revisó la construcción de la refinería paquete por paquete: dejó %s por aclarar, promovió %s y durante las '
                'auditorías se recuperaron %s. La auditoría de 2024, a los ingresos y egresos del proyecto, sólo emitió %s.') % (
            mdp(por[2022]['porAclarar'] + por[2023]['porAclarar']), plural(por[2022]['PO'] + por[2023]['PO'], 'pliego de observaciones', 'pliegos de observaciones'),
            mdp(por[2022]['recuperado'] + por[2023]['recuperado']), plural(por[2024]['acciones'], 'recomendación', 'recomendaciones'))
    if fid == 'salud':
        return ('En la compra de medicamentos, en la transición a IMSS-Bienestar y en su operación en 2024, la ASF no cuantificó montos por aclarar, pero emitió %s: '
                'faltas administrativas que el órgano interno de control de cada institución debe investigar y, en su caso, sancionar.') % (
            plural(tot['PRAS'], 'promoción de responsabilidad administrativa sancionatoria', 'promociones de responsabilidad administrativa sancionatoria'))
    if fid == 'tren-toluca':
        mayor = max(inf, key=lambda x: x['porAclarar'])
        return ('De 2022 a 2024 la ASF revisó cada año lo que faltaba para terminar el tren: el tramo de Zinacantepec, la estación Vasco de Quiroga, '
                'los viaductos de Santa Fe y el material rodante con sus sistemas ferroviarios. Dejó %s por aclarar y promovió %s. '
                'Una sola auditoría, la del material rodante de %d, concentra %s: el %s. Durante la revisión de 2024 se recuperaron %s.') % (
            mdp(tot['porAclarar']), plural(tot['PO'], 'pliego de observaciones', 'pliegos de observaciones'), mayor['cp'],
            mdp(mayor['porAclarar']), '{:.0f} %'.format(mayor['porAclarar'] / tot['porAclarar'] * 100), mdp(por[2024]['recuperado']))
    if fid == 'aifa':
        term = next(x for x in inf if x['cp'] == 2022 and x['num'] == 341)
        return ('En la Cuenta Pública 2022 la ASF revisó la terminal de pasajeros, el estacionamiento, la interconexión vial y los recursos destinados a construir '
                'y hacer funcionar el aeropuerto; en la de 2024, su gestión financiera. Sólo la terminal dejó dinero por aclarar: %s, con %s. '
                'En las cinco auditorías emitió %s.') % (
            mdp(term['porAclarar']), plural(term['acciones'].get('PO', 0), 'pliego de observaciones', 'pliegos de observaciones'),
            plural(tot['PRAS'], 'promoción de responsabilidad administrativa', 'promociones de responsabilidad administrativa'))
    if fid == 'cuchillo-ii':
        x = next(y for y in inf if y['cp'] == 2023)['extractos']
        return ('La Conagua construye un acueducto de %s km para llevar agua potable al Área Metropolitana de Monterrey y su zona conurbada, '
                'en beneficio de %s usuarios según la ASF. En sus tres revisiones, de 2022 a 2024, la ASF dejó %s por aclarar y promovió %s.') % (
            '{:,.1f}'.format(x['longitudKm']), '{:,}'.format(int(x['usuarios'])), mdp(tot['porAclarar']),
            plural(tot['PO'], 'pliego de observaciones', 'pliegos de observaciones'))
    if fid == 'birmex':
        x = inf[0]['extractos']
        return ('La auditoría forense a Birmex de la Cuenta Pública 2023 revisó la compra del inmueble de Huehuetoca para el Centro Federal de '
                'Almacenamiento y Distribución de Insumos para la Salud (CEFEDIS), la «Megafarmacia»: se pactó en %s más IVA y el equipamiento '
                'se adjudicó en forma directa por %s. En la compra, la ASF observó que no se acreditó haber avisado a la Función Pública del '
                'contrato plurianual ni justificado su anticipo. La auditoría completa dejó %s por aclarar, sobre todo por pagos a almacenes '
                'privados sin la evidencia de que se recibió el servicio: %s a Almacenaje y Distribución Avior y %s a Farmacéuticos Maypo.') % (
            mdp(x['cefedisPrecio']), mdp(x['cefedisEquipamiento']), mdp(tot['porAclarar']), mdp(x['almacenAvior']), mdp(x['almacenMaypo']))
    if fid == 'defensa':
        return ('En las %s aquí reunidas, la ASF no dejó montos por aclarar ni promovió acciones: lo que llegó a observar se solventó antes del informe. '
                'Que una auditoría salga limpia también es un dato, y se reporta igual que uno con hallazgos.') % plural(tot['auditorias'], 'auditoría', 'auditorías')
    return ''


def ficha_deuda(sda):
    ent = sorted(sda['entidades'], key=lambda e: -e['dyoIld'])
    total = sum(e['dyo'] for e in ent)
    niveles = sorted({e['resultado'] for e in ent})
    medios = [e['entidad'] for e in ent if e['sdIld'] > 0.075]
    return {
        'id': 'deuda-estados', 'categoria': 'deuda', 'icono': '🏛️',
        'titulo': 'Deuda de los estados: el Sistema de Alertas',
        'ente': 'SHCP · Sistema de Alertas de la Ley de Disciplina Financiera',
        'hallazgo': ('Con la Cuenta Pública 2025, los %d estados medidos quedaron en «%s»; ninguno en observación ni en endeudamiento elevado. '
                     'Los más endeudados respecto de sus ingresos de libre disposición son %s. En %s el pago de la deuda ya pesa en rango medio. '
                     'Tlaxcala no se mide porque no tiene deuda inscrita en el Registro Público Único.') % (
            len(ent), niveles[0] if len(niveles) == 1 else ' y '.join(niveles),
            ', '.join('%s (%s)' % (e['entidad'], '{:.1f} %'.format(e['dyoIld'] * 100)) for e in ent[:3]),
            ', '.join(medios[:-1]) + ' y ' + medios[-1] if len(medios) > 1 else (medios[0] if medios else 'ningún estado')),
        'cifras': [
            {'valor': mdp(total), 'etq': 'deuda y obligaciones de los 31 estados medidos', 'estado': 'derivado', 'nota': 'Suma de la columna «Deuda y Obligaciones» del Sistema de Alertas.'},
            {'valor': '{:.1f} %'.format(ent[0]['dyoIld'] * 100), 'etq': 'deuda sobre ingresos de libre disposición en %s, el más alto' % ent[0]['entidad'], 'estado': 'oficial'},
            {'valor': str(len([e for e in ent if e['resultado'] == 'Endeudamiento Sostenible'])) + ' de ' + str(len(ent)), 'etq': 'en endeudamiento sostenible', 'estado': 'oficial'},
        ],
        'tabla': [{'entidad': e['entidad'], 'dyoIld': e['dyoIld'], 'dyo': e['dyo'], 'resultado': e['resultado']} for e in ent[:6]],
        'documentos': [{'titulo': 'Resultado del Sistema de Alertas, Cuenta Pública 2025 (variables por entidad, XLSX)', 'url': sda['url'], 'sha256': sda['sha256']},
                       {'titulo': 'Sistema de Alertas: página oficial con todas las mediciones', 'url': SDA_PAGINA}],
        'fuente': SDA_FUENTE,
        'alcance': 'Según la SHCP, el Sistema de Alertas mide a los entes con financiamientos inscritos en el Registro Público Único cuya fuente o garantía de pago son sus ingresos de libre disposición. Clasifica en tres niveles: sostenible, en observación y elevado.',
    }


def estados(b, sda):
    """Deuda y semaforo del Sistema de Alertas en DB.estados."""
    db, _ = json.JSONDecoder().raw_decode(b[b.index('{', b.index('window.AUDIT_DB')):])
    color = {'Endeudamiento Sostenible': 'Verde', 'Endeudamiento en Observación': 'Amarillo', 'Endeudamiento Elevado': 'Rojo'}
    for st in db['estados']:
        e = next((x for x in sda['entidades'] if norm(x['entidad']) == norm(st['name']) or norm(x['entidad']).startswith(norm(st['name']) + ' ')), None)
        if e:
            nuevos = {'deuda': round(e['dyo'] / 1e6, 1), 'semaforoDeuda': color[e['resultado']], 'deudaIld': round(e['dyoIld'] * 100, 1),
                      'deudaFuente': SDA_FUENTE}
        elif norm(st['name']) == 'tlaxcala':
            nuevos = {'deuda': 0, 'semaforoDeuda': 'Verde', 'deudaIld': 0,
                      'deudaFuente': SDA_FUENTE + '. Tlaxcala no es objeto de medición: no tiene financiamientos inscritos en el Registro Público Único; la Ley de Disciplina Financiera (art. 14) lo clasifica como sostenible.'}
        else:
            sys.exit('Sin dato del Sistema de Alertas para %s' % st['name'])
        ini = b.index('"abbr": %s' % json.dumps(st['abbr'], ensure_ascii=False))
        fin = b.index('"asfMontoObservado"', ini)
        trozo = b[ini:fin]
        for k in ('deudaIld', 'deudaFuente'):
            trozo = re.sub(r'\r\n +"%s": .*?,(?=\r\n)' % k, '', trozo)
        for k, v in nuevos.items():
            if k in ('deuda', 'semaforoDeuda'):
                trozo, n = re.subn(r'("%s": ).*?(,\r\n)' % k, lambda m: m.group(1) + json.dumps(v, ensure_ascii=False) + m.group(2), trozo, count=1)
                if n != 1:
                    sys.exit('No encuentro %s en %s' % (k, st['name']))
        sang = re.search(r'\r\n( +)"semaforoDeuda"', trozo).group(1)
        extra = ''.join('\r\n%s"%s": %s,' % (sang, k, json.dumps(nuevos[k], ensure_ascii=False)) for k in ('deudaIld', 'deudaFuente'))
        cierre = trozo.index('\r\n', trozo.index('"semaforoDeuda"'))
        trozo = trozo[:cierre] + extra + trozo[cierre:]
        b = b[:ini] + trozo + b[fin:]
    return b


def main():
    d = json.loads(DATOS.read_text(encoding='utf-8'))
    idx = {(x['cp'], x['num']): x for x in d['informes']}
    fichas = []
    for fid, cat, ico, tit, ente, lista, in FICHAS:
        inf = [idx[k] for k in lista]
        tot, anios = resumen_ficha(inf)
        cifras = [
            {'valor': str(tot['auditorias']), 'etq': 'informes individuales revisados', 'estado': 'oficial'},
            {'valor': mdp(tot['porAclarar']), 'etq': 'por aclarar, suma de esos informes', 'estado': 'derivado'},
            {'valor': '{:,}'.format(tot['PO']) + ' · ' + '{:,}'.format(tot['PRAS']), 'etq': 'pliegos de observaciones · promociones de responsabilidad', 'estado': 'derivado'},
        ]
        if tot['recuperado']:
            cifras.append({'valor': mdp(tot['recuperado']), 'etq': 'recuperados durante las auditorías', 'estado': 'derivado'})
        if fid == 'birmex':
            cifras[1]['estado'] = 'oficial'
            cifras[1]['etq'] = 'por aclarar en la auditoría'
            cifras.append({'valor': mdp(inf[0]['extractos']['cefedisInmuebleConIva']), 'etq': 'precio del inmueble de Huehuetoca, con IVA', 'estado': 'oficial'})
        fichas.append({
            'id': fid, 'categoria': cat, 'icono': ico, 'titulo': tit, 'ente': ente,
            'hallazgo': hallazgo(fid, tot, anios, inf),
            'cifras': cifras, 'anios': anios,
            'auditorias': [{'cp': x['cp'], 'num': x['num'], 'clave': x['claveAuditoria'], 'tipo': x['tipo'],
                            'ente': x['ente'], 'titulo': x['titulo'], 'porAclarar': x['porAclarar'], 'recuperado': x['recuperado'],
                            'acciones': x['acciones'], 'resumen': x['resumen'], 'url': x['url'], 'sha256': x['sha256'],
                            'paginas': x['paginas'],
                            'universo': round(x['universoMiles'] * 1e3, 2) if x['universoMiles'] else None,
                            'muestra': round(x['muestraMiles'] * 1e3, 2) if x['muestraMiles'] else None,
                            **({'extractos': x['extractos']} if x.get('extractos') else {})} for x in inf],
            'fuente': 'ASF, informes individuales de la fiscalización superior de las Cuentas Públicas %s' % ', '.join(str(a['cp']) for a in anios),
            'alcance': 'Reúne sólo las auditorías enlistadas abajo. La ASF pudo practicar otras a estos entes que no están aquí.',
        })
    fichas.insert(len(fichas) - 1, ficha_deuda(d['sistemaAlertas']))
    coleccion = {'consulta': '26 de septiembre de 2026', 'fichas': fichas}
    b = BASE.read_bytes().decode('utf-8')
    b = insertar(b, 'expedientes', coleccion)
    b = estados(b, d['sistemaAlertas'])
    BASE.write_bytes(b.encode('utf-8'))
    for f in fichas:
        print('%-15s %s' % (f['id'], ' | '.join(c['valor'] for c in f['cifras'])))


if __name__ == '__main__':
    main()
