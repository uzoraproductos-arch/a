#!/usr/bin/env python3
"""Integra a assets/js/audit-database.js la colección «ambiente»: el costo
ambiental (reloj, huella, basura municipal, presupuesto ambiental 2026-2027,
leyes aplicables y quién mide hoy cada dato).

Uso:
    python3 herramientas/integrar_ambiente.py

Lee investigaciones/presupuesto-ambiental.json (lo produce
extraer_presupuesto_ambiental.py). Las cifras del costo del daño ambiental no
se repiten aquí: el motor las toma de la colección cuentas_ecologicas (INEGI,
CEEM 2024). Es idempotente: si la colección existe, la reemplaza.
"""
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BASE = RAIZ / 'assets' / 'js' / 'audit-database.js'
PRESUP = RAIZ / 'investigaciones' / 'presupuesto-ambiental.json'
CONSULTA = '26 de septiembre de 2026'

HOST_TP = 'https://www.transparenciapresupuestaria.gob.mx'
FUENTES = {
    'DBGIR': {
        'corto': 'SEMARNAT, Diagnóstico de residuos, abril 2026',
        'doc': 'SEMARNAT-INECC, Diagnóstico Básico para la Gestión Integral de los Residuos, abril de 2026',
        'url': 'https://www.gob.mx/cms/uploads/attachment/file/1078946/Diagn_stico_B_sico_Gesti_n_Integral_Residuos.pdf',
        'sha256': 'af47fb7034805c1822832af441d9bc3ad672abcaa558c8089f3bfe2bd2a0bb5e'},
    'CNGMD': {
        'corto': 'INEGI, Censo de Gobiernos Municipales 2023',
        'doc': 'INEGI, Censo Nacional de Gobiernos Municipales y Demarcaciones Territoriales de la Ciudad de México 2023, presentación de resultados, 28 de febrero de 2024',
        'url': 'https://www.inegi.org.mx/contenidos/programas/cngmd/2023/doc/cngmd2023_resultados_geogr_amb.pdf',
        'sha256': '37e26cff2604a710fe94c76ea4a4fcbc31f2cb119986edb7a843c6ced136424d'},
    'PEF': {
        'corto': 'PEF 2026, DOF 21-11-2025',
        'doc': 'Decreto de Presupuesto de Egresos de la Federación 2026, DOF 21-11-2025 (edición vespertina)',
        'url': 'https://www.diputados.gob.mx/LeyesBiblio/ref/pef_2026/PEF_2026_orig_21nov25.pdf',
        'sha256': '6db4a86b588a0f76928e5d61298579c4aff2c29c3ace68fdedbfa5afceb8f2bc'},
    'AV2T2026': {
        'corto': 'SHCP, avance del gasto al 2.º trimestre 2026',
        'doc': 'SHCP, Presupuesto de Egresos 2026, avance del gasto (AC01) al segundo trimestre, base de datos abierta (Transparencia Presupuestaria)',
        'url': HOST_TP + '/work/models/PTP/DatosAbiertos/Bases_de_datos_presupuesto/CSV/pef_ac01_avance_2t_2026.csv'},
    'PPEF2027': {
        'corto': 'SHCP, Proyecto de PEF 2027, datos abiertos',
        'doc': 'SHCP, Proyecto de Presupuesto de Egresos de la Federación 2027, base de datos abierta (Transparencia Presupuestaria)',
        'url': HOST_TP + '/work/models/PTP/DatosAbiertos/Bases_de_datos_presupuesto/XLSX/PPEF_2027.xlsx'},
    'LGPGIR': {
        'corto': 'Ley General de Residuos, reforma DOF 19-01-2026',
        'doc': 'Ley General para la Prevención y Gestión Integral de los Residuos, última reforma DOF 19-01-2026',
        'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LGPGIR.pdf',
        'sha256': 'b34326588bd6e7519e33411d3658239e3aefb56cef0fae5d775bc894af64a565'},
}

