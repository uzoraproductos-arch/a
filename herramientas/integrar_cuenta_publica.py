#!/usr/bin/env python3
"""Integra a assets/js/audit-database.js la colección «cuenta_publica_asf»:
qué es la Cuenta Pública, el calendario legal de su revisión, las cifras de la
Matriz de Datos Básicos de la ASF (Cuenta Pública 2024, consolidado de las tres
entregas, y primera entrega de la 2025) y qué significa cada acción.

Uso:
    python3 herramientas/integrar_cuenta_publica.py

Lee investigaciones/asf-mdb-2024.json (lo produce extraer_mdb_asf.py). Las
cifras de la primera entrega 2025 se capturan a mano de su matriz (página 11,
un solo renglón de totales). Es idempotente. También corrige dos fichas del
catálogo: la 7 (LFRCF, citaba la reforma de 2021) y la 14 (informes de la ASF,
apuntaba a la portada y hablaba de «2,100 pliegos»).
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from integrar_ambiente import BASE, insertar, _valor  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parent.parent
MDB = RAIZ / 'investigaciones' / 'asf-mdb-2024.json'
CONSULTA = '26 de septiembre de 2026'
ASF = 'https://www.asf.gob.mx/Trans/Informes/'

FUENTES = {
    'MDB2024': {
        'corto': 'ASF, Matriz de Datos Básicos CP 2024 (feb. 2026)',
        'doc': 'Auditoría Superior de la Federación, Matriz de Datos Básicos del Informe del Resultado de la Fiscalización Superior de la Cuenta Pública 2024, primera, segunda y tercera entregas (consolidado), corte febrero de 2026',
        'url': ASF + 'IR2024c/Documentos/Matriz/MDB_Consolidado.pdf',
        'sha256': '49732c8da82eaafc6bdd67b0b0ce5c995773294d7e48e5412ad73e5c4fe15d66'},
    'IR2024': {
        'corto': 'ASF, Informe del Resultado CP 2024',
        'doc': 'Auditoría Superior de la Federación, Informe del Resultado de la Fiscalización Superior de la Cuenta Pública 2024, tercera entrega (portal con los informes individuales)',
        'url': ASF + 'IR2024c/index.html'},
    'MDB2025A': {
        'corto': 'ASF, Matriz de Datos Básicos CP 2025, 1.ª entrega (jun. 2026)',
        'doc': 'Auditoría Superior de la Federación, Matriz de Datos Básicos, Fiscalización Superior de la Cuenta Pública 2025, primera entrega, corte junio de 2026',
        'url': ASF + 'IR2025a/Documentos/Matriz/IR2025_Entrega_a.pdf',
        'sha256': 'f0cd6497346ca2247f4db83f663fdcc99c517fc6f94c239f0970d3edb855edcc'},
    'IR2025A': {
        'corto': 'ASF, Informe del Resultado CP 2025, 1.ª entrega',
        'doc': 'Auditoría Superior de la Federación, Informe del Resultado de la Fiscalización Superior de la Cuenta Pública 2025, primera entrega',
        'url': ASF + 'IR2025a/index.html'},
    'LFRCF': {
        'corto': 'Ley de Fiscalización, reforma DOF 14-05-2026',
        'doc': 'Ley de Fiscalización y Rendición de Cuentas de la Federación, última reforma DOF 14-05-2026',
        'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LFRCF.pdf',
        'sha256': 'cc687a4d8d9de93d2d3ec9b40b26d0273e108bb002a6f611806dc36ebce5ba2c'},
    'CPEUM': {
        'corto': 'Constitución, art. 74 fr. VI',
        'doc': 'Constitución Política de los Estados Unidos Mexicanos, últimas reformas DOF 02-06-2026',
        'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf',
        'sha256': 'ca63a23a4b7444ebdbdad93759fbf46bd14c069e587c5878decf89fc9c12ca8e'},
    'CPSHCP': {
        'corto': 'SHCP, portal de la Cuenta Pública',
        'doc': 'Secretaría de Hacienda y Crédito Público, Cuenta Pública (portal oficial, ejercicios 1996 a 2025)',
        'url': 'https://www.cuentapublica.hacienda.gob.mx'},
    'ASFDATOS': {
        'corto': 'ASF, Sistema Público de Consulta',
        'doc': 'Auditoría Superior de la Federación, Sistema Público de Consulta de Auditorías (ASF Datos)',
        'url': 'https://www.asfdatos.gob.mx/'},
}

# Calendario de la Cuenta Pública 2025. Las fechas salen de la ley; "hecho"
# marca lo que ya ocurrió al día de la consulta.
CALENDARIO = [
    {'fecha': '2025-12-31', 'titulo': 'Cierra el ejercicio 2025', 'texto': 'Termina el año en que se gastó el dinero que se revisa.', 'hecho': True},
    {'fecha': '2026-04-30', 'titulo': 'Hacienda entrega la Cuenta Pública 2025', 'texto': 'La SHCP la presenta a la Cámara de Diputados a más tardar el 30 de abril del año siguiente.',
     'fundamento': 'CPEUM, art. 74, fr. VI', 'fuente': 'CPEUM', 'hecho': True},
    {'fecha': '2026-06-30', 'titulo': 'Primera entrega de la ASF', 'texto': 'Informes individuales que concluyen en el periodo. En 2026 fueron 33 auditorías a la distribución de las participaciones federales.',
     'fundamento': 'LFRCF, art. 35', 'fuente': 'LFRCF', 'hecho': True},
    {'fecha': '2026-10-30', 'titulo': 'Segunda entrega de la ASF', 'texto': 'Último día hábil de octubre (el 31 de octubre de 2026 cae en sábado).',
     'fundamento': 'LFRCF, art. 35', 'fuente': 'LFRCF', 'hecho': False},
    {'fecha': '2027-02-20', 'titulo': 'Tercera entrega e Informe General', 'texto': 'Últimos informes individuales y el Informe General Ejecutivo, que es público.',
     'fundamento': 'LFRCF, arts. 33 y 35', 'fuente': 'LFRCF', 'hecho': False},
]

PLAZOS = [
    {'plazo': '10 días hábiles', 'que': 'para que la ASF envíe a cada ente su informe individual, con sus acciones y recomendaciones, después de entregarlo a la Cámara', 'fundamento': 'LFRCF, art. 39'},
    {'plazo': '30 días hábiles', 'que': 'para que el ente responda y aporte la información que aclare lo observado', 'fundamento': 'LFRCF, art. 39'},
    {'plazo': '120 días hábiles', 'que': 'para que la ASF se pronuncie sobre esas respuestas: solventa, no solventa, archiva o concluye', 'fundamento': 'LFRCF, art. 41'},
    {'plazo': '90 días hábiles', 'que': 'para enviar a investigación el dictamen técnico de los pliegos de observaciones no solventados', 'fundamento': 'LFRCF, art. 41'},
]

ACCIONES = [
    {'clave': 'R', 'nombre': 'Recomendación', 'tipo': 'preventiva', 'que': 'Sugerencia para fortalecer el control interno y el cumplimiento de metas.', 'fundamento': 'LFRCF, art. 42; glosario de la MDB'},
    {'clave': 'RD', 'nombre': 'Recomendación al desempeño', 'tipo': 'preventiva', 'que': 'Sugerencia para que el ente cumpla sus objetivos y metas y ejerza sus recursos con eficiencia.', 'fundamento': 'Glosario de la MDB'},
    {'clave': 'PEFCF', 'nombre': 'Promoción del ejercicio de la facultad de comprobación fiscal', 'tipo': 'correctiva', 'que': 'Avisa al SAT de un posible incumplimiento fiscal detectado en la auditoría.', 'fundamento': 'LFRCF, art. 40, fr. III'},
    {'clave': 'SA', 'nombre': 'Solicitud de aclaración', 'tipo': 'correctiva', 'que': 'Pide al ente documentos adicionales que aclaren operaciones o montos no justificados.', 'fundamento': 'LFRCF, art. 40, fr. I'},
    {'clave': 'PRAS', 'nombre': 'Promoción de responsabilidad administrativa sancionatoria', 'tipo': 'correctiva', 'que': 'Da vista al órgano interno de control para que investigue y, en su caso, sancione.', 'fundamento': 'LFRCF, art. 40, fr. V'},
    {'clave': 'PO', 'nombre': 'Pliego de observaciones', 'tipo': 'correctiva', 'que': 'Fija en cantidad líquida un presunto daño o perjuicio a la Hacienda Pública o al patrimonio de un ente.', 'fundamento': 'LFRCF, art. 40, fr. II'},
]

CP2025A = {
    'entrega': 'primera', 'corte': 'junio de 2026', 'auditorias': 33,
    'universo': 301366198860.50, 'muestra': 301366198860.50, 'representatividad': 100.0,
    'acciones': 7, 'R': 6, 'RD': 0, 'PEFCF': 0, 'SA': 1, 'PRAS': 0, 'PO': 0,
    'recuperaciones': 20669471.05, 'porAclarar': 1403459.00,
    'que': 'Una auditoría a la SHCP, como coordinadora de la distribución de las participaciones federales, y una a cada una de las 32 entidades.',
    'fuente': 'MDB2025A', 'pagina': 11, 'estado': 'oficial',
}

REF_NUEVAS = [
    {'num': 80, 'id': 'ref-asf-mdb2024', 'categoria': 'fiscalizacion_auditoria', 'categoria_nombre': 'Fiscalización Superior y Auditoría',
     'cita_apa': 'Auditoría Superior de la Federación. (2026). Matriz de Datos Básicos del Informe del Resultado de la Fiscalización Superior de la Cuenta Pública 2024: primera, segunda y tercera entregas (consolidado). ASF.',
     'url': ASF + 'IR2024c/Documentos/Matriz/MDB_Consolidado.pdf',
     'descripcion': 'Resumen numérico oficial de la revisión de la Cuenta Pública 2024: 2,264 auditorías, 6,274 acciones, montos recuperados y montos por aclarar, por grupo funcional, sector y entidad federativa. Corte a febrero de 2026.'},
    {'num': 81, 'id': 'ref-asf-ir2025a', 'categoria': 'fiscalizacion_auditoria', 'categoria_nombre': 'Fiscalización Superior y Auditoría',
     'cita_apa': 'Auditoría Superior de la Federación. (2026). Informe del Resultado de la Fiscalización Superior de la Cuenta Pública 2025: primera entrega. ASF.',
     'url': ASF + 'IR2025a/index.html',
     'descripcion': 'Primera entrega de la revisión de la Cuenta Pública 2025 (junio de 2026): 33 auditorías a la distribución y pago de las participaciones federales, con su matriz de datos básicos.'},
]

CORRIGE = {
    'ref-lfrcf': {
        'cita_apa': 'Ley de Fiscalización y Rendición de Cuentas de la Federación [LFRCF]. Diario Oficial de la Federación, 18 de julio de 2016 (México). Última reforma publicada el 14 de mayo de 2026. Cámara de Diputados.',
        'descripcion': 'Regula la revisión de la Cuenta Pública por la Auditoría Superior de la Federación: las tres entregas de informes individuales (art. 35), el Informe General del 20 de febrero (art. 33), los plazos para responder (arts. 39 y 41) y las acciones que puede promover, como los pliegos de observaciones (art. 40).'},
    'ref-asf-cp': {
        'cita_apa': 'Auditoría Superior de la Federación. (2026). Informe del Resultado de la Fiscalización Superior de la Cuenta Pública 2024: tercera entrega e informes individuales. ASF.',
        'url': ASF + 'IR2024c/index.html',
        'descripcion': 'Portal oficial con los informes individuales de las 2,264 auditorías a la Cuenta Pública 2024, el Informe General Ejecutivo, los informes simplificados y la matriz de datos básicos.'},
}


def construir():
    m = json.loads(MDB.read_text(encoding='utf-8'))
    corta = lambda d: {k: d[k] for k in ('auditorias', 'universo', 'muestra', 'representatividad', 'acciones', 'R', 'RD', 'PEFCF', 'SA', 'PRAS', 'PO', 'recuperaciones', 'porAclarar') if k in d}
    return {
        'consulta': CONSULTA,
        'nota': 'Pesos corrientes. Los montos de la ASF vienen en miles de pesos y aquí se muestran en pesos. '
                'Un monto por aclarar no es un desfalco comprobado: es lo que, al cierre de la auditoría, '
                'carecía de documentación que acreditara el uso del dinero, y puede solventarse después.',
        'fuentes': FUENTES,
        'calendario': CALENDARIO,
        'plazos': PLAZOS,
        'acciones': ACCIONES,
        'cp2024': {
            'corte': m['corte'], 'entregas': m['entregas'], 'fuente': 'MDB2024', 'pagina': 11, 'estado': 'oficial',
            'total': corta(m['total']),
            'grupos': [{'grupo': g['grupo'], 'subtotal': corta(g['subtotal']),
                        'sectores': [dict(nombre=s['nombre'], **{k: s[k] for k in ('auditorias', 'acciones', 'PO', 'recuperaciones', 'porAclarar')}) for s in g['sectores']]}
                       for g in m['grupos']],
            'federalizado': corta(m['federalizadoTotal']),
            'coordinadoras': corta(m['federalizadoCoordinadoras']),
            'entidades': m['entidades'],
            'paginaEntidades': '19 a 23',
        },
        'cp2025': CP2025A,
    }


def main():
    b = BASE.read_bytes().decode('utf-8')
    b = insertar(b, 'cuenta_publica_asf', construir())
    ancla = '"id": "ref-cngmd2023"'
    i = b.index(ancla)
    fin = b.index('\r\n    }', i) + len('\r\n    }')
    for ref in reversed(REF_NUEVAS):
        if '"id": "%s"' % ref['id'] in b:
            continue
        cuerpo = ',\r\n    {\r\n' + ',\r\n'.join('      "%s": %s' % (k, _valor(v)) for k, v in ref.items()) + '\r\n    }'
        b = b[:fin] + cuerpo + b[fin:]
    for rid, campos in CORRIGE.items():
        i = b.index('"id": "%s"' % rid)
        fin = b.index('\r\n    }', i)
        bloque = b[i:fin]
        for k, v in campos.items():
            ini = bloque.index('"%s": ' % k)
            eol = bloque.find('\r\n', ini)
            eol = len(bloque) if eol < 0 else eol
            coma = ',' if bloque[ini:eol].rstrip().endswith(',') else ''
            bloque = bloque[:ini] + '"%s": %s' % (k, json.dumps(v, ensure_ascii=False)) + coma + bloque[eol:]
        b = b[:i] + bloque + b[fin:]
    BASE.write_bytes(b.encode('utf-8'))
    print('cuenta_publica_asf integrada')


if __name__ == '__main__':
    main()
