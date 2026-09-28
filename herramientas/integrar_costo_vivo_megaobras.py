# -*- coding: utf-8 -*-
"""Costo en vivo de las megaobras (módulo 2, «Simulación en vivo»), 28-09-2026.

Es una interpretación de Auditavisión hecha solo con cifras oficiales: cada
obra corre a un ritmo anual que suma dos componentes documentados, y la
operación de cada uno se publica junto al número.

1. Lo que el erario le pone este año: su asignación en el PEF 2026 (datos
   abiertos, sumados por clave de cartera, unidad responsable o ramo).
2. Lo que sigue costando el dinero que ya se perdió: el sobrecosto, la
   cancelación o el gasto sin obra que documentan la ASF o Hacienda,
   multiplicado por la tasa implícita del costo financiero de la deuda
   pública en 2026 (costo financiero del PEF 2026 ÷ SHRFSP estimado para
   2026 en los Criterios 2027). Es el interés que cuesta cada año tener ese
   dinero financiado con deuda. Donde la ASF documenta los intereses que de
   verdad se pagaron (rescate carretero), se usa ese dato y no la tasa.

Las obras sin un solo componente documentado no corren: el simulador dice qué
documento falta. Nada se estima.

Uso:  python3 herramientas/integrar_costo_vivo_megaobras.py <PEF_2026.csv>
Escribe costo_vivo_megaobras en assets/auditor/js/audit-database.js.
Idempotente.
"""
import csv
import hashlib
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'audit-database.js')
CSV_SHA = '6dec5f3ad52126c3257a74e7e177eada0c591ed8109d861becf767e959c86c03'

COSTO_FINANCIERO_2026 = 1572073.3   # PEF 2026, Anexo 8 (panoramaErario, egr-costofin)
SHRFSP_2026 = 20062321.6            # CGPE 2027, p. 67, estimado de cierre 2026 (deuda.shrfsp)


def mdp(x):
    return round(x / 1e6, 1)


def pef(ruta):
    h = hashlib.sha256(open(ruta, 'rb').read()).hexdigest()
    if h != CSV_SHA:
        sys.exit('La huella del CSV no coincide: ' + h)
    t = {'tren_maya': 0.0, 'aifa': 0.0, 'interurbano': 0.0, 'ramo34': 0.0}
    for x in csv.DictReader(open(ruta, encoding='utf-8-sig')):
        m = float(x['MONTO_PEF_2026'])
        if x['ID_RAMO'] == '7' and x['DESC_UR'] == 'Tren Maya, S.A. de C.V.':
            t['tren_maya'] += m
        if x['ID_RAMO'] == '7' and x['DESC_UR'].startswith('Aeropuerto Internacional Felipe'):
            t['aifa'] += m
        if x['ID_CLAVE_CARTERA'] == '13093110008':
            t['interurbano'] += m
        if x['ID_RAMO'] == '34':
            t['ramo34'] += m
    return {k: mdp(v) for k, v in t.items()}


def bloque_json(raw, clave):
    i = raw.index('"' + clave + '": {')
    j = raw.index('{', i)
    prof = 0
    for k in range(j, len(raw)):
        if raw[k] == '{':
            prof += 1
        elif raw[k] == '}':
            prof -= 1
            if prof == 0:
                return j, k + 1
    raise ValueError(clave)