RESIDUOS = {
    'generacionTdia': {'valor': 139902, 'estado': 'oficial', 'fuente': 'DBGIR', 'pagina': 31},
    'perCapitaKg': {'valor': 1.076, 'estado': 'oficial', 'fuente': 'DBGIR', 'pagina': 34},
    'recolectadaTdia': {'valor': 108146, 'pct': 77.30, 'estado': 'oficial', 'fuente': 'DBGIR', 'pagina': 31,
                        'nota': 'Dato del Censo de Gobiernos Municipales 2023 (recolección promedio de 2022).'},
    'separadaTdia': {'valor': 14679, 'pct': 10.4, 'estado': 'oficial', 'fuente': 'DBGIR', 'pagina': 31},
    'sitiosDisposicion': {'valor': 2250, 'tdia': 98047, 'estado': 'oficial', 'fuente': 'DBGIR', 'pagina': 32},
    'rellenosSanitarios': {'valor': 52, 'tdia': 15254.605, 'pct': 15.6, 'estado': 'oficial', 'fuente': 'DBGIR', 'pagina': 32,
                           'nota': 'El resto de los sitios de disposición final se clasifica como no controlado conforme a la NOM-083-SEMARNAT-2003.'},
    'municipiosSinRecoleccion': {'valor': 150, 'tdia': 528.3, 'oaxaca': 127, 'estado': 'oficial', 'fuente': 'DBGIR', 'pagina': 49},
    'vehiculos': {'valor': 17593, 'pctAntes2002': 25.15, 'estado': 'oficial', 'fuente': 'DBGIR', 'pagina': 31},
    'sinPartidaFederal': {'texto': 'Después del periodo 2013–2018, no se cuenta con ninguna partida presupuestal federal para la gestión de residuos; Banobras es la única fuente de recursos financieros disponible.',
                          'estado': 'oficial', 'fuente': 'DBGIR', 'pagina': 32},
    'recolectadaSerie': {'anios': [2010, 2012, 2014, 2016, 2018, 2020, 2022],
                         'tdia': [86342, 99770, 102887, 104734, 107055, 106523, 108146],
                         'estado': 'oficial', 'fuente': 'CNGMD', 'pagina': 31},
}

LEYES = [
    {'norma': 'Constitución, artículo 4º', 'dice': 'Toda persona tiene derecho a un medio ambiente sano para su desarrollo y bienestar; el daño y deterioro ambiental genera responsabilidad para quien lo provoque.', 'refKey': 'ref-cpeum'},
    {'norma': 'Constitución, artículo 115, fracción III, inciso c)', 'dice': 'Limpia, recolección, traslado, tratamiento y disposición final de residuos: es un servicio público a cargo del municipio.', 'refKey': 'ref-cpeum'},
    {'norma': 'Ley General de Residuos, artículo 10, fracciones IV y V', 'dice': 'El municipio presta el servicio por sí o a través de gestores, y otorga las autorizaciones y concesiones de una o más actividades del servicio. Por eso la concesión de la basura se decide en el cabildo.', 'refKey': 'ref-lgpgir'},
    {'norma': 'Ley General del Equilibrio Ecológico, artículo 28', 'dice': 'Las obras que puedan causar desequilibrio ecológico requieren evaluación de impacto ambiental previa por la SEMARNAT: la Manifestación de Impacto Ambiental.', 'refKey': 'ref-lgeepa'},
    {'norma': 'Ley General de Cambio Climático', 'dice': 'Establece las obligaciones para enfrentar los efectos adversos del cambio climático y reglamenta la protección al ambiente en esa materia.', 'refKey': 'ref-lgcc'},
    {'norma': 'Ley del IEPS, artículo 2º, fracción I, inciso H)', 'dice': 'Grava los combustibles fósiles: es el llamado impuesto al carbono, un impuesto con justificación ambiental que entra a la bolsa general.', 'refKey': 'ref-lieps'},
]

