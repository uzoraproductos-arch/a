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
]

# Leyes que leímos y no integramos, con su porqué: la página lo dice en la ficha del municipio.
ESPERA = {
    'JAL-002': {'nombre': 'Acatlán de Juárez', 'url': _li('Acatl%C3%A1n%20de%20Ju%C3%A1rez'),
                'sha256': '78ac7763e957e8e33f85401a41b94335c6421595e88795632fa7ee18bcf179c8',
                'motivo': 'su art. 25 pone las tasas como «20%», «25%» y «30%» bajo el título «Tasa bimestral al millar», y así no se sabe cuánto es.'},
    'JAL-030': {'nombre': 'Chapala', 'url': _li('Chapala'),
                'sha256': 'fef31659e5b631cfbc1c63cda3666036d1e0b6a3e96ec94bdcad34857118a031',
                'motivo': 'su art. 42 pone las tasas como «0.20%», «0.25%» y «0.30%» bajo el título «Tasa bimestral al millar», y así no se sabe cuánto es.'},
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
        if m.get('multa') and not (0 < m['multa']['min'] <= m['multa']['max']):
            raise SystemExit('cc_predial: la multa de %s está al revés' % m['id'])
    ids = [m['id'] for m in MUNICIPIOS]
    claves = ['%s-%s' % (m['ent'], m['cve']) for m in MUNICIPIOS]
    if len(set(ids)) != len(ids) or len(set(claves)) != len(claves):
        raise SystemExit('cc_predial: un municipio está dos veces')
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
    """Gemela de base() de cc-predial.js: construido, rústico o baldío."""
    if tipo == 'rust' and m.get('rustico'):
        return _r2(vf * m['rustico']['millar'] / 1000 + m['rustico']['cf'])
    if tipo != 'baldio' or m['baldio']['tipo'] == 'igual':
        return bimestral(m, vf)
    b = m['baldio']
    if b['tipo'] == 'sobretasa':
        return _r2(bimestral(m, vf) * (1 + b['pct'] / 100))
    return _r2(vf * b['millar'] / 1000 + b['cf'])


def datos(base):
    revisa()
    cc = cc_inmueble.datos(base)
    uma = base['calculadora_civica']['parametros']['uma']
    return {'anio': ANIO, 'inpc': cc['inpc'], 'inpc_ult': cc['inpc_ult'],
            'uma': uma['diaria'], 'uma_f': uma['fuente'], 'ent': ENTIDADES,
            'mun': MUNICIPIOS, 'espera': ESPERA, 'lhm': {'tope': 250, 'tope_esp': 100}}


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
    espera = '; '.join('%s: <a href="%s">su ley</a> %s' % (esc(w['nombre']), esc(w['url']), esc(w['motivo'])) for w in ESPERA.values())
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
      <select class="ci-in" id="cpTipo"><option value="edif">Construido (casa, departamento, local)</option><option value="rust">Rústico (fuera de la zona urbana)</option><option value="baldio">Baldío en zona urbana</option></select>
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
      <li><b>El predial es bimestral.</b> A tu valor fiscal se le resta el límite inferior de su tramo; la diferencia se multiplica por la tasa del tramo y se suma la cuota fija: <code>((VF − LI) × T) + CF</code>. Eso pagas cada bimestre, y por seis, al año. La tabla es de cada Ley de Ingresos. Algunos municipios (Zapotlanejo, Juanacatlán, Tepatitlán) no usan tramos: cobran una <b>tasa al millar</b> sobre el valor más una cuota fija, y a los predios rústicos les ponen la suya.</li>
      <li><b>Los baldíos pagan más</b> «por razones extrafiscales»: unas leyes les ponen una sobretasa (100 % en Zapopan, Guadalajara, El Salto y Lagos de Moreno: aquí, el doble del impuesto; 90 % en Ocotlán; 50 % en Ixtlahuacán de los Membrillos) y otras, una tasa al millar sobre el valor más una cuota fija. La de Zapotlán el Grande no les pone otra tasa.</li>
      <li><b>Los descuentos</b> son factores sobre el impuesto: 0.50 es pagar la mitad. Muchos valen «sobre el primer» tanto del valor fiscal: aquí el descuento se calcula sobre el impuesto que daría ese valor, la lectura que explica la Ley de Tlaquepaque (art. 32, fr. III, f). Si te tocan varios, se da el mayor; el de adultos mayores (y en algunos municipios el de pensionados) se suma al de pago anticipado, que se calcula sobre lo que queda.</li>
      <li><b>Se paga en los primeros quince días del primer mes de cada bimestre</b> (Ley de Hacienda Municipal, art. 103). Desde el día siguiente corren los <b>recargos</b>, por cada mes o fracción, con la tasa que fija la Ley de Ingresos; no pasan de 250 % del adeudo, o de 100 % si pagas por tu cuenta (art. 52). El adeudo además se <b>actualiza</b> con el INPC (art. 44 bis): aquí, el del mes anterior al pago entre el del mes anterior al vencimiento. En la base, el último INPC es el de {ult}.</li>
      <li><b>Si te cobran</b>, se suman la <b>multa</b> (un porcentaje del impuesto omitido, cuando la ley de ingresos lo fija), la <b>notificación</b> y los <b>gastos de ejecución</b>. Aquí cambia mucho de una ley a otra: unas cobran la notificación en UMA y un porcentaje del crédito por cada diligencia (el requerimiento y el embargo); otras cobran un porcentaje por notificar el requerimiento y otro por el embargo, con su tope en UMA o en pesos; Tepatitlán, cuotas fijas en pesos. La página sigue la de tu municipio y te dice el artículo. La UMA es la de {anio}: ${uma} diarios ({uma_f}).</li>
    </ol>
    <p><b>Un ejemplo real, sin datos de la persona.</b> Un mandamiento de ejecución de la Tesorería de Zapopan cobró un predio con valor fiscal de $7,613,320.00. Cae en el tramo que empieza en $5,158,931.01: (7,613,320.00 − 5,158,931.01) × 0.0003473 + 1,485.21 = <b>$2,337.62 por bimestre</b>, $14,025.72 por los seis de un año y $7,012.86 por tres; la multa fue de 50 % del impuesto ($7,012.86 y $3,506.43) y la notificación, seis UMA de 2022 ($577.32). Escribe ese valor en Zapopan y verás las mismas cifras {chip_d}.</p>
    <p><b>Lo que esta cuenta no hace:</b> no es tu estado de cuenta ni una resolución: el adeudo oficial te lo da la tesorería de tu municipio, y cambia cada mes. Usa la tarifa y las tasas de {anio}; los años anteriores tuvieron las suyas en su propia ley, así que para un adeudo viejo la cifra es aproximada. No calcula el valor fiscal (lo fija el catastro), los derechos de agua o basura, los convenios ni las condonaciones o programas de descuento en recargos que aprueba cada municipio, ni las erogaciones extraordinarias de un embargo (avalúo, edictos, traslado). Si no estás de acuerdo con un requerimiento, la ley te da recursos con plazo: el de reconsideración y el juicio ante el Tribunal de Justicia Administrativa; acércate a un abogado o a la Procuraduría de Desarrollo Urbano o de la Defensa del Contribuyente de tu estado.</p>
    <p><b>Municipios integrados:</b> {lista}. Para los demás damos cuánto recaudaron de predial (INEGI) y su tabla queda por integrar: es falta de esta plataforma, no del municipio, que la publica en su Ley de Ingresos. <b>Leídas y en espera</b> {chip_p}: {espera}. No adivinamos una tasa.</p>
    <p class="ci-fuentes">Fuentes, cotejadas el 19-11-2026: <ul class="ci-lista">{leyes}<li><a href="{lhm_url}">{lhm_tx}</a> (huella SHA-256 <code>{lhm_sha}…</code>), arts. 44 bis, 52 y 103</li></ul> INPC: <a href="{inpc_url}">{f_inpc}</a> · Recaudación de cada municipio: INEGI, EFIPEM 2024 {chip_o}.</p>
    <p class="ci-hermanas">Sigue con la Calculadora: <a href="herramienta-calculadora-inmueble.html">🏠 Vendes una casa o un terreno</a> · <a href="herramienta-calculadora-ticket.html">🧾 Tu estado de cuenta</a></p>
  </aside>
  <script type="application/json" id="cpDatos">{datos}</script>
</div>'''.format(
        anio=ANIO, ents=ents, anios=anios, bims=bims, ult=ult, uma=format(D['uma'], ',.2f'), uma_f=esc(D['uma_f']),
        lista=lista, espera=espera, chip_p=chip('pendiente'), leyes=leyes, lhm_url=esc(LHM['url']), lhm_tx=esc(LHM['tx']), lhm_sha=LHM['sha256'][:12],
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
    # La cobranza: notificación solo con requerimiento y embargo una vez (El Salto), cuotas en pesos (Tepatitlán).
    y = "{imp:1000,da:2025,db:1,ha:2025,hb:6,f:[2026,6,1],multa:0,sit:S}"
    prog2 = ("global.window={};global.document={getElementById:function(){return null}};require(%s);var D=%s;"
             "function M(i){return D.mun.filter(function(m){return m.id===i})[0]}"
             "var o={};['not','req','emb'].forEach(function(S){var r=window.AuditorPredial.adeudo(D,M('elsalto'),%s);o['s'+S]=[r.notif,r.ejec];"
             "r=window.AuditorPredial.adeudo(D,M('tepatitlan'),%s);o['t'+S]=[r.notif,r.ejec];});console.log(JSON.stringify(o));"
             % (json.dumps(js), json.dumps(D), y, y))
    r2 = subprocess.run(['node', '-e', prog2], capture_output=True, text=True)
    o = json.loads(r2.stdout or '{}')
    uma = D['uma']
    esperado = {'snot': [0, 0], 'tnot': [0, 0], 'treq': [578.79, 0], 'temb': [578.79, 710.34]}
    for k, v in esperado.items():
        if o.get(k) != v:
            mal += 1
            print('✗ cobranza', k, o.get(k), 'esperaba', v)
    sreq, semb = o.get('sreq', [0, 1]), o.get('semb', [0, 0])
    if not (uma <= sreq[0] <= 30 * uma) or sreq[1] != 0 or not (0 < semb[1] <= 45 * uma) or semb[0] != sreq[0]:
        mal += 1
        print('✗ cobranza de El Salto', sreq, semb)
    if abs(json.loads(lineas[1]) - EJEMPLO['anual']) > 0.005:
        mal += 1
        print('✗ el navegador no da $14,025.72 al año para el ejemplo:', lineas[1])
    if mal:
        print('%d diferencias en el simulador del predial' % mal)
        return 1
    print('✓ Simulador del predial: %d municipios (%d leídos y en espera), %d casos iguales en Python y en el navegador; '
          'la cobranza sigue a cada ley; el mandamiento de Zapopan cuadra ($2,337.62)' % (len(MUNICIPIOS), len(ESPERA), len(casos)))
    return 0


if __name__ == '__main__':
    if '--prueba' in sys.argv:
        sys.exit(prueba())
