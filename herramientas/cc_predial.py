# -*- coding: utf-8 -*-
"""Octava aplicación de la Calculadora Cívica: «Tu impuesto predial, según tu
municipio» (19-11-2026, pedido del autor: «un simulador del impuesto predial
con sus correspondientes filtros y montos según el municipio», con un
mandamiento de ejecución de Zapopan por falta de pago como ejemplo; y «en las
leyes de ingresos municipales también vendrán los montos: cambian por
municipios»).

**Cada municipio cobra el predial con su propia Ley de Ingresos** (Constitución,
art. 115, fr. IV; Ley de Hacienda Municipal del Estado de Jalisco, art. 103,
último párrafo): la tabla, los descuentos y los accesorios cambian de uno a
otro. Por eso cada municipio es un renglón de MUNICIPIOS, con su ley, su
huella SHA-256 y el artículo de cada cifra. Cotejadas el 19-11-2026 contra los
PDF de la Biblioteca Virtual del Congreso del Estado de Jalisco (leyes de
ingresos 2026, archivo «-300126») y la Ley de Hacienda Municipal vigente
(última reforma registrada: decreto 29857, archivo «-171025»):

  - Zapopan: arts. 45 (tarifa y baldíos), 46 (pago anticipado), 47 y 48
    (beneficios y cuál se suma), 56 (recargos), 59 (multa), 60 (gastos).
  - Guadalajara: arts. 23 a 27 (tarifa, baldíos, pago anticipado, beneficios
    y fr. XII, cuál se suma), 33 (recargos) y 34 (gastos).
  - San Pedro Tlaquepaque: art. 32 (tarifa, baldíos, beneficios), 38
    (recargos) y 39 (gastos).
  - Tonalá: arts. 40 a 43 (tarifa, baldíos, beneficios, pago anticipado y
    art. 43, fr. III, cuál se suma), 49 (recargos), 50 (multa), 52 (gastos).
  - Tlajomulco de Zúñiga: arts. 35 a 38 (tarifa, baldíos, beneficios, pago
    anticipado), 46 (multa), 47 (recargos), 50 (gastos).
  - Segunda entrega, el mismo día (pedido del autor: «continúa con los
    municipios»): El Salto (arts. 20 a 27, 33, 35 y 37), Zapotlanejo (37 a 44,
    51, 52 y 54), Juanacatlán (18 a 21, 26, 28 y 30), Ixtlahuacán de los
    Membrillos (22 a 27, 33, 35 y 37), Puerto Vallarta (38 a 40, 48 y 112),
    Lagos de Moreno (18 a 21, 28, 29 y 31), Tepatitlán de Morelos (17 a 20, 28,
    29 y 31), Zapotlán el Grande (30 a 33, 41, 42 y 44) y Ocotlán (37 a 40, 47,
    48 y 50). Unos cobran por tramos y otros con una tasa al millar más una
    cuota fija (tarifa 'millar', con su tasa de rústicos en 'rustico'); la
    cobranza también cambia: 'req' (la notificación solo se cobra con el
    requerimiento), 'emb' (los gastos solo por el embargo, una vez), topes en
    pesos ('max_pesos') y cuotas en pesos ('pesos', Tepatitlán).
    Acatlán de Juárez y Chapala se leyeron y quedan en ESPERA: escriben la tasa
    con «%» bajo «tasa bimestral al millar» y no adivinamos cuál es.
  - Ley de Hacienda Municipal: art. 44 bis (actualización con el INPC), 52
    (recargos por mes o fracción desde el día siguiente al vencimiento; tope
    de 250 %, o de 100 % si se paga de forma espontánea) y 103 (el predial se
    paga en los primeros quince días del primer mes de cada bimestre).

Para los demás municipios del país la página dice cuánto recaudó cada uno de
predial en 2024 (INEGI, EFIPEM, municipios-efipem.js) y que su tabla aún no
está integrada: **es falta de la plataforma, no del municipio** (su ley está
publicada). Un municipio nuevo entra con su renglón aquí, cotejado con su ley.

Lo que la ley no dice y decidimos a la vista (derivado, y la página lo dice):
  - «Sobre el primer $X del valor fiscal»: el descuento se calcula sobre el
    impuesto que daría un valor de $X con la misma tarifa (así lo explica la
    Ley de Tlaquepaque, art. 32, fr. III, f, y el Municipio de Zapopan en sus
    preguntas frecuentes del predial 2026).
  - La sobretasa de 100 % a baldíos duplica el impuesto bimestral.
  - Donde la ley no dice si un beneficio se suma al pago anticipado
    (Tlaquepaque), se toma el mayor de los dos.
  - Los recargos se calculan sobre el impuesto omitido, con la tasa de 2026
    para todos los meses (cada año tuvo la suya en su ley).

**La cuenta la hace el navegador** (cc-predial.js) con estos renglones, el
INPC de la base y la UMA 2026. Nada se guarda ni se envía. No es un estado de
cuenta: el adeudo oficial lo da la tesorería de cada municipio.
Lo llama apartados.insp_nativa() (INSP_NATIVAS['ccpredial']).
"""
import html
import json
import re
import math
import os
import subprocess
import sys

from presupuesto_modulos import chip
import cc_inmueble

ESTILOS = ['cc-inmueble.css', 'cc-predial.css']
SCRIPTS = ['municipios-efipem.js', 'cc-predial.js']
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANIO = 2026
CONGRESO = 'https://congresoweb.congresojal.gob.mx/BibliotecaVirtual/legislacion/Ingresos/Documentos_PDF-Ingresos/'


def _li(nombre):
    return (CONGRESO + 'Ley%20de%20Ingresos%20del%20Municipio%20de%20' + nombre
            + ',%20Jalisco%20para%20el%20ejercicio%20fiscal%202026-300126.pdf')


LHM = {'tx': 'Ley de Hacienda Municipal del Estado de Jalisco, texto vigente (Congreso del Estado, archivo del 17-10-2025)',
       'url': 'https://congresoweb.congresojal.gob.mx/bibliotecavirtual/legislacion/Leyes/Documentos_PDF-Leyes/Ley%20de%20Hacienda%20Municipal%20del%20Estado%20de%20Jalisco%20-171025.pdf',
       'sha256': 'd5acf2038028a367b044fb3e903ac77d4310ac39ae146ac6a5ed1f75d24cd476'}