QUIEN_MIDE = [
    {'dato': 'Costo del daño ambiental (PIB ecológico)', 'mide': 'INEGI', 'estado': 'vigente', 'nota': 'Organismo autónomo; desde 2025 también mide la pobreza que medía el CONEVAL.'},
    {'dato': 'Generación y manejo de residuos', 'mide': 'SEMARNAT e INECC', 'estado': 'vigente', 'nota': 'Diagnóstico nacional, edición de abril de 2026.'},
    {'dato': 'Servicio de basura por municipio', 'mide': 'INEGI (Censo de Gobiernos Municipales)', 'estado': 'vigente', 'nota': 'Levantamiento cada dos años; el último publicado es el de 2023.'},
    {'dato': 'Permisos ambientales de las obras (MIA)', 'mide': 'SEMARNAT, Dirección General de Impacto y Riesgo Ambiental', 'estado': 'vigente', 'nota': ''},
    {'dato': 'Presupuesto ambiental', 'mide': 'SHCP y Cámara de Diputados', 'estado': 'vigente', 'nota': 'El proyecto 2027 se aprueba a más tardar el 15 de noviembre de 2026.'},
    {'dato': 'Acceso a la información', 'mide': 'Secretaría Anticorrupción y Buen Gobierno («Transparencia para el Pueblo»)', 'estado': 'cambió', 'nota': 'Antes el INAI, extinto en marzo de 2025.'},
    {'dato': 'Contrataciones públicas', 'mide': 'ComprasMX', 'estado': 'cambió', 'nota': 'Antes CompraNet, sustituido en abril de 2025.'},
]

PENDIENTES = [
    'Huella ambiental de las megaobras: las Manifestaciones de Impacto Ambiental están en el portal de la SEMARNAT (dgiraDocs), que no fue accesible al integrar. Ninguna cifra de hectáreas se muestra hasta tener el documento oficial.',
    'Concesión y costo del servicio de basura, municipio por municipio: vienen en los microdatos del módulo de residuos del Censo de Gobiernos Municipales 2023 del INEGI; falta descargarlos.',
    'Costo del daño ambiental 2025: el INEGI publica las Cuentas Económicas y Ecológicas cada diciembre; la de 2025 se espera en diciembre de 2026.',
]

REF_NUEVAS = [
    {'num': 76, 'id': 'ref-lgpgir', 'categoria': 'leyes_federales', 'categoria_nombre': 'Leyes Hacendarias y Presupuestales',
     'cita_apa': 'Ley General para la Prevención y Gestión Integral de los Residuos. Diario Oficial de la Federación, 8 de octubre de 2003, última reforma 19 de enero de 2026 (México). Cámara de Diputados del H. Congreso de la Unión.',
     'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LGPGIR.pdf',
     'descripcion': 'Reparte la gestión de los residuos entre Federación, estados y municipios. Su artículo 10 deja al municipio la recolección, el traslado, el tratamiento y la disposición final de la basura, y le permite prestar el servicio por sí o por gestores y otorgar concesiones.'},
    {'num': 77, 'id': 'ref-lgcc', 'categoria': 'leyes_federales', 'categoria_nombre': 'Leyes Hacendarias y Presupuestales',
     'cita_apa': 'Ley General de Cambio Climático. Diario Oficial de la Federación, 6 de junio de 2012, última reforma 1 de abril de 2024 (México). Cámara de Diputados del H. Congreso de la Unión.',
     'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LGCC.pdf',
     'descripcion': 'Establece las disposiciones para enfrentar los efectos adversos del cambio climático y reglamenta la protección al ambiente en esa materia.'},
    {'num': 78, 'id': 'ref-dbgir2026', 'categoria': 'estadistica_oficial', 'categoria_nombre': 'Estadística Oficial del Estado Mexicano',
     'cita_apa': 'Secretaría de Medio Ambiente y Recursos Naturales e Instituto Nacional de Ecología y Cambio Climático. (2026). Diagnóstico Básico para la Gestión Integral de los Residuos. SEMARNAT.',
     'url': 'https://www.gob.mx/cms/uploads/attachment/file/1078946/Diagn_stico_B_sico_Gesti_n_Integral_Residuos.pdf',
     'descripcion': 'Diagnóstico nacional de residuos publicado en abril de 2026: generación de 139,902 toneladas diarias de residuos sólidos urbanos (1.076 kg por habitante), recolección, disposición final e infraestructura.'},
    {'num': 79, 'id': 'ref-cngmd2023', 'categoria': 'estadistica_oficial', 'categoria_nombre': 'Estadística Oficial del Estado Mexicano',
     'cita_apa': 'Instituto Nacional de Estadística y Geografía. (2024). Censo Nacional de Gobiernos Municipales y Demarcaciones Territoriales de la Ciudad de México 2023: presentación de resultados generales. INEGI.',
     'url': 'https://www.inegi.org.mx/contenidos/programas/cngmd/2023/doc/cngmd2023_resultados_geogr_amb.pdf',
     'descripcion': 'Censo de los gobiernos municipales. Su módulo de residuos sólidos urbanos reporta la basura recolectada cada día (108,146 toneladas en 2022), el sistema de recolección y la disposición final.'},
]


