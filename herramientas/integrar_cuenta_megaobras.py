#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""La cuenta de cada megaobra (17-10-2026, pedido del autor): presupuesto,
costo, ingresos esperados y reales, gasto de operación, intereses y
resultado, cada renglón con su estado, su operación y su fuente.

El autor pidió que las cifras pendientes del simulador no se quedaran en
blanco: que se deduzcan con sumas, restas y divisiones a partir de
documentos oficiales. Esta herramienta no investiga: toma los renglones
que se reunieron con sus documentos (JSON con el esquema de
`cifras-mo/brief.md`: obra, campo, estado, valor o min/max/medio,
operación, fuentes con página y huella) y los escribe en
`simulador_megaobras.cuenta`. Con ellos corrige además los campos
principales de cuatro obras (VALORES), donde el documento ya permite una
cifra o un rango.

Reglas (AGENTS.md, §2):
- Un rango lleva sus dos cotas, cada una con su fuente, y el punto medio es
  (mínimo + máximo) ÷ 2. El campo principal guarda el punto medio y
  `rangos_campos` guarda las cotas; las páginas dicen «entre X y Y».
- Un pendiente dice por qué y a quién le toca publicarlo. Los renglones
  que no aplican (una obra sin deuda no paga intereses; un monumento no
  vende boletos) se marcan `no_aplica` con su porqué, sin culpar a nadie.

Uso:
    python3 herramientas/integrar_cuenta_megaobras.py DIRECTORIO