# Beneficio: f = factor que pagas (0.50 = pagas la mitad); tope = «sobre el
# primer $X del valor fiscal»; hasta = solo si el valor fiscal no rebasa $X;
# suma = se suma al pago anticipado (si no, se toma el mayor); grupo = para
# ordenar el menú.
MUNICIPIOS = [
    {'id': 'zapopan', 'ent': 'JAL', 'cve': '120', 'nombre': 'Zapopan',
     'ley': 'Ley de Ingresos del Municipio de Zapopan, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Zapopan'), 'sha256': '9efd905b4127bd832157d9b0a41e5beeecc0b91c313af934b31f71ce44a73a8c',
     'art_tarifa': 'art. 45, fr. I',
     'tramos': [[0.01, 0.00, 0.0002300], [620100.01, 142.63, 0.0002300], [944864.01, 217.33, 0.0002495],
                [1304860.01, 307.15, 0.0002691], [1875923.01, 460.83, 0.0002886], [2680270.01, 692.97, 0.0003082],
                [3707349.01, 1009.52, 0.0003277], [5158931.01, 1485.21, 0.0003473], [7642490.01, 2347.76, 0.0003668],
                [12643390.01, 4182.10, 0.0003864], [26960590.01, 9714.27, 0.0004059], [71716206.01, 27880.58, 0.0004255],
                [174033618.01, 71416.64, 0.0004450], [437096000.01, 188479.40, 0.0004646], [1251787029.01, 566984.86, 0.0004841]],
     'baldio': {'tipo': 'sobretasa', 'pct': 100, 'art': 'art. 45, fr. I'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo antes del 1 de marzo', 'f': 0.90, 'art': 'art. 46'},
                {'id': 'tdc', 'et': 'Pagas el año en enero o febrero con tarjeta de crédito a meses', 'f': 0.93, 'art': 'art. 46'}],
     'pronto_nota': 'Si pagas el año completo en marzo o abril no hay descuento, pero no causas los accesorios de esos meses (art. 46).',
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad o en viudez (tu casa)', 'f': 0.50, 'tope': 1500000, 'suma': True, 'art': 'art. 47, fr. IV'},
         {'id': 'm60', 'et': 'Tienes de 60 a 69 años (tu casa)', 'f': 0.50, 'tope': 1750000, 'suma': True, 'art': 'art. 47, fr. V, a'},
         {'id': 'm70', 'et': 'Tienes de 70 a 79 años (tu casa)', 'f': 0.40, 'tope': 1750000, 'suma': True, 'art': 'art. 47, fr. V, b'},
         {'id': 'm80', 'et': 'Tienes 80 años o más (tu casa)', 'f': 0.20, 'tope': 1750000, 'suma': True, 'art': 'art. 47, fr. V, c'},
         {'id': 'jefa', 'et': 'Madre jefa de familia, inscrita en el padrón estatal (tu casa)', 'f': 0.50, 'hasta': 1800000, 'art': 'art. 47, fr. IX'},
         {'id': 'eco', 'et': 'Techo verde, calentador o celdas solares, agua de lluvia o cargador eléctrico (casa)', 'f': 0.75, 'tope': 1800000, 'art': 'art. 47, fr. VII'},
         {'id': 'agro', 'et': 'Predio agropecuario en producción, con dictamen', 'f': 0.10, 'art': 'art. 45, fr. II'},
         {'id': 'ac', 'et': 'Asociación civil de asistencia social, con dictamen', 'f': 0.30, 'art': 'art. 47, fr. I'},
         {'id': 'esc', 'et': 'Escuela con validez oficial (el predio donde enseña)', 'f': 0.50, 'art': 'art. 47, fr. II'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.50, 'art': 'art. 47, fr. III'},
         {'id': 'inc', 'et': 'Empresa con 5 % o más de personas con discapacidad o adultas mayores', 'f': 0.75, 'art': 'art. 47, fr. VIII'}],
     'suma_art': 'art. 48',
     'recargo': {'pct': 1.47, 'art': 'art. 56'},
     'multa': {'min': 20, 'max': 50, 'art': 'art. 59'},
     'notif': {'uma': 6, 'art': 'art. 60, fr. I'},
     'ejec': {'pct': 3, 'min_uma': 6, 'max_uma': 3 * 365, 'art': 'art. 60, fr. II'},
     'pago_url': 'https://pagos.zapopan.gob.mx/PagoEnLinea/'},

    {'id': 'guadalajara', 'ent': 'JAL', 'cve': '039', 'nombre': 'Guadalajara',
     'ley': 'Ley de Ingresos del Municipio de Guadalajara, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Guadalajara'), 'sha256': '25cc699111fcca8359db8c11694b326299c0bf60880b695af1a3282294c9174e',
     'art_tarifa': 'art. 23, fr. I',
     'tramos': [[0.00, 0.00, 0.0002540], [776142.91, 197.15, 0.0002540], [1053400.42, 267.58, 0.0002794],
                [1325856.38, 343.71, 0.0003048], [1668739.76, 448.23, 0.0003302], [2188819.00, 619.97, 0.0003556],
                [3146685.52, 960.59, 0.0003810], [4944269.47, 1645.47, 0.0004064], [9858156.02, 3642.48, 0.0004318],
                [42976151.22, 17942.84, 0.0004572]],
     'baldio': {'tipo': 'sobretasa', 'pct': 100, 'art': 'art. 23, fr. I'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo antes del 1 de marzo', 'f': 0.90, 'art': 'art. 24, fr. I'}],
     'pronto_nota': 'Pagando así tampoco causas los accesorios del primer bimestre (art. 25).',
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad o en viudez (tu casa)', 'f': 0.50, 'tope': 1123500, 'art': 'art. 27, fr. VI'},
         {'id': 'm60', 'et': 'Tienes de 60 a 74 años (tu casa)', 'f': 0.50, 'tope': 1123500, 'suma': True, 'art': 'art. 27, fr. VII, a'},
         {'id': 'm75', 'et': 'Tienes de 75 a 79 años (tu casa)', 'f': 0.40, 'tope': 1123500, 'suma': True, 'art': 'art. 27, fr. VII, b'},
         {'id': 'm80', 'et': 'Tienes 80 años o más (tu casa)', 'f': 0.20, 'tope': 1123500, 'suma': True, 'art': 'art. 27, fr. VII, c'},
         {'id': 'jefa', 'et': 'Madre de familia en situación vulnerable, con constancia (tu casa)', 'f': 0.50, 'hasta': 3000000, 'art': 'art. 27, fr. X'},
         {'id': 'cuida', 'et': 'Cuidas a una persona con discapacidad o enfermedad degenerativa (tu casa)', 'f': 0.50, 'tope': 1123500, 'art': 'art. 27, fr. XI'},
         {'id': 'agro', 'et': 'Predio rústico agropecuario o habitado por sus dueños, con dictamen', 'f': 0.50, 'art': 'art. 23, fr. I'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.20, 'art': 'art. 27, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa (el inmueble de culto)', 'f': 0.50, 'art': 'art. 27, fr. II'},
         {'id': 'mon', 'et': 'Monumento histórico o artístico conservado, con dictamen', 'f': 0.00, 'art': 'art. 27, fr. III'},
         {'id': 'amb', 'et': 'Inmueble de valor histórico o artístico ambiental, con dictamen', 'f': 0.40, 'art': 'art. 27, fr. IV'},
         {'id': 'cen', 'et': 'Vivienda nueva en zona de protección del patrimonio, con dictamen', 'f': 0.50, 'art': 'art. 27, fr. V'}],
     'suma_art': 'art. 27, fr. XII',
     'recargo': {'pct': 1.47, 'art': 'art. 33'},
     'multa': None,
     'notif': {'uma': 6, 'art': 'art. 34, fr. I'},
     'ejec': {'pct': 3, 'min_uma': 6, 'max_uma': 1.5 * 365, 'art': 'art. 34, fr. II'},
     'pago_url': 'https://guadalajara.gob.mx/'},

    {'id': 'tlaquepaque', 'ent': 'JAL', 'cve': '098', 'nombre': 'San Pedro Tlaquepaque',
     'ley': 'Ley de Ingresos del Municipio de San Pedro Tlaquepaque, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('San%20Pedro%20Tlaquepaque'), 'sha256': 'aabf7148882e78a05bbb05fc75123a7025ab6f0613b91119d95f755e35ecc3a6',
     'art_tarifa': 'art. 32, fr. I',
     'tramos': [[0.01, 5.00, 0.000230], [2043875.01, 475.09, 0.000253], [2324002.01, 545.96, 0.000276],
                [2963624.04, 722.50, 0.000299], [3873820.01, 994.65, 0.000322], [5093420.01, 1387.36, 0.000345],
                [7955874.64, 2374.91, 0.000368], [15457730.41, 5135.59, 0.000391], [28949500.01, 10410.87, 0.000414]],
     'tramos_nota': 'El último renglón de la ley dice «$ 10.410.87»: lo leemos como $10,410.87.',
     'baldio': {'tipo': 'millar', 'millar': 0.81, 'cf': 5.00, 'art': 'art. 32, fr. II'},
     'pronto': [{'id': 'mar', 'et': 'Pagas el año completo antes del 1 de abril', 'f': 0.85, 'art': 'art. 32, fr. III, d, 1'},
                {'id': 'abr', 'et': 'Pagas el año completo en abril', 'f': 0.95, 'art': 'art. 32, fr. III, d, 2'}],
     'pronto_nota': 'Pagando el año antes del 1 de junio no causas los recargos de los dos primeros bimestres (art. 32, fr. III, d).',
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez o con 60 años o más (tu casa)', 'f': 0.50, 'tope': 1000000, 'art': 'art. 32, fr. III, e'},
         {'id': 'm65', 'et': 'Tienes 65 años o más desde antes del 1 de enero (tu casa)', 'f': 0.00, 'tope': 1000000, 'art': 'art. 32, fr. III, f'},
         {'id': 'agro', 'et': 'Predio rústico de ejido o comunidad agraria en producción', 'f': 0.10, 'art': 'art. 32, fr. III, a, 1'},
         {'id': 'agrop', 'et': 'Predio rústico privado en producción agropecuaria', 'f': 0.50, 'art': 'art. 32, fr. III, a, 2'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 1000000, 'art': 'art. 32, fr. III, b'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 32, fr. III, c'},
         {'id': 'pat', 'et': 'Finca patrimonial o histórica acreditada por el INAH', 'f': 0.50, 'art': 'art. 32, fr. III, k'},
         {'id': 'esc', 'et': 'Centro de educación superior con validez oficial', 'f': 0.50, 'art': 'art. 32, fr. III, n'},
         {'id': 'agua1', 'et': 'Captación de agua de lluvia básica, con constancia', 'f': 0.90, 'art': 'art. 32, fr. III, q, 1'},
         {'id': 'agua2', 'et': 'Captación de agua de lluvia tecnificada, con constancia', 'f': 0.80, 'art': 'art. 32, fr. III, q, 2'},
         {'id': 'verde', 'et': 'Construcción verde acreditada (una sola vez)', 'f': 0.70, 'art': 'art. 32, fr. II'}],
     'suma_art': None,
     'recargo': {'pct': 1.0, 'art': 'art. 38'},
     'multa': None,
     'notif': {'uma': 4, 'art': 'art. 39, fr. I'},
     'ejec': {'pct': 3, 'min_uma': 4, 'max_uma': 4 * 365, 'art': 'art. 39, fr. II'},
     'pago_url': 'https://www.tlaquepaque.gob.mx/'},

    {'id': 'tonala', 'ent': 'JAL', 'cve': '101', 'nombre': 'Tonalá',
     'ley': 'Ley de Ingresos del Municipio de Tonalá, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Tonal%C3%A1'), 'sha256': 'a07aedd6961fdb303e96c2fa590f78804fa2392ad6ad00c2021424e069f7e5f2',
     'art_tarifa': 'art. 40, fr. I',
     'tramos': [[0.01, 30.00, 0.000230], [180000.01, 71.40, 0.000250], [300000.01, 101.40, 0.000250],
                [550000.01, 163.90, 0.000275], [950000.01, 273.90, 0.000300], [1450000.01, 423.90, 0.000325],
                [2350000.01, 716.40, 0.000350], [3850000.01, 1241.40, 0.000375], [8450000.01, 2966.40, 0.000400],
                [25450000.01, 9766.40, 0.000425], [68450000.01, 28041.40, 0.000450]],
     'baldio': {'tipo': 'millar', 'millar': 0.81, 'cf': 25.00, 'art': 'art. 40, fr. II'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo del 1 de enero al 28 de febrero', 'f': 0.85, 'art': 'art. 42, a'},
                {'id': 'abr', 'et': 'Pagas el año completo del 1 de marzo al 30 de abril', 'f': 0.95, 'art': 'art. 42, b'}],
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez o con 60 años o más (tu casa)', 'f': 0.50, 'tope': 2000000, 'suma': True, 'art': 'art. 43'},
         {'id': 'jefa', 'et': 'Jefa madre de familia, con constancia (tu casa)', 'f': 0.50, 'hasta': 2000000, 'art': 'art. 43, fr. I, e'},
         {'id': 'agro', 'et': 'Predio agropecuario en producción, con dictamen', 'f': 0.10, 'art': 'art. 43, fr. V'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 1000000, 'art': 'art. 41, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 41, fr. II'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.50, 'art': 'art. 41, fr. III'}],
     'suma_art': 'art. 43, fr. III',
     'recargo': {'pct': 1.50, 'art': 'art. 49'},
     'multa': {'min': 20, 'max': 50, 'art': 'art. 50'},
     'notif': {'uma': 4, 'art': 'art. 52, fr. I'},
     'ejec': {'pct': 3, 'art': 'art. 52, fr. II'},
     'pago_url': 'https://tonala.gob.mx/'},

    {'id': 'tlajomulco', 'ent': 'JAL', 'cve': '097', 'nombre': 'Tlajomulco de Zúñiga',
     'ley': 'Ley de Ingresos del Municipio de Tlajomulco de Zúñiga, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Tlajomulco%20de%20Z%C3%BA%C3%B1iga'), 'sha256': 'a03ed71535516679a25ab3156218edc02ab2d1553e8077f6a19b889b558a8e29',
     'art_tarifa': 'art. 35, fr. I',
     'tramos': [[0.01, 10.00, 0.000240], [357530.01, 95.81, 0.000240], [564000.01, 145.36, 0.000264],
                [906775.01, 235.86, 0.000288], [1519621.01, 412.36, 0.000312], [2946168.01, 857.45, 0.000336],
                [7080715.01, 2246.66, 0.000360], [19478169.01, 6709.75, 0.000384], [64278346.01, 23913.02, 0.000408],
                [284788228.01, 113881.06, 0.000432]],
     'baldio': {'tipo': 'millar', 'millar': 0.70, 'cf': 4.00, 'art': 'art. 35, fr. III'},
     'pronto': [{'id': 'ene', 'et': 'Pagas el año completo en enero', 'f': 0.85, 'art': 'art. 37, fr. I'},
                {'id': 'mar', 'et': 'Pagas el año completo en febrero o marzo', 'f': 0.90, 'art': 'art. 37, fr. II'},
                {'id': 'abr', 'et': 'Pagas el año completo en abril', 'f': 0.95, 'art': 'art. 37, fr. III'}],
     'pronto_nota': 'Pagando así no causas los recargos de ese periodo (art. 37).',
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez o con 60 años o más (tu casa)', 'f': 0.50, 'tope': 1635000, 'art': 'art. 38'},
         {'id': 'jefa', 'et': 'Madre jefa de familia, inscrita en el padrón estatal (tu casa)', 'f': 0.50, 'hasta': 1635000, 'art': 'art. 38, fr. VI'},
         {'id': 'agro', 'et': 'Predio rústico agropecuario en producción (hasta 90 %; berries, 50 %)', 'f': 0.10, 'art': 'art. 35, fr. II'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil', 'f': 0.50, 'art': 'art. 36, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa (inmueble de asistencia o educación)', 'f': 0.50, 'art': 'art. 36, fr. II'},
         {'id': 'pat', 'et': 'Inmueble inscrito en el Inventario Estatal del Patrimonio Cultural', 'f': 0.30, 'art': 'art. 36, fr. III'}],
     'suma_art': 'art. 38',
     'recargo': {'pct': 1.0, 'art': 'art. 47'},
     'multa': {'min': 40, 'max': 50, 'art': 'art. 46'},
     'notif': {'pct': 8, 'min_uma': 1, 'max_uma': 30, 'art': 'art. 50, frs. I y IV'},
     'ejec': {'pct': 8, 'min_uma': 1, 'max_uma': 45, 'art': 'art. 50, frs. II y IV'},
     'pago_url': 'https://tlajomulco.gob.mx/'},

    # ── 19-11-2026, segunda entrega: el resto de la zona metropolitana y las ciudades medias. ──
    {'id': 'elsalto', 'ent': 'JAL', 'cve': '070', 'nombre': 'El Salto',
     'ley': 'Ley de Ingresos del Municipio de El Salto, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('El%20Salto'), 'sha256': '92de467ef49d9c2f8de6b7165813e829a87943819deabdfa3bfe231bdd89fde1',
     'art_tarifa': 'art. 20',
     'tramos': [[0.01, 40.00, 0.000210], [166400.01, 74.95, 0.000210], [213059.01, 84.75, 0.000231],
                [265341.01, 96.83, 0.000252], [487968.01, 152.94, 0.000273], [1977307.01, 559.53, 0.000294],
                [11326987.01, 3308.34, 0.000315], [33886503.01, 10414.59, 0.000336], [72360418.01, 23341.83, 0.000357],
                [148214225.01, 50421.64, 0.000378]],
     'baldio': {'tipo': 'sobretasa', 'pct': 100, 'art': 'art. 20'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.85, 'art': 'art. 23'},
                {'id': 'abr', 'et': 'Pagas el año completo en marzo o abril', 'f': 0.95, 'art': 'art. 23'}],
     'pronto_nota': 'La ley dice «hasta el 15 %» para enero y febrero: aquí usamos el 15 %. Pagando el año antes del 1 de mayo tampoco causas los recargos del primer bimestre (art. 22).',
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez o con 60 años o más (tu casa)', 'f': 0.50, 'tope': 450000, 'art': 'art. 24'},
         {'id': 'jefa', 'et': 'Madre jefa de familia, pagando en el primer bimestre (tu casa)', 'f': 0.50, 'tope': 487698, 'art': 'art. 25'},
         {'id': 'techo1', 'et': 'Naturación extensiva del techo, con constancia', 'f': 0.80, 'art': 'art. 27'},
         {'id': 'techo2', 'et': 'Naturación intensiva del techo (jardín), con constancia', 'f': 0.70, 'art': 'art. 27'},
         {'id': 'agro', 'et': 'Predio rústico agropecuario en producción, con constancia (hasta 50 %)', 'f': 0.50, 'art': 'art. 22'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 353821, 'art': 'art. 21'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 21'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado (hasta 60 %)', 'f': 0.40, 'art': 'art. 21'}],
     'suma_art': 'art. 24',
     'recargo': {'pct': 1.6, 'art': 'art. 35'},
     'multa': {'min': 3.18, 'max': 10.60, 'art': 'art. 33'},
     'notif': {'pct': 5.30, 'min_uma': 1, 'max_uma': 30, 'req': True, 'art': 'art. 37 (requerimiento en la cabecera)'},
     'ejec': {'pct': 5, 'max_uma': 45, 'emb': True, 'art': 'art. 37 (embargo en la cabecera)'}},

    {'id': 'zapotlanejo', 'ent': 'JAL', 'cve': '124', 'nombre': 'Zapotlanejo',
     'ley': 'Ley de Ingresos del Municipio de Zapotlanejo, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Zapotlanejo'), 'sha256': '7290d72d58511d0a7afb48fa39c364157f6ca0ac3f77230be250889979d744d2',
     'art_tarifa': 'art. 37, fr. III, a', 'tarifa': 'millar', 'millar': 0.23,
     'tramos': [[0.00, 38.40, 0.00023]],
     'rustico': {'millar': 0.26, 'cf': 26.11, 'art': 'art. 37, fr. II'},
     'baldio': {'tipo': 'millar', 'millar': 0.45, 'cf': 38.40, 'art': 'art. 37, fr. III, b'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.85, 'art': 'art. 40, a'},
                {'id': 'abr', 'et': 'Pagas el año completo en marzo o abril', 'f': 0.95, 'art': 'art. 40, b'}],
     'pronto_nota': 'La ley dice «se les aplicará un factor de 0.15 sobre el monto del impuesto» (y 0.05 en marzo y abril): lo leemos como 15 % y 5 % de descuento, como lo dicen sus vecinos. Pagando el año antes del 1 de mayo no causas los recargos del primer bimestre (art. 39).',
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad o en viudez (tu casa)', 'f': 0.50, 'tope': 705948.97, 'art': 'art. 41'},
         {'id': 'jefa', 'et': 'Madre jefa de familia, inscrita en el padrón estatal (tu casa)', 'f': 0.50, 'hasta': 705948.97, 'art': 'art. 44'},
         {'id': 'agro', 'et': 'Predio rústico agropecuario en producción, con constancia', 'f': 0.50, 'art': 'art. 39'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 705948.97, 'art': 'art. 38, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 38, fr. II'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.50, 'art': 'art. 38, fr. III'}],
     'nota': 'El art. 42 da un beneficio a quien tiene 60 años o más, pero no dice de cuánto: por eso no está en la lista.',
     'suma_art': 'art. 43',
     'recargo': {'pct': 1.0, 'art': 'art. 52'},
     'multa': {'min': 10, 'max': 30, 'art': 'art. 51'},
     'notif': {'pct': 5, 'min_uma': 1, 'max_uma': 30, 'req': True, 'art': 'art. 54, fr. I, a'},
     'ejec': {'pct': 5, 'max_uma': 45, 'emb': True, 'art': 'art. 54, fr. II, a'}},

    {'id': 'juanacatlan', 'ent': 'JAL', 'cve': '051', 'nombre': 'Juanacatlán',
     'ley': 'Ley de Ingresos del Municipio de Juanacatlán, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Juanacatl%C3%A1n'), 'sha256': '0c8ef837accf1b5753e97d7a479785a52ec717b89e933512bc797b62a793b7e8',
     'art_tarifa': 'art. 18, fr. III, a', 'tarifa': 'millar', 'millar': 0.21,
     'tramos': [[0.00, 14.88, 0.00021]],
     'rustico': {'millar': 0.24, 'cf': 14.88, 'art': 'art. 18, fr. II'},
     'baldio': {'tipo': 'millar', 'millar': 0.36, 'cf': 14.88, 'art': 'art. 18, fr. III, b'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.85, 'art': 'art. 20, a'},
                {'id': 'abr', 'et': 'Pagas el año completo en marzo o abril', 'f': 0.95, 'art': 'art. 20, b'}],
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez o con 60 años o más (tu casa)', 'f': 0.50, 'art': 'art. 21'},
         {'id': 'agro', 'et': 'Predio rústico agropecuario en producción, con constancia (no invernaderos)', 'f': 0.50, 'art': 'art. 18, fr. II'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 600000, 'art': 'art. 19, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 19, fr. II'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.40, 'art': 'art. 19, fr. III'}],
     'nota': 'En el art. 18, fr. II, la frase de la cuota fija de los rústicos llega cortada («…en los incisos a) cuota fija de $14.88»): la leemos como $14.88, la misma de los urbanos.',
     'suma_art': 'art. 21',
     'recargo': {'pct': 1.0, 'art': 'art. 28'},
     'multa': {'min': 10, 'max': 30, 'art': 'art. 26, fr. II'},
     'notif': {'pct': 5, 'min_uma': 1, 'max_pesos': 3136.80, 'req': True, 'art': 'art. 30, fr. I, a'},
     'ejec': {'pct': 5, 'max_pesos': 4704.51, 'emb': True, 'art': 'art. 30, fr. II, a'}},

    {'id': 'ixtlahuacan', 'ent': 'JAL', 'cve': '044', 'nombre': 'Ixtlahuacán de los Membrillos',
     'ley': 'Ley de Ingresos del Municipio de Ixtlahuacán de los Membrillos, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Ixtlahuac%C3%A1n%20de%20los%20Membrillos'), 'sha256': '454897599068f8b598c1650caae2fa5e92d1ad44e9e4519ba3c4a16b5f946904',
     'art_tarifa': 'art. 22, fr. I, tabla 01',
     'tramos': [[0.01, 28.84, 0.00025], [183935.01, 74.82, 0.00027], [246803.01, 91.80, 0.00029],
                [482947.01, 160.28, 0.00031], [820936.01, 265.06, 0.00033], [1315500.01, 428.26, 0.00036],
                [2075986.01, 702.04, 0.00039], [3904573.01, 1415.19, 0.00042], [10281384.01, 4093.45, 0.00045],
                [38281100.01, 16693.32, 0.00048]],
     'tramos_nota': 'La tabla 01 cierra un tramo en $820,933.00 y abre el siguiente en $820,936.01: dejamos los límites como los escribe la ley.',
     'baldio': {'tipo': 'sobretasa', 'pct': 50, 'art': 'art. 22'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.85, 'art': 'art. 24, a'},
                {'id': 'abr', 'et': 'Pagas el año completo en marzo o abril', 'f': 0.95, 'art': 'art. 24, b'}],
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez o con 60 años o más (tu casa; hasta 50 %)', 'f': 0.50, 'tope': 1049800, 'art': 'art. 25'},
         {'id': 'jefa', 'et': 'Jefa de familia o mamá soltera, con constancia del DIF (tu casa; hasta 50 %)', 'f': 0.50, 'tope': 1049800, 'art': 'art. 25'},
         {'id': 'techo1', 'et': 'Naturación extensiva del techo, con constancia', 'f': 0.80, 'art': 'art. 27, fr. I'},
         {'id': 'techo2', 'et': 'Naturación intensiva del techo (jardín), con constancia', 'f': 0.70, 'art': 'art. 27, fr. II'},
         {'id': 'agro', 'et': 'Predio rústico agropecuario en producción, con constancia', 'f': 0.50, 'art': 'art. 22'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 500000, 'art': 'art. 23, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 23, fr. II'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.40, 'art': 'art. 23, fr. III'}],
     'suma_art': 'art. 25',
     'recargo': {'pct': 1.0, 'art': 'art. 35'},
     'multa': {'min': 15, 'max': 30, 'art': 'art. 33, fr. II'},
     'notif': {'pct': 5, 'min_uma': 1, 'max_uma': 30, 'req': True, 'art': 'art. 37, fr. I, a'},
     'ejec': {'pct': 5, 'max_uma': 45, 'emb': True, 'art': 'art. 37, fr. II, a'}},

    {'id': 'vallarta', 'ent': 'JAL', 'cve': '067', 'nombre': 'Puerto Vallarta',
     'ley': 'Ley de Ingresos del Municipio de Puerto Vallarta, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Puerto%20Vallarta'), 'sha256': 'd697b1973cca8a6ed22c5db9b9ff2ec2a99e8a3d05ce45421e9436a76afcb958',
     'art_tarifa': 'art. 38, fr. V, a, tabla 1',
     'tramos': [[0.01, 0.00, 0.000250], [584775.01, 146.20, 0.000250], [988162.01, 247.05, 0.000275],
                [1630274.01, 423.64, 0.000300], [2500184.01, 684.62, 0.000325], [4067064.01, 1193.86, 0.000350],
                [6559136.01, 2066.09, 0.000375], [13143342.01, 4535.17, 0.000400], [48372251.01, 18626.74, 0.000425],
                [219067566.01, 91172.25, 0.000450]],
     'rustico': {'millar': 0.20, 'cf': 8.00, 'art': 'art. 38, fr. II'},
     'baldio': {'tipo': 'millar', 'millar': 0.80, 'cf': 6.00, 'art': 'art. 38, fr. V, b y d'},
     'pronto': [{'id': 'ene', 'et': 'Pagas el año completo en enero', 'f': 0.85, 'art': 'art. 39, fr. I'},
                {'id': 'feb', 'et': 'Pagas el año completo en febrero', 'f': 0.90, 'art': 'art. 39, fr. I'},
                {'id': 'abr', 'et': 'Pagas el año completo en marzo o abril', 'f': 0.95, 'art': 'art. 39, fr. I'}],
     'pronto_nota': 'Pagando el año antes del 1 de junio no causas los recargos del primer bimestre (art. 39, fr. II).',
     'beneficios': [
         {'id': 'm60', 'et': 'Pensionado, jubilado, con discapacidad, en viudez o de 60 a 74 años (tu casa)', 'f': 0.50, 'tope': 2000000, 'art': 'art. 40, fr. III'},
         {'id': 'm75', 'et': 'Tienes de 75 a 79 años (tu casa)', 'f': 0.40, 'tope': 2000000, 'art': 'art. 40, fr. IV'},
         {'id': 'm80', 'et': 'Tienes 80 años o más (tu casa)', 'f': 0.20, 'tope': 2000000, 'art': 'art. 40, fr. V'},
         {'id': 'agro', 'et': 'Predio agropecuario en producción, con dictamen (pagando el año)', 'f': 0.50, 'tope': 2000000, 'art': 'art. 38, fr. IV'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 2000000, 'art': 'art. 40, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa (pagando el año)', 'f': 0.50, 'art': 'art. 40, fr. II'}],
     'suma_art': 'art. 40',
     'recargo': {'pct': 1.10, 'art': 'art. 48'},
     'multa': None,
     'notif': {'uma': 1, 'art': 'art. 112, fr. I'},
     'ejec': {'pct': 5, 'min_uma': 1, 'max_uma': 365, 'art': 'art. 112, fr. II'}},

    {'id': 'lagos', 'ent': 'JAL', 'cve': '053', 'nombre': 'Lagos de Moreno',
     'ley': 'Ley de Ingresos del Municipio de Lagos de Moreno, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Lagos%20de%20Moreno'), 'sha256': '27332e612a99019c90cb8b78a0d4fbcd742dd5350eac5e763dca30fcc13da10e',
     'art_tarifa': 'art. 18, fr. I, tabla 1',
     'tramos': [[0.01, 45.00, 0.000250], [207000.01, 96.75, 0.000250], [360700.01, 135.18, 0.000275],
                [552000.01, 187.79, 0.000300], [814000.01, 266.39, 0.000325], [1237000.01, 403.87, 0.000350],
                [1995000.01, 669.17, 0.000375], [3674000.01, 1298.80, 0.000400], [9450000.01, 3609.20, 0.000425],
                [52000000.01, 21692.95, 0.000450]],
     'baldio': {'tipo': 'sobretasa', 'pct': 100, 'art': 'art. 18, fr. I'},
     'pronto': [{'id': 'abr', 'et': 'Pagas el año completo de enero a abril', 'f': 0.85, 'art': 'art. 20'}],
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez o con 60 años o más (tu casa)', 'f': 0.50, 'tope': 594496, 'art': 'art. 21, fr. I'},
         {'id': 'jefa', 'et': 'Madre jefa de familia, único sostén del hogar', 'f': 0.50, 'art': 'art. 21, fr. III'},
         {'id': 'agro', 'et': 'Predio agropecuario en producción, con dictamen', 'f': 0.50, 'art': 'art. 18, fr. II'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 559979, 'art': 'art. 19, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 19, fr. II'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.40, 'art': 'art. 19, fr. III'}],
     'suma_art': 'art. 21',
     'recargo': {'pct': 1.0, 'art': 'art. 29'},
     'multa': {'min': 10, 'max': 30, 'art': 'art. 28'},
     'notif': {'pct': 5, 'min_uma': 1, 'max_uma': 30, 'req': True, 'art': 'art. 31, fr. I, a'},
     'ejec': {'pct': 5, 'max_uma': 45, 'emb': True, 'art': 'art. 31, fr. II, a'}},

    {'id': 'tepatitlan', 'ent': 'JAL', 'cve': '093', 'nombre': 'Tepatitlán de Morelos',
     'ley': 'Ley de Ingresos del Municipio de Tepatitlán de Morelos, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Tepatitl%C3%A1n%20de%20Morelos'), 'sha256': '52a4c59b9550563ac65002542f437dea4204432981b9a50a47b3c99fe48231d8',
     'art_tarifa': 'art. 17, fr. III, a', 'tarifa': 'millar', 'millar': 0.16,
     'tramos': [[0.00, 15.00, 0.00016]],
     'rustico': {'millar': 0.23, 'cf': 5.00, 'art': 'art. 17, fr. II, b'},
     'baldio': {'tipo': 'millar', 'millar': 0.30, 'cf': 15.00, 'art': 'art. 17, fr. III, b'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.85, 'art': 'art. 19, a'},
                {'id': 'abr', 'et': 'Pagas el año completo en marzo o abril', 'f': 0.95, 'art': 'art. 19, b'}],
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez o con 60 años o más (tu casa)', 'f': 0.50, 'tope': 1278000, 'art': 'art. 20'},
         {'id': 'agro', 'et': 'Predio rústico agropecuario en producción, con constancia', 'f': 0.50, 'art': 'art. 17, fr. II'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 1500000, 'art': 'art. 18, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 18, fr. II'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.40, 'art': 'art. 18, fr. III'}],
     'suma_art': 'art. 20',
     'recargo': {'pct': 2.0, 'art': 'art. 29'},
     'multa': {'min': 10, 'max': 30, 'art': 'art. 28'},
     'notif': {'pesos': 578.79, 'req': True, 'art': 'art. 31, fr. I, a',
               'pesos_nota': 'Por notificar el requerimiento la ley da de $244.94 a $578.79 (art. 31, fr. I): aquí tomamos la cuota más alta.'},
     'ejec': {'pesos': 710.34, 'emb': True, 'art': 'art. 31, fr. II'}},

    {'id': 'zapotlan', 'ent': 'JAL', 'cve': '023', 'nombre': 'Zapotlán el Grande',
     'ley': 'Ley de Ingresos del Municipio de Zapotlán el Grande, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Zapotl%C3%A1n%20el%20Grande'), 'sha256': '674aefb0d55d60787b5675271e9949c4aafb912ef550e505e4a47734439880a4',
     'art_tarifa': 'art. 30, fr. I',
     'tramos': [[0.01, 0.00, 0.000220], [207000.01, 45.54, 0.000220], [360700.01, 79.35, 0.000242],
                [552000.01, 125.65, 0.000264], [814000.01, 194.82, 0.000286], [1237000.01, 315.79, 0.000308],
                [1995000.01, 549.26, 0.000330], [3674000.01, 1103.33, 0.000352], [9450000.01, 3136.48, 0.000374],
                [52000000.01, 19050.18, 0.000396]],
     'baldio': {'tipo': 'igual', 'art': 'art. 30, fr. I'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.90, 'art': 'art. 32, a'},
                {'id': 'mar', 'et': 'Pagas el año completo en marzo', 'f': 0.95, 'art': 'art. 32, b'}],
     'pronto_nota': 'Pagando así no causas los recargos generados hasta ese momento (art. 32, c).',
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez, madre jefa de familia o con 60 años o más (tu casa, pagando el año antes de abril)', 'f': 0.50, 'tope': 1600000, 'art': 'art. 33'},
         {'id': 'eco', 'et': 'Usas ecotecnias en tu casa (pagando el año antes de abril)', 'f': 0.80, 'tope': 1600000, 'art': 'art. 33'},
         {'id': 'techo1', 'et': 'Naturación extensiva del techo, con constancia', 'f': 0.80, 'art': 'art. 31, fr. VI, a'},
         {'id': 'techo2', 'et': 'Naturación intensiva del techo o jardín vertical, con constancia', 'f': 0.70, 'art': 'art. 31, fr. VI, b'},
         {'id': 'agro', 'et': 'Predio agropecuario en producción, en el padrón municipal', 'f': 0.50, 'art': 'art. 30, fr. II'},
         {'id': 'ac', 'et': 'Institución de asistencia, asociación civil o escuela privada (pagando el año antes de abril)', 'f': 0.50, 'tope': 1600000, 'art': 'art. 31, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa con predio de más de $2,500,000 (pagando el año antes de abril)', 'f': 0.50, 'art': 'art. 31, fr. II'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado (pagando el año antes de abril)', 'f': 0.40, 'art': 'art. 31, fr. IV'}],
     'nota': 'La ley de Zapotlán el Grande no le pone sobretasa a los baldíos: pagan con la misma tabla. Los descuentos de «sobre $1,600,000 de valor fiscal» los leemos como «sobre el primer $1,600,000».',
     'suma_art': 'art. 33',
     'recargo': {'pct': 1.5, 'art': 'art. 42'},
     'multa': {'min': 20, 'max': 55, 'art': 'art. 41'},
     'notif': {'uma': 6, 'art': 'art. 44, fr. I'},
     'ejec': {'pct': 2, 'min_uma': 6, 'max_uma': 1.5 * 365, 'art': 'art. 44, fr. II'}},

    {'id': 'ocotlan', 'ent': 'JAL', 'cve': '063', 'nombre': 'Ocotlán',
     'ley': 'Ley de Ingresos del Municipio de Ocotlán, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Ocotl%C3%A1n'), 'sha256': '2b8297f1a2309afc8c9cb9dab6d08870024c46f4897c6debf33742408aca6fcb',
     'art_tarifa': 'art. 37',
     'tramos': [[0.01, 0.00, 0.000350], [253137.01, 88.60, 0.000350], [365900.01, 128.07, 0.000375],
                [521970.01, 186.59, 0.000399], [744900.01, 275.46, 0.000424], [1121370.01, 435.08, 0.000448],
                [1808800.01, 742.87, 0.000473], [3697800.01, 1636.37, 0.000497], [10772150.01, 5151.37, 0.000522],
                [50045600.01, 25652.11, 0.000546]],
     'tramos_nota': 'La tabla escribe «$3,697.800.00» y «$3,697.800.01»: los leemos como $3,697,800.',
     'baldio': {'tipo': 'sobretasa', 'pct': 90, 'art': 'art. 37'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.85, 'art': 'art. 39, a'},
                {'id': 'mar', 'et': 'Pagas el año completo en marzo', 'f': 0.90, 'art': 'art. 39, b'},
                {'id': 'abr', 'et': 'Pagas el año completo en abril', 'f': 0.95, 'art': 'art. 39, c'}],
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez, con 60 años o más, jefa de familia vulnerable o con cáncer o VIH (tu casa)', 'f': 0.50, 'tope': 589837.50, 'art': 'art. 40'},
         {'id': 'cuida', 'et': 'Cuidas a una persona con discapacidad (tu casa)', 'f': 0.50, 'tope': 589837.50, 'art': 'art. 40'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 589837.50, 'art': 'art. 38, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 38, fr. II'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.40, 'art': 'art. 38, fr. III'}],
     'suma_art': 'art. 40',
     'recargo': {'pct': 1.0, 'art': 'art. 48'},
     'multa': {'min': 20, 'max': 20, 'art': 'art. 47'},
     'notif': {'pct': 10, 'min_uma': 1, 'max_pesos': 3078.91, 'req': True, 'art': 'art. 50, fr. I, a'},
     'ejec': {'pct': 5, 'max_pesos': 4619.00, 'emb': True, 'art': 'art. 50, fr. II, a'}},
    # ── 19-11-2026, tercera entrega: nueve cabeceras regionales más. ──
    {'id': 'ameca', 'ent': 'JAL', 'cve': '006', 'nombre': 'Ameca',
     'ley': 'Ley de Ingresos del Municipio de Ameca, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Ameca'), 'sha256': '7cf8e9a6f6476e16f930f0a91e57b50ad96afbe5c76249be417d9e222fd33b29',
     'art_tarifa': 'art. 18, fr. III, a', 'tarifa': 'millar', 'millar': 0.22,
     'tramos': [[0.00, 10.13, 0.00022]],
     'rustico': {'millar': 0.22, 'cf': 10.13, 'art': 'art. 18, fr. II, a'},
     'baldio': {'tipo': 'millar', 'millar': 0.32, 'cf': 10.13, 'art': 'art. 18, fr. III, b'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.85, 'art': 'art. 20, a'},
                {'id': 'abr', 'et': 'Pagas el año completo en marzo o abril', 'f': 0.95, 'art': 'art. 20, b'}],
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, madre jefa de familia, en viudez o con 60 años o más (tu casa)', 'f': 0.50, 'tope': 477000, 'art': 'art. 21'},
         {'id': 'agro', 'et': 'Predio rústico agropecuario en producción, con constancia', 'f': 0.50, 'art': 'art. 18, fr. II'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 424000, 'art': 'art. 19, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 19, fr. II'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.40, 'art': 'art. 19, fr. III'}],
     'suma_art': 'art. 21',
     'recargo': {'pct': 1.0, 'art': 'art. 28'},
     'multa': {'min': 10, 'max': 30, 'art': 'art. 26, fr. II'},
     'notif': {'pct': 5, 'min_uma': 1, 'max_uma': 30, 'req': True, 'art': 'art. 30, fr. I, a',
               'nota': 'La Ley de Ameca pone el mínimo y el tope de la cobranza en «salarios mínimos»; desde la reforma constitucional de 2016 (DOF 27-01-2016, transitorio tercero) esas referencias se leen en UMA, y así los contamos.'},
     'ejec': {'pct': 5, 'max_uma': 45, 'emb': True, 'art': 'art. 30, fr. II, a'}},

    {'id': 'arandas', 'ent': 'JAL', 'cve': '008', 'nombre': 'Arandas',
     'ley': 'Ley de Ingresos del Municipio de Arandas, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Arandas'), 'sha256': 'a338446b4f0335f5d706915e5d7d2c2da88f761a68a8080c0daa505fa28a9e53',
     'art_tarifa': 'art. 18, fr. I',
     'tramos': [[0.01, 0.00, 0.00073], [77887.01, 56.86, 0.0007305], [145976.01, 106.60, 0.000731],
                [220477.01, 161.06, 0.000815], [338772.01, 257.47, 0.00082], [485408.01, 377.71, 0.000825],
                [721948.01, 572.85, 0.00083], [1255792.01, 1015.94, 0.000835], [2391048.01, 1963.88, 0.00084],
                [6120120.01, 5096.30, 0.000845]],
     'baldio': {'tipo': 'sobretasa', 'pct': 100, 'art': 'art. 18'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.85, 'art': 'art. 20, a'},
                {'id': 'abr', 'et': 'Pagas el año completo en marzo o abril', 'f': 0.90, 'art': 'art. 20, b'}],
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez o con 60 años o más (tu casa)', 'f': 0.50, 'art': 'art. 21'},
         {'id': 'agro', 'et': 'Predio agropecuario en producción, en el padrón municipal', 'f': 0.50, 'art': 'art. 18'},
         {'id': 'techo1', 'et': 'Naturación extensiva del techo, pagando el año en enero o febrero', 'f': 0.80, 'art': 'art. 22 Bis, fr. I'},
         {'id': 'techo2', 'et': 'Naturación intensiva del techo, pagando el año en enero o febrero', 'f': 0.70, 'art': 'art. 22 Bis, fr. II'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'art': 'art. 19, fr. I'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.40, 'art': 'art. 19, fr. IV'}],
     'nota': 'Arandas topa el impuesto: si tu predio no cambió de valor ni de metros construidos, no pagas más de lo de 2025 más 5 %; si cambió, no más de lo de 2025 más 35 % (art. 18). El simulador no sabe lo que pagaste en 2025: compáralo tú. A las asociaciones religiosas les remite al art. 105 de la Ley de Hacienda Municipal, sin decir el porcentaje, y por eso no están en la lista.',
     'suma_art': None,
     'recargo': {'pct': 1.47, 'art': 'art. 29'},
     'multa': {'min': 10, 'max': 10, 'art': 'art. 28'},
     'notif': {'pct': 5, 'min_pesos': 499.00, 'max_pesos': 2930.00, 'req': True, 'art': 'art. 31, fr. I, a'},
     'ejec': {'pct': 5, 'min_pesos': 615.00, 'max_pesos': 4395.00, 'emb': True, 'art': 'art. 31, fr. II, a'}},

    {'id': 'atotonilco', 'ent': 'JAL', 'cve': '013', 'nombre': 'Atotonilco el Alto',
     'ley': 'Ley de Ingresos del Municipio de Atotonilco el Alto, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Atotonilco%20el%20Alto'), 'sha256': 'd49081f2921c45d356c63f61ed8b636a538df699aa7293f0002fafa82d331c72',
     'art_tarifa': 'art. 17, fr. III, a', 'tarifa': 'millar', 'millar': 0.18,
     'tramos': [[0.00, 23.00, 0.00018]],
     'rustico': {'millar': 0.20, 'cf': 23.00, 'art': 'art. 17, fr. II, a'},
     'baldio': {'tipo': 'millar', 'millar': 0.30, 'cf': 23.00, 'art': 'art. 17, fr. III, b'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.85, 'art': 'art. 19, a'},
                {'id': 'abr', 'et': 'Pagas el año completo en marzo o abril', 'f': 0.95, 'art': 'art. 19, b'}],
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez o con 60 años o más (tu casa)', 'f': 0.50, 'tope': 1500000, 'art': 'art. 20'},
         {'id': 'agro', 'et': 'Predio rústico agropecuario en producción de 10 hectáreas o más, con constancia', 'f': 0.70, 'art': 'art. 17, fr. II'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 1500000, 'art': 'art. 18, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 18, fr. II'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.40, 'art': 'art. 18, fr. III'}],
     'suma_art': 'art. 20',
     'recargo': {'pct': 1.0, 'art': 'art. 29'},
     'multa': {'min': 10, 'max': 30, 'art': 'art. 28'},
     'notif': {'pct': 5, 'min_uma': 1, 'max_uma': 30, 'req': True, 'art': 'art. 31, fr. I, a'},
     'ejec': {'pct': 5, 'max_uma': 45, 'emb': True, 'art': 'art. 31, fr. II, a'}},

    {'id': 'autlan', 'ent': 'JAL', 'cve': '015', 'nombre': 'Autlán de Navarro',
     'ley': 'Ley de Ingresos del Municipio de Autlán de Navarro, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Autl%C3%A1n%20de%20Navarro'), 'sha256': '6c730c97a6d76f011fa4367269f60fad2988bd8492e2cbed014f14e34af28220',
     'art_tarifa': 'art. 18, fr. III, a', 'tarifa': 'millar', 'millar': 0.21,
     'tramos': [[0.00, 13.01, 0.00021]],
     'rustico': {'millar': 0.20, 'cf': 13.00, 'art': 'art. 18, fr. II, a'},
     'baldio': {'tipo': 'millar', 'millar': 0.35, 'cf': 32.19, 'art': 'art. 18, fr. III, c'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.85, 'art': 'art. 20, a'},
                {'id': 'abr', 'et': 'Pagas el año completo en marzo o abril', 'f': 0.95, 'art': 'art. 20, b'}],
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez, con 60 años o más o cuidador de una persona con discapacidad severa (tu casa)', 'f': 0.50, 'tope': 560000, 'art': 'art. 21'},
         {'id': 'agro', 'et': 'Predio rústico agropecuario en producción, con constancia', 'f': 0.50, 'art': 'art. 18, fr. II'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 600000, 'art': 'art. 19, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 19, fr. II'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.40, 'art': 'art. 19, fr. III'}],
     'nota': 'Para el baldío usamos la tasa de los predios dentro de la zona urbana de la cabecera (0.35 al millar); fuera de ella es 0.30 al millar, con la misma cuota fija de $32.19 (art. 18, fr. III, b). La ley dice además que el predial «en ningún caso» será inferior a una UMA (art. 21), sin decir si por bimestre o por año.',
     'suma_art': 'art. 21',
     'recargo': {'pct': 1.0, 'art': 'art. 28'},
     'multa': {'min': 10, 'max': 30, 'art': 'art. 27'},
     'notif': {'pct': 5, 'min_uma': 1, 'max_uma': 30, 'req': True, 'art': 'art. 30, fr. I, a'},
     'ejec': {'pct': 5, 'max_uma': 45, 'emb': True, 'art': 'art. 30, fr. II, a'}},

    {'id': 'cihuatlan', 'ent': 'JAL', 'cve': '022', 'nombre': 'Cihuatlán',
     'ley': 'Ley de Ingresos del Municipio de Cihuatlán, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Cihuatl%C3%A1n'), 'sha256': 'c2b201bcd66bd5b6b88d3f48117d3a6fe8aecccf3afbee9a97bbdb065bd8d094',
     'art_tarifa': 'art. 18, fr. III, f', 'tarifa': 'millar', 'millar': 0.17,
     'tramos': [[0.00, 18.02, 0.00017]],
     'rustico': {'millar': 0.20, 'cf': 15.78, 'art': 'art. 18, fr. II, d'},
     'baldio': {'tipo': 'millar', 'millar': 0.33, 'cf': 18.02, 'art': 'art. 18, fr. III, g'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.85, 'art': 'art. 20, a'},
                {'id': 'abr', 'et': 'Pagas el año completo en marzo o abril', 'f': 0.95, 'art': 'art. 20, b'}],
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez o con 60 años o más (tu casa)', 'f': 0.50, 'tope': 425000, 'art': 'art. 21'},
         {'id': 'agro', 'et': 'Predio rústico agropecuario en producción, con constancia', 'f': 0.50, 'art': 'art. 18, fr. II, d'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 420000, 'art': 'art. 19, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 19, fr. II'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.40, 'art': 'art. 19, fr. III'}],
     'nota': 'Son las tasas de los predios con valor real, según la Ley de Hacienda Municipal (art. 18, fr. II, d, y fr. III, f y g). Si tu predio se valuó por última vez antes del año 2000, la ley le pone tasas más altas (de 0.16 a 1.50 al millar) hasta que se actualice su valor.',
     'suma_art': 'art. 21',
     'recargo': {'pct': 1.0, 'art': 'art. 29'},
     'multa': {'min': 10, 'max': 30, 'art': 'art. 28'},
     'notif': {'pct': 5, 'min_uma': 1, 'max_uma': 30, 'req': True, 'art': 'art. 31, fr. I, a'},
     'ejec': {'pct': 5, 'max_uma': 45, 'emb': True, 'art': 'art. 31, fr. II, a'}},

    {'id': 'jocotepec', 'ent': 'JAL', 'cve': '050', 'nombre': 'Jocotepec',
     'ley': 'Ley de Ingresos del Municipio de Jocotepec, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Jocotepec'), 'sha256': 'a3a1d601931f847c20066ec7bc81a008a7a9de03c2956cc2380ea6abadc38aae',
     'art_tarifa': 'art. 40, fr. II, b', 'tarifa': 'millar', 'millar': 0.21,
     'tramos': [[0.00, 5.46, 0.00021]],
     'rustico': {'millar': 0.21, 'cf': 12.01, 'art': 'art. 40, fr. I, b'},
     'baldio': {'tipo': 'millar', 'millar': 0.85, 'cf': 5.46, 'art': 'art. 40, fr. II, d'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.85, 'art': 'art. 41, a'},
                {'id': 'abr', 'et': 'Pagas el año completo en marzo o abril', 'f': 0.95, 'art': 'art. 41, b'}],
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez o con 60 años o más (tu casa)', 'f': 0.50, 'tope': 420000, 'suma': True, 'art': 'art. 43, fr. IV'},
         {'id': 'ac', 'et': 'Asociación civil de asistencia o enseñanza gratuita, con dictamen', 'f': 0.50, 'art': 'art. 43, fr. I'},
         {'id': 'esc', 'et': 'Centro de educación superior (predio de enseñanza o investigación)', 'f': 0.50, 'art': 'art. 43, fr. II'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.40, 'art': 'art. 43, fr. III'},
         {'id': 'jardin', 'et': 'Baldío convertido en jardín ornamental, con dictamen', 'f': 0.50, 'art': 'art. 40, fr. II'}],
     'nota': 'Para el baldío usamos la tasa de los predios dentro de la zona urbana de hasta 10,000 m² (0.85 al millar); fuera de la zona urbana es 0.53 y dentro, con más de 10,000 m², 1.05 (art. 40, fr. II, c y e). A los predios agropecuarios la ley les da una «tasa preferente» de 0.84 al millar, más alta que la general de 0.21 (art. 40, fr. I, c), y por eso no la ponemos como descuento. El de naturación de techos va «del 20 al 30 %» sin decir cuándo cada uno (art. 41, c). Si tu predio no cambió de valor, el impuesto no sube más de 25 % sobre el del año anterior (art. 43, fr. VI).',
     'suma_art': 'art. 44',
     'recargo': {'pct': 1.0, 'art': 'art. 53'},
     'multa': {'min': 10, 'max': 30, 'art': 'art. 52'},
     'notif': {'pct': 5, 'min_uma': 1, 'max_uma': 30, 'req': True, 'art': 'art. 55, fr. I, a'},
     'ejec': {'pct': 5, 'max_uma': 45, 'emb': True, 'art': 'art. 55, fr. II, a'}},

    {'id': 'labarca', 'ent': 'JAL', 'cve': '018', 'nombre': 'La Barca',
     'ley': 'Ley de Ingresos del Municipio de La Barca, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('La%20Barca'), 'sha256': '6ff772001f1a4794f6ee461d0489cee205ac4e6703203445e62dac753371061e',
     'art_tarifa': 'art. 27, fr. I',
     'tramos': [[0.01, 18.00, 0.000250], [183818.01, 63.95, 0.000255], [284110.01, 89.53, 0.000260],
                [384972.01, 115.75, 0.000265], [512026.01, 149.42, 0.000270], [729900.01, 208.25, 0.000275],
                [1295666.01, 363.83, 0.000280], [2858250.01, 801.36, 0.000285], [8010092.01, 2269.63, 0.000290],
                [23804554.01, 6850.03, 0.000295]],
     'baldio': {'tipo': 'sobretasa', 'pct': 100, 'art': 'art. 27'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.85, 'art': 'art. 29, a'},
                {'id': 'abr', 'et': 'Pagas el año completo en marzo o abril', 'f': 0.95, 'art': 'art. 29, b'}],
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez o con 60 años o más (tu casa)', 'f': 0.50, 'tope': 420000, 'art': 'art. 31'},
         {'id': 'jefa', 'et': 'Madre jefa de familia', 'f': 0.50, 'art': 'art. 28, fr. IV'},
         {'id': 'eco', 'et': 'Casa con calentador solar, celdas solares o captación de lluvia, con dictamen', 'f': 0.75, 'tope': 750000, 'art': 'art. 30'},
         {'id': 'agro', 'et': 'Predio agropecuario en producción, en el padrón municipal', 'f': 0.50, 'art': 'art. 27, fr. II'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 415000, 'art': 'art. 28, fr. I'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.40, 'art': 'art. 28, fr. III'}],
     'nota': 'A las asociaciones religiosas, la Ley de La Barca les remite al art. 105 de la Ley de Hacienda Municipal, sin decir el porcentaje, y por eso no están en la lista.',
     'suma_art': 'art. 31',
     'recargo': {'pct': 1.3, 'art': 'art. 39'},
     'multa': {'min': 30, 'max': 50, 'art': 'art. 37, fr. II'},
     'notif': {'pct': 5, 'min_uma': 1, 'max_uma': 30, 'req': True, 'art': 'art. 41, fr. I, a'},
     'ejec': {'pct': 5, 'max_uma': 45, 'emb': True, 'art': 'art. 41, fr. II, a'}},

    {'id': 'sanjuan', 'ent': 'JAL', 'cve': '073', 'nombre': 'San Juan de los Lagos',
     'ley': 'Ley de Ingresos del Municipio de San Juan de los Lagos, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('San%20Juan%20de%20los%20Lagos'), 'sha256': '9509052c26476d1b134f1c56accc8a1bc21702e2dab1a13a1c3ceb4cc4fd2b91',
     'art_tarifa': 'art. 22, fr. II, a', 'tarifa': 'millar', 'millar': 0.23,
     'tramos': [[0.00, 37.80, 0.00023]],
     'rustico': {'millar': 0.23, 'cf': 38.00, 'art': 'art. 22, fr. I, a'},
     'baldio': {'tipo': 'millar', 'millar': 0.46, 'cf': 37.80, 'art': 'art. 22, fr. II, b'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.85, 'art': 'art. 24'},
                {'id': 'abr', 'et': 'Pagas el año completo en marzo o abril', 'f': 0.90, 'art': 'art. 24'}],
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez o con 60 años o más (tu casa)', 'f': 0.50, 'tope': 873613.62, 'art': 'art. 25'},
         {'id': 'agro', 'et': 'Predio rústico agropecuario en producción, con constancia', 'f': 0.50, 'art': 'art. 22, fr. I'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 873613.62, 'art': 'art. 23, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 23, fr. II'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.40, 'art': 'art. 23, fr. III'}],
     'suma_art': 'art. 25',
     'recargo': {'pct': 1.47, 'art': 'art. 33'},
     'multa': {'min': 10, 'max': 30, 'art': 'art. 31, fr. II'},
     'notif': {'pct': 5, 'min_uma': 1, 'max_uma': 30, 'req': True, 'art': 'art. 35, fr. I'},
     'ejec': {'pct': 5, 'max_uma': 45, 'emb': True, 'art': 'art. 35, fr. II'}},

    {'id': 'tequila', 'ent': 'JAL', 'cve': '094', 'nombre': 'Tequila',
     'ley': 'Ley de Ingresos del Municipio de Tequila, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Tequila'), 'sha256': 'dc16f67912f50a8e845dfc055be0f54c4f76a0548086c17700ed9cc22d346c11',
     'art_tarifa': 'art. 32',
     'tramos': [[0.01, 87.15, 0.00026], [159350.01, 128.58, 0.00026], [280800.01, 160.16, 0.00032],
                [436300.01, 209.92, 0.00037], [699564.01, 307.33, 0.00042], [1210560.01, 521.94, 0.00047],
                [2616069.01, 1182.53, 0.00053], [5927800.01, 2937.75, 0.00058], [13696000.01, 7443.31, 0.00063],
                [29030931.01, 17104.31, 0.00068]],
     'baldio': {'tipo': 'igual', 'art': 'art. 32'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.85, 'art': 'art. 34'},
                {'id': 'abr', 'et': 'Pagas el año completo en marzo o abril', 'f': 0.95, 'art': 'art. 34'}],
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez, madre jefa de familia o con 60 años o más (tu casa)', 'f': 0.50, 'tope': 1190910, 'art': 'art. 33'},
         {'id': 'eco', 'et': 'Casa con techo naturado, calentador solar, celdas solares o captación de lluvia, con dictamen', 'f': 0.75, 'art': 'art. 34'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 530000, 'art': 'art. 33'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 33'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.40, 'art': 'art. 33'}],
     'nota': 'Para los descuentos del art. 33 la ley pide no deber al municipio otros impuestos, derechos ni aprovechamientos. Quien paga todo lo atrasado del predial, con multas y recargos generados hasta abril de 2026, tiene 75 % de descuento en esas multas y recargos (art. 34): el simulador no lo resta.',
     'suma_art': 'art. 33',
     'recargo': {'pct': 1.0, 'art': 'art. 42'},
     'multa': {'min': 20, 'max': 50, 'art': 'art. 43'},
     'notif': {'pesos': 106.85, 'art': 'art. 45 (en la cabecera)'},
     'ejec': {'pct': 5, 'min_pesos': 106.85, 'art': 'art. 45 (en la cabecera)'}},
    {'id': 'tamazula', 'ent': 'JAL', 'cve': '085', 'nombre': 'Tamazula de Gordiano',
     'ley': 'Ley de Ingresos del Municipio de Tamazula de Gordiano, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Tamazula%20de%20Gordiano'), 'sha256': 'f4c7cc8f2836404021a26e94866d136bd8d4e864630f71effe1c4b54c6dd32b2',
     'art_tarifa': 'art. 36, fr. I',
     'tramos': [[0.01, 0.00, 0.00022], [207000.01, 45.54, 0.00022], [360700.01, 79.35, 0.000242],
                [552000.01, 125.65, 0.000264], [814000.01, 194.82, 0.000286], [1237000.01, 315.79, 0.000308],
                [1995000.01, 549.26, 0.00033], [3674000.01, 1103.33, 0.000352], [9450000.01, 3136.48, 0.000374],
                [52000000.01, 19050.18, 0.000396]],
     'minimo': {'pesos': 50.00, 'art': 'art. 42'},
     'baldio': {'tipo': 'sobretasa', 'pct': 100, 'art': 'art. 36, fr. I'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.85, 'art': 'art. 37, a'},
                {'id': 'abr', 'et': 'Pagas el año completo en marzo o abril', 'f': 0.95, 'art': 'art. 37, b'}],
     'pronto_nota': 'El art. 37 dice además que si pagas en enero o febrero por internet, en kioscos, tiendas o bancos «se aplicará la tarifa de factor del 0.93»: no aclara si sustituye o se suma al 0.85, así que el simulador usa el 0.85 de la ventanilla.',
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez o con 60 años o más (tu casa; pagas el año antes de mayo)', 'f': 0.50, 'tope': 1200000, 'art': 'art. 39'},
         {'id': 'madre', 'et': 'Madre jefa de familia inscrita en el padrón estatal (tu casa)', 'f': 0.50, 'hasta': 1123500, 'art': 'art. 39 bis'},
         {'id': 'eco', 'et': 'Casa con techo naturado, calentador solar, celdas solares o captación de lluvia, con dictamen', 'f': 0.75, 'tope': 750000, 'art': 'art. 41'},
         {'id': 'agro', 'et': 'Predio agropecuario en producción, registrado', 'f': 0.50, 'tope': 750000, 'art': 'art. 36, fr. II'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'art': 'art. 38, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa (valor fiscal de más de $2,500,000)', 'f': 0.50, 'art': 'art. 38, fr. II'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.50, 'art': 'art. 38, fr. III'}],
     'suma_art': 'art. 42',
     'nota': 'Tamazula da un solo beneficio, el de mayor cuantía, y a un solo inmueble (art. 42); y en ningún caso el predial baja de $50 por bimestre (art. 42). La escuela gratuita con validez oficial tiene 80 % de descuento (art. 38, fr. I, f).',
     'recargo': {'pct': 1.47, 'art': 'art. 57'},
     'multa': {'min': 30, 'max': 30, 'art': 'art. 55'},
     'notif': {'uma': 6, 'art': 'art. 58, fr. I'},
     'ejec': {'pct': 3, 'min_uma': 6, 'max_uma': 547.5, 'art': 'art. 58, fr. II'}},
    {'id': 'encarnacion', 'ent': 'JAL', 'cve': '035', 'nombre': 'Encarnación de Díaz',
     'ley': 'Ley de Ingresos del Municipio de Encarnación de Díaz para el ejercicio fiscal 2026',
     'url': CONGRESO + 'Ley%20de%20Ingresos%20del%20Municipio%20de%20Encarnaci%C3%B3n%20de%20D%C3%ADaz%20para%20el%20ejercicio%20fiscal%202026-300126.pdf',
     'sha256': '5c56b16f26258c569560f603102a3abac92c091f4ee2b10f68a2f85050dd668a',
     'art_tarifa': 'art. 17, fr. III, a', 'tarifa': 'millar', 'millar': 0.20,
     'tramos': [[0.00, 25.00, 0.00020]],
     'rustico': {'millar': 0.21, 'cf': 22.00, 'art': 'art. 17, fr. II, a'},
     'baldio': {'tipo': 'millar', 'millar': 0.32, 'cf': 25.00, 'art': 'art. 17, fr. III, b'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.80, 'art': 'art. 19, a'}],
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez o con 60 años o más (tu casa)', 'f': 0.50, 'tope': 462000, 'art': 'art. 20'},
         {'id': 'agro', 'et': 'Predio rústico agropecuario en producción, con constancia', 'f': 0.50, 'art': 'art. 17, fr. II'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 421000, 'art': 'art. 18, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 18, fr. II'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.40, 'art': 'art. 18, fr. III'}],
     'suma_art': 'art. 20',
     'nota': 'El art. 20 da un solo beneficio, el de mayor cuantía, y dice que el predial no baja de las cuotas fijas, salvo para pensionados, jubilados y adultos mayores. La tasa de la fr. I del art. 17 (10 al millar) es para predios que aún tributan con su base fiscal registrada, sin valuación: el simulador no la usa.',
     'recargo': {'pct': 1.47, 'art': 'art. 29'},
     'multa': {'min': 10, 'max': 30, 'art': 'art. 28'},
     'notif': {'pct': 5, 'min_uma': 1, 'max_uma': 30, 'req': True, 'art': 'art. 31, fr. I, a (en la cabecera)'},
     'ejec': {'pct': 5, 'max_uma': 45, 'emb': True, 'art': 'art. 31, fr. II, a (en la cabecera)'}},
    {'id': 'acatic', 'ent': 'JAL', 'cve': '001', 'nombre': 'Acatic',
     'ley': 'Ley de Ingresos del Municipio de Acatic, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Acatic'), 'sha256': 'f71518e3bfecb3650a3bf35c2c73a407636f07d4e551879dd1f3f1999a52cae0',
     'art_tarifa': 'art. 17, fr. III, a', 'tarifa': 'millar', 'millar': 0.21,
     'tramos': [[0.00, 28.30, 0.00021]],
     'rustico': {'millar': 0.23, 'cf': 20.00, 'art': 'art. 17, fr. II, b'},
     'baldio': {'tipo': 'millar', 'millar': 0.32, 'cf': 28.30, 'art': 'art. 17, fr. III, b'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.85, 'art': 'art. 19, a'},
                {'id': 'abr', 'et': 'Pagas el año completo en marzo o abril', 'f': 0.95, 'art': 'art. 19, b'}],
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez, madre soltera o con 60 años o más (tu casa)', 'f': 0.50, 'tope': 440000, 'art': 'art. 20'},
         {'id': 'agro', 'et': 'Predio rústico agropecuario en producción, con constancia', 'f': 0.75, 'art': 'art. 17, fr. II'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 415000, 'art': 'art. 18, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 18, fr. II'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.40, 'art': 'art. 18, fr. III'}],
     'suma_art': 'art. 20',
     'recargo': {'pct': 1.0, 'art': 'art. 28'},
     'multa': {'min': 10, 'max': 30, 'art': 'art. 29'},
     'nota': 'La multa del art. 29 va por lo que tardaste: 10 % de 1 a 6 meses, 20 % de 6 a 12 y 30 % de más de 12.',
     'notif': {'pct': 5, 'min_uma': 1, 'max_pesos': 2727.00, 'req': True, 'art': 'art. 31, fr. I, a'},
     'ejec': {'pct': 5, 'max_pesos': 4091.00, 'emb': True, 'art': 'art. 31, fr. II, a'}},

    {'id': 'ayotlan', 'ent': 'JAL', 'cve': '016', 'nombre': 'Ayotlán',
     'ley': 'Ley de Ingresos del Municipio de Ayotlán, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Ayotl%C3%A1n'), 'sha256': '1222f77a6582a4ffdcab167245d5e67154b613f4453467a2f1233c1c6cb86bd1',
     'art_tarifa': 'art. 17, fr. III, a', 'tarifa': 'millar', 'millar': 0.25,
     'tramos': [[0.00, 27.80, 0.00025]],
     'rustico': {'millar': 0.25, 'cf': 23.10, 'art': 'art. 17, fr. II, a'},
     'baldio': {'tipo': 'millar', 'millar': 0.38, 'cf': 27.80, 'art': 'art. 17, fr. III, b'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.85, 'art': 'art. 19, a'},
                {'id': 'abr', 'et': 'Pagas el año completo en marzo o abril', 'f': 0.95, 'art': 'art. 19, b'}],
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez o con 60 años o más (tu casa)', 'f': 0.50, 'tope': 720000, 'art': 'art. 20'},
         {'id': 'agro', 'et': 'Predio rústico agropecuario en producción, con constancia', 'f': 0.50, 'art': 'art. 17, fr. II'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 720000, 'art': 'art. 18, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 18, fr. II'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.40, 'art': 'art. 18, fr. III'}],
     'nota': 'El art. 21 da además 50 % (enero y febrero) o 25 % (marzo y abril) a quien registra su título del PROCEDE o del INSUS, o manifiesta su construcción: el simulador no lo resta.',
     'suma_art': 'art. 20',
     'recargo': {'pct': 1.0, 'art': 'art. 29'},
     'multa': {'min': 30, 'max': 30, 'art': 'art. 28'},
     'notif': {'pct': 5, 'min_uma': 1, 'max_uma': 30, 'req': True, 'art': 'art. 31, fr. I, a'},
     'ejec': {'pct': 5, 'max_uma': 45, 'emb': True, 'art': 'art. 31, fr. II, a'}},

    {'id': 'colotlan', 'ent': 'JAL', 'cve': '025', 'nombre': 'Colotlán',
     'ley': 'Ley de Ingresos del Municipio de Colotlán, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Colotl%C3%A1n'), 'sha256': '13731e9817c34816aeb20382b14a6b5b5a88176713b27cb3d757d2c9120e481e',
     'art_tarifa': 'art. 17, fr. III, a', 'tarifa': 'millar', 'millar': 0.17,
     'tramos': [[0.00, 16.54, 0.00017]],
     'rustico': {'millar': 0.21, 'cf': 13.89, 'art': 'art. 17, fr. II, a'},
     'baldio': {'tipo': 'millar', 'millar': 0.31, 'cf': 28.93, 'art': 'art. 17, fr. III, b'},
     'pronto': [{'id': 'ene', 'et': 'Pagas el año completo en enero', 'f': 0.85, 'art': 'art. 19, a'},
                {'id': 'feb', 'et': 'Pagas el año completo en febrero', 'f': 0.90, 'art': 'art. 19, b'},
                {'id': 'mar', 'et': 'Pagas el año completo en marzo', 'f': 0.95, 'art': 'art. 19, c'}],
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez o con 60 años o más (tu casa)', 'f': 0.50, 'art': 'art. 20'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'art': 'art. 18, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 18, fr. II'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.40, 'art': 'art. 18, fr. III'}],
     'nota': 'El art. 20 da el 50 % a pensionados y personas mayores «durante los primeros cuatro meses del año»: pregunta en la Hacienda Municipal si vale para los bimestres que pagues después.',
     'suma_art': 'art. 20',
     'recargo': {'pct': 1.0, 'art': 'art. 29'},
     'multa': {'min': 10, 'max': 30, 'art': 'art. 28'},
     'notif': {'pct': 5, 'min_uma': 1, 'max_uma': 30, 'req': True, 'art': 'art. 31, fr. I, a'},
     'ejec': {'pct': 5, 'max_uma': 45, 'emb': True, 'art': 'art. 31, fr. II, a'}},

    {'id': 'elarenal', 'ent': 'JAL', 'cve': '009', 'nombre': 'El Arenal',
     'ley': 'Ley de Ingresos del Municipio de El Arenal, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('El%20Arenal'), 'sha256': 'ccb0cd6768cd711ac53ba0c066d11e8af225aa4ce0de349b80c8b431e4661edf',
     'art_tarifa': 'art. 17, fr. III, a', 'tarifa': 'millar', 'millar': 0.16,
     'tramos': [[0.00, 36.63, 0.00016]],
     'rustico': {'millar': 0.2, 'cf': 36.63, 'art': 'art. 17, fr. II, a'},
     'baldio': {'tipo': 'millar', 'millar': 0.3, 'cf': 36.63, 'art': 'art. 17, fr. III, b'},
     'pronto': [{'id': 'mar', 'et': 'Pagas el año completo en enero, febrero o marzo', 'f': 0.85, 'art': 'art. 19, a'}],
     'pronto_nota': 'Si pagas el año completo en abril no hay descuento, pero no causas los recargos de ese periodo (art. 19, b).',
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez o con 60 años o más (tu casa)', 'f': 0.50, 'art': 'art. 20'},
         {'id': 'agro', 'et': 'Predio rústico agropecuario en producción, con constancia', 'f': 0.50, 'art': 'art. 17, fr. II'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 415000, 'art': 'art. 18, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 18, fr. II'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.40, 'art': 'art. 18, fr. III'}],
     'suma_art': 'art. 20',
     'recargo': {'pct': 1.0, 'art': 'art. 29'},
     'multa': {'min': 10, 'max': 30, 'art': 'art. 28'},
     'notif': {'pct': 5, 'min_uma': 1, 'max_uma': 30, 'req': True, 'art': 'art. 31, fr. I, a'},
     'ejec': {'pct': 5, 'max_uma': 45, 'emb': True, 'art': 'art. 31, fr. II, a'}},

    {'id': 'jalostotitlan', 'ent': 'JAL', 'cve': '046', 'nombre': 'Jalostotitlán',
     'ley': 'Ley de Ingresos del Municipio de Jalostotitlán, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Jalostotitl%C3%A1n'), 'sha256': '27c98a00ecf88b612275bf7c193cba26fdff1aee0c318e64a9cedd28afb548e0',
     'art_tarifa': 'art. 18, fr. II, a', 'tarifa': 'millar', 'millar': 0.22,
     'tramos': [[0.00, 25.00, 0.00022]],
     'rustico': {'millar': 0.20, 'cf': 23.00, 'art': 'art. 18, fr. I, a'},
     'baldio': {'tipo': 'millar', 'millar': 0.32, 'cf': 25.00, 'art': 'art. 18, fr. II, b'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.85, 'art': 'art. 20, a'},
                {'id': 'abr', 'et': 'Pagas el año completo en marzo o abril', 'f': 0.95, 'art': 'art. 20, b'}],
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez o con 60 años o más (tu casa)', 'f': 0.50, 'tope': 420000, 'art': 'art. 21'},
         {'id': 'nat1', 'et': 'Techo naturado extensivo, con constancia, pagando el año en enero o febrero', 'f': 0.80, 'art': 'art. 20-Bis, fr. I'},
         {'id': 'nat2', 'et': 'Techo naturado intensivo, con constancia, pagando el año en enero o febrero', 'f': 0.70, 'art': 'art. 20-Bis, fr. II'},
         {'id': 'agro', 'et': 'Predio rústico agropecuario en producción, con constancia', 'f': 0.50, 'art': 'art. 18, fr. I'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 400000, 'art': 'art. 19, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 19, fr. II'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.40, 'art': 'art. 19, fr. III'}],
     'nota': 'El descuento por techo naturado no se junta con el pago anticipado ni con el de pensionados (art. 20-Bis).',
     'suma_art': 'art. 21',
     'recargo': {'pct': 1.0, 'art': 'art. 29'},
     'multa': {'min': 10, 'max': 30, 'art': 'art. 28'},
     'notif': {'pct': 5, 'min_uma': 1, 'max_uma': 30, 'req': True, 'art': 'art. 31, fr. I, a'},
     'ejec': {'pct': 5, 'max_uma': 45, 'emb': True, 'art': 'art. 31, fr. II, a'}},

    {'id': 'magdalena', 'ent': 'JAL', 'cve': '055', 'nombre': 'Magdalena',
     'ley': 'Ley de Ingresos del Municipio de Magdalena, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Magdalena'), 'sha256': '54e2582c99cd5686ca7d33213926aed8d1c789982a1f4b1b7f7b449e2a4fc288',
     'art_tarifa': 'art. 17, fr. II, a', 'tarifa': 'millar', 'millar': 0.21,
     'tramos': [[0.00, 45.00, 0.00021]],
     'rustico': {'millar': 0.21, 'cf': 25.00, 'art': 'art. 17, fr. I, a'},
     'baldio': {'tipo': 'millar', 'millar': 0.31, 'cf': 45.00, 'art': 'art. 17, fr. II, b'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.85, 'art': 'art. 19, a'},
                {'id': 'abr', 'et': 'Pagas el año completo en marzo o abril', 'f': 0.95, 'art': 'art. 19, b'}],
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez, madre jefa de familia (Predial Rosa) o con 60 años o más (tu casa)', 'f': 0.50, 'tope': 700000, 'art': 'art. 20'},
         {'id': 'agro', 'et': 'Predio rústico agropecuario en producción, con constancia', 'f': 0.80, 'art': 'art. 17, fr. I'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 700000, 'art': 'art. 18'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 18, fr. I'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.40, 'art': 'art. 18, fr. II'}],
     'nota': 'Si tu casa subió de valor por una revaluación, el art. 21 limita lo que puede subir el impuesto frente al año pasado: 10 % hasta $383,000, 15 % hasta $500,000 y 20 % hasta $1,000,000 de valor fiscal. El simulador no conoce lo que pagaste el año pasado y no aplica ese tope.',
     'suma_art': 'art. 20',
     'recargo': {'pct': 1.0, 'art': 'art. 29'},
     'multa': {'min': 10, 'max': 30, 'art': 'art. 28'},
     'notif': {'pct': 5, 'min_uma': 1, 'max_uma': 30, 'req': True, 'art': 'art. 31, fr. I, a'},
     'ejec': {'pct': 5, 'max_uma': 45, 'emb': True, 'art': 'art. 31, fr. II, a'}},

    {'id': 'sanmiguel', 'ent': 'JAL', 'cve': '078', 'nombre': 'San Miguel el Alto',
     'ley': 'Ley de Ingresos del Municipio de San Miguel el Alto, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('San%20Miguel%20el%20Alto'), 'sha256': 'ec3c1da4a00491aabb4f203f2823c06dd57a4621acb2cec8f2c99d61317a460d',
     'art_tarifa': 'art. 17, fr. III, a', 'tarifa': 'millar', 'millar': 0.17,
     'tramos': [[0.00, 25.00, 0.00017]],
     'rustico': {'millar': 0.20, 'cf': 19.00, 'art': 'art. 17, fr. II, a'},
     'baldio': {'tipo': 'millar', 'millar': 0.30, 'cf': 25.00, 'art': 'art. 17, fr. III, b'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.85, 'art': 'art. 19, a'},
                {'id': 'jul', 'et': 'Pagas el año completo de marzo a julio', 'f': 0.95, 'art': 'art. 19, b'}],
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez o con 60 años o más (tu casa)', 'f': 0.50, 'tope': 436800, 'art': 'art. 20'},
         {'id': 'agro', 'et': 'Predio rústico agropecuario en producción, con constancia', 'f': 0.50, 'art': 'art. 17, fr. II'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 431600, 'art': 'art. 18, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 18, fr. II'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.40, 'art': 'art. 18, fr. III'}],
     'nota': 'La multa del art. 28 habla del pago «de los derechos» aunque está entre los accesorios de los impuestos; por esa duda el simulador no la pone.',
     'suma_art': 'art. 20',
     'recargo': {'pct': 1.0, 'art': 'art. 29'},
     'notif': {'pct': 5, 'min_uma': 1, 'max_uma': 30, 'req': True, 'art': 'art. 31, fr. I, a'},
     'ejec': {'pct': 5, 'max_uma': 45, 'emb': True, 'art': 'art. 31, fr. II, a'}},

    {'id': 'teocaltiche', 'ent': 'JAL', 'cve': '091', 'nombre': 'Teocaltiche',
     'ley': 'Ley de Ingresos del Municipio de Teocaltiche, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Teocaltiche'), 'sha256': 'deaae9476d2a15775a7c9c821b304d9552a2b01b1712437809907875f27b0ee1',
     'art_tarifa': 'art. 38, fr. III, a', 'tarifa': 'millar', 'millar': 0.20,
     'tramos': [[0.00, 30.30, 0.00020]],
     'rustico': {'millar': 0.25, 'cf': 19.13, 'art': 'art. 38, fr. II, a'},
     'baldio': {'tipo': 'millar', 'millar': 0.41, 'cf': 30.30, 'art': 'art. 38, fr. III, b'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.90, 'art': 'art. 40, fr. I'},
                {'id': 'mar', 'et': 'Pagas el año completo en marzo', 'f': 0.95, 'art': 'art. 40, fr. II'}],
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez o con 60 años o más (tu casa)', 'f': 0.50, 'tope': 450000, 'art': 'art. 41'},
         {'id': 'nat1', 'et': 'Techo naturado extensivo, con constancia', 'f': 0.80, 'art': 'art. 42, fr. I'},
         {'id': 'nat2', 'et': 'Techo naturado intensivo o jardín vertical, con constancia', 'f': 0.70, 'art': 'art. 42, fr. II'},
         {'id': 'agro', 'et': 'Predio rústico agropecuario en producción, con constancia', 'f': 0.50, 'art': 'art. 38, fr. II'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 441000, 'art': 'art. 39, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 39, fr. I'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.40, 'art': 'art. 39, fr. II'}],
     'nota': 'El art. 50 dice que el recargo es de 1 % mensual «acumulativo»; el simulador lo suma mes por mes, sin recargo sobre recargo.',
     'suma_art': 'art. 41',
     'recargo': {'pct': 1.0, 'art': 'art. 50'},
     'multa': {'min': 25, 'max': 25, 'art': 'art. 49'},
     'notif': {'pct': 5, 'max_pesos': 2440.22, 'req': True, 'art': 'art. 52, fr. I, a'},
     'ejec': {'pct': 5, 'max_pesos': 4449.16, 'emb': True, 'art': 'art. 52, fr. II, a'}},

    {'id': 'tototlan', 'ent': 'JAL', 'cve': '105', 'nombre': 'Tototlán',
     'ley': 'Ley de Ingresos del Municipio de Tototlán, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Tototl%C3%A1n'), 'sha256': '7ec563f9cbbc0980a644e4bc317a25c4696ef12b28286e002d389335ee634f30',
     'art_tarifa': 'art. 18, fr. II, a', 'tarifa': 'millar', 'millar': 0.21,
     'tramos': [[0.00, 22.30, 0.00021]],
     'rustico': {'millar': 0.26, 'cf': 18.59, 'art': 'art. 18, fr. I, a'},
     'baldio': {'tipo': 'millar', 'millar': 0.40, 'cf': 22.30, 'art': 'art. 18, fr. II, b'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.85, 'art': 'art. 20'},
                {'id': 'abr', 'et': 'Pagas el año completo en marzo o abril', 'f': 0.95, 'art': 'art. 20'}],
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez o con 60 años o más (tu casa)', 'f': 0.50, 'tope': 420000, 'art': 'art. 21'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 457537.50, 'art': 'art. 19, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 19, fr. II'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado, con constancia de Obras Públicas', 'f': 0.50, 'art': 'art. 19, fr. III'}],
     'nota': 'El art. 18, fr. I da 50 % a los predios agropecuarios de 10 hectáreas o más, pero junto a esa reducción escribe un «0.30» que no explica; por esa duda el simulador no la ofrece.',
     'suma_art': 'art. 21',
     'recargo': {'pct': 1.0, 'art': 'art. 30'},
     'multa': {'min': 9, 'max': 32, 'art': 'art. 29'},
     'notif': {'pct': 5, 'min_uma': 1, 'max_uma': 30, 'req': True, 'art': 'art. 32, fr. I'},
     'ejec': {'pct': 5, 'max_uma': 45, 'emb': True, 'art': 'art. 32, fr. II'}},

    {'id': 'zacoalco', 'ent': 'JAL', 'cve': '119', 'nombre': 'Zacoalco de Torres',
     'ley': 'Ley de Ingresos del Municipio de Zacoalco de Torres, Jalisco, para el ejercicio fiscal 2026',
     'url': _li('Zacoalco%20de%20Torres'), 'sha256': 'cf7efe9e1f7a82132532363343380297373758a13e8d58e78159a75c1b6abdaf',
     'art_tarifa': 'art. 21, fr. I',
     'tramos': [[0.01, 0.00, 0.000220], [207000.01, 45.54, 0.000242], [360700.01, 82.74, 0.000266],
                [552000.01, 133.62, 0.000290], [814000.01, 209.60, 0.000315], [1237000.01, 342.85, 0.000339],
                [1995000.01, 599.81, 0.000363], [3674000.01, 1209.29, 0.000387], [9450000.01, 3444.60, 0.000411],
                [52000000.01, 20932.65, 0.000436]],
     'baldio': {'tipo': 'igual', 'art': 'art. 21 (su fr. II está derogada)'},
     'pronto': [{'id': 'feb', 'et': 'Pagas el año completo en enero o febrero', 'f': 0.85, 'art': 'art. 23, fr. I'},
                {'id': 'mar', 'et': 'Pagas el año completo en marzo', 'f': 0.90, 'art': 'art. 23, fr. II'},
                {'id': 'abr', 'et': 'Pagas el año completo en abril', 'f': 0.95, 'art': 'art. 23, fr. III'}],
     'pronto_nota': 'Con tarjeta de crédito a meses el descuento es de 10 % antes del 1 de marzo y de 5 % antes del 1 de abril (art. 23, fr. IV).',
     'beneficios': [
         {'id': 'jub', 'et': 'Pensionado, jubilado, con discapacidad, en viudez o con 60 años o más (tu casa)', 'f': 0.50, 'tope': 1000000, 'art': 'art. 24'},
         {'id': 'ac', 'et': 'Institución de asistencia o asociación civil, con dictamen', 'f': 0.50, 'tope': 1000000, 'art': 'art. 22, fr. I'},
         {'id': 'rel', 'et': 'Asociación religiosa', 'f': 0.50, 'art': 'art. 22, fr. II'},
         {'id': 'pat', 'et': 'Inmueble del patrimonio cultural, bien conservado', 'f': 0.40, 'art': 'art. 22, fr. III'}],
     'suma_art': 'art. 24',
     'recargo': {'pct': 1.0, 'art': 'art. 32'},
     'multa': {'min': 10, 'max': 30, 'art': 'art. 31'},
     'notif': {'pct': 5, 'min_uma': 1, 'max_uma': 30, 'req': True, 'art': 'art. 34, fr. I, a'},
     'ejec': {'pct': 5, 'max_uma': 45, 'emb': True, 'art': 'art. 34, fr. II, a'}},
]