def _valor(v):
    return json.dumps(v, ensure_ascii=True)


def construir():
    p = json.loads(PRESUP.read_text(encoding='utf-8'))
    FUENTES['AV2T2026']['sha256'] = p['sha256']['AV2T2026']
    FUENTES['PPEF2027']['sha256'] = p['sha256']['PPEF2027']
    return {
        'consulta': CONSULTA,
        'nota': 'Pesos nominales. El costo del daño ambiental es del INEGI (Cuentas Económicas y Ecológicas 2024); '
                'los relojes lo reparten por segundo y por persona, y esas cuentas son derivadas. '
                'Esta plataforma no estima ninguna cifra ambiental propia.',
        'fuentes': FUENTES,
        'residuos': RESIDUOS,
        'presupuesto': {
            'ramo': p['ramo'], 'nombre': p['nombre'],
            'aprobado2026': {'valor': p['total2026']['aprobado'], 'estado': 'oficial', 'fuente': 'PEF', 'pagina': 'Anexo 1, DOF p. 32'},
            'modificado2026': {'valor': p['total2026']['modificado'], 'estado': 'oficial', 'fuente': 'AV2T2026', 'pagina': 'base de datos'},
            'pagado2026': {'valor': p['total2026']['pagado'], 'corte': '30 de junio de 2026', 'estado': 'oficial', 'fuente': 'AV2T2026', 'pagina': 'base de datos'},
            'proyecto2027': {'valor': p['proyecto2027'], 'estado': 'oficial', 'fuente': 'PPEF2027', 'pagina': 'base de datos',
                             'nota': 'Proyecto enviado por el Ejecutivo el 8 de septiembre de 2026; la Cámara de Diputados puede modificarlo hasta el 15 de noviembre.'},
            'unidades': p['unidades'],
        },
        'leyes': LEYES,
        'quienMide': QUIEN_MIDE,
        'pendientes': PENDIENTES,
    }


def insertar(b, clave, datos):
    cuerpo = json.dumps(datos, ensure_ascii=True, indent=2)
    cuerpo = '\n'.join('  ' + l if i else l for i, l in enumerate(cuerpo.split('\n')))
    bloque = ('"%s": ' % clave + cuerpo).replace('\n', '\r\n')
    marca = '\r\n"%s": ' % clave
    cierre = b.rfind('\r\n};')
    if cierre < 0 or b[cierre + 4:].strip():
        sys.exit('No encuentro el cierre de window.AUDIT_DB; no toco nada.')
    if marca in b:
        ini = b.index(marca)
        # la coleccion termina en la siguiente clave de primer nivel o en el cierre
        sig = b.find('\r\n"', ini + len(marca))
        fin = sig if 0 <= sig < cierre else cierre
        cola = b[fin:]
        coma = ',' if cola.startswith('\r\n"') else ''
        return b[:ini] + '\r\n' + bloque + coma + cola
    previo = b[:cierre].rstrip()
    return previo + ',\r\n' + bloque + b[cierre:]


def referencias(b):
    ancla = '"id": "ref-oaj-trimestre2026"'
    i = b.index(ancla)
    fin = b.index('\r\n    }', i) + len('\r\n    }')
    for ref in reversed(REF_NUEVAS):
        if '"id": "%s"' % ref['id'] in b:
            continue
        cuerpo = ',\r\n    {\r\n' + ',\r\n'.join('      "%s": %s' % (k, _valor(v)) for k, v in ref.items()) + '\r\n    }'
        b = b[:fin] + cuerpo + b[fin:]
    return b


def main():
    b = BASE.read_bytes().decode('utf-8')
    b = insertar(b, 'ambiente', construir())
    b = referencias(b)
    BASE.write_bytes(b.encode('utf-8'))
    print('ambiente integrada')


if __name__ == '__main__':
    main()
