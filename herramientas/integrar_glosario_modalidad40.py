#!/usr/bin/env python3
"""Agrega al glosario la continuación voluntaria (Modalidad 40), para la nota
«Al momento» del IMSS (pedido del autor, 28-10-2026: «si un concepto no está
bien claro, nosotros podérselo describir a través de nuestro glosario»).

Uso:
    python3 herramientas/integrar_glosario_modalidad40.py

La definición sale de sus fuentes, citadas en «ley»: Ley del Seguro Social,
texto vigente (última reforma DOF 15-01-2026), arts. 218 a 220, y el Acuerdo
ACDO.AS2.HCT.101026/302.P.DG del Consejo Técnico del IMSS (DOF 21-10-2026).

Usa las mismas funciones de integrar_glosario_fiscalizacion.py: es
idempotente y no duplica términos.
"""
import integrar_glosario_fiscalizacion as g

g.FIS = '👷 Trabajo y Salario'
g.TERMINOS = [
    {'termino': 'Continuación Voluntaria (Modalidad 40)',
     'definicion': 'El derecho de quien deja de tener patrón a seguir cotizando por su cuenta al IMSS para su pensión: los seguros de invalidez '
                   'y vida y de retiro, cesantía y vejez, pero no el de enfermedades y maternidad. Se pide dentro de los cinco años siguientes '
                   'a la baja, con al menos 52 semanas cotizadas en los últimos cinco años, y las cuotas se pagan por mes adelantado. La ley '
                   'dice que te inscribes con tu último salario o uno superior; desde el 22 de octubre de 2026, como medida temporal, el IMSS '
                   'limita a los nuevos inscritos a su último salario registrado o hasta ese salario más una UMA, sin pagos hacia atrás.',
     'ley': 'Arts. 218, 219 y 220 Ley del Seguro Social (última reforma DOF 15-01-2026) · Acuerdo ACDO.AS2.HCT.101026/302.P.DG del '
            'Consejo Técnico del IMSS, punto cuarto (DOF 21-10-2026)'},
]
g.CORRECCIONES_GLOSARIO = []
g.REF_NUEVAS = []
g.CORRECCIONES_REF = []

if __name__ == '__main__':
    g.main()