# Leyes que leímos y no integramos, con su porqué: la página lo dice en la ficha del municipio.
ESPERA = {
    'JAL-002': {'nombre': 'Acatlán de Juárez', 'url': _li('Acatl%C3%A1n%20de%20Ju%C3%A1rez'),
                'sha256': '78ac7763e957e8e33f85401a41b94335c6421595e88795632fa7ee18bcf179c8',
                'motivo': 'su art. 25 pone las tasas como «20%», «25%» y «30%» bajo el título «Tasa bimestral al millar», y así no se sabe cuánto es.'},
    'JAL-024': {'nombre': 'Cocula', 'url': CONGRESO + 'Ley%20de%20Ingresos%20del%20Municipio%20de%20Cocula,%20Jalisco%20para%20el%20ejercicio%20fiscal%202025-300126.pdf',
                'sha256': 'e62bfb50bfcaf4c026ed25bb5ca6fbbc2ed12888fbec8ad719e635ce3a5451b1',
                'motivo': 'su art. 18 cobra «sobre el valor determinado, el 25%» a las casas, 35 % a los baldíos y 24.6 % a los rústicos, sin decir que es al millar: leído así sería la cuarta parte del valor cada bimestre, y no se sabe cuánto es. (Ojo: el Congreso la guarda con el nombre «2025», pero es la ley de 2026: así lo dice su decreto 30015/LXIV/25.)'},
    'JAL-030': {'nombre': 'Chapala', 'url': _li('Chapala'),
                'sha256': 'fef31659e5b631cfbc1c63cda3666036d1e0b6a3e96ec94bdcad34857118a031',
                'motivo': 'su art. 42 pone las tasas como «0.20%», «0.25%» y «0.30%» bajo el título «Tasa bimestral al millar», y así no se sabe cuánto es.'},
    'JAL-066': {'nombre': 'Poncitlán', 'url': _li('Poncitl%C3%A1n'),
                'sha256': '2058a203cb1f47f227a7bbc5d621ec0c998c65996017509cbf5b427622dd6f13',
                'motivo': 'su tarifa es clara, pero su art. 31, fr. II pone a los gastos de ejecución un mínimo de dos UMA y un máximo de una UMA, y así no se sabe cuánto cobra.'},
    'JAL-083': {'nombre': 'Tala', 'url': _li('Tala'),
                'sha256': 'a69572767eaa6f604ea404be3e4115418ca1808e35c3f66846d2056766a7693e',
                'motivo': 'su art. 32 dice que las tasas son «bimestrales y al millar», pero las escribe como «0.2%», «0.23%» y «0.35%», y así no se sabe cuánto es.'},
    'JAL-082': {'nombre': 'Sayula', 'url': _li('Sayula'),
                'sha256': 'ac82f5b4be7e4818c7e8aa50ca5c78bd23949e82a6208cb3f60b4bca73157070',
                'motivo': 'su tabla general es clara, pero su art. 33 cobra a los baldíos «una tasa de 0.33» sin decir si es al millar ni sobre qué valores, y así no se sabe cuánto pagan.'},
    'JAL-100': {'nombre': 'Tomatlán', 'url': _li('Tomatl%C3%A1n'),
                'sha256': '7bcf36b70581f7ab29ae1ee19272622e48dd86fd3052e07afd48a8c7f1ed8af1',
                'motivo': 'su art. 18 escribe las tasas como «0.20% al millar», «0.14% al millar» y «0.30% al millar», y así no se sabe cuánto es.'},
    'JAL-108': {'nombre': 'Tuxpan', 'url': _li('Tuxpan'),
                'sha256': '764138a07d47ecae571651ac371a5e3aef732b2d00d83df4b94e35a86d2ebb13',
                'motivo': 'su art. 33 dice «al millar el: 0.00021», «0.00017» y «0.00031»: leído así sería un impuesto casi nulo, y no se sabe cuánto es.'},
}