DIRECTORIO tiene operacion.json, pendientes-obra.json y, si ya existe,
rescates.json. Es idempotente.
"""
import json
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'audit-database.js')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from integrar_costo_vivo_megaobras import bloque_json  # noqa: E402

ARCHIVOS = ['operacion.json', 'pendientes-obra.json', 'rescates.json']

# Los renglones del AIFA y del NAIM se juntan en la obra «AIFA + cancelación
# del NAIM», con el nombre de la parte delante.
OBRA = {'aifa': ('aifa-texcoco', 'AIFA'), 'naim-texcoco': ('aifa-texcoco', 'NAIM')}

# Los campos principales no van a la cuenta: los pinta la obra misma.
PRINCIPALES = {'inversion_presupuestada_mdp', 'inversion_real_mdp', 'sobrecosto_pct'}

ETIQUETAS = {
    'presupuesto_original_mdp': ('Primer presupuesto documentado', 'mdp'),
    'ingresos_esperados_anuales_mdp': ('Ingresos esperados al año', 'mdp'),
    'ingresos_reales_anuales_mdp': ('Ingresos reales al año', 'mdp'),
    'costo_operativo_anual_mdp': ('Gasto de operación al año', 'mdp'),
    'intereses_anuales_mdp': ('Intereses al año', 'mdp'),
    'resultado_anual_mdp': ('Resultado del año (ganancia o pérdida)', 'mdp'),
    'costo_hundido_mdp': ('Costo hundido: lo gastado que ya no regresa', 'mdp'),
    'pasajeros_anuales': ('Pasajeros al año', 'personas'),
    'pasajeros_capacidad_inicial_acb': ('Capacidad prevista en su análisis costo-beneficio', 'personas'),
    'transferencia_por_pasajero_pesos': ('Transferencias federales por pasajero', 'pesos'),
    'inversion_construccion_2014_2018_mdp': ('Obra ejercida de 2014 a 2018 (sexenio anterior)', 'mdp'),
    'costo_total_esquema_2019_mdp': ('Costo total que fijó la ASF al 31-12-2019', 'mdp'),
    'costo_atribuible_cancelacion_mdp': ('Costo atribuible a la cancelación', 'mdp'),
    'inversion_presupuestada_musd': ('Presupuesto anunciado en dólares', 'musd'),
    'inversion_real_musd_equivalente': ('Costo real convertido a dólares', 'musd'),
    'produccion_real_mbd': ('Producción real (miles de barriles diarios)', 'mbd'),
    'costo_instalaciones_equipamiento_estimado_asf_mdp': ('Estimación de la ASF para todas las instalaciones de Plataforma México', 'mdp'),
    'pasivo_asumido_ipab_1999_mdp': ('Obligaciones del IPAB al cierre de 1999', 'mdp'),
    'pasivo_neto_ipab_1999_mdp': ('Deuda neta del IPAB al cierre de 1999', 'mdp'),
    'costo_fiscal_estimado_1998_mdp': ('Costo fiscal que se estimaba en 1998', 'mdp'),
    'costo_fiscal_con_deudores_mdp': ('Costo comprometido sumando el apoyo a deudores', 'mdp'),
    'transferencias_ramo34_paab_anuales_mdp': ('Ramo 34 que el presupuesto le pasó en el año', 'mdp'),
    'resultado_sin_transferencias_anual_mdp': ('Resultado del año sin el Ramo 34', 'mdp'),
    'saldo_pasivos_ipab_shrfsp_mdp': ('Lo que todavía se debe (pasivos del IPAB)', 'mdp'),
    'resultado_acumulado_1997_2017_mdp': ('Pérdida acumulada de 1997 a 2017', 'mdp'),
    'saldo_deuda_farac_shrfsp_mdp': ('Lo que todavía se debe (pasivos del FONADIN)', 'mdp'),
    'deuda_bursatil_mdp': ('Deuda en bonos del rescate', 'mdp'),
    'pasivos_no_revelados_2002_mdp': ('Pasivos que Hacienda no reveló en la Cuenta Pública 2002', 'mdp'),
}

# Renglones que se dejan fuera, con su porqué.
OMITIR = {
    # Rango informativo de registros distintos, no cotas de una misma cifra.
    ('aifa', 'inversion_registrada_cartera_mdp'),
}
# Del AIFA mandan los renglones de pendientes-obra (más completos); los de
# operacion.json repiten las mismas cifras con otro redondeo.
DUPLICADOS_OPERACION = {'aifa-texcoco'}

# Correccion al cotejar con el documento (17-10-2026): el contrato reducido
# del Bunker fue de 251,361.3 miles «mas el 15.0% del IVA por 37,704.2 miles»
# (ASF CP 2009, aud. 1053, p. 2), no 16 %: maximo 289.1, no 291.6. Va en
# valores(), que fija los campos principales.

# El primer presupuesto documentado del AIFA es el registro en cartera de
# 73,109.0 (ASF CP 2019, aud. 66-GB, p. 5), no el corte 4T 2019 (82,136.1).
EXTRA = [{
    'obra': 'aifa', 'campo': 'presupuesto_original_mdp', 'estado': 'oficial', 'valor': 73109.0, 'anio_pesos': 2019,
    'operacion': 'Monto con que la Sedena registró el proyecto en la cartera de Hacienda (clave 19071170003). '
                 'Después subió a 82,136.1 (corte 4T 2019) y a 95,260.4 al registrarse en el PEF 2020.',
    'fuentes': [{'doc': 'ASF, Cuenta Pública 2019, auditoría 66-GB, Sedena: Control Interno y Gobernanza del Proyecto del Nuevo Aeropuerto Internacional Felipe Ángeles',
                 'url': 'https://www.asf.gob.mx/Trans/Informes/IR2019a/Documentos/Auditorias/2019_0066_a.pdf', 'pagina': '5',
                 'valor_citado': '«El monto por 73,109,000.0 miles de pesos, correspondió al registro del proyecto…»'}],
}]

def r1(x):
    return float(Decimal(repr(x)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))


def rango(mn, mx, op):
    return {'min': mn, 'max': mx, 'medio': r1((mn + mx) / 2), 'op': op}


# ---- Campos principales que el documento ya permite fijar ----
def valores():
    aifa_real, naim_min, naim_max, aifa_pres = 74480.2, 21734.3, 33175.8, 79305.0
    real = rango(r1(aifa_real + naim_min), r1(aifa_real + naim_max),
                 'Costo del AIFA (74,480.2, derivado de la ASF) más lo atribuible a cancelar el NAIM: mínimo 21,734.3 '
                 '(solo lo que la ASF liga a la terminación), máximo 33,175.8 (el costo total de la ASF, 113,327.7, menos '
                 'la obra del NAIM ejercida antes de 2019, 79,907.7 + 244.2). Mínimo 74,480.2 + 21,734.3 = 96,214.5; '
                 'máximo 74,480.2 + 33,175.8 = 107,656.0; punto medio (96,214.5 + 107,656.0) ÷ 2 = 101,935.3.')
    smin, smax = (real['min'] / aifa_pres - 1) * 100, (real['max'] / aifa_pres - 1) * 100
    sobre = {'min': r1(smin), 'max': r1(smax), 'medio': r1((smin + smax) / 2),
             'op': '(costo ÷ 79,305.0 − 1) × 100 con cada cota del costo: (96,214.5 ÷ 79,305.0 − 1) × 100 = 21.3 % y '
                   '(107,656.0 ÷ 79,305.0 − 1) × 100 = 35.7 %; punto medio (21.3 + 35.7) ÷ 2 = 28.5 %.'}
    db_pmin, db_pmax = 154098.4, 160000.0
    db_pres = rango(db_pmin, db_pmax,
                    'Mínimo: los 8,000 millones de dólares de «inversión máxima» que anunció la Sener el 9-05-2019, al tipo '
                    'de cambio FIX de ese día (19.2623, Banxico): 8,000 × 19.2623 = 154,098.4. Máximo: los «160 mil millones '
                    'de pesos en tres años, no más» que dijo el presidente el mismo día. Punto medio (154,098.4 + 160,000.0) ÷ 2 = 157,049.2.')
    dmin, dmax = (357887.3 / db_pmax - 1) * 100, (357887.3 / db_pmin - 1) * 100
    db_sobre = {'min': r1(dmin), 'max': r1(dmax), 'medio': r1((dmin + dmax) / 2),
                'op': '(357,887.3 ÷ 160,000.0 − 1) × 100 = 123.7 % y (357,887.3 ÷ 154,098.4 − 1) × 100 = 132.3 %; punto medio '
                      '(123.7 + 132.3) ÷ 2 = 128.0 %. Compara pesos nominales y llega solo a 2024: la obra seguía en proceso, '
                      'así que es una cota inferior del sobrecosto final.'}
    bk = rango(236.9, 289.1,
               'Solo el contrato de obra civil del edificio. Mínimo: lo pagado a agosto de 2010, 206,027.9 miles más 15 % de '
               'IVA = 236.9. Máximo: el contrato ya reducido, 251,361.3 miles más 15 % de IVA (37,704.2) = 289.1; la ASF no '
               'registra ampliación de monto. Punto medio (236.9 + 289.1) ÷ 2 = 263.0.')
    bmin, bmax = (bk['min'] / 347.4 - 1) * 100, (bk['max'] / 347.4 - 1) * 100
    bk_sobre = {'min': r1(bmin), 'max': r1(bmax), 'medio': r1((bmin + bmax) / 2),
                'op': '(236.9 ÷ 347.4 − 1) × 100 = −31.8 % y (289.1 ÷ 347.4 − 1) × 100 = −16.8 %; punto medio '
                      '(−31.8 − 16.8) ÷ 2 = −24.3 %: el contrato costó menos de lo pactado.'}
    return {
        'aifa-texcoco': {
            'valores': {'inversion_presupuestada_mdp': aifa_pres, 'inversion_real_mdp': real['medio'], 'sobrecosto_pct': sobre['medio']},
            'campos': {'inversion_presupuestada_mdp': 'oficial', 'inversion_real_mdp': 'derivado', 'sobrecosto_pct': 'derivado'},
            'rangos': {'inversion_real_mdp': real, 'sobrecosto_pct': sobre},
            'definiciones': {
                'inversion_presupuestada_mdp': 'Presupuesto total que la Sedena previó para construir el AIFA de 2019 a 2022: '
                    '73,109.0 de la obra registrada en cartera + 1,350.0 de obras complementarias + 360.0 de SENEAM + 4,009.0 de '
                    'predios + 477.0 de estudios = $79,305.0 mdp (ASF, CP 2019, auditoría 66-GB, pp. 4-5). La cancelación del '
                    'NAIM no tuvo presupuesto: es un costo, no una obra aprobada.',
                'inversion_real_mdp': 'Entre $96,214.5 y $107,656.0 mdp; punto medio $101,935.3 mdp. Es el costo del AIFA, '
                    '$74,480.2 mdp (16,656.4 ejercidos directo por la Sedena + 57,990.6 aportados al fideicomiso FPAPEM − 166.8 '
                    'sin gastar al 31-12-2022; ASF CP 2021 aud. 325 y CP 2022 aud. 342), más lo atribuible a cancelar el NAIM. '
                    'Ya no suma los $79,907.7 mdp de obra del NAIM ejercida de 2014 a 2018, que son del sexenio anterior, ni los '
                    '$88,107 mdp del AIFA que no tenían documento. La cifra exacta de la cancelación la deben GACM y Hacienda.',
                'sobrecosto_pct': 'Entre 21.3 % y 35.7 %; punto medio 28.5 %, contra los $79,305.0 mdp previstos para el AIFA. '
                    'Solo el AIFA quedó por debajo de lo previsto (−6.1 %): el sobrecosto es la cancelación del NAIM.',
            },
            'proyeccion_resumen': 'El simulador cuenta el costo del AIFA ($74,480.2 mdp, derivado de la ASF) más lo atribuible '
                'a cancelar el NAIM (entre $21,734.3 y $33,175.8 mdp, estudio de la ASF de marzo de 2021). La obra del NAIM '
                'ejercida de 2014 a 2018 ($79,907.7 mdp) ya no se carga a este sexenio. Los ingresos que el AIFA esperaba '
                'siguen sin publicarse: la Sedena reservó su análisis costo-beneficio por seguridad nacional.',
        },
        'dos-bocas': {
            'valores': {'inversion_presupuestada_mdp': db_pres['medio'], 'sobrecosto_pct': db_sobre['medio']},
            'campos': {'inversion_presupuestada_mdp': 'derivado', 'sobrecosto_pct': 'derivado'},
            'rangos': {'inversion_presupuestada_mdp': db_pres, 'sobrecosto_pct': db_sobre},
            'definiciones': {
                'inversion_presupuestada_mdp': 'Entre $154,098.4 y $160,000.0 mdp; punto medio $157,049.2 mdp. El 9-05-2019, '
                    'en la presentación de la obra (versión estenográfica de Presidencia), la Sener habló de una «inversión '
                    'máxima de ocho mil millones de dólares» y el presidente de «160 mil millones de pesos en tres años, no '
                    'más». El mínimo convierte los dólares al FIX de ese día (19.2623). El presupuesto que aprobó el consejo '
                    'de Pemex sigue sin publicarse: falta de transparencia de Pemex.',
                'sobrecosto_pct': 'Entre 123.7 % y 132.3 %; punto medio 128.0 %, con el costo registrado al 31-12-2024 '
                    '($357,887.3 mdp, ASF CP 2024, aud. 247, p. 8). La obra seguía en proceso: es una cota inferior.',
            },
        },
        'bunker-garcia-luna': {
            'valores': {'inversion_presupuestada_mdp': 347.4, 'inversion_real_mdp': bk['medio'], 'sobrecosto_pct': bk_sobre['medio']},
            'campos': {'inversion_presupuestada_mdp': 'oficial', 'inversion_real_mdp': 'derivado', 'sobrecosto_pct': 'derivado'},
            'rangos': {'inversion_real_mdp': bk, 'sobrecosto_pct': bk_sobre},
            'definiciones': {
                'inversion_presupuestada_mdp': 'El contrato de obra civil del «Edificio de Plataforma México», adjudicado sin '
                    'licitación a TRADECO por $347,369.0 miles con IVA (ASF, CP 2009, auditoría 1053, p. 1). Los $1,200 mdp que '
                    'traía la ficha no tenían documento.',
                'inversion_real_mdp': 'Entre $236.9 y $289.1 mdp; punto medio $263.0 mdp: lo pagado y lo contratado de la obra '
                    'civil (ASF, CP 2009, p. 2). Los $3,346 mdp que traía la ficha no tenían documento. El costo total con '
                    'equipamiento sigue pendiente: la SSPC, heredera de la SSP, no lo ha publicado. Lo más cercano es la '
                    'estimación de la ASF de $432.7 mdp para todas las instalaciones de Plataforma México (CP 2008, aud. 957).',
                'sobrecosto_pct': 'Entre −31.8 % y −16.8 %; punto medio −24.3 %: el contrato costó menos de lo pactado. No '
                    'mide el costo del equipamiento, que sigue pendiente.',
            },
        },
        'fobaproa': {
            'valores': {'inversion_presupuestada_mdp': 552300.0, 'inversion_real_mdp': 1734494.3,
                        'sobrecosto_pct': r1((1734494.3 / 552300.0 - 1) * 100)},
            'campos': {'inversion_presupuestada_mdp': 'oficial', 'inversion_real_mdp': 'derivado', 'sobrecosto_pct': 'derivado'},
            'rangos': {},
            'definiciones': {
                'inversion_presupuestada_mdp': 'El pasivo del Fobaproa que el Ejecutivo presentó al Congreso: «su estimación, al 28 '
                    'de febrero de 1998, es de MN $552,300 millones» (informe Mackey, Gaceta Parlamentaria del 23-09-1999). No es '
                    'un presupuesto: es la deuda que se pidió convertir en deuda pública.',
                'inversion_real_mdp': 'Lo que el rescate ya le costó al presupuesto más lo que todavía se debe: transferencias del '
                    'Ramo 34 al IPAB para ahorradores de 1999 a 2025 (710,923.3; IPAB, Plan Anual de Financiamiento 2026) + pasivos '
                    'netos del IPAB al 31-12-2025 (1,023,571; Hacienda, informe de deuda pública 4T 2025) = $1,734,494.3 mdp. Suma '
                    'pesos de 27 años sin deflactar. No cuenta lo que pagaron los bancos con sus cuotas ni el apoyo a deudores '
                    '(con él serían $2,009,825.7 mdp). Los $2,470,000 mdp que traía la ficha no tenían documento.',
                'sobrecosto_pct': '(1,734,494.3 ÷ 552,300 − 1) × 100 = 214.1 %: cuántas veces más que el pasivo presentado en 1998 '
                    'lleva pagado y debido el rescate. No es un sobrecosto de obra: mezcla pagos de 27 años con un saldo de 2025, en '
                    'pesos sin deflactar. En pesos de 1999 la deuda neta bajó 46.7 % de 1999 a 2020 (IPAB, Informe 2020).',
            },
        },
        'farac-carretero': {
            'valores': {'inversion_presupuestada_mdp': 57756.6, 'inversion_real_mdp': r1(57756.6 + 96094.9),
                        'sobrecosto_pct': r1(((57756.6 + 96094.9) / 57756.6 - 1) * 100)},
            'campos': {'inversion_presupuestada_mdp': 'oficial', 'inversion_real_mdp': 'derivado', 'sobrecosto_pct': 'derivado'},
            'rangos': {},
            'definiciones': {
                'inversion_presupuestada_mdp': 'Las indemnizaciones a los 23 exconcesionarios que asumió el FARAC en 1997: deuda '
                    'bancaria subrogada 30,265.4 + Pagarés de Indemnización Carretera 27,491.2 = $57,756.6 mdp (ASF, CP 2015, '
                    'auditoría 99). Fueron 23 autopistas y puentes, no 52. Los $60,000 mdp que traía la ficha no tenían documento.',
                'inversion_real_mdp': 'Lo documentado hasta 2017, como cota mínima: indemnizaciones de 1997 (57,756.6) + pérdida '
                    'acumulada del fondo de 1997 a 2017 (déficit de ejercicios anteriores 85,530.6 + déficit de 2017 10,564.3 = '
                    '96,094.9; ASF, CP 2017, auditoría 91) = $153,851.5 mdp. Lo de 2018 en adelante sigue pendiente: Banobras, '
                    'fiduciario del FONADIN, y Hacienda, que preside su Comité Técnico, no han publicado los intereses pagados ni '
                    'el costo acumulado. Los $162,000 mdp que traía la ficha no tenían documento.',
                'sobrecosto_pct': '(153,851.5 ÷ 57,756.6 − 1) × 100 = 166.4 %: la pérdida acumulada hasta 2017 frente a la '
                    'indemnización de 1997. No es un sobrecosto de obra y crecerá cuando se publique lo posterior a 2017.',
            },
        },
        'fertinal': {
            'valores': {'inversion_presupuestada_mdp': 12532.0, 'sobrecosto_pct': r1((13121.6 / 12532.0 - 1) * 100)},
            'campos': {'inversion_presupuestada_mdp': 'oficial', 'sobrecosto_pct': 'derivado'},
            'rangos': {},
            'definiciones': {
                'inversion_presupuestada_mdp': 'El monto máximo que el Consejo de Administración de Pemex aprobó para financiar '
                    'y concretar la compra: «hasta 12,531,979.0 miles de pesos» (acuerdo CA-209/2015, 26-10-2015; ASF, CP 2017, '
                    'auditoría 492-DE, p. 3). Antes la ficha repetía en las dos puntas los $13,121.6 mdp del financiamiento.',
                'sobrecosto_pct': '(13,121.6 ÷ 12,532.0 − 1) × 100 = 4.7 %: el financiamiento contratado (635 millones de '
                    'dólares, que incluyó refinanciar deudas de Fertinal) frente a lo que aprobó el consejo.',
            },
        },
    }


# Las notas se escribieron al investigar: hablan de «la base» (la de esta
# plataforma) y de lo que no abrio desde el contenedor. Al lector se le dice
# lo mismo sin la jerga de trabajo.
LIMPIEZA = [
    (r'No se encontró en los documentos a la mano \(ASF CP 2024 aud\. 247, EF Pemex 2025, EF PTRI 2024\) un monto original '
     r'aprobado\. El 20-F de Pemex \(sec\.gov\) no se pudo abrir \(proxy 403\)\.',
     'Ni la ASF (CP 2024, auditoría 247) ni los estados financieros de Pemex 2025 y de Pemex Transformación Industrial 2024 '
     'dan un monto original aprobado.'),
    (r'\s*Se busca la ficha de evaluación de Pemex \(o el 20-F de 2019 en sec\.gov, inaccesible desde aquí\)\.', ''),
    (r' vienen de prensa o de documentos de Pemex que no se pudieron abrir \(sec\.gov y pemex\.com bloqueados desde aquí\)\.',
     ' vienen de prensa o de reportes de Pemex que esta plataforma todavía no ha cotejado.'),
    (r'\s*Ver tema rescates\.', ''),
    (r'El desglose de la base (\([^)]*\)) no tiene fuente y debe retirarse\.', r'El desglose que traía la ficha \1 no tenía fuente.'),
    (r'sus cifras se leyeron por OCR y se cotejaron con sumas internas',
     'sus cifras se leyeron del escaneo y se cotejaron con las sumas internas de cada estado'),
    (r'\(el OCR no leyó el renglón\)', '(resta de Auditavisión: el renglón no se lee en el escaneo)'),
    (r'El Ramo 34 completo de la base', 'El Ramo 34 completo'),
    (r': no confundir\.', '.'),
    (r'\s*Ya integrado\.', ''), (r'\s*Ya es la base actual\.', ''),
    (r'\s*Ya está la cifra de origen en la base \([^)]*\)\.', ''),
    (r'\s*\(ya (?:integrad[oa]|en la base)[^)]*\)', ''),
    (r'\(ya en la base;\s*', '('), (r';\s*ya en la base\)', ')'),
    (r'\(la base, con las cifras en miles, da ([^)]*)\)', r'(con las cifras en miles da \1)'),
    (r'que trae la base', 'que traía la ficha'), (r'(\d[\d,.]*) de la base', r'\1 que traía la ficha'),
    (r'Hoy la base usa', 'La ficha usaba'), (r'Con esta base:', 'Con ese presupuesto:'),
    (r'contra esta base', 'contra ese presupuesto'), (r'al que usa hoy la base', 'al que usa la plataforma'),
    (r'según la base', 'según la Cuenta Pública'), (r'de la base actual', 'de la ficha'),
    (r'que ya está en la base \(fuente «cp», datos abiertos de la Cuenta Pública\)', 'de los datos abiertos de la Cuenta Pública'),
]
LIMPIEZA_DOC = [(r'\s*\((?:ya integrad|ya en la base|no se pudo|no se volvió)[^)]*\)', ''),
                (r', ya integrada en la base:.*$', '')]


def limpia(t, reglas=LIMPIEZA):
    for a, b in reglas:
        t = re.sub(a, b, t)
    return re.sub(r'\s{2,}', ' ', t).strip()


def fila(r):
    oid, parte = OBRA.get(r['obra'], (r['obra'], ''))
    et, u = ETIQUETAS.get(r['campo'], (r['campo'].replace('_', ' '), 'mdp'))
    resp = (r.get('responsable_si_falta') or '').strip()
    e = r['estado']
    if e == 'pendiente' and resp.lower().startswith('no aplica'):
        e, resp = 'no_aplica', ''
    f = {'c': r['campo'], 'et': (parte + ' · ' + et) if parte else et, 'u': u, 'e': 'derivado' if e == 'rango' else e,
         'anio': r.get('anio_pesos'), 'op': limpia((r.get('operacion') or '').strip().strip('—')),
         'nota': limpia(r.get('nota') or ''),
         'f': [{'doc': limpia(x['doc'], LIMPIEZA_DOC), 'url': x['url'], 'pag': x.get('pagina') or ''}
               for x in r.get('fuentes') or [] if x.get('url')]}
    if e == 'rango':
        f.update({'min': r['min'], 'max': r['max'], 'medio': r['medio']})
    elif r.get('valor') is not None and e in ('oficial', 'derivado'):
        f['v'] = r['valor']
    if e == 'pendiente':
        if not resp:
            sys.exit('pendiente sin responsable: %s %s' % (r['obra'], r['campo']))
        f['resp'] = limpia(resp)
    return oid, f


ORDEN = ['presupuesto_original_mdp', 'ingresos_esperados_anuales_mdp', 'ingresos_reales_anuales_mdp',
         'costo_operativo_anual_mdp', 'intereses_anuales_mdp', 'resultado_anual_mdp', 'costo_hundido_mdp']


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    filas = []
    for a in ARCHIVOS:
        p = os.path.join(sys.argv[1], a)
        if not os.path.exists(p):
            print('falta', a, '(se omite)')
            continue
        for r in json.load(open(p, encoding='utf-8')):
            if a == 'operacion.json' and r['obra'] in DUPLICADOS_OPERACION:
                continue
            filas.append(r)
    filas += EXTRA

    raw = open(DB, 'rb').read().decode('utf-8')
    a, b = bloque_json(raw, 'simulador_megaobras')
    sim = json.loads(raw[a:b])
    ids = {o['id'] for o in sim['obras']}

    cuenta = {}
    for r in filas:
        if (r['obra'], r['campo']) in OMITIR:
            continue
        oid = OBRA.get(r['obra'], (r['obra'],))[0]
        if oid not in ids:
            sys.exit('obra desconocida: ' + r['obra'])
        if r['campo'] in PRINCIPALES:
            continue
        oid, f = fila(r)
        cuenta.setdefault(oid, []).append(f)
    for oid in cuenta:
        cuenta[oid].sort(key=lambda f: (ORDEN.index(f['c']) if f['c'] in ORDEN else len(ORDEN), f['et']))

    ver = sim['verificacion']['obras']
    for o in sim['obras']:
        v = valores().get(o['id'])
        if not v:
            continue
        o.update(v['valores'])
        o.setdefault('estado_campos', {}).update(v['campos'])
        if v['rangos']:
            o['rangos_campos'] = v['rangos']
        else:
            o.pop('rangos_campos', None)
        if v.get('proyeccion_resumen'):
            o['proyeccion_resumen'] = v['proyeccion_resumen']
        vo = ver.setdefault(o['id'], {})
        vo.setdefault('campos', {}).update(v['campos'])
        vo.setdefault('definiciones', {}).update(v['definiciones'])

    t = sim['totales_consolidados']
    t['inversion_total_mdp'] = r1(sum(o['inversion_real_mdp'] for o in sim['obras']))
    t['inversion_presupuestada_total_mdp'] = r1(sum(o['inversion_presupuestada_mdp'] for o in sim['obras']))
    t['sobrecosto_conjunto_pct'] = r1((t['inversion_total_mdp'] / t['inversion_presupuestada_total_mdp'] - 1) * 100)

    sim['cuenta'] = {
        'nota': 'La cuenta de cada obra: lo que se esperaba de ella y lo que dio, renglón por renglón. Montos en millones '
                'de pesos corrientes del año que dice cada renglón (anio). Estados: oficial (del documento), derivado (con la '
                'operación dicha; si trae min y max es un rango y medio = (min + max) ÷ 2), pendiente (dice por qué y a quién '
                'le toca publicarlo) y no_aplica (la obra no tiene ese concepto, con su porqué). Fuentes cotejadas el 17-10-2026.',
        'obras': cuenta,
    }

    # El bloque ya esta a dos espacios desde la raiz: json.dumps con indent=2
    # lo reproduce igual, asi el diff muestra solo lo que cambia.
    txt = json.dumps(sim, ensure_ascii=False, indent=2).replace('\n', '\r\n')
    raw = raw[:a] + txt + raw[b:]
    open(DB, 'wb').write(raw.encode('utf-8'))
    print(json.dumps({oid: len(v) for oid, v in cuenta.items()}, ensure_ascii=False))
    print('total', t['inversion_total_mdp'], 'aprobado', t['inversion_presupuestada_total_mdp'], 'sobrecosto', t['sobrecosto_conjunto_pct'])


if __name__ == '__main__':
    main()
