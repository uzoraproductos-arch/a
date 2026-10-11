#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fichas del compendio de fuentes para «Crisis ambientales», la quinta
aplicacion de Costo Ambiental (11-10-2026). Cada documento se abrio y se
cotejo antes de citarlo; las paginas y las citas estan en
herramientas/crisis_ambientales.py.

    python3 herramientas/anclar_crisis.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from integrar_glosario_modulos import _cuerpo  # noqa: E402

BASE = pathlib.Path(__file__).resolve().parent.parent / 'assets' / 'auditor' / 'js' / 'audit-database.js'

REF_NUEVAS = [
    {'num': 120, 'id': 'ref-cenapred-impacto-2023', 'categoria': 'estadistica_oficial',
     'categoria_nombre': 'Estadística Oficial del Estado Mexicano',
     'cita_apa': 'Centro Nacional de Prevención de Desastres. (2024). Impacto socioeconómico de los desastres en México durante 2023: resumen ejecutivo. CENAPRED.',
     'url': 'https://www.cenapred.gob.mx/es/Publicaciones/archivos/504-RESUMENEJECUTIVOIMPACTO2023.PDF',
     'descripcion': 'Daños y pérdidas por desastres en 2023. El cuadro 1.2 (p. 8) estima el huracán Otis en $84,207 millones de pesos corrientes; el texto de la p. 6 le atribuye $88,910 millones, que es el total de todo el año. La plataforma usa el cuadro y anota la diferencia.'},
    {'num': 121, 'id': 'ref-cenapred-impacto-2024', 'categoria': 'estadistica_oficial',
     'categoria_nombre': 'Estadística Oficial del Estado Mexicano',
     'cita_apa': 'Centro Nacional de Prevención de Desastres. (2025). Impacto socioeconómico de los desastres en México durante 2024: resumen ejecutivo. CENAPRED.',
     'url': 'https://www.cenapred.gob.mx/es/Publicaciones/archivos/521-RESUMENEJECUTIVOIMPACTO2024.PDF',
     'descripcion': 'Daños y pérdidas por desastres en 2024: $14,434 millones de pesos, 0.046% del PIB (p. 6). Recuerda los años más costosos de la serie 2000-2024: 2010 ($92,300 millones), 2017 (más de $88,400 millones) y 2023 ($88,910 millones). La serie año por año solo se publica como gráfica (figura 1.1), sin cuadro.'},
    {'num': 122, 'id': 'ref-asf-cp2023-0362', 'categoria': 'fiscalizacion_auditoria',
     'categoria_nombre': 'Fiscalización Superior y Auditoría',
     'cita_apa': 'Auditoría Superior de la Federación. (2024). Informe individual de la auditoría 2023-0-07100-19-0362-2024: Secretaría de la Defensa Nacional, adquisición de enseres. Fiscalización Superior de la Cuenta Pública 2023, segunda entrega.',
     'url': 'https://www.asf.gob.mx/Trans/Informes/IR2023b/Documentos/Auditorias/2023_0362_a.pdf',
     'descripcion': 'Revisa las compras de enseres para la emergencia del huracán Otis. Encuentra 12 contratos adjudicados de manera directa por $1,065,798.2 miles de pesos, y bienes que no estaban en el programa de compras. Promueve 1 ejercicio de la facultad de comprobación fiscal y 2 responsabilidades administrativas sancionatorias; no cuantifica un monto por aclarar.'},
    {'num': 123, 'id': 'ref-asf-cp2024-0353', 'categoria': 'fiscalizacion_auditoria',
     'categoria_nombre': 'Fiscalización Superior y Auditoría',
     'cita_apa': 'Auditoría Superior de la Federación. (2025). Informe individual de la auditoría 353: Secretaría de la Defensa Nacional, adquisición de enseres. Fiscalización Superior de la Cuenta Pública 2024, segunda entrega.',
     'url': 'https://www.asf.gob.mx/Trans/Informes/IR2024b/Documentos/Auditorias/2024_0353_a.pdf',
     'descripcion': 'Revisa $442,234.9 miles de pesos pagados por refrigeradores y estufas. De 13 resultados, en 4 no se detectaron irregularidades y 9 fueron solventados; el dictamen es limpio.'},
    {'num': 124, 'id': 'ref-dof-otis-desastre', 'categoria': 'estadistica_oficial',
     'categoria_nombre': 'Estadística y Documentos Oficiales',
     'cita_apa': 'Coordinación Nacional de Protección Civil. (2023, 2 de noviembre). Declaratoria de Desastre Natural por la ocurrencia de lluvia severa, vientos fuertes, inundación fluvial y pluvial el 24 y 25 de octubre de 2023 en 47 municipios del Estado de Guerrero. Diario Oficial de la Federación.',
     'url': 'https://dof.gob.mx/nota_detalle.php?codigo=5707457&fecha=02/11/2023',
     'descripcion': 'Declaratoria de desastre por el huracán Otis. La nota aclaratoria del 3 de noviembre de 2023 la deja en dos municipios: Acapulco de Juárez y Coyuca de Benítez (DOF, código 5707645). La de emergencia se publicó el 30 de octubre de 2023 (código 5707225).'},
    {'num': 125, 'id': 'ref-shcp-plan-otis', 'categoria': 'hacendario_fiscal', 'categoria_nombre': 'Hacendario y Fiscal',
     'cita_apa': 'Gobierno de México. (2023, 1 de noviembre). Inicia plan de reconstrucción en Guerrero por 61 mil 313 mdp: presidente AMLO [Comunicado]. Archivo de la Presidencia 2018-2024, gob.mx.',
     'url': 'https://www.gob.mx/amlo/prensa/inicia-plan-de-reconstruccion-en-guerrero-por-61-mil-313-mdp-presidente-amlo',
     'descripcion': 'El secretario de Hacienda presenta el costo del Plan General de Reconstrucción de Acapulco y Coyuca de Benítez: «61 mil 313 millones de pesos», en 20 renglones, dos de ellos «por determinar». El plan firmado el 31 de octubre de 2023 no trae el total.'},
]


def main():
    b = BASE.read_bytes().decode('utf-8')
    ancla = b.index('"id": "ref-gomez-granillo-1995"')
    corte = b.index('\r\n    }', ancla) + len('\r\n    }')
    nuevas = 0
    for ref in reversed(REF_NUEVAS):
        if '"id": "%s"' % ref['id'] not in b:
            b = b[:corte] + ',\r\n' + _cuerpo(ref) + b[corte:]
            nuevas += 1
    BASE.write_bytes(b.encode('utf-8'))
    print('crisis: %d fichas nuevas' % nuevas)


if __name__ == '__main__':
    main()