# Las Tablas de Valores Unitarios de cada municipio (lo que fija el catastro para armar el valor fiscal).
# Cada valor es oficial y lleva su documento; armar el valor fiscal con ellos es derivado. Valores en pesos por m²,
# por calidad: [moderno, semimoderno, antiguo] × [bueno, regular, malo].
_ZAP_TV = 'https://s3.zapopan.gob.mx/geomatica/tablasvalor/2026/'
# El Periódico Oficial «El Estado de Jalisco» publica cada decreto de tablas; la mayoría son copias escaneadas: una celda
# que no se lee sin duda en la copia publicada va como None («ilegible»), nunca adivinada.
_POE = 'https://apiperiodico.jalisco.gob.mx/api/newspaper/getAsset?q='
TABLAS = {
    'zapopan': {
        'tx': 'Tablas de Valores Unitarios de Suelo y Construcción de Zapopan para 2026 (Decreto 29987/LXIV/25 del Congreso de Jalisco, Periódico Oficial «El Estado de Jalisco», 18-12-2025), copia de la Dirección de Catastro: «1. Valores de construcción»',
        'url': _ZAP_TV + '1.%20Valores%20de%20construcci%C3%B3n.pdf',
        'sha256': '476f0ba7f1dcf4f5db8a0997ab317f8c9b9c4c67adeef2a5e7e5a57d315070f4',
        'edades': [['mod', 'Moderna: de 0 a 10 años', 10], ['semi', 'Semimoderna: de 10 a 30 años', 30], ['ant', 'Antigua: de más de 30 años', None]],
        'estados': ['Bueno', 'Regular', 'Malo'],
        'usos': {
            'hab': {'et': 'Habitacional, comercial o de servicios', 'cal': [
                ['Lujo', [[17450, 16050, 11650], [15700, 12450, 9050], [10500, 6300, 4500]]],
                ['Superior', [[12700, 11600, 8500], [11350, 9050, 6600], [7450, 4450, 3250]]],
                ['Medio', [[8800, 7700, 5600], [7600, 5950, 4300], [4750, 2500, 1850]]],
                ['Económico', [[6500, 5700, 4200], [5600, 4200, 3000], [2950, 1500, 1200]]],
                ['Austero (autoconstrucción sin acabados)', [[5100, 4500, 3200], [4300, 3200, 2300], [2250, 1100, 890]]]]},
            'ind': {'et': 'Industrial', 'cal': [
                ['Especial', [[6100, 5500, 4100], [4600, 3000, 2100], [2350, 1250, 900]]],
                ['Superior', [[5500, 5000, 3600], [4100, 2800, 1900], [2100, 1010, 810]]],
                ['Medio', [[4600, 4300, 3100], [3500, 2200, 1650], [1750, 850, 680]]],
                ['Económico', [[4000, 3600, 2650], [3000, 2000, 1300], [1550, 660, 520]]]]}},
        'niveles': {'pct': 10, 'art': 'Nota 3: más de 4 niveles desde su desplante, +10 % por estructura'},
        'suelo': {'tx': 'Valor Catastral Zapopan 2026 (planos con el valor de cada calle; 828 MB)',
                  'url': _ZAP_TV + 'Valor%20Catastral%20Zapopan%202026.pdf',
                  'nota': 'En Zapopan el suelo se valúa por calle: el valor de tu calle viene en los planos de la tabla. Aún no los integramos (el archivo pesa 828 MB y son planos): búscalo ahí o pídelo en Catastro.'},
        'demeritos': {'tx': '9. Tabla de deméritos e incrementos', 'url': _ZAP_TV + '9.%20Tabla%20de%20dem%C3%A9ritos%20e%20incrementos.pdf',
                      'sha256': '4934cffc962cd971f851807908b0763a9d197f91be0891a977b36f535a360fea',
                      'nota': 'El valor del terreno baja por mucha profundidad, poco frente (2 a 6 m), lote interior (50 %) o pendiente, y sube en esquina (10 % habitacional, 15 % mixto o industrial, 20 % comercial); los factores se multiplican y nunca bajan más de 50 % ni suben más de 35 %. El simulador no los aplica: si te tocan, usa tu propio factor.'}},    'guadalajara': {
        'tx': 'Decreto 29909/LXIV/25, Tablas de Valores Unitarios de Suelo y Construcción de Guadalajara para 2026, Periódico Oficial «El Estado de Jalisco», 13-12-2025, sección XIII, pág. 6 del archivo («Valores de construcción 2026»)',
        'url': _POE + 'newspaper/24344/newspaper251215101716.pdf',
        'sha256': '3d4e244e3f71700005edb0500162177fdeff90cfb2b683e2bcb04abde58ce142',
        'escaneo': True,
        'edades': [['m1', 'Moderno 1: de 0 a 5 años', 5], ['m2', 'Moderno 2: de 6 a 10 años', 10], ['s1', 'Semimoderno 1: de 11 a 20 años', 20],
                   ['s2', 'Semimoderno 2: de 21 a 30 años', 30], ['a1', 'Antiguo 1: de 31 a 40 años', 40], ['a2', 'Antiguo 2: de más de 40 años', None]],
        'estados': ['Bueno', 'Regular', 'Malo'],
        'usos': {
            'hab': {'et': 'Habitacional, comercial o de servicios', 'cal': [
                ['Lujo', [[19700, 17340, 11170], [18700, 16590, 10560], [16960, 14230, 8640], [15070, 11950, None], [12770, 8990, 5200], [9640, 5740, 3730]]],
                ['Superior', [[14100, 12390, 7970], [13300, 11960, None], [12100, 10200, 6520], [10790, None, None], [9120, 6550, 4720], [6890, 5560, 4010]]],
                ['Medio', [[9900, 8280, 5330], [9400, 7940, 5110], [8500, 7100, 4650], [7000, 5910, 4090], [5760, 4530, 3270], [4400, 3550, None]]],
                ['Económico', [[7340, 6100, 3930], [7000, 5790, 3740], [6300, 5300, 3430], [4860, 4400, 3040], [3600, 3300, 2130], [2400, 1930, 1410]]]]}},
        'niveles': {'pct': 10, 'art': 'Nota 2: más de 4 niveles (con sótano), +10 %; con 10 niveles o más la nota sube a +15 %'},
        'suelo': {'tx': 'el mismo decreto, «Índice de valores por colonias, lotes tipo y código de polígono» (págs. 29 a 38 del archivo)',
                  'url': _POE + 'newspaper/24344/newspaper251215101716.pdf',
                  'nota': 'En Guadalajara el suelo se valúa por colonia y polígono: el valor de la tuya viene en el índice del decreto. Aún no lo integramos (es una copia escaneada): búscalo ahí.'}},
    'tlajomulco': {
        'tx': 'Decreto 29968/LXIV/25, Tablas de Valores Unitarios de Suelo y Construcción de Tlajomulco de Zúñiga para 2026, Periódico Oficial «El Estado de Jalisco», 15-12-2025, pág. 6 del archivo («Valores de construcción»)',
        'url': _POE + 'newspaper/24405/newspaper251217072240.pdf',
        'sha256': 'd74b16dff00a56508c75ff088d2e93a1ee84d31c935cbaa01de21d99f4a0f8f1',
        'escaneo': True,
        'edades': [['m1', 'Moderno 1: de 0 a 5 años', 5], ['m2', 'Moderno 2: de 6 a 10 años', 10], ['s1', 'Semimoderno 1: de 11 a 20 años', 20],
                   ['s2', 'Semimoderno 2: de 21 a 30 años', 30], ['a1', 'Antiguo 1: de 31 a 40 años', 40], ['a2', 'Antiguo 2: de 41 o más años', None]],
        'estados': ['Bueno', 'Regular', 'Malo'],
        'usos': {
            'hab': {'et': 'Habitacional, comercial o de servicios', 'cal': [
                ['Lujo', [[17460, 15800, 11670], [16860, 15250, 11270], [15350, 11600, 8750], [14500, 11000, 8060], [11250, 6700, 5000], [11000, 6000, 4300]]],
                ['Superior', [[13150, 11600, 8950], [12750, 11200, 8550], [11200, 8700, 6650], [10300, 7850, 5930], [8850, 5150, 3800], [8000, 4550, 3500]]],
                ['Medio', [[9500, 8350, 6150], [9100, 7950, 5750], [8000, 6150, 4400], [7500, 5770, 4250], [5600, 3000, 2100], [5550, 2700, 1900]]],
                ['Económico', [[6850, 5850, 4450], [6650, 5650, 4250], [5850, 4350, 3250], [5400, 3980, 2950], [3600, 1740, 1260], [3490, 1530, 1090]]]]},
            'ind': {'et': 'Industrial', 'cal': [
                ['Especial', [[6800, 6200, 4500], [6480, 5870, 4200], [5100, 3400, 2200], [4800, 3100, 2100], [2900, 1000, 700], [2550, 920, 610]]],
                ['Superior', [[6100, 5500, 4050], [5790, 5240, 3750], [4500, 3000, 2000], [4200, 2800, 1850], [2550, 900, 600], [2280, 810, 540]]],
                ['Medio', [[5200, 4740, 3400], [4900, 4450, 3100], [3900, 2500, 1700], [3600, 2400, 1600], [2150, 750, 500], [1920, 700, 450]]],
                ['Económico', [[4300, 4000, 2800], [4100, 3800, 2700], [3300, 2200, 1450], [3100, 2050, 1350], [1750, 660, 450], [1650, 600, 400]]]]}},
        'niveles': None,
        'suelo': {'tx': 'el mismo decreto, índice de fraccionamientos y planos de valores (desde la pág. 18 del archivo)',
                  'url': _POE + 'newspaper/24405/newspaper251217072240.pdf',
                  'nota': 'En Tlajomulco el suelo se valúa por fraccionamiento y zona: el valor del tuyo viene en el índice y los planos del decreto. Aún no los integramos: búscalo ahí.'}},
    'vallarta': {
        'tx': 'Decreto 29936/LXIV/25, Tablas de Valores Unitarios de Suelo y Construcción de Puerto Vallarta para 2026, Periódico Oficial «El Estado de Jalisco», 18-12-2025, pág. 6 del archivo («Valores de construcción»)',
        'url': _POE + 'newspaper/24480/newspaper251222040914.pdf',
        'sha256': '26cb5b51e61b6024410d036f08c9119af109ff34d3be61bc62e69b87bb15eb0d',
        'escaneo': True,
        'edades': [['m1', 'Moderno 1: de 0 a 5 años', 5], ['m2', 'Moderno 2: de 6 a 10 años', 10], ['s1', 'Semimoderno 1: de 11 a 20 años', 20],
                   ['s2', 'Semimoderno 2: de 21 a 30 años', 30], ['a1', 'Antiguo 1: de 31 a 40 años', 40], ['a2', 'Antiguo 2: de 41 o más años', None]],
        'estados': ['Bueno', 'Regular', 'Malo'],
        'usos': {
            'hab': {'et': 'Habitacional, comercial o de servicios', 'cal': [
                ['Lujo', [[17990, 16140, 14410], [16860, 15590, 13920], [15580, 12430, 11050], [15050, 12000, 10640], [8500, 7060, 6230], [8210, 7010, 6020]]],
                ['Superior', [[13580, 12480, 10100], [13110, 12050, 9750], [10400, 9910, 7770], [10040, 9570, 7500], [5420, 4930, 4430], [5230, 4760, 4280]]],
                ['Medio', [[8640, 7800, 6250], [8340, 7530, 6040], [6660, 5950, 4830], [6430, 5740, 4660], [3940, 3450, 2960], [3810, 3330, 2860]]],
                ['Económico', [[4960, 4260, 3820], [4790, 4110, 3690], [4260, 3820, 3400], [4110, 3690, 3290], [2460, 2090, 1970], [2380, 2020, 1900]]]]}},
        'niveles': {'pct': 10, 'art': 'Nota 5: más de 4 niveles (con sótano), +10 %; con más de 10 niveles la nota sube a +15 %'},
        'suelo': {'tx': 'el mismo decreto, valores unitarios por sectores y planos (desde la pág. 18 del archivo)',
                  'url': _POE + 'newspaper/24480/newspaper251222040914.pdf',
                  'nota': 'En Puerto Vallarta el suelo se valúa por sector y zona: el valor del tuyo viene en los planos del decreto. Aún no los integramos: búscalo ahí.'}},
    'lagos': {
        'tx': 'Decreto 29925/LXIV/25, Tablas de Valores Unitarios de Suelo y Construcción de Lagos de Moreno para 2026, Periódico Oficial «El Estado de Jalisco», 13-12-2025, pág. 7 del archivo («Valores de construcción»)',
        'url': _POE + 'newspaper/24357/newspaper251215103319.pdf',
        'sha256': '0eda2dc5528611262d4333ef97961c2202f25714c0a10c24965d6b86bae6e826',
        'escaneo': True,
        'edades': [["m1", "Moderno 1: de 0 a 5 años", 5], ["m2", "Moderno 2: de 6 a 10 años", 10], ["s1", "Semimoderno 1: de 11 a 20 años", 20], ["s2", "Semimoderno 2: de 21 a 30 años", 30], ["a1", "Antiguo 1: de 31 a 40 años", 40], ["a2", "Antiguo 2: de 41 o más años", None]],
        'estados': ['Bueno', 'Regular', 'Malo'],
        'usos': {
            'hab': {'et': 'Habitacional, comercial o de servicios', 'cal': [
                ["Lujo", [[13304, 12002, 8726], [12260, 11039, 8027], [11718, 9272, 6741], [10117, 7258, 5273], [8789, 5261, 3633], [7821, 4171, 2709]]],
                ["Superior", [[9272, 8600, 6195], [8552, 7865, 5716], [8379, 6615, 4830], [7204, 5167, 3758], [6269, 3791, 2730], [5629, 3009, 2036]]],
                ["Medio", [[6542, 5733, 4148], [6052, 5117, 3671], [5733, 3917, 3203], [4923, 3060, 2495], [4001, 2111, 1554], [3544, 1697, 1199]]],
                ["Económico", [[4830, 4232, 3066], [4480, 3839, 2786], [4127, 3056, 2195], [3488, 2432, 1746], [2489, 1092, 798], [2122, 824, 656]]]]}},
        'niveles': {'pct': 10, 'art': 'Nota 5: más de 4 niveles (con sótano), +10 %; con más de 10 niveles la nota sube a +15 %'},
        'suelo': {'tx': 'el mismo decreto, valores de suelo por zona y planos', 'url': _POE + 'newspaper/24357/newspaper251215103319.pdf', 'nota': 'En Lagos de Moreno el suelo se valúa por zona: el valor de la tuya viene en el decreto. Aún no lo integramos: búscalo ahí.'}},
    'tepatitlan': {
        'tx': 'Decreto 29964/LXIV/25, Tablas de Valores Unitarios de Suelo y Construcción de Tepatitlán de Morelos para 2026, Periódico Oficial «El Estado de Jalisco», 15-12-2025, pág. 9 del archivo («Valores de construcción 2026»)',
        'url': _POE + 'newspaper/24397/newspaper251217065431.pdf',
        'sha256': '6199d43095073e9985ef9577fcc9bf0159d16a377e2db1915ee4500e3a0d08bd',
        'escaneo': True,
        'edades': [["m1", "Moderno 1: de 0 a 5 años", 5], ["m2", "Moderno 2: de 6 a 10 años", 10], ["s1", "Semimoderno 1: de 11 a 20 años", 20], ["s2", "Semimoderno 2: de 21 a 30 años", 30], ["a1", "Antiguo 1: de 31 a 40 años", 40], ["a2", "Antiguo 2: de 41 o más años", None]],
        'estados': ['Bueno', 'Regular', 'Malo'],
        'usos': {
            'hab': {'et': 'Habitacional, comercial o de servicios', 'cal': [
                ["Lujo", [[13840, 12520, 9170], [13360, 12090, 8860], [12240, 9670, 7050], [11080, 7930, 5780], [8100, 5300, 3840], [7930, 4400, 3000]]],
                ["Superior", [[10550, 9440, 6970], [10190, 9110, 6720], [9200, 7450, 5320], [8330, 6110, 4360], [5610, 3990, 2960], [5500, 3310, 2310]]],
                ["Medio", [[7660, 6530, 4880], [7400, 6100, 4540], [6700, 4990, 3620], [6060, 4090, 2960], [4030, 2490, 1810], [3740, 2100, 1470]]],
                ["Económico", [[5820, 5050, 3670], [5670, 4810, 3480], [4960, 3660, 2640], [4420, 3080, 2220], [2940, 1320, 960], [2630, 1050, 830]]],
                ["Austero", [[4520, 3840, 2710], [4290, 3650, 2570], [3750, 2460, 1850], [3380, 2220, 1670], [1850, 1020, 750], [1570, 870, 640]]]]}},
        'niveles': {'pct': 10, 'art': 'Nota 5: más de 4 niveles (con sótano), +10 %; con más de 10 niveles la nota sube a +15 %'},
        'suelo': {'tx': 'el mismo decreto, valores de suelo por zona y planos', 'url': _POE + 'newspaper/24397/newspaper251217065431.pdf', 'nota': 'En Tepatitlán de Morelos el suelo se valúa por zona: el valor de la tuya viene en el decreto. Aún no lo integramos: búscalo ahí.'}},
    'ocotlan': {
        'tx': 'Decreto 29932/LXIV/25, Tablas de Valores Unitarios de Suelo y Construcción de Ocotlán para 2026, Periódico Oficial «El Estado de Jalisco», 15-12-2025, pág. 6 del archivo («Valores de construcción»)',
        'url': _POE + 'newspaper/24418/newspaper251217075651.pdf',
        'sha256': 'a4f4c99818e4308f3a32163efef53e3b0f1451fddfa6c5d83aaaa30f34fbc91a',
        'escaneo': True,
        'edades': [["m1", "Moderno 1: de 0 a 5 años", 5], ["m2", "Moderno 2: de 6 a 10 años", 10], ["s1", "Semimoderno 1: de 11 a 20 años", 20], ["s2", "Semimoderno 2: de 21 a 30 años", 30], ["a1", "Antiguo 1: de 31 a 40 años", 40], ["a2", "Antiguo 2: de 41 o más años", None]],
        'estados': ['Bueno', 'Regular', 'Malo'],
        'usos': {
            'hab': {'et': 'Habitacional, comercial o de servicios', 'cal': [
                ["Lujo", [[14210, 13060, 9500], [13680, 12570, 9140], [12770, 10120, 7350], [11520, 8270, 6010], [9620, 5740, 4180], [9000, 4750, 3260]]],
                ["Superior", [[10590, 9740, 7080], [10230, 9400, 6830], [9510, 7540, 5480], [8610, 6180, 4490], [7170, 4280, 3110], [6730, 3550, 2430]]],
                ["Medio", [[7660, 6710, 4880], [7400, 6270, 4540], [6730, 5190, 3770], [6090, 4250, 3080], [4670, 2490, 1810], [4330, 2100, 1470]]],
                ["Económico", [[5970, 5180, 3770], [5820, 4930, 3570], [5080, 3760, 2730], [4530, 3160, 2300], [3050, 1350, 980], [2730, 1070, 850]]]]}},
        'niveles': {'pct': 10, 'art': 'Nota 5: más de 4 niveles (con sótano), +10 %; con más de 10 niveles la nota sube a +15 %'},
        'suelo': {'tx': 'el mismo decreto, valores de suelo por zona y planos', 'url': _POE + 'newspaper/24418/newspaper251217075651.pdf', 'nota': 'En Ocotlán el suelo se valúa por zona: el valor de la tuya viene en el decreto. Aún no lo integramos: búscalo ahí.'}},
    'sanjuan': {
        'tx': 'Decreto 29942/LXIV/25, Tablas de Valores Unitarios de Suelo y Construcción de San Juan de los Lagos para 2026, Periódico Oficial «El Estado de Jalisco», 15-12-2025, pág. 6 del archivo («Valores de construcción»)',
        'url': _POE + 'newspaper/24396/newspaper251217065242.pdf',
        'sha256': '2b8d8225dce182fb0c1d8ac1ca247ffb6fd14f75a9090b1760845638f7b80218',
        'escaneo': True,
        'edades': [["mod", "Moderno: hasta 10 años", 10], ["semi", "Semimoderno: de más de 10 y hasta 30 años", 30], ["ant", "Antiguo: de más de 30 años", None]],
        'estados': ['Bueno', 'Regular', 'Malo'],
        'usos': {
            'hab': {'et': 'Habitacional, comercial o de servicios', 'cal': [
                ["Lujo", [[13610, 12390, 9290], [11670, 9170, 6910], [8810, 5240, 3930]]],
                ["Superior", [[8570, 7900, 5760], [7750, 6150, 4460], [5800, 3470, 2500]]],
                ["Medio", [[5610, 4900, 3670], [4900, 3800, 2760], [3430, 1840, 1350]]],
                ["Económico", [[4160, 3670, 2690], [3560, 2640, 1920], [2140, 940, 680]]],
                ["Austero", [[3430, 2940, 2210], [2940, 2170, 1590], [1780, 800, 560]]]]},
            'ind': {'et': 'Industrial', 'cal': [
                ["Especial", [[4400, 4010, 2940], [3320, 2180, 1460], [1870, 660, 460]]],
                ["Superior", [[3920, 3550, 2630], [2960, 1960, 1310], [1690, 590, 400]]],
                ["Medio", [[3320, 3040, 2230], [2500, 1660, 1100], [1420, 500, 340]]],
                ["Económico", [[2850, 2600, 1900], [2150, 1420, 950], [1210, 440, 300]]]]}},
        'niveles': None,
        'suelo': {'tx': 'el mismo decreto, valores de suelo por zona y planos', 'url': _POE + 'newspaper/24396/newspaper251217065242.pdf', 'nota': 'En San Juan de los Lagos el suelo se valúa por zona: el valor de la tuya viene en los planos del decreto. Aún no lo integramos: búscalo ahí.'}},
    'jocotepec': {
        'tx': 'Decreto 29919/LXIV/25, Tablas de Valores Unitarios de Suelo y Construcción de Jocotepec para 2026, Periódico Oficial «El Estado de Jalisco», 13-12-2025, pág. 6 del archivo («Valores de construcción»)',
        'url': _POE + 'newspaper/24352/newspaper251215102655.pdf',
        'sha256': '9cb7cdaa531abd358843a382f6321434dd66c8b29f3098eb06e292251e63194c',
        'escaneo': True,
        'edades': [["mod", "Moderno: hasta 10 años", 10], ["semi", "Semimoderno: de más de 10 y hasta 30 años", 30], ["ant", "Antiguo: de más de 30 años", None]],
        'estados': ['Bueno', 'Regular', 'Malo'],
        'usos': {
            'hab': {'et': 'Habitacional, comercial o de servicios', 'cal': [
                ["Lujo", [[13120, 12060, 8770], [11780, 9340, 6790], [8880, 5300, 3850]]],
                ["Superior", [[9780, 8990, 6530], [8780, 6960, 5060], [6620, 3950, 2870]]],
                ["Medio", [[7070, 6190, 4500], [6210, 4790, 3480], [4310, 2300, 1670]]],
                ["Económico", [[5510, 4790, 3480], [4690, 3470, 2520], [2820, None, 910]]]]}},
        'niveles': None,
        'suelo': {'tx': 'el mismo decreto, valores de suelo por zona y planos', 'url': _POE + 'newspaper/24352/newspaper251215102655.pdf', 'nota': 'En Jocotepec el suelo se valúa por zona: el valor de la tuya viene en los planos del decreto. Aún no lo integramos: búscalo ahí.'}},
    'magdalena': {
        'tx': 'Decreto 29926/LXIV/25, Tablas de Valores Unitarios de Suelo y Construcción de Magdalena para 2026, Periódico Oficial «El Estado de Jalisco», 13-12-2025, pág. 6 del archivo («Valores de construcción»)',
        'url': _POE + 'newspaper/24358/newspaper251215103417.pdf',
        'sha256': '5dd311f1b32052df267a53fd448add9eb9332350bba6cb76643a5dda2c862eb2',
        'escaneo': True,
        'edades': [["m1", "Moderno 1: de 0 a 5 años", 5], ["m2", "Moderno 2: de 6 a 10 años", 10], ["s1", "Semimoderno 1: de 11 a 20 años", 20], ["s2", "Semimoderno 2: de 21 a 30 años", 30], ["a1", "Antiguo 1: de 31 a 40 años", 40], ["a2", "Antiguo 2: de 41 o más años", None]],
        'estados': ['Bueno', 'Regular', 'Malo'],
        'usos': {
            'hab': {'et': 'Habitacional, comercial o de servicios', 'cal': [
                ["Lujo", [[11160, 10250, 7460], [10790, 9920, 7210], [10040, 8220, 5780], [9090, 6730, 4750], [6760, 4500, 2770], [6320, 3750, 2160]]],
                ["Superior", [[7990, 7340, 5360], [7730, 7100, 5160], [7180, 5790, 4140], [6510, 4710, 3390], [5400, 3260, 2350], [5080, 2720, 1840]]],
                ["Medio", [[5610, 4730, 3570], [5410, 4420, 3320], [4940, 3790, 2770], [4450, 3110, 2260], [3410, 1830, 1330], [3170, 1530, 1070]]],
                ["Económico", [[4150, 3600, 2640], [4060, 3430, 2500], [3550, 2610, 1910], [3170, 2210, 1610], [2140, 950, 670], [1900, 750, 590]]]]}},
        'niveles': {'pct': 10, 'art': 'Nota 5: más de 4 niveles (con sótano), +10 %; con más de 10 niveles la nota sube a +15 %'},
        'suelo': {'tx': 'el mismo decreto, valores de suelo por zona y planos', 'url': _POE + 'newspaper/24358/newspaper251215103417.pdf', 'nota': 'En Magdalena el suelo se valúa por zona: el valor de la tuya viene en el decreto. Aún no lo integramos: búscalo ahí.'}},
    'tlaquepaque': {
        'tx': 'Decreto 29949/LXIV/25, Tablas de Valores Unitarios de Suelo y Construcción de San Pedro Tlaquepaque para 2026, Periódico Oficial «El Estado de Jalisco», 15-12-2025, pág. 9 del archivo («Valores unitarios de la construcción año 2026»)',
        'url': _POE + 'newspaper/24379/newspaper251217061214.pdf',
        'sha256': '88bbc7203d4b34e732285c722fb0d54d3f216d9aa3f79a5f2817bcfbae7e196e',
        'escaneo': True,
        'edades': [['mod', 'Moderno: hasta 10 años', 10], ['semi', 'Semimoderno: de 11 a 30 años', 30], ['ant', 'Antiguo: de más de 30 años', None]],
        'estados': ['Bueno', 'Regular', 'Malo'],
        'usos': {
            'hab': {'et': 'Habitacional, comercial o de servicios', 'cal': [
                ['Lujo', [[16280, 14950, 10890], [13410, 9820, 7000], [8060, None, 2480]]],
                ['Superior', [[11620, 10680, 7760], [10010, 7400, None], [6040, 2480, 1810]]],
                ['Medio', [[8370, 7310, 5430], [7300, 5630, 4080], [4620, 1800, 1340]]],
                ['Económico', [[6290, 5460, 3930], [5260, 3890, 2830], [3200, 1340, 1030]]],
                ['Austero', [[4990, 4220, 3180], [4080, 3030, 2200], [2490, 1100, 800]]]]}},
        'niveles': {'pct': 10, 'art': 'Nota 3: más de 4 niveles, +10 % por estructura'},
        'suelo': {'tx': 'el mismo decreto, planos de valores de suelo por zona (págs. 18 a 65 del archivo)',
                  'url': _POE + 'newspaper/24379/newspaper251217061214.pdf',
                  'nota': 'En Tlaquepaque el suelo se valúa por zona: el valor de la tuya viene en los planos del decreto. Aún no los integramos (son planos escaneados): búscalo ahí.'}},
}


