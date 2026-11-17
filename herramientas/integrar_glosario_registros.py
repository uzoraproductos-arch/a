#!/usr/bin/env python3
"""Agrega al glosario el registro de deudores alimentarios y el de garantías
mobiliarias (pedido del autor, 17-11-2026: integrar las garantías y los
deudores alimentarios «por el momento electoral»).

Uso:
    python3 herramientas/integrar_glosario_registros.py

Cada definición sale de su ley, citada en «ley» (textos vigentes de la Cámara
de Diputados): Constitución (última reforma DOF 07-10-2026), Ley General de
los Derechos de Niñas, Niños y Adolescentes (última reforma DOF 15-01-2026) y
Código de Comercio (última reforma DOF 14-11-2025). Usa las mismas funciones
de integrar_glosario_fiscalizacion.py: es idempotente.
"""
import integrar_glosario_fiscalizacion as g

RUG_VIEJA = ('El registro de la Secretaría de Economía donde se inscriben las garantías sobre bienes muebles que respaldan un crédito o una obligación '
             'mercantil: la prenda sin transmisión de posesión, el arrendamiento y el factoraje financieros, la reserva de dominio, el fideicomiso de '
             'garantía y los embargos sobre bienes muebles, entre otros. Inscribirlas hace que valgan frente a terceros y les da prelación. Es una '
             'sección del Registro Público de Comercio y funciona en línea; la consulta pide cuenta de usuario, y las certificaciones se pagan. '
             'No es una lista de fianzas de contratos con el gobierno ni de personas sancionadas.')
RUG_DEF = ('El registro de la Secretaría de Economía donde se inscriben las garantías sobre bienes muebles que respaldan un crédito o una obligación '
           'mercantil. No es una lista de fianzas de contratos con el gobierno ni de personas sancionadas. Ahí van la prenda sin transmisión de '
           'posesión, el arrendamiento y el factoraje financieros, la reserva de dominio, el fideicomiso de garantía y los embargos sobre bienes '
           'muebles, entre otros. Inscribirlas hace que valgan frente a terceros y les da prelación. Es una sección del Registro Público de Comercio '
           'y funciona en línea; la consulta pide cuenta de usuario, y las certificaciones se pagan.')

g.TERMINOS = [
    {'termino': 'Deudor Alimentario Moroso',
     'definicion': 'La persona a quien un juez declaró en incumplimiento de la pensión de alimentos que debe, casi siempre a sus hijas e hijos. '
                   'Se inscribe en el Registro Nacional de Obligaciones Alimentarias, a cargo del Sistema Nacional DIF, con su nombre, su CURP, su RFC, '
                   'el juzgado y el expediente. Mientras lo sea, no puede registrarse como candidato a un cargo de elección popular ni ser nombrado en el '
                   'servicio público, y se le puede exigir el certificado de no inscripción para el pasaporte, la licencia de conducir o ante notario. '
                   'El certificado lo pide cada persona, gratis. Auditavisión no copia ese registro ni publica nombres.',
     'ley': 'Art. 38, fr. VII Constitución (DOF 29-05-2023) · Arts. 135 Bis a 135 Septies Ley General de los Derechos de Niñas, Niños y Adolescentes (DOF 08-05-2023)'},
    {'termino': 'Registro Único de Garantías Mobiliarias (RUG)',
     'definicion': RUG_DEF,
     'ley': 'Arts. 32 bis 1 a 32 bis 9 Código de Comercio (sección adicionada DOF 27-08-2009, reformada DOF 13-06-2014)'},
]
g.CORRECCIONES_GLOSARIO = [('Registro Único de Garantías Mobiliarias (RUG)', 'definicion', RUG_VIEJA, RUG_DEF)]
g.REF_NUEVAS = []
g.CORRECCIONES_REF = []

if __name__ == '__main__':
    g.main()