def construir(p, sm):
    obra = {o['id']: o for o in sm['obras']}
    ver = sm['verificacion']['obras']
    tasa = round(COSTO_FINANCIERO_2026 / SHRFSP_2026 * 100, 2)

    def sobrecosto(i):
        o = obra[i]
        return round(o['inversion_real_mdp'] - o['inversion_presupuestada_mdp'], 1)

    def flujo(et, v, fuente, como):
        return {'tipo': 'flujo', 'et': et, 'mdp': v, 'estado': 'oficial', 'fuente': fuente, 'como': como}

    SUP_INT = ('Supuesto: ese dinero se financió con deuda pública y cuesta lo mismo que la deuda en promedio. '
               'Es estimación propia: el gobierno no etiqueta qué deuda pagó cada obra.')

    def base(et, v, estado, fuente, como):
        return {'tipo': 'intereses', 'et': et, 'base_mdp': v, 'estado': estado, 'fuente': fuente, 'como': como,
                'estimacion_propia': True, 'supuesto': SUP_INT}

    def falta(lim, texto, fuente=None):
        d = {'limitacion': lim, 'texto': texto}
        if fuente:
            d['fuente'] = fuente
        return d

    assert obra['tren-maya']['estado_campos']['inversion_real_mdp'] in ('oficial', 'derivado')
    assert obra['tren-toluca']['estado_campos']['inversion_real_mdp'] in ('oficial', 'derivado')
    assert obra['estela-luz']['estado_campos']['inversion_real_mdp'] == 'oficial'
    naicm = ver['aifa-texcoco']['naicm']['costo']
    tula = obra['refineria-tula']['inversion_real_mdp']

    obras = {
        'tren-maya': {'componentes': [
            flujo('Presupuesto 2026 de Tren Maya, S.A. de C.V.', p['tren_maya'], 'pef26csv',
                  'Suma de sus renglones en el PEF 2026: $30,000.0 mdp de inversión en vía (K019) y $744.1 mdp de operación (E015)'),
            base('Lo pagado por encima de lo autorizado en cartera', sobrecosto('tren-maya'), 'derivado', 'cp',
                 'Ejercido 2020-2025 según la Cuenta Pública ($497,350.2 mdp) menos el monto autorizado en cartera al 4T 2021 ($167,341.6 mdp)')]},
        'tren-toluca': {'componentes': [
            flujo('Presupuesto 2026 del Tren Interurbano (clave 13093110008)', p['interurbano'], 'pef26csv',
                  'Renglones del PEF 2026 con la clave de cartera del proyecto, a cargo de la Agencia Reguladora del Transporte Ferroviario'),
            base('Lo que su costo reconocido creció desde 2019', sobrecosto('tren-toluca'), 'derivado', 'opa',
                 'Costo total que la cartera de Hacienda reconoce al 2T 2026 ($153,694.3 mdp) menos el que registraba al 4T 2019 ($76,346.8 mdp). Es costo reconocido, no todo pagado: la Cuenta Pública registra $65,506.4 mdp pagados con recursos fiscales de 2014 a 2025. El Libro Blanco de la SCT (2018, p. 39) registra que en diciembre de 2013 el proyecto entró a cartera con $34,114.9 mdp')]},
        'aifa-texcoco': {'componentes': [
            flujo('Presupuesto 2026 del AIFA, S.A. de C.V.', p['aifa'], 'pef26csv', 'Sus renglones de operación en el PEF 2026 (E014)'),
            base('Costo de cancelar el aeropuerto de Texcoco', naicm, 'oficial', 'asfnaicm',
                 'La ASF fijó en $113,327.7 mdp el costo de cancelar el NAIM al 31-12-2019 (marzo de 2021)')]},
        'fobaproa': {'componentes': [
            flujo('Ramo 34 en el PEF 2026 (apoyo a ahorradores y deudores de la banca)', p['ramo34'], 'pef26csv',
                  'Todo el Ramo 34 del PEF 2026. No se le suman intereses aparte: el rescate ya es deuda, y lo que el presupuesto paga por ella es este ramo')],
            'contexto': 'Al 31-12-2025 los pasivos netos del IPAB sumaban $1,023,571 mdp, cifra preliminar de Hacienda (anexo de deuda pública del 4T 2025, p. C24). Es lo que sigue debiendo el rescate.',
            'contexto_fuente': 'ipab4t25'},
        'estela-luz': {'componentes': [
            base('Lo que costó de más sobre el contrato original', sobrecosto('estela-luz'), 'derivado', 'asf_estela',
                 'Costo final según la ASF ($1,304.9 mdp) menos el contrato de construcción de 2009 ($393.5 mdp)')]},
        'refineria-tula': {'componentes': [
            base('Lo gastado en una refinería que no se construyó', tula, 'derivado', 'asf_tula14',
                 'Ejercido en estudios ($659.3 mdp) y en el terreno ($468.3 mdp), según la ASF, antes de detener el proyecto')]},
        'farac-carretero': {'componentes': [
            {'tipo': 'flujo', 'et': 'Pago anual de la deuda del rescate, repartido de 2018 a 2033', 'mdp': round(351969.6 / 16, 1),
             'estado': 'derivado', 'fuente': 'asf_farac17', 'estimacion_propia': True,
             'como': 'La ASF estimó en $351,969.6 mdp el capital y los intereses por pagar de 2018 a 2033 (CP 2017, p. 6), entre los 16 años de ese periodo',
             'supuesto': 'Supuesto: el pago se reparte parejo en los 16 años. La ASF no publica el calendario año por año; en 2017 se pagaron $10,368.6 mdp de intereses.'}]},
        'dos-bocas': {'componentes': [
            {'tipo': 'flujo', 'et': 'Lo que Pemex le aportó a la empresa de la refinería en 2024 (último año documentado)', 'mdp': 42696.7,
             'estado': 'oficial', 'fuente': 'tri24', 'estimacion_propia': True,
             'como': 'Aportaciones de Pemex Transformación Industrial a PTI Infraestructura de Desarrollo, S.A. de C.V., la filial que construye la refinería Olmeca: $42,696,652 miles de pesos en 2024 y $34,032,790 miles en 2023 (estados financieros de Pemex TRI 2024, nota 12, p. 47)',
             'supuesto': 'Supuesto: 2026 sigue el ritmo de 2024. Desde el 19-03-2025 Pemex TRI se extinguió y Pemex ya no publica por separado lo que le pone a la refinería.'}],
            'contexto': 'La misma nota (p. 49) da los resultados de PTI Infraestructura en 2024: ventas por $7,116.8 mdp contra un costo de ventas de $7,018.9 mdp y una pérdida neta de $1,473.7 mdp (en 2023 tuvo utilidad de $3,949.5 mdp). Su capital al cierre de 2024, lo que Pemex ha metido en ella, sumaba $363,619.9 mdp. Al 31-12-2024 la refinería estaba «en etapa de pruebas y estabilización» (p. 11).',
            'contexto_fuente': 'tri24',
            'falta': [falta('sin_desglose', 'Los estados de PTI Infraestructura son de toda la filial y vienen condensados: no separan depreciación, intereses ni mantenimiento de la refinería, y no hay estados separados de 2025.')]},
        'megafarmacia': {'componentes': [
            {'tipo': 'flujo', 'et': 'Operación y mantenimiento que Birmex previó al año', 'mdp': round(10806.4 / 32, 1),
             'estado': 'derivado', 'fuente': 'opa', 'estimacion_propia': True,
             'como': 'El registro del CEFEDIS (clave 2312NEF0001) en la cartera de Hacienda, corte 4T 2025, prevé $10,806.4 mdp de operación y mantenimiento en un horizonte de evaluación de 32 años',
             'supuesto': 'Supuesto: el gasto previsto se reparte parejo en los 32 años. Es lo que Birmex planeó, no lo que ha gastado: eso no se publica.'},
            base('Lo que creció su monto de inversión reconocido', round(3948.6 - 3614.6, 1), 'derivado', 'opa',
                 'Monto total de inversión en cartera al 4T 2025 ($3,948.6 mdp) menos el del 4T 2023 ($3,614.6 mdp)')],
            'falta': [
            falta('dictamen', 'El auditor externo de Birmex se abstuvo de opinar sobre sus estados financieros de 2024: la entidad no entregó la balanza de comprobación definitiva ni los auxiliares contables. Sobre el CEFEDIS (la Megafarmacia) escribió que no fue invitado al inventario físico de noviembre de 2024 y que desconoce «como controla la entidad dicho proyecto, en sus registros contables» (dictamen, párrafos III a V, pp. 1 y 2).', 'birmex24'),
            falta('no_localizado', 'El proyecto no aparece en los cortes de seguimiento de la cartera del 4T 2024 ni del 2T 2026, y las recetas surtidas no forman parte de ningún estado financiero publicado.')]},
        'agronitrogenados': {'componentes': [
            base('Lo que Pemex dio por perdido en tres plantas de Agronitrogenados que nunca rehabilitó', 4206.0, 'oficial', 'asf_fert17',
                 'Deterioro por baja de activos ociosos de ProAgro (antes Agronitrogenados) en los estados financieros 2017 de Pemex Fertilizantes: $4,206.0 mdp según la ASF (CP 2017, auditoría 492-DE, pp. 37 y 40; en la p. 44 aparece como $4,206.7 mdp). Son las plantas de nitrato de amonio, ácido nítrico y UAN-32, que al comprarse en 2013 llevaban 14 años sin operar')],
            'contexto': 'La misma auditoría documenta en pesos: la compra de los activos por $5,427.2 mdp (20-12-2013, p. 4); una inversión total aprobada de $14,998.9 mdp entre compra y rehabilitación (agosto de 2015, p. 5); $8,271.1 mdp erogados de septiembre de 2014 a diciembre de 2017 en rehabilitar las dos plantas de urea, que a fines de 2017 seguían sin producir (pp. 42-44), y una deuda de $7,696.8 mdp con Nafin que Pemex recibió con la empresa (p. 5). Esas cifras no se suman aquí: solo cuenta lo que Pemex ya reconoció como perdido.',
            'contexto_fuente': 'asf_fert17',
            'falta': [falta('no_localizado', 'No localizamos resultados separados de ProAgro posteriores a 2017: no sabemos si las plantas de urea producen hoy ni cuánto cuesta mantenerlas. Por eso no hay flujo anual, solo el costo de lo ya perdido.')]},
        'fertinal': {'componentes': [
            base('Lo que Pemex dio por perdido del precio pagado por Fertinal', 4007.0, 'oficial', 'asf_fert17',
                 'Deterioro del crédito mercantil de Fertinal: $4,007.0 mdp (ASF, CP 2017, p. 37). Es la parte de lo pagado en 2016 por encima del valor de sus activos que Pemex reconoció como perdida')],
            'contexto': 'La ASF (CP 2016) documenta que en su primer año con Pemex, 2016, Fertinal registró una pérdida integral de 565.7 millones de dólares, $11,690.6 mdp (p. 31), y dictaminó que la compra «no es un negocio rentable» (p. 38). En 2017 sus plantas trabajaron entre el 26.0 % y el 84.4 % de su capacidad (CP 2017, p. 37). Entre 2015 y 2017 el patrimonio de Pemex Fertilizantes, que incluye a Fertinal y a ProAgro, perdió $21,174.0 mdp (p. 37). Esas cifras no se suman aquí: la pérdida de 2016 no es la de hoy y el patrimonio es de toda la empresa.',
            'contexto_fuente': 'asf_fert16',
            'falta': [falta('no_localizado', 'No localizamos estados financieros de Fertinal posteriores a 2017: no sabemos si hoy gana o pierde. Por eso no hay flujo anual, solo el costo de lo ya perdido.')]},
        'enciclomedia': {'falta': [
            falta('no_localizado', 'Hacienda autorizó $21,398.3 mdp para 2005-2010, pero no encontramos un documento oficial que sume lo que de verdad se pagó. Sin ese total no hay sobrecosto que medir.')]},
        'bunker-garcia-luna': {'falta': [
            falta('no_localizado', 'No encontramos informe de la ASF ni registro de cartera que diga cuánto costó el edificio ni qué uso tiene hoy.')]},
    }
    return {
        'nota': 'Interpretación de Auditavisión para la «Simulación en vivo» del módulo 2. La escribe herramientas/integrar_costo_vivo_megaobras.py; el motor calcula los intereses con la tasa.',
        'tasa': {
            'pct': tasa,
            'costo_financiero_mdp': COSTO_FINANCIERO_2026,
            'shrfsp_mdp': SHRFSP_2026,
            'estado': 'derivado',
            'como': 'Costo financiero de la deuda en el PEF 2026 ($1,572,073.3 mdp, Anexo 8) entre el saldo histórico de los requerimientos financieros del sector público estimado para el cierre de 2026 ($20,062,321.6 mdp, Criterios 2027, p. 67).',
        },
        'fuentes': {
            'pef26csv': {
                'doc': 'SHCP, Presupuesto de Egresos de la Federación 2026, datos abiertos (PEF_2026.csv), columna MONTO_PEF_2026',
                'url': 'https://www.transparenciapresupuestaria.gob.mx/work/models/PTP/DatosAbiertos/Bases_de_datos_presupuesto/CSV/PEF_2026.csv',
                'sha256': CSV_SHA,
            },
            'ipab4t25': {
                'doc': 'SHCP, Informes sobre la situación económica, las finanzas públicas y la deuda pública, cuarto trimestre de 2025, anexo de deuda pública, p. C24 (pasivos del IPAB)',
                'url': 'https://www.finanzaspublicas.hacienda.gob.mx/work/models/Finanzas_Publicas/docs/congreso/infotrim/2025/ivt/05adp/itandpdc_202504.pdf',
                'sha256': '51a632d59c855ae50c994eafdc40a645fa91237c36faad27108fefd07e39e732',
            },
            'tri24': {
                'doc': 'Pemex Transformación Industrial, estados financieros separados dictaminados al 31 de diciembre de 2024, Cuenta Pública 2024, tomo VIII (notas 1 y 12)',
                'url': 'https://www.cuentapublica.hacienda.gob.mx/work/models/CP/2024/tomo/VIII/52T9M.05.DAR.pdf',
                'sha256': 'b326741b89e7ad809fe17df118e400a20e70d1e79f49ea7b9350d1218a38a90d',
            },
            'birmex24': {
                'doc': 'Laboratorios de Biológicos y Reactivos de México, S.A. de C.V., dictamen del auditor externo sobre los estados financieros 2024 (denegación de opinión), Cuenta Pública 2024, tomo VII',
                'url': 'https://www.cuentapublica.hacienda.gob.mx/work/models/CP/2024/tomo/VII/12NEF.05.DAR.pdf',
                'sha256': 'bb3ec2a2fd5c9fdc385e0b4ffe173dba33d069b0e265922c6d77df68cb0dc617',
            },
            'asf_fert16': {
                'doc': 'ASF, Cuenta Pública 2016, auditoría 468-DE, Pemex Fertilizantes: Gestión Financiera (compra de Grupo Fertinal)',
                'url': 'https://www.asf.gob.mx/Trans/Informes/IR2016ii/Documentos/Auditorias/2016_0468_a.pdf',
                'sha256': '7028e6acd9ba71064179ce42229b6ad06dfcb36b349c2370d0626608bb340af3',
            },
            'asf_fert17': {
                'doc': 'ASF, Informe Individual de la Cuenta Pública 2017, auditoría de desempeño 492-DE «Producción, Distribución y Comercialización de Amoniaco, Fertilizantes y sus Derivados», Pemex Fertilizantes',
                'url': 'https://www.asf.gob.mx/Trans/Informes/IR2017c/Documentos/Auditorias/2017_0492_a.pdf',
                'sha256': 'd1f61d814ce1e5dd1f2c4d2e291cddf7ba0b651e75e252a8fe163d51ce1527f5',
            },
            'cgpe27': {
                'doc': 'SHCP, Criterios Generales de Política Económica para 2027, p. 67, cuadro «Estimación de las finanzas públicas, 2026-2027»',
                'url': 'https://gaceta.diputados.gob.mx/PDF/66/2026/sep/20260908-C.pdf',
                'sha256': '5978f0631d2c88165b54bfce9c3fed2b8cca45eb44b3f267f3025c88f3c6d66a',
            },
        },
        'limitaciones': {
            'no_localizado': 'No localizado: nuestra búsqueda no encontró el documento.',
            'sin_desglose': 'Sin desglose por proyecto: el documento trae datos de toda la empresa o en otra unidad.',
            'acceso_fallido': 'Acceso fallido: el enlace oficial no permitió descargarlo.',
            'dictamen': 'Salvedad documentada: el propio dictamen oficial señala que la información no es suficiente.',
        },
        'obras': obras,
    }


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    p = pef(sys.argv[1])
    raw = open(DB, 'rb').read().decode('utf-8')
    a, b = bloque_json(raw, 'simulador_megaobras')
    datos = construir(p, json.loads(raw[a:b]))
    nl = '\r\n'
    txt = json.dumps(datos, ensure_ascii=False, indent=2)
    txt = '\n  '.join(txt.split('\n')).replace('\n', nl)
    if '"costo_vivo_megaobras": {' in raw:
        a, b = bloque_json(raw, 'costo_vivo_megaobras')
        raw = raw[:a] + txt + raw[b:]
    else:
        fin = raw.rindex(nl + '};')
        raw = raw[:fin] + ',' + nl + '  "costo_vivo_megaobras": ' + txt + raw[fin:]
    open(DB, 'wb').write(raw.encode('utf-8'))
    print(json.dumps({'pef': p, 'tasa': datos['tasa']['pct']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