# Dónde se publicó cada decreto de Tablas de Valores Unitarios de Suelo y Construcción (oficial). Clave INEGI →
# [decreto del Congreso, fecha del Periódico Oficial, archivo del ejemplar (se abre con _POE + archivo)]. Se buscaron en su consulta pública,
# ejemplar por ejemplar, de septiembre de 2025 a noviembre de 2026; los municipios que faltan no aparecieron ahí.
POE_CONSULTA = 'https://periodicooficial.jalisco.gob.mx/'
DECRETOS_TV = {
    'JAL': {'anio': 2026, 'buscado': 'septiembre de 2025 a noviembre de 2026', 'lista': {
        '001': ['29871/LXIV/25', '2025-12-13', 'newspaper/24366/newspaper251216033135.pdf'],
        '002': ['29872/LXIV/25', '2025-12-13', 'newspaper/24337/newspaper251215100952.pdf'],
        '003': ['29873/LXIV/25', '2025-12-15', 'newspaper/24382/newspaper251217062246.pdf'],
        '005': ['29875/LXIV/25', '2025-12-13', 'newspaper/24338/newspaper251215101055.pdf'],
        '006': ['29876/LXIV/25', '2025-12-11', 'newspaper/24324/newspaper251212094544.pdf'],
        '007': ['29943/LXIV/25', '2025-12-15', 'newspaper/24383/newspaper251217062355.pdf'],
        '008': ['29877/LXIV/25', '2025-12-11', 'newspaper/24325/newspaper251212094731.pdf'],
        '009': ['29901/LXIV/25', '2025-12-11', 'newspaper/24316/newspaper251212092223.pdf'],
        '010': ['29878/LXIV/25', '2025-12-11', 'newspaper/24301/newspaper251212085349.pdf'],
        '011': ['29879/LXIV/25', '2025-12-11', 'newspaper/24302/newspaper251212085600.pdf'],
        '012': ['29880/LXIV/25', '2025-12-15', 'newspaper/24410/newspaper251217073231.pdf'],
        '013': ['29881/LXIV/25', '2025-12-11', 'newspaper/24300/newspaper251212080953.pdf'],
        '014': ['29882/LXIV/25', '2025-12-11', 'newspaper/24303/newspaper251212085855.pdf'],
        '015': ['29883/LXIV/25', '2025-12-11', 'newspaper/24304/newspaper251212090124.pdf'],
        '016': ['29884/LXIV/25', '2025-12-11', 'newspaper/24305/newspaper251212090416.pdf'],
        '017': ['29885/LXIV/25', '2025-12-13', 'newspaper/24339/newspaper251215101153.pdf'],
        '018': ['29922/LXIV/25', '2025-12-13', 'newspaper/24355/newspaper251215103022.pdf'],
        '019': ['29886/LXIV/25', '2025-12-11', 'newspaper/24306/newspaper251212090801.pdf'],
        '020': ['29887/LXIV/25', '2025-12-11', 'newspaper/24307/newspaper251212090933.pdf'],
        '021': ['29889/LXIV/25', '2025-12-11', 'newspaper/24308/newspaper251212091035.pdf'],
        '022': ['29893/LXIV/25', '2025-12-11', 'newspaper/24309/newspaper251212091128.pdf'],
        '023': ['29990/LXIV/25', '2025-12-18', 'newspaper/24477/newspaper251222040507.pdf'],
        '024': ['29894/LXIV/25', '2025-12-11', 'newspaper/24310/newspaper251212091320.pdf'],
        '025': ['29895/LXIV/25', '2025-12-11', 'newspaper/24311/newspaper251212091451.pdf'],
        '026': ['29896/LXIV/25', '2025-12-15', 'newspaper/24409/newspaper251217073133.pdf'],
        '028': ['29897/LXIV/25', '2025-12-13', 'newspaper/24341/newspaper251215101418.pdf'],
        '029': ['29898/LXIV/25', '2025-12-13', 'newspaper/24342/newspaper251215101528.pdf'],
        '030': ['29890/LXIV/25', '2025-12-11', 'newspaper/24312/newspaper251212091727.pdf'],
        '031': ['29891/LXIV/25', '2025-12-15', 'newspaper/24375/newspaper251217060428.pdf'],
        '032': ['29892/LXIV/25', '2025-12-11', 'newspaper/24313/newspaper251212091847.pdf'],
        '033': ['29899/LXIV/25', '2025-12-11', 'newspaper/24314/newspaper251212091953.pdf'],
        '034': ['29900/LXIV/25', '2025-12-11', 'newspaper/24315/newspaper251212092117.pdf'],
        '035': ['29905/LXIV/25', '2025-12-11', 'newspaper/24319/newspaper251212092633.pdf'],
        '036': ['29906/LXIV/25', '2025-12-11', 'newspaper/24320/newspaper251212092748.pdf'],
        '037': ['29902/LXIV/25', '2025-12-11', 'newspaper/24317/newspaper251212092335.pdf'],
        '038': ['29908/LXIV/25', '2025-12-15', 'newspaper/24387/newspaper251217063347.pdf'],
        '039': ['29909/LXIV/25', '2025-12-13', 'newspaper/24344/newspaper251215101716.pdf'],
        '040': ['29910/LXIV/25', '2025-12-13', 'newspaper/24345/newspaper251215101837.pdf'],
        '041': ['29911/LXIV/25', '2025-12-13', 'newspaper/24346/newspaper251215101940.pdf'],
        '042': ['29912/LXIV/25', '2025-12-11', 'newspaper/24322/newspaper251212092905.pdf'],
        '043': ['29923/LXIV/25', '2025-12-13', 'newspaper/24363/newspaper251215105326.pdf'],
        '044': ['29913/LXIV/25', '2025-12-13', 'newspaper/24365/newspaper251216031510.pdf'],
        '045': ['29914/LXIV/25', '2025-12-13', 'newspaper/24347/newspaper251215102059.pdf'],
        '046': ['29915/LXIV/25', '2025-12-13', 'newspaper/24348/newspaper251215102147.pdf'],
        '047': ['29916/LXIV/25', '2025-12-13', 'newspaper/24349/newspaper251215102310.pdf'],
        '048': ['29917/LXIV/25', '2025-12-13', 'newspaper/24350/newspaper251215102425.pdf'],
        '049': ['29918/LXIV/25', '2025-12-13', 'newspaper/24351/newspaper251215102520.pdf'],
        '050': ['29919/LXIV/25', '2025-12-13', 'newspaper/24352/newspaper251215102655.pdf'],
        '051': ['29920/LXIV/25', '2025-12-13', 'newspaper/24353/newspaper251215102833.pdf'],
        '052': ['29921/LXIV/25', '2025-12-13', 'newspaper/24354/newspaper251215102933.pdf'],
        '053': ['29925/LXIV/25', '2025-12-13', 'newspaper/24357/newspaper251215103319.pdf'],
        '054': ['29903/LXIV/25', '2025-12-11', 'newspaper/24318/newspaper251212092443.pdf'],
        '055': ['29926/LXIV/25', '2025-12-13', 'newspaper/24358/newspaper251215103417.pdf'],
        '056': ['29952/LXIV/25', '2025-12-15', 'newspaper/24411/newspaper251217073439.pdf'],
        '057': ['29924/LXIV/25', '2025-12-13', 'newspaper/24356/newspaper251215103131.pdf'],
        '058': ['29927/LXIV/25', '2025-12-13', 'newspaper/24359/newspaper251215103555.pdf'],
        '059': ['29928/LXIV/25', '2025-12-13', 'newspaper/24360/newspaper251215103633.pdf'],
        '060': ['29929/LXIV/25', '2025-12-13', 'newspaper/24361/newspaper251215103735.pdf'],
        '061': ['29930/LXIV/25', '2025-12-13', 'newspaper/24362/newspaper251215103830.pdf'],
        '062': ['29931/LXIV/25', '2025-12-18', 'newspaper/24479/newspaper251222040706.pdf'],
        '063': ['29932/LXIV/25', '2025-12-15', 'newspaper/24418/newspaper251217075651.pdf'],
        '064': ['29933/LXIV/25', '2025-12-15', 'newspaper/24417/newspaper251217074415.pdf'],
        '065': ['29934/LXIV/25', '2025-12-15', 'newspaper/24393/newspaper251217064532.pdf'],
        '066': ['29935/LXIV/25', '2025-12-15', 'newspaper/24415/newspaper251217074132.pdf'],
        '067': ['29936/LXIV/25', '2025-12-18', 'newspaper/24480/newspaper251222040914.pdf'],
        '068': ['29984/LXIV/25', '2025-12-18', 'newspaper/24470/newspaper251222035157.pdf'],
        '069': ['29937/LXIV/25', '2025-12-15', 'newspaper/24378/newspaper251217061113.pdf'],
        '070': ['29904/LXIV/25', '2025-12-13', 'newspaper/24343/newspaper251215101613.pdf'],
        '071': ['29938/LXIV/25', '2025-12-15', 'newspaper/24376/newspaper251217060911.pdf'],
        '072': ['29939/LXIV/25', '2025-12-15', 'newspaper/24416/newspaper251217074224.pdf'],
        '073': ['29942/LXIV/25', '2025-12-15', 'newspaper/24396/newspaper251217065242.pdf'],
        '074': ['29944/LXIV/25', '2025-12-15', 'newspaper/24386/newspaper251217063232.pdf'],
        '075': ['29945/LXIV/25', '2025-12-18', 'newspaper/24481/newspaper251222041012.pdf'],
        '076': ['29946/LXIV/25', '2025-12-15', 'newspaper/24392/newspaper251217064422.pdf'],
        '077': ['29947/LXIV/25', '2025-12-15', 'newspaper/24390/newspaper251217064154.pdf'],
        '078': ['29948/LXIV/25', '2025-12-15', 'newspaper/24404/newspaper251217071958.pdf'],
        '079': ['29907/LXIV/25', '2025-12-15', 'newspaper/24384/newspaper251217062810.pdf'],
        '080': ['29950/LXIV/25', '2025-12-15', 'newspaper/24413/newspaper251217073701.pdf'],
        '081': ['29951/LXIV/25', '2025-12-15', 'newspaper/24412/newspaper251217073600.pdf'],
        '082': ['29953/LXIV/25', '2025-12-15', 'newspaper/24401/newspaper251217070739.pdf'],
        '083': ['29954/LXIV/25', '2025-12-15', 'newspaper/24408/newspaper251217072537.pdf'],
        '084': ['29955/LXIV/25', '2025-12-15', 'newspaper/24403/newspaper251217071532.pdf'],
        '085': ['29956/LXIV/25', '2025-12-15', 'newspaper/24389/newspaper251217064056.pdf'],
        '086': ['29957/LXIV/25', '2025-12-15', 'newspaper/24407/newspaper251217072355.pdf'],
        '087': ['29958/LXIV/25', '2025-12-15', 'newspaper/24391/newspaper251217064245.pdf'],
        '088': ['29960/LXIV/25', '2025-12-15', 'newspaper/24377/newspaper251217061015.pdf'],
        '089': ['29959/LXIV/25', '2025-12-15', 'newspaper/24381/newspaper251217062030.pdf'],
        '090': ['29961/LXIV/25', '2025-12-15', 'newspaper/24398/newspaper251217065601.pdf'],
        '091': ['29962/LXIV/25', '2025-12-15', 'newspaper/24399/newspaper251217070318.pdf'],
        '092': ['29963/LXIV/25', '2025-12-15', 'newspaper/24400/newspaper251217070628.pdf'],
        '093': ['29964/LXIV/25', '2025-12-15', 'newspaper/24397/newspaper251217065431.pdf'],
        '094': ['29965/LXIV/25', '2025-12-15', 'newspaper/24385/newspaper251217063111.pdf'],
        '095': ['29966/LXIV/25', '2025-12-15', 'newspaper/24388/newspaper251217063507.pdf'],
        '096': ['29967/LXIV/25', '2025-12-15', 'newspaper/24395/newspaper251217064757.pdf'],
        '097': ['29968/LXIV/25', '2025-12-15', 'newspaper/24405/newspaper251217072240.pdf'],
        '098': ['29949/LXIV/25', '2025-12-15', 'newspaper/24379/newspaper251217061214.pdf'],
        '099': ['29969/LXIV/25', '2025-12-15', 'newspaper/24380/newspaper251217061940.pdf'],
        '100': ['29970/LXIV/25', '2025-12-15', 'newspaper/24402/newspaper251217070922.pdf'],
        '101': ['29971/LXIV/25', '2025-12-18', 'newspaper/24458/newspaper251222034000.pdf'],
        '102': ['29972/LXIV/25', '2025-12-18', 'newspaper/24459/newspaper251222034051.pdf'],
        '103': ['29973/LXIV/25', '2025-12-18', 'newspaper/24460/newspaper251222034205.pdf'],
        '104': ['29974/LXIV/25', '2025-12-18', 'newspaper/24461/newspaper251222034252.pdf'],
        '106': ['29975/LXIV/25', '2025-12-18', 'newspaper/24462/newspaper251222034339.pdf'],
        '108': ['29976/LXIV/25', '2025-12-18', 'newspaper/24463/newspaper251222034447.pdf'],
        '109': ['29977/LXIV/25', '2025-12-18', 'newspaper/24464/newspaper251222034536.pdf'],
        '110': ['29978/LXIV/25', '2025-12-18', 'newspaper/24465/newspaper251222034708.pdf'],
        '111': ['29979/LXIV/25', '2025-12-18', 'newspaper/24466/newspaper251222034749.pdf'],
        '112': ['29980/LXIV/25', '2025-12-18', 'newspaper/24467/newspaper251222034853.pdf'],
        '113': ['29940/LXIV/25', '2025-12-15', 'newspaper/24414/newspaper251217074030.pdf'],
        '114': ['29981/LXIV/25', '2025-12-18', 'newspaper/24468/newspaper251222035010.pdf'],
        '115': ['29982/LXIV/25', '2025-12-18', 'newspaper/24469/newspaper251222035048.pdf'],
        '116': ['29983/LXIV/25', '2025-12-15', 'newspaper/24394/newspaper251217064651.pdf'],
        '117': ['29888/LXIV/25', '2025-12-13', 'newspaper/24340/newspaper251215101310.pdf'],
        '118': ['29985/LXIV/25', '2025-12-18', 'newspaper/24471/newspaper251222035328.pdf'],
        '119': ['29986/LXIV/25', '2025-12-18', 'newspaper/24472/newspaper251222035446.pdf'],
        '120': ['29987/LXIV/25', '2025-12-18', 'newspaper/24474/newspaper251222035804.pdf'],
        '121': ['29988/LXIV/25', '2025-12-18', 'newspaper/24475/newspaper251222040249.pdf'],
        '123': ['29989/LXIV/25', '2025-12-18', 'newspaper/24476/newspaper251222040348.pdf'],
        '124': ['29991/LXIV/25', '2025-12-18', 'newspaper/24478/newspaper251222040558.pdf'],
        '125': ['29941/LXIV/25', '2025-12-15', 'newspaper/24374/newspaper251217060255.pdf'],
    }},
}


