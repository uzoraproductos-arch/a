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
]

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


def bimestral(m, vf):
    t = [x for x in m['tramos'] if vf >= x[0]]
    li, cf, tasa = t[-1] if t else m['tramos'][0]
    return round((vf - li) * tasa + cf, 2)


def datos(base):
    revisa()
    cc = cc_inmueble.datos(base)
    uma = base['calculadora_civica']['parametros']['uma']
    return {'anio': ANIO, 'inpc': cc['inpc'], 'inpc_ult': cc['inpc_ult'],
            'uma': uma['diaria'], 'uma_f': uma['fuente'], 'ent': ENTIDADES,
            'mun': MUNICIPIOS, 'lhm': {'tope': 250, 'tope_esp': 100}}


def construir(base, ref):
    D = datos(base)
    MES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    ult = '%s de %d' % (MES[D['inpc_ult'][1] - 1], D['inpc_ult'][0])
    ents = ''.join('<option value="%s"%s>%s</option>' % (esc(k), ' selected' if k == 'JAL' else '', esc(v))
                   for k, v in sorted(ENTIDADES.items(), key=lambda x: x[1]))
    anios = ''.join('<option value="%d"%s>%d</option>' % (a, ' selected' if a == ANIO else '', a) for a in range(ANIO + 1, 2014, -1))
    bims = ''.join('<option value="%d">%d.º (%s y %s)</option>' % (b, b, MES[2 * b - 2], MES[2 * b - 1]) for b in range(1, 7))
    leyes = ''.join('<li><b>%s</b>: <a href="%s">%s</a> (huella SHA-256 <code>%s…</code>)</li>'
                    % (esc(m['nombre']), esc(m['url']), esc(m['ley']), m['sha256'][:12]) for m in MUNICIPIOS)
    lista = ', '.join(esc(m['nombre']) for m in MUNICIPIOS)
    return '''<div class="ci" id="cpRaiz">
  <section class="ci-arranque" aria-labelledby="cpTit">
    <p class="ci-kicker">Calculadora Cívica · simulador</p>
    <h2 class="ci-grande" id="cpTit">Tu impuesto predial, según tu municipio</h2>
    <p class="ci-txt">Cada municipio cobra el predial con <b>su propia Ley de Ingresos</b>: la tabla, los descuentos, los recargos y lo que cuesta un requerimiento cambian de uno a otro. Elige el tuyo, escribe el valor fiscal de tu predio (viene en tu recibo) y la página saca tu predial de {anio}, paso por paso y con su artículo. Si debes bimestres, también lo que costaría ponerte al corriente: actualización, recargos, multa y gastos de cobranza, como en un mandamiento de ejecución.</p>
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
      <label class="ci-et" for="cpTipo">Tipo de predio</label>
      <select class="ci-in" id="cpTipo"><option value="edif">Construido (casa, departamento, local) o rústico</option><option value="baldio">Baldío en zona urbana</option></select>
      <label class="ci-et" for="cpBen">¿Tienes derecho a algún descuento?</label>
      <select class="ci-in" id="cpBen"></select>
      <label class="ci-et" for="cpPago">¿Cómo pagas?</label>
      <select class="ci-in" id="cpPago"></select>
    </fieldset>

    <fieldset class="ci-grupo">
      <legend class="ci-tit"><span class="ci-n" aria-hidden="true">3</span> ¿Debes bimestres? <small>(opcional)</small></legend>
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
    <h2 class="ci-tit"><span class="ci-n" aria-hidden="true">4</span> Tu cuenta, paso por paso {chip_d}</h2>
    <div class="ci-total" id="cpTotal"></div>
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

  <aside class="ci-aviso" aria-labelledby="cpLeeTit">
    <h2 class="ci-tit" id="cpLeeTit"><span aria-hidden="true">📐</span> Cómo se calcula</h2>
    <ol class="ci-lista">
      <li><b>El predial es bimestral.</b> A tu valor fiscal se le resta el límite inferior de su tramo; la diferencia se multiplica por la tasa del tramo y se suma la cuota fija: <code>((VF − LI) × T) + CF</code>. Eso pagas cada bimestre, y por seis, al año. La tabla es de cada Ley de Ingresos.</li>
      <li><b>Los baldíos pagan más</b> «por razones extrafiscales»: en Zapopan y Guadalajara, una sobretasa de 100 % (aquí, el doble del impuesto); en Tlaquepaque, Tonalá y Tlajomulco, una tasa al millar sobre el valor más una cuota fija.</li>
      <li><b>Los descuentos</b> son factores sobre el impuesto: 0.50 es pagar la mitad. Muchos valen «sobre el primer» tanto del valor fiscal: aquí el descuento se calcula sobre el impuesto que daría ese valor, la lectura que explica la Ley de Tlaquepaque (art. 32, fr. III, f). Si te tocan varios, se da el mayor; el de adultos mayores (y en algunos municipios el de pensionados) se suma al de pago anticipado, que se calcula sobre lo que queda.</li>
      <li><b>Se paga en los primeros quince días del primer mes de cada bimestre</b> (Ley de Hacienda Municipal, art. 103). Desde el día siguiente corren los <b>recargos</b>, por cada mes o fracción, con la tasa que fija la Ley de Ingresos; no pasan de 250 % del adeudo, o de 100 % si pagas por tu cuenta (art. 52). El adeudo además se <b>actualiza</b> con el INPC (art. 44 bis): aquí, el del mes anterior al pago entre el del mes anterior al vencimiento. En la base, el último INPC es el de {ult}.</li>
      <li><b>Si te cobran</b>, se suman la <b>multa</b> (un porcentaje del impuesto omitido, cuando la ley de ingresos lo fija), la <b>notificación</b> (unas veces la UMA diaria; en Tlajomulco, 8 % del crédito) y los <b>gastos de ejecución</b> por cada diligencia: el requerimiento y el embargo (3 % u 8 % del crédito, con su mínimo y su tope en UMA). La UMA es la de {anio}: ${uma} diarios ({uma_f}).</li>
    </ol>
    <p><b>Un ejemplo real, sin datos de la persona.</b> Un mandamiento de ejecución de la Tesorería de Zapopan cobró un predio con valor fiscal de $7,613,320.00. Cae en el tramo que empieza en $5,158,931.01: (7,613,320.00 − 5,158,931.01) × 0.0003473 + 1,485.21 = <b>$2,337.62 por bimestre</b>, $14,025.72 por los seis de un año y $7,012.86 por tres; la multa fue de 50 % del impuesto ($7,012.86 y $3,506.43) y la notificación, seis UMA de 2022 ($577.32). Escribe ese valor en Zapopan y verás las mismas cifras {chip_d}.</p>
    <p><b>Lo que esta cuenta no hace:</b> no es tu estado de cuenta ni una resolución: el adeudo oficial te lo da la tesorería de tu municipio, y cambia cada mes. Usa la tarifa y las tasas de {anio}; los años anteriores tuvieron las suyas en su propia ley, así que para un adeudo viejo la cifra es aproximada. No calcula el valor fiscal (lo fija el catastro), los derechos de agua o basura, los convenios ni las condonaciones o programas de descuento en recargos que aprueba cada municipio, ni las erogaciones extraordinarias de un embargo (avalúo, edictos, traslado). Si no estás de acuerdo con un requerimiento, la ley te da recursos con plazo: el de reconsideración y el juicio ante el Tribunal de Justicia Administrativa; acércate a un abogado o a la Procuraduría de Desarrollo Urbano o de la Defensa del Contribuyente de tu estado.</p>
    <p><b>Municipios integrados:</b> {lista}. Para los demás damos cuánto recaudaron de predial (INEGI) y su tabla queda por integrar: es falta de esta plataforma, no del municipio, que la publica en su Ley de Ingresos.</p>
    <p class="ci-fuentes">Fuentes, cotejadas el 19-11-2026: <ul class="ci-lista">{leyes}<li><a href="{lhm_url}">{lhm_tx}</a> (huella SHA-256 <code>{lhm_sha}…</code>), arts. 44 bis, 52 y 103</li></ul> INPC: <a href="{inpc_url}">{f_inpc}</a> · Recaudación de cada municipio: INEGI, EFIPEM 2024 {chip_o}.</p>
    <p class="ci-hermanas">Sigue con la Calculadora: <a href="herramienta-calculadora-inmueble.html">🏠 Vendes una casa o un terreno</a> · <a href="herramienta-calculadora-ticket.html">🧾 Tu estado de cuenta</a></p>
  </aside>
  <script type="application/json" id="cpDatos">{datos}</script>
</div>'''.format(
        anio=ANIO, ents=ents, anios=anios, bims=bims, ult=ult, uma=format(D['uma'], ',.2f'), uma_f=esc(D['uma_f']),
        lista=lista, leyes=leyes, lhm_url=esc(LHM['url']), lhm_tx=esc(LHM['tx']), lhm_sha=LHM['sha256'][:12],
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
    casos = [(m['id'], v) for m in MUNICIPIOS for v in (150000, 950000, 2500000, 7613320, 30000000, 2e9)]
    D = {'mun': MUNICIPIOS, 'inpc': {}, 'inpc_ult': [2026, 1], 'uma': 117.31, 'lhm': {'tope': 250, 'tope_esp': 100}}
    prog = ("global.window={};global.document={getElementById:function(){return null}};require(%s);"
            "var D=%s,c=%s;console.log(JSON.stringify(c.map(function(x){var m=D.mun.filter(function(y){return y.id===x[0]})[0];"
            "return window.AuditorPredial.bimestral(m,x[1]);})));"
            "var m=D.mun[0];var r=window.AuditorPredial.calcula(D,m,{vf:7613320,tipo:'edif',ben:'',pago:'bim'});console.log(JSON.stringify(r.anual));"
            % (json.dumps(js), json.dumps(D), json.dumps(casos)))
    r = subprocess.run(['node', '-e', prog], capture_output=True, text=True)
    if r.returncode:
        print(r.stderr)
        return 1
    lineas = r.stdout.strip().split('\n')
    nav = json.loads(lineas[0])
    for (mid, v), n in zip(casos, nav):
        py = bimestral(next(m for m in MUNICIPIOS if m['id'] == mid), v)
        if abs(py - n) > 0.005:
            mal += 1
            print('✗', mid, v, 'Python', py, 'navegador', n)
    if abs(json.loads(lineas[1]) - EJEMPLO['anual']) > 0.005:
        mal += 1
        print('✗ el navegador no da $14,025.72 al año para el ejemplo:', lineas[1])
    if mal:
        print('%d diferencias en el simulador del predial' % mal)
        return 1
    print('✓ Simulador del predial: %d municipios, %d casos iguales en Python y en el navegador; el mandamiento de Zapopan cuadra ($2,337.62)'
          % (len(MUNICIPIOS), len(casos)))
    return 0


if __name__ == '__main__':
    if '--prueba' in sys.argv:
        sys.exit(prueba())
