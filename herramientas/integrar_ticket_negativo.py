"""Integra la coleccion ticket_negativo en assets/js/audit-database.js.

La usa el bloque 2 del modulo 5 (Costo Ambiental): el ticket ciudadano en
negativo reparte por habitante la deuda publica total, los intereses de la
deuda y el dano ambiental. Aqui solo vive la cifra que la base no tenia: el
Saldo Historico de los Requerimientos Financieros del Sector Publico
(SHRFSP) estimado al cierre de 2026. Los intereses (PEF 2026, Anexo 8), el
dano ambiental (INEGI) y la poblacion (CONAPO) se leen de sus colecciones.

Extracto de la pagina en investigaciones/fuentes-ambiente/.
Uso: python3 herramientas/integrar_ticket_negativo.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from integrar_ambiente import insertar  # noqa: E402

BASE = pathlib.Path(__file__).resolve().parent.parent / 'assets' / 'js' / 'audit-database.js'

DATOS = {
    'consulta': '26 de septiembre de 2026',
    'nota': ('Cada renglón del ticket reparte una cifra oficial entre los habitantes del país. '
             'Es un promedio: nadie firma la deuda pública ni causa el daño ambiental a partes iguales, '
             'pero todos lo pagamos con impuestos, servicios y salud.'),
    'fuentes': {
        'CGPE27': {
            'corto': 'SHCP, Criterios Generales de Política Económica 2027',
            'doc': ('Secretaría de Hacienda y Crédito Público, Criterios Generales de Política Económica '
                    'para 2027, Gaceta Parlamentaria, año XXIX, núm. 7121-C, 8 de septiembre de 2026'),
            'url': 'https://gaceta.diputados.gob.mx/PDF/66/2026/sep/20260908-C.pdf',
            'sha256': '5978f0631d2c88165b54bfce9c3fed2b8cca45eb44b3f267f3025c88f3c6d66a'
        }
    },
    'shrfsp': {
        'nombre': 'Saldo Histórico de los Requerimientos Financieros del Sector Público (SHRFSP)',
        'que': ('La medida más amplia de la deuda pública: deuda del Gobierno Federal, de Pemex y CFE, '
                'de la banca de desarrollo, pasivos del IPAB y de los proyectos de inversión diferida. '
                'Es lo que el sector público debe, acumulado a lo largo de los años.'),
        'estimado2026_mdp': 20062321.6,
        'estimado2026_pib': 54.0,
        'aprobado2026_mdp': 20259590.7,
        'estimado2027_mdp': 21665995.8,
        'estado': 'oficial',
        'fuente': 'CGPE27',
        'pagina': '67, cuadro «Estimación de las finanzas públicas, 2026-2027», columna 2026 estimado'
    }
}


def main():
    b = BASE.read_bytes().decode('utf-8')
    b = insertar(b, 'ticket_negativo', DATOS)
    BASE.write_bytes(b.encode('utf-8'))
    print('ticket_negativo integrada')


if __name__ == '__main__':
    main()