def valor_construccion(T, uso, ical, iedad, iest, niveles=False):
    """Gemela de valorConstruccion() de cc-predial.js: el valor unitario oficial y, si aplica, +% por niveles."""
    v = T['usos'][uso]['cal'][ical][1][iedad][iest]
    if v is None:
        return None
    return _r2(v * (1 + T['niveles']['pct'] / 100)) if niveles and T.get('niveles') else v


# El registro, estado por estado: dónde publica cada congreso las leyes de ingresos municipales y lo que
# consta en un documento oficial de los municipios sin ley. Solo entra lo cotejado; los demás estados quedan
# «por revisar», como falta de esta plataforma.
OAX_LGIM = {'tx': 'Ley General de Ingresos Municipales del Estado de Oaxaca para el Ejercicio Fiscal 2026',
            'url': 'https://www.finanzasoaxaca.gob.mx/pdf/asistencia/leyes_fiscales/VIGENTES/word/LEY%20GENERAL%20DE%20INGRESOS%20MUNICIPALES%202026.docx',
            'sha256': '4ca912a70b9e922292c1ca9748ce0f5f93d37db59572b449ffb1b1da1c31f962'}
OAX_VE = {'tx': 'Congreso del Estado de Oaxaca, versión estenográfica de la sesión extraordinaria del 31 de marzo de 2026',
          'url': 'https://congresooaxaca.gob.mx/docs66.congresooaxaca.gob.mx/version_estenografs/Version_Estenografica_Sesion_Extraordinaria_Primer_Periodo_Ordinario_Sesiones_Segundo_Annio_Ejercicio_LXVI_Legislatura_31_marzo_2026.pdf',
          'sha256': 'c2a1f28ace973de7b550a345d1902c3dd35fcda20eac3cf16df6c761242768eb'}
REGISTRO = {
    'JAL': {'donde': 'Biblioteca Virtual del Congreso del Estado de Jalisco',
            'url': 'https://congresoweb.congresojal.gob.mx/BibliotecaVirtual/busquedasleyes/Listado%272.cfm',
            'como': 'Una Ley de Ingresos por municipio, con su tabla del predial; el Congreso las guarda en PDF.',
            'ojo': 'El archivo de Cocula 2026 está guardado con el nombre «2025».'},
    'OAX': {'donde': 'Gaceta Parlamentaria del Congreso del Estado de Oaxaca y Periódico Oficial del Estado',
            'url': 'https://www.congresooaxaca.gob.mx/',
            'como': ('La %s es una sola para los 570 municipios, pero no trae tarifas: «Las tasas, cuotas y tarifas… serán '
                     'propuestas por los Ayuntamientos, en las Leyes de Ingresos que apruebe el Congreso» (art. 1). Cada '
                     'municipio necesita su propia ley; el Congreso las aprobó por tandas de diciembre de 2025 a marzo de 2026.') % OAX_LGIM['tx'],
            'ley': OAX_LGIM,
            'sin_ley': {
                'OAX-023': {'nombre': 'Cuilápam de Guerrero',
                            'motivo': 'El 31 de marzo de 2026 el Congreso del Estado votó (33 a 0) que era improcedente aprobar su Ley de Ingresos 2026. El presidente de la comisión explicó que la ley no contó con la mayoría calificada desde la sesión de cabildo.',
                            'doc': OAX_VE},
                'OAX-080': {'nombre': 'San Agustín Amatengo',
                            'motivo': 'El 31 de marzo de 2026 el Congreso del Estado votó (33 a 0) que era improcedente aprobar su Ley de Ingresos 2026.',
                            'doc': OAX_VE}}},
}

ENTIDADES = {'AGS': 'Aguascalientes', 'BC': 'Baja California', 'BCS': 'Baja California Sur', 'CAM': 'Campeche',
             'COAH': 'Coahuila', 'COL': 'Colima', 'CHIS': 'Chiapas', 'CHIH': 'Chihuahua', 'CDMX': 'Ciudad de México',
             'DGO': 'Durango', 'GTO': 'Guanajuato', 'GRO': 'Guerrero', 'HGO': 'Hidalgo', 'JAL': 'Jalisco',
             'MÉX': 'Estado de México', 'MICH': 'Michoacán', 'MOR': 'Morelos', 'NAY': 'Nayarit', 'NL': 'Nuevo León',
             'OAX': 'Oaxaca', 'PUE': 'Puebla', 'QRO': 'Querétaro', 'QROO': 'Quintana Roo', 'SLP': 'San Luis Potosí',
             'SIN': 'Sinaloa', 'SON': 'Sonora', 'TAB': 'Tabasco', 'TAM': 'Tamaulipas', 'TLAX': 'Tlaxcala',
             'VER': 'Veracruz', 'YUC': 'Yucatán', 'ZAC': 'Zacatecas'}

# El caso del mandamiento de ejecución que trajo el autor (Zapopan, 2021-2022),
# sin datos de la persona: valor fiscal, la cuota, la tasa y lo que resultó.
EJEMPLO = {'vf': 7613320.00, 'bim': 2337.62, 'anual': 14025.72, 'tres': 7012.86, 'multa50': 7012.86,
           'notif_uma2022': 577.32, 'uma2022': 96.22}


def esc(t):
    return html.escape(str(t))


def revisa():
    """Cada renglón completo y su tabla en orden; si no, se detiene."""
    for m in MUNICIPIOS:
        for k in ('id', 'ent', 'cve', 'nombre', 'ley', 'url', 'sha256', 'tramos', 'baldio', 'pronto', 'beneficios', 'recargo', 'notif', 'ejec'):
            if k not in m:
                raise SystemExit('cc_predial: a %s le falta %s' % (m.get('id'), k))
        if m['ent'] not in ENTIDADES or len(m['sha256']) != 64:
            raise SystemExit('cc_predial: %s trae mal su entidad o su huella' % m['id'])
        li = [t[0] for t in m['tramos']]
        if li != sorted(li) or any(not (0 < t[2] < 0.01) for t in m['tramos']):
            raise SystemExit('cc_predial: la tabla de %s no está en orden o trae una tasa rara' % m['id'])
        # La tarifa es continua: la cuota fija de cada tramo es (casi) lo que da el anterior en su límite.
        for a, b in zip(m['tramos'], m['tramos'][1:]):
            fin = a[1] + (b[0] - 0.01 - a[0]) * a[2]
            if abs(fin - b[1]) > max(2.0, b[1] * 0.02):
                raise SystemExit('cc_predial: en %s la cuota fija %s no sigue del tramo anterior (%.2f)' % (m['id'], b[1], fin))
        for b in m['beneficios']:
            if not (0 <= b['f'] < 1) or not b.get('art'):
                raise SystemExit('cc_predial: beneficio %s de %s mal' % (b['id'], m['id']))
        if m['baldio']['tipo'] not in ('sobretasa', 'millar', 'igual') or not m['baldio'].get('art'):
            raise SystemExit('cc_predial: el baldío de %s trae un tipo que la página no sabe cobrar' % m['id'])
        if m.get('tarifa') == 'millar' and (len(m['tramos']) != 1 or abs(m['tramos'][0][2] * 1000 - m['millar']) > 1e-9):
            raise SystemExit('cc_predial: la tasa al millar de %s no coincide con su tabla' % m['id'])
        for k in ('notif', 'ejec'):
            g = m[k]
            if not (g.get('pct') or g.get('uma') or g.get('pesos')) or not g.get('art'):
                raise SystemExit('cc_predial: %s de %s no dice cuánto se cobra' % (k, m['id']))
        if m.get('minimo') and not (m['minimo'].get('pesos', 0) > 0 and m['minimo'].get('art')):
            raise SystemExit('cc_predial: el mínimo de %s no dice cuánto ni su artículo' % m['id'])
        if m.get('multa') and not (0 < m['multa']['min'] <= m['multa']['max']):
            raise SystemExit('cc_predial: la multa de %s está al revés' % m['id'])
    ids = [m['id'] for m in MUNICIPIOS]
    claves = ['%s-%s' % (m['ent'], m['cve']) for m in MUNICIPIOS]
    if len(set(ids)) != len(ids) or len(set(claves)) != len(claves):
        raise SystemExit('cc_predial: un municipio está dos veces')
    for mid, T in TABLAS.items():
        if mid not in [m['id'] for m in MUNICIPIOS] or len(T['sha256']) != 64:
            raise SystemExit('cc_predial: la tabla de valores de %s no tiene municipio o huella' % mid)
        for u in T['usos'].values():
            for nom, eds in u['cal']:
                if len(eds) != len(T['edades']) or any(len(f) != 3 or [v for v in f if v is not None] != sorted([v for v in f if v is not None], reverse=True) for f in eds):
                    raise SystemExit('cc_predial: la tabla de %s, calidad %s, no va de bueno a malo' % (mid, nom))
                if any(v is None for f in eds for v in f) and not T.get('escaneo'):
                    raise SystemExit('cc_predial: la tabla de %s trae una celda vacía sin ser copia escaneada' % mid)
            primero = [eds[0][0] for nom, eds in u['cal']]
            if primero != sorted(primero, reverse=True):
                raise SystemExit('cc_predial: las calidades de %s no van de mayor a menor' % mid)
    for e, dv in DECRETOS_TV.items():
        for k, d in dv['lista'].items():
            if e not in ENTIDADES or not re.fullmatch(r'\d{3}', k) or not re.fullmatch(r'\d+/LXIV/\d\d', d[0]) \
                    or not re.fullmatch(r'20\d\d-\d\d-\d\d', d[1]) or not re.fullmatch(r'newspaper/\d+/[\w.]+\.pdf', d[2]):
                raise SystemExit('cc_predial: el decreto de tablas de valores %s-%s está incompleto' % (e, k))
    for mid, T in TABLAS.items():
        m = [x for x in MUNICIPIOS if x['id'] == mid][0]
        d = DECRETOS_TV.get(m['ent'], {}).get('lista', {}).get(m['cve'])
        if d and d[0] not in T['tx']:
            raise SystemExit('cc_predial: la tabla de valores de %s no cita su decreto %s' % (mid, d[0]))
    for e, r in REGISTRO.items():
        if e not in ENTIDADES or not (r['donde'] and r['url'].startswith('https://')):
            raise SystemExit('cc_predial: el registro de %s está incompleto' % e)
        for k, w in r.get('sin_ley', {}).items():
            if not k.startswith(e + '-') or len(w['doc']['sha256']) != 64 or not w['motivo']:
                raise SystemExit('cc_predial: %s está sin ley pero sin su documento' % k)
    for k, w in ESPERA.items():
        if k in claves or len(w['sha256']) != 64 or not w['motivo']:
            raise SystemExit('cc_predial: %s está en ESPERA y en MUNICIPIOS, o le falta su porqué' % k)


def _r2(v):
    """Como Math.round(v * 100) / 100 del navegador (los medios centavos van hacia arriba)."""
    return math.floor(v * 100 + 0.5) / 100


def bimestral(m, vf):
    t = [x for x in m['tramos'] if vf >= x[0]]
    li, cf, tasa = t[-1] if t else m['tramos'][0]
    return _r2((vf - li) * tasa + cf)


def base(m, vf, tipo):
    """Gemela de base() de cc-predial.js: construido, rústico o baldío, y el mínimo bimestral si la ley lo pone."""
    b = _base(m, vf, tipo)
    return max(b, m['minimo']['pesos']) if m.get('minimo') else b


def _base(m, vf, tipo):
    if tipo == 'rust' and m.get('rustico'):
        return _r2(vf * m['rustico']['millar'] / 1000 + m['rustico']['cf'])
    if tipo != 'baldio' or m['baldio']['tipo'] == 'igual':
        return bimestral(m, vf)
    b = m['baldio']
    if b['tipo'] == 'sobretasa':
        return _r2(bimestral(m, vf) * (1 + b['pct'] / 100))
    return _r2(vf * b['millar'] / 1000 + b['cf'])


def inverso(m, imp):
    """Gemela de inverso() de cc-predial.js: el valor fiscal que da un impuesto bimestral (predio construido)."""
    if m.get('minimo') and imp <= m['minimo']['pesos']:
        return None
    for li, cf, t in reversed(m['tramos']):
        if imp >= cf:
            v = _r2(li + (imp - cf) / t)
            return v if v >= li else None
    return None


def valor_fiscal(ts, vs, tc=0, vc=0, fc=1):
    """Gemela de valorFiscal(): terreno × suelo + construcción × valor × factor."""
    return _r2(ts * vs + tc * vc * (fc if fc > 0 else 1))


def datos(base):
    revisa()
    cc = cc_inmueble.datos(base)
    uma = base['calculadora_civica']['parametros']['uma']
    return {'anio': ANIO, 'inpc': cc['inpc'], 'inpc_ult': cc['inpc_ult'],
            'uma': uma['diaria'], 'uma_f': uma['fuente'], 'ent': ENTIDADES,
            'mun': MUNICIPIOS, 'espera': ESPERA, 'reg': REGISTRO, 'tablas': TABLAS, 'dtv': DECRETOS_TV, 'poe': _POE, 'lhm': {'tope': 250, 'tope_esp': 100}}


def construir(base, ref):
    D = datos(base)
    MES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    ult = '%s de %d' % (MES[D['inpc_ult'][1] - 1], D['inpc_ult'][0])
    nom = {m['id']: m['nombre'] for m in MUNICIPIOS}
    lt = sorted(nom[k] for k in TABLAS)
    con_tabla = esc(', '.join(lt[:-1]) + ' y ' + lt[-1])
    ents = ''.join('<option value="%s"%s>%s</option>' % (esc(k), ' selected' if k == 'JAL' else '', esc(v))
                   for k, v in sorted(ENTIDADES.items(), key=lambda x: x[1]))
    anios = ''.join('<option value="%d"%s>%d</option>' % (a, ' selected' if a == ANIO else '', a) for a in range(ANIO + 1, 2014, -1))
    bims = ''.join('<option value="%d">%d.º (%s y %s)</option>' % (b, b, MES[2 * b - 2], MES[2 * b - 1]) for b in range(1, 7))
    leyes = ''.join('<li><b>%s</b>: <a href="%s">%s</a> (huella SHA-256 <code>%s…</code>)</li>'
                    % (esc(m['nombre']), esc(m['url']), esc(m['ley']), m['sha256'][:12]) for m in MUNICIPIOS)
    lista = ', '.join(esc(m['nombre']) for m in MUNICIPIOS)
    espera = '; '.join('%s: <a href="%s">su ley</a> %s' % (esc(w['nombre']), esc(w['url']), esc(w['motivo'])) for w in ESPERA.values())
    nmun = {'JAL': 125, 'OAX': 570}
    reg_filas = ''.join('<tr><th scope="row">%s</th><td>%s</td><td>%d · %d</td><td><a href="%s">%s</a>. %s %s</td></tr>' % (
        esc(ENTIDADES[e]), format(nmun.get(e, 0), ','), sum(1 for m in MUNICIPIOS if m['ent'] == e),
        sum(1 for k in ESPERA if k.startswith(e + '-')), esc(r['url']), esc(r['donde']), esc(r['como']), esc(r.get('ojo', '')))
        for e, r in sorted(REGISTRO.items(), key=lambda x: ENTIDADES[x[0]]))
    resto = len(ENTIDADES) - len(REGISTRO)
    reg_filas += '<tr><th scope="row">Los otros %d estados</th><td>—</td><td>0 · 0</td><td>%s Por revisar: aún no ubicamos dónde publica cada congreso sus leyes municipales.</td></tr>' % (resto, chip('pendiente'))
    sin = [(k, w, r) for e, r in REGISTRO.items() for k, w in r.get('sin_ley', {}).items()]
    reg_sin = ('<h3 class="ci-tit">Municipios sin Ley de Ingresos %d aprobada %s</h3><ul class="ci-lista">%s</ul>'
               '<p class="ci-nota">Sin una ley aprobada para %d, no hay una tarifa del Congreso que podamos usar: con qué cobra el predial ese municipio lo debe aclarar su tesorería. Lo decimos porque consta en el documento; no adivinamos qué cobra en su lugar.</p>') % (
        ANIO, chip('oficial'), ''.join('<li><b>%s (%s)</b>. %s <a href="%s">%s</a> (huella SHA-256 <code>%s…</code>).</li>' % (
            esc(w['nombre']), esc(ENTIDADES[k.split('-')[0]]), esc(w['motivo']), esc(w['doc']['url']), esc(w['doc']['tx']), w['doc']['sha256'][:12]) for k, w, r in sin), ANIO) if sin else ''
    return '''<div class="ci" id="cpRaiz">
  <section class="ci-arranque" aria-labelledby="cpTit">
    <p class="ci-kicker">Calculadora Cívica · simulador</p>
    <h2 class="ci-grande" id="cpTit">Tu impuesto predial, según tu municipio</h2>
    <p class="ci-txt">Cada municipio cobra el predial con <b>su propia Ley de Ingresos</b>: la tabla, los descuentos, los recargos y lo que cuesta un requerimiento cambian de uno a otro. Elige el tuyo, escribe el valor fiscal de tu predio (viene en tu recibo; si no lo sabes, ármalo con los metros de tu terreno y tu construcción) y la página saca tu predial de {anio}, paso por paso y con su artículo. Si ya te cobraron, escribe lo que dice tu recibo y la página lo compara con la ley. Si debes bimestres, también lo que costaría ponerte al corriente: actualización, recargos, multa y gastos de cobranza, como en un mandamiento de ejecución.</p>
    <p class="ci-privado">🔒 La cuenta la hace tu navegador: lo que escribes no se guarda ni se envía.</p>
  </section>

  <form class="ci-form" id="cpForm" novalidate>
    <fieldset class="ci-grupo">
      <legend class="ci-tit"><span class="ci-n" aria-hidden="true">1</span> Tu municipio</legend>
      <div class="ci-fila">
        <div><label class="ci-et" for="cpEnt">Estado</label><select class="ci-in" id="cpEnt">{ents}</select></div>
        <div><label class="ci-et" for="cpMun">Municipio</label><select class="ci-in" id="cpMun"></select></div>
      </div>
      <div class="cp-mun" id="cpMunFicha" aria-live="polite"></div>
    </fieldset>

    <fieldset class="ci-grupo" id="cpPredio">
      <legend class="ci-tit"><span class="ci-n" aria-hidden="true">2</span> Tu predio</legend>
      <label class="ci-et" for="cpVf">Valor fiscal (pesos)</label>
      <input class="ci-in" id="cpVf" inputmode="decimal" autocomplete="off" placeholder="Ej.: 2,500,000">
      <p class="ci-pista">Es el valor catastral que viene en tu recibo o en tu estado de cuenta predial; lo fija el catastro con las tablas de valores que aprueba el Congreso del Estado.</p>
      <details class="cp-vf" id="cpVfCalc">
        <summary>¿No sabes tu valor fiscal? Ármalo con tu terreno y tu construcción</summary>
        <p class="ci-pista">El catastro lo arma así: <b>metros de terreno × valor unitario de suelo de tu zona</b>, más <b>metros construidos × valor unitario de tu tipo de construcción</b> (y, si tu tabla lo da, un factor por la edad o el estado de conservación). Los valores unitarios vienen en las <b>Tablas de Valores Unitarios</b> de tu municipio, que aprueba el Congreso del Estado cada año y se publican en el periódico oficial del estado; en Jalisco, en el <a href="https://periodicooficial.jalisco.gob.mx/">Periódico Oficial «El Estado de Jalisco»</a>. Ya integramos los valores de construcción de {con_tabla} (elige tu municipio y se ponen solos), y de los demás municipios de Jalisco te damos la liga a su decreto en la ficha del paso 1.</p>
        <div class="ci-fila">
          <div><label class="ci-et" for="cpTs">Terreno (m²)</label><input class="ci-in" id="cpTs" inputmode="decimal" autocomplete="off" placeholder="Ej.: 160"></div>
          <div><label class="ci-et" for="cpVs">Valor de suelo ($/m²)</label><input class="ci-in" id="cpVs" inputmode="decimal" autocomplete="off" placeholder="De tu tabla"></div>
        </div>
        <div class="cp-tabla" id="cpTabla" hidden>
          <p class="ci-pista" id="cpTablaTit"></p>
          <div class="ci-fila">
            <div><label class="ci-et" for="cpTUso">Uso</label><select class="ci-in" id="cpTUso"></select></div>
            <div><label class="ci-et" for="cpTCal">Calidad</label><select class="ci-in" id="cpTCal"></select></div>
          </div>
          <div class="ci-fila">
            <div><label class="ci-et" for="cpTEdad">Edad</label><select class="ci-in" id="cpTEdad"></select></div>
            <div><label class="ci-et" for="cpTEst">Estado de conservación</label><select class="ci-in" id="cpTEst"></select></div>
          </div>
          <label class="ci-check" id="cpTNivL"><input type="checkbox" id="cpTNiv"> El edificio tiene más de 4 niveles</label>
          <p class="ci-nota" id="cpTablaVal" aria-live="polite"></p>
        </div>
        <div class="ci-fila">
          <div><label class="ci-et" for="cpTc">Construcción (m²)</label><input class="ci-in" id="cpTc" inputmode="decimal" autocomplete="off" placeholder="Ej.: 120"></div>
          <div><label class="ci-et" for="cpVc">Valor de construcción ($/m²)</label><input class="ci-in" id="cpVc" inputmode="decimal" autocomplete="off" placeholder="De tu tabla"></div>
        </div>
        <label class="ci-et" for="cpFc">Factor por edad o conservación <small>(si tu tabla lo da; si no, déjalo en 1)</small></label>
        <input class="ci-in" id="cpFc" inputmode="decimal" autocomplete="off" value="1">
        <p class="ci-acciones"><button type="button" class="ci-boton ci-boton-2" id="cpVfUsa">Usar este valor</button></p>
        <p class="ci-nota" id="cpVfRes" aria-live="polite"></p>
        <p class="ci-pista"><b>Ojo: el valor catastral no es lo que vale tu casa en el mercado.</b> El precio de venta lo estiman portales y herramientas privadas (por ejemplo, <a href="https://monopolio.com.mx/avaluos" rel="noopener">Monopolio</a>, con inteligencia artificial y casas parecidas) <span class="est-chip est-pendiente">sin verificar</span>: no son de esta plataforma, no publican su método y ese precio <b>no sirve para el predial</b>, que se cobra sobre el valor catastral. Si escribes aquí el precio de mercado, el simulador te dará un predial más alto que el real.</p>
      </details>
      <label class="ci-et" for="cpTipo">Tipo de predio</label>
      <select class="ci-in" id="cpTipo"><option value="edif">Construido (casa, departamento, local)</option><option value="rust">Rústico (fuera de la zona urbana)</option><option value="baldio">Baldío en zona urbana</option></select>
      <label class="ci-et" for="cpBen">¿Tienes derecho a algún descuento?</label>
      <select class="ci-in" id="cpBen"></select>
      <label class="ci-et" for="cpPago">¿Cómo pagas?</label>
      <select class="ci-in" id="cpPago"></select>
    </fieldset>

    <fieldset class="ci-grupo" id="cpRecibo">
      <legend class="ci-tit"><span class="ci-n" aria-hidden="true">3</span> ¿Ya te cobraron? Compara tu recibo con la ley <small>(opcional)</small></legend>
      <p class="ci-pista">Escribe solo el renglón del <b>impuesto predial</b> de tu recibo, sin agua, aseo ni otros derechos. La página lo compara con lo que dice la Ley de Ingresos de tu municipio para el valor fiscal que escribiste.</p>
      <div class="ci-fila">
        <div><label class="ci-et" for="cpCobro">Lo que te cobran de predial (pesos)</label><input class="ci-in" id="cpCobro" inputmode="decimal" autocomplete="off" placeholder="Ej.: 1,250"></div>
        <div><label class="ci-et" for="cpPer">¿Por cuánto tiempo?</label><select class="ci-in" id="cpPer"><option value="bim">Por un bimestre</option><option value="anual">Por el año</option></select></div>
      </div>
    </fieldset>

    <fieldset class="ci-grupo">
      <legend class="ci-tit"><span class="ci-n" aria-hidden="true">4</span> ¿Debes bimestres? <small>(opcional)</small></legend>
      <label class="ci-check"><input type="checkbox" id="cpDebe"> Sí, quiero saber cuánto pagaría por ponerme al corriente</label>
      <div id="cpDeuda" hidden>
        <label class="ci-et" for="cpImp">Impuesto de cada bimestre que debes (pesos)</label>
        <input class="ci-in" id="cpImp" inputmode="decimal" autocomplete="off" placeholder="Se llena con tu cuenta de arriba">
        <p class="ci-pista">Si debes años anteriores, el impuesto de esos años fue otro: viene en tu estado de cuenta o en el requerimiento.</p>
        <div class="ci-fila">
          <div><label class="ci-et" for="cpDa">Debes desde el año</label><select class="ci-in" id="cpDa">{anios}</select></div>
          <div><label class="ci-et" for="cpDb">bimestre</label><select class="ci-in" id="cpDb">{bims}</select></div>
        </div>
        <div class="ci-fila">
          <div><label class="ci-et" for="cpHa">Hasta el año</label><select class="ci-in" id="cpHa">{anios}</select></div>
          <div><label class="ci-et" for="cpHb">bimestre</label><select class="ci-in" id="cpHb">{bims}</select></div>
        </div>
        <label class="ci-et" for="cpF">¿Qué día pagarías?</label>
        <input class="ci-in" id="cpF" type="date">
        <label class="ci-et" for="cpSit">¿Ya te requirieron?</label>
        <select class="ci-in" id="cpSit">
          <option value="esp">No: pago por mi cuenta, antes de que me notifiquen</option>
          <option value="not">Me notificaron el adeudo</option>
          <option value="req">Me llegó un requerimiento de pago o un mandamiento de ejecución</option>
          <option value="emb">Además me embargaron</option>
        </select>
        <div id="cpMultaCaja"><label class="ci-et" for="cpMulta">Multa que te impusieron (porcentaje del impuesto omitido)</label><select class="ci-in" id="cpMulta"></select></div>
      </div>
    </fieldset>
    <p class="ci-acciones"><button type="submit" class="ci-boton">Saca la cuenta</button></p>
  </form>

  <section class="ci-res" id="cpRes" aria-live="polite" hidden>
    <h2 class="ci-tit"><span class="ci-n" aria-hidden="true">5</span> Tu cuenta, paso por paso {chip_d}</h2>
    <div class="ci-total" id="cpTotal"></div>
    <div class="cp-contraste" id="cpContraste" hidden></div>
    <div class="ci-tabla-caja"><table class="ci-tabla"><caption>Cómo se llega al impuesto</caption>
      <thead><tr><th scope="col">Paso</th><th scope="col">Pesos</th><th scope="col">Regla</th></tr></thead>
      <tbody id="cpPasos"></tbody></table></div>
    <div class="ci-tabla-caja" id="cpDeudaCaja" hidden><table class="ci-tabla"><caption>Si te pones al corriente</caption>
      <thead><tr><th scope="col">Concepto</th><th scope="col">Pesos</th><th scope="col">Regla</th></tr></thead>
      <tbody id="cpDeudaPasos"></tbody></table></div>
    <p class="ci-nota" id="cpNota"></p>
  </section>

  <section class="ci-grupo cp-compara" aria-labelledby="cpCompTit">
    <h2 class="ci-tit" id="cpCompTit"><span aria-hidden="true">⚖️</span> El mismo predio en cada municipio {chip_d}</h2>
    <p class="ci-nota">Con el valor fiscal que escribiste (o $2,500,000 si aún no escribes nada), lo que cobraría de predial al año cada municipio que ya integramos, sin descuentos. Solo cambia la ley; el predio es el mismo. Ojo: el valor fiscal de un mismo terreno tampoco sería igual en otro municipio, porque cada uno tiene sus tablas de valores.</p>
    <div class="ci-tabla-caja"><table class="ci-tabla"><caption id="cpCompCap">Predial anual de un predio construido</caption>
      <thead><tr><th scope="col">Municipio</th><th scope="col">Al año</th><th scope="col">Recargos al mes · multa</th></tr></thead>
      <tbody id="cpComp"></tbody></table></div>
  </section>

  <section class="ci-grupo cp-registro" aria-labelledby="cpRegTit">
    <h2 class="ci-tit" id="cpRegTit"><span aria-hidden="true">🗂️</span> Las leyes del predial, estado por estado</h2>
    <p class="ci-nota">El predial de cada municipio sale de su propia Ley de Ingresos. Aquí llevamos la cuenta de cuántas ya integramos, cuáles leímos y dejamos en espera porque no se entienden, y qué municipios no tienen ley aprobada, según un documento oficial. Un estado «por revisar» es falta de esta plataforma, no del estado.</p>
    <div class="ci-tabla-caja"><table class="ci-tabla"><caption>Leyes de Ingresos municipales {anio}</caption>
      <thead><tr><th scope="col">Estado</th><th scope="col">Municipios</th><th scope="col">Integradas · en espera</th><th scope="col">Dónde las publica</th></tr></thead>
      <tbody>{reg_filas}</tbody></table></div>
    {reg_sin}
  </section>

  <aside class="ci-aviso" aria-labelledby="cpLeeTit">
    <h2 class="ci-tit" id="cpLeeTit"><span aria-hidden="true">📐</span> Cómo se calcula</h2>
    <ol class="ci-lista">
      <li><b>El predial es bimestral.</b> A tu valor fiscal se le resta el límite inferior de su tramo; la diferencia se multiplica por la tasa del tramo y se suma la cuota fija: <code>((VF − LI) × T) + CF</code>. Eso pagas cada bimestre, y por seis, al año. La tabla es de cada Ley de Ingresos. Muchos municipios (Zapotlanejo, Tepatitlán, Ameca, Autlán, San Juan de los Lagos y otros) no usan tramos: cobran una <b>tasa al millar</b> sobre el valor más una cuota fija, y a los predios rústicos les ponen la suya.</li>
      <li><b>Los baldíos pagan más</b> «por razones extrafiscales»: unas leyes les ponen una sobretasa (100 % en Zapopan, Guadalajara, El Salto y Lagos de Moreno: aquí, el doble del impuesto; 90 % en Ocotlán; 50 % en Ixtlahuacán de los Membrillos) y otras, una tasa al millar sobre el valor más una cuota fija. La de Zapotlán el Grande no les pone otra tasa.</li>
      <li><b>Los descuentos</b> son factores sobre el impuesto: 0.50 es pagar la mitad. Muchos valen «sobre el primer» tanto del valor fiscal: aquí el descuento se calcula sobre el impuesto que daría ese valor, la lectura que explica la Ley de Tlaquepaque (art. 32, fr. III, f). Si te tocan varios, se da el mayor; el de adultos mayores (y en algunos municipios el de pensionados) se suma al de pago anticipado, que se calcula sobre lo que queda.</li>
      <li><b>Se paga en los primeros quince días del primer mes de cada bimestre</b> (Ley de Hacienda Municipal, art. 103). Desde el día siguiente corren los <b>recargos</b>, por cada mes o fracción, con la tasa que fija la Ley de Ingresos; no pasan de 250 % del adeudo, o de 100 % si pagas por tu cuenta (art. 52). El adeudo además se <b>actualiza</b> con el INPC (art. 44 bis): aquí, el del mes anterior al pago entre el del mes anterior al vencimiento. En la base, el último INPC es el de {ult}.</li>
      <li><b>Si te cobran</b>, se suman la <b>multa</b> (un porcentaje del impuesto omitido, cuando la ley de ingresos lo fija), la <b>notificación</b> y los <b>gastos de ejecución</b>. Aquí cambia mucho de una ley a otra: unas cobran la notificación en UMA y un porcentaje del crédito por cada diligencia (el requerimiento y el embargo); otras cobran un porcentaje por notificar el requerimiento y otro por el embargo, con su mínimo y su tope en UMA o en pesos; Tepatitlán, cuotas fijas en pesos. La página sigue la de tu municipio y te dice el artículo. La UMA es la de {anio}: ${uma} diarios ({uma_f}).</li>
    </ol>
    <p><b>Un ejemplo real, sin datos de la persona.</b> Un mandamiento de ejecución de la Tesorería de Zapopan cobró un predio con valor fiscal de $7,613,320.00. Cae en el tramo que empieza en $5,158,931.01: (7,613,320.00 − 5,158,931.01) × 0.0003473 + 1,485.21 = <b>$2,337.62 por bimestre</b>, $14,025.72 por los seis de un año y $7,012.86 por tres; la multa fue de 50 % del impuesto ($7,012.86 y $3,506.43) y la notificación, seis UMA de 2022 ($577.32). Escribe ese valor en Zapopan y verás las mismas cifras {chip_d}.</p>
    <p><b>Tu recibo contra la ley.</b> Si escribes lo que te cobran, la página lo compara con su cuenta: si la diferencia no pasa de 1 % (o de un peso), coincide; si pasa, te da las causas más comunes y, con lo que te cobran, el valor fiscal que daría ese impuesto en la tabla de tu municipio {chip_d}. <b>Una diferencia no quiere decir que te cobren mal</b>: es una señal para pedir el desglose en la tesorería. Muchas veces el recibo suma derechos o adeudos, o el catastro actualizó tu valor.</p>
    <p><b>Lo que esta cuenta no hace:</b> no es tu estado de cuenta ni una resolución: el adeudo oficial te lo da la tesorería de tu municipio, y cambia cada mes. Usa la tarifa y las tasas de {anio}; los años anteriores tuvieron las suyas en su propia ley, así que para un adeudo viejo la cifra es aproximada. No calcula el valor fiscal (lo fija el catastro), los derechos de agua o basura, los convenios ni las condonaciones o programas de descuento en recargos que aprueba cada municipio, ni las erogaciones extraordinarias de un embargo (avalúo, edictos, traslado). Si no estás de acuerdo con un requerimiento, la ley te da recursos con plazo: el de reconsideración y el juicio ante el Tribunal de Justicia Administrativa; acércate a un abogado o a la Procuraduría de Desarrollo Urbano o de la Defensa del Contribuyente de tu estado.</p>
    <p><b>Municipios integrados:</b> {lista}. Para los demás damos cuánto recaudaron de predial (INEGI) y su tabla queda por integrar: es falta de esta plataforma, no del municipio, que la publica en su Ley de Ingresos. <b>Leídas y en espera</b> {chip_p}: {espera}. No adivinamos una tasa.</p>
    <p class="ci-fuentes">Fuentes, cotejadas el 19-11-2026: <ul class="ci-lista">{leyes}<li><a href="{lhm_url}">{lhm_tx}</a> (huella SHA-256 <code>{lhm_sha}…</code>), arts. 44 bis, 52 y 103</li></ul> INPC: <a href="{inpc_url}">{f_inpc}</a> · Recaudación de cada municipio: INEGI, EFIPEM 2024 {chip_o}.</p>
    <p class="ci-hermanas">Sigue con la Calculadora: <a href="herramienta-calculadora-inmueble.html">🏠 Vendes una casa o un terreno</a> · <a href="herramienta-calculadora-ticket.html">🧾 Tu estado de cuenta</a></p>
  </aside>
  <script type="application/json" id="cpDatos">{datos}</script>
</div>'''.format(
        con_tabla=con_tabla, anio=ANIO, ents=ents, anios=anios, bims=bims, ult=ult, uma=format(D['uma'], ',.2f'), uma_f=esc(D['uma_f']),
        lista=lista, espera=espera, reg_filas=reg_filas, reg_sin=reg_sin, chip_p=chip('pendiente'), leyes=leyes, lhm_url=esc(LHM['url']), lhm_tx=esc(LHM['tx']), lhm_sha=LHM['sha256'][:12],
        inpc_url=esc(cc_inmueble.datos(base)['f']['inpc_url']), f_inpc=esc(cc_inmueble.datos(base)['f']['inpc']),
        chip_d=chip('derivado'), chip_o=chip('oficial'), datos=cc_inmueble._json(D))


# ---- Prueba: el caso del mandamiento y que Python y el navegador den lo mismo ----

def prueba():
    revisa()
    zap = next(m for m in MUNICIPIOS if m['id'] == 'zapopan')
    mal = 0
    b = bimestral(zap, EJEMPLO['vf'])
    if b != EJEMPLO['bim'] or round(b * 6, 2) != EJEMPLO['anual'] or round(b * 3, 2) != EJEMPLO['tres']:
        mal += 1
        print('✗ el mandamiento de Zapopan no da $2,337.62 por bimestre:', b)
    if round(EJEMPLO['anual'] * 0.5, 2) != 7012.86 or round(6 * EJEMPLO['uma2022'], 2) != EJEMPLO['notif_uma2022']:
        mal += 1
        print('✗ la multa o la notificación del ejemplo')
    js = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'cc-predial.js')
    casos = [(m['id'], v, t) for m in MUNICIPIOS for v in (150000, 950000, 2500000, 7613320, 30000000, 2e9) for t in ('edif', 'rust', 'baldio')]
    D = {'mun': MUNICIPIOS, 'inpc': {}, 'inpc_ult': [2026, 1], 'uma': 117.31, 'lhm': {'tope': 250, 'tope_esp': 100}}
    prog = ("global.window={};global.document={getElementById:function(){return null}};require(%s);"
            "var D=%s,c=%s;console.log(JSON.stringify(c.map(function(x){var m=D.mun.filter(function(y){return y.id===x[0]})[0];"
            "return window.AuditorPredial.base(m,x[1],x[2]);})));"
            "var m=D.mun[0];var r=window.AuditorPredial.calcula(D,m,{vf:7613320,tipo:'edif',ben:'',pago:'bim'});console.log(JSON.stringify(r.anual));"
            % (json.dumps(js), json.dumps(D), json.dumps(casos)))
    r = subprocess.run(['node', '-e', prog], capture_output=True, text=True)
    if r.returncode:
        print(r.stderr)
        return 1
    lineas = r.stdout.strip().split('\n')
    nav = json.loads(lineas[0])
    for (mid, v, t), n in zip(casos, nav):
        py = base(next(m for m in MUNICIPIOS if m['id'] == mid), v, t)
        if abs(py - n) > 0.005:
            mal += 1
            print('✗', mid, v, t, 'Python', py, 'navegador', n)
    # La cobranza: notificación solo con requerimiento y embargo una vez (El Salto), cuotas en pesos (Tepatitlán),
    # mínimos y topes en pesos (Arandas, Tequila).
    y = "{imp:1000,da:2025,db:1,ha:2025,hb:6,f:[2026,6,1],multa:0,sit:S}"
    prog2 = ("global.window={};global.document={getElementById:function(){return null}};require(%s);var D=%s;"
             "function M(i){return D.mun.filter(function(m){return m.id===i})[0]}"
             "var o={};['not','req','emb'].forEach(function(S){var r=window.AuditorPredial.adeudo(D,M('elsalto'),%s);o['s'+S]=[r.notif,r.ejec];"
             "r=window.AuditorPredial.adeudo(D,M('tepatitlan'),%s);o['t'+S]=[r.notif,r.ejec];"
             "r=window.AuditorPredial.adeudo(D,M('arandas'),%s);o['a'+S]=[r.notif,r.ejec];"
             "r=window.AuditorPredial.adeudo(D,M('tequila'),%s);o['q'+S]=[r.notif,r.ejec];});console.log(JSON.stringify(o));"
             % (json.dumps(js), json.dumps(D), y, y, y, y))
    r2 = subprocess.run(['node', '-e', prog2], capture_output=True, text=True)
    o = json.loads(r2.stdout or '{}')
    uma = D['uma']
    # Mínimos en pesos con requerimiento y embargo (Arandas); notificación en pesos y 5 % por cada diligencia (Tequila).
    esperado = {'snot': [0, 0], 'tnot': [0, 0], 'treq': [578.79, 0], 'temb': [578.79, 710.34],
                'anot': [0, 0], 'areq': [499, 0], 'aemb': [499, 615],
                'qnot': [106.85, 0], 'qreq': [106.85, 336], 'qemb': [106.85, 672]}
    for k, v in esperado.items():
        if o.get(k) != v:
            mal += 1
            print('✗ cobranza', k, o.get(k), 'esperaba', v)
    sreq, semb = o.get('sreq', [0, 1]), o.get('semb', [0, 0])
    if not (uma <= sreq[0] <= 30 * uma) or sreq[1] != 0 or not (0 < semb[1] <= 45 * uma) or semb[0] != sreq[0]:
        mal += 1
        print('✗ cobranza de El Salto', sreq, semb)
    # El mínimo bimestral (Tamazula, $50) y las cuentas al revés: Python y el navegador, iguales.
    tam = next(m for m in MUNICIPIOS if m['id'] == 'tamazula')
    if base(tam, 10000, 'edif') != 50.0 or base(tam, 1000000, 'edif') != bimestral(tam, 1000000):
        mal += 1
        print('✗ el mínimo de Tamazula')
    inv = [(m['id'], i) for m in MUNICIPIOS for i in (60, 333.33, 1485.21, 2337.62, 9000)]
    prog3 = ("global.window={};global.document={getElementById:function(){return null}};require(%s);var D=%s;"
             "console.log(JSON.stringify(%s.map(function(x){var m=D.mun.filter(function(y){return y.id===x[0]})[0];"
             "return window.AuditorPredial.inverso(m,x[1]);})));console.log(window.AuditorPredial.valorFiscal({ts:160,vs:3250.5,tc:120,vc:6400,fc:0.85}));"
             % (json.dumps(js), json.dumps(D), json.dumps(inv)))
    r3 = subprocess.run(['node', '-e', prog3], capture_output=True, text=True)
    l3 = r3.stdout.strip().split('\n')
    for (mid, i), n in zip(inv, json.loads(l3[0])):
        mm = next(m for m in MUNICIPIOS if m['id'] == mid)
        py = inverso(mm, i)
        if py != n or (py is not None and abs(bimestral(mm, py) - i) > 0.02):
            mal += 1
            print('✗ inverso', mid, i, py, n)
    # La tabla de valores de Zapopan: cada celda igual en Python y en el navegador, con y sin el +10 % por niveles.
    cel = [(mid, u, i, e, k, n) for mid, T in TABLAS.items() for u, U in T['usos'].items() for i in range(len(U['cal']))
           for e in range(len(T['edades'])) for k in range(3) for n in (False, True)]
    prog4 = ("global.window={};global.document={getElementById:function(){return null}};require(%s);var T=%s;"
             "console.log(JSON.stringify(%s.map(function(x){return window.AuditorPredial.valorConstruccion(T[x[0]],x[1],x[2],x[3],x[4],x[5]);})));"
             % (json.dumps(js), json.dumps(TABLAS), json.dumps(cel)))
    r4 = subprocess.run(['node', '-e', prog4], capture_output=True, text=True)
    nav4 = json.loads(r4.stdout or '[]')
    if len(nav4) != len(cel):
        mal += 1
        print('✗ la tabla de valores no corrió en el navegador', r4.stderr[:300])
    for x, n in zip(cel, nav4):
        if valor_construccion(TABLAS[x[0]], *x[1:]) != n:
            mal += 1
            print('✗ tabla de valores', x, n)
    if valor_construccion(TABLAS['zapopan'], 'hab', 2, 0, 0) != 8800:
        mal += 1
        print('✗ Zapopan, medio moderno bueno debe ser $8,800 por m²')
    if float(l3[1]) != valor_fiscal(160, 3250.5, 120, 6400, 0.85):
        mal += 1
        print('✗ valorFiscal', l3[1])
    # Al revés no es exacto: el impuesto viene redondeado al centavo, así que regresa a unos pesos del valor (centavo ÷ tasa).
    zi = inverso(zap, EJEMPLO['bim'])
    if zi is None or bimestral(zap, zi) != EJEMPLO['bim'] or abs(zi - EJEMPLO['vf']) > 0.01 / 0.0003473 + 0.01:
        mal += 1
        print('✗ el inverso del mandamiento de Zapopan no regresa a su valor fiscal:', zi)
    if abs(json.loads(lineas[1]) - EJEMPLO['anual']) > 0.005:
        mal += 1
        print('✗ el navegador no da $14,025.72 al año para el ejemplo:', lineas[1])
    if mal:
        print('%d diferencias en el simulador del predial' % mal)
        return 1
    print('✓ Simulador del predial: %d municipios (%d leídos y en espera), %d casos iguales en Python y en el navegador '
          '(y %d celdas de tablas de valores); la cobranza sigue a cada ley; el mandamiento de Zapopan cuadra ($2,337.62)' % (len(MUNICIPIOS), len(ESPERA), len(casos), len(cel)))
    return 0


if __name__ == '__main__':
    if '--prueba' in sys.argv:
        sys.exit(prueba())
