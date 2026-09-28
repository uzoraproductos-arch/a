# -*- coding: utf-8 -*-
"""Olmeca, CEFEDIS y el «Búnker» con los documentos que sí existen (28-09-2026).

Refinería Olmeca (Dos Bocas):
- ASF, CP 2024, auditoría 247 «Ingresos y egresos del proyecto de la
  Refinería Olmeca en Dos Bocas»: Pemex aportó $42,696,652.3 miles al capital
  de PTI Infraestructura de Desarrollo (p. 1 y 7); la filial erogó
  $41,998,275.1 miles sin IVA por 192 contratos (pp. 1 y 11), de los que
  $15,609.0 miles fueron servicios administrativos (p. 12); al 31-12-2024
  registraba $357,887,290.0 miles de «obra en proceso» que «corresponde a lo
  registrado para construcción de la RODB» (p. 8); recibió $14,463,214.0 miles
  de devoluciones de IVA (p. 13). La refinería se arrienda a Pemex (p. 8).
- Pemex, estados financieros consolidados 2025 (Cuenta Pública 2025): PTI ID
  se consolida sin estados propios (p. 35); primer tren de crudo en operación
  en febrero de 2025 y segundo en mayo (p. 54 de las notas presupuestarias);
  263 mil barriles diarios en diciembre y pico de 313 mil (p. 55).
- Segundo Informe de Gobierno 2026, p. 378: de septiembre de 2025 a junio de
  2026 procesó en promedio 188 mil barriles diarios; 263 mil en diciembre de
  2025, 77 % de su capacidad.
La inversión real pasa a ser la obra en proceso de la ASF («oficial»); el
presupuesto original sigue sin documento.

CEFEDIS (Megafarmacia): estructura de costos del registro 2312NEF0001 en la
cartera de Hacienda, corte 4T 2025 (huella en integrar_cefedis.py), y el
dictamen de Birmex 2025 (20-03-2026): el auditor externo volvió a abstenerse
de opinar (pp. 3 y 5 del PDF, escaneo). Inversión física de Birmex ejercida
en 2025: $10,083.8 miles (Segundo Informe, anexo, p. 655 del PDF).

Búnker: la ASF (CP 2008, auditoría 957, Plataforma México, pp. 88-90) estimó
$432,678.8 miles para «construcción de instalaciones y equipamiento» de
Plataforma México de 2007 a 2009 y $14,277,786.3 miles para el sistema
completo de 2007 a 2012; en 2008 se ejercieron $1,188,506.4 miles. En la CP
2011 (auditoría 16) la Coordinación General de Plataforma México ejerció
$1,898,114.6 miles, con $14,116.3 miles de recuperaciones probables y
dictamen con salvedad (pp. 1 y 23). El costo del edificio sigue pendiente.

Uso:  python3 herramientas/integrar_olmeca_cefedis_bunker.py
Solo toca assets/auditor/js/audit-database.js. Idempotente.
"""
import hashlib
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'audit-database.js')
INV = os.path.join(RAIZ, 'investigaciones')
ASF = 'https://www.asf.gob.mx/Trans/Informes/'
CP = 'https://www.cuentapublica.hacienda.gob.mx/work/models/CP/2025/tomo/'

FUENTES = {
    'asf_olmeca24': ('costo-vivo/ASF_CP2024_0247_RefineriaOlmeca.pdf',
                     '0b517333d735160e535f43df7b25eba6a8b6211a1eeeefcc4756f484947319f3',
                     'ASF, Cuenta Pública 2024, auditoría 247, Pemex: Ingresos y egresos del proyecto de la Refinería Olmeca en Dos Bocas',
                     ASF + 'IR2024c/Documentos/Auditorias/2024_0247_a.pdf'),
    'pemex_ef25': ('costo-vivo/PEMEX_EstadosFinancierosConsolidados2025.pdf',
                   '0a6fe9e89e0d94714ea441134ac3c1ee7446c4c4713baaf9e62d8ebd554b86b2',
                   'Petróleos Mexicanos, estados financieros consolidados 2025 y notas presupuestarias (Cuenta Pública 2025, tomo VIII)',
                   CP + 'VIII/52TYY.05.DAR.pdf'),
    'informe26': ('entregas/Presidencia_SegundoInformeGobierno2026.pdf',
                  'cc95e5ade7cb306b734e9dc1e61e1defcba14c444e5705de24be6ca6e115fa9d',
                  'Presidencia de la República, Segundo Informe de Gobierno 2025-2026',
                  'https://www.segundoinformedegobierno.gob.mx/gmx_media/2-ig-informe-consolidado-final_01_09_2026'),
    'birmex25': ('entregas/BIRMEX_EstadosFinancieros2025.pdf',
                 '8e6ac20ea6c1d68bec52344cfdfef49255860048822d824d0b4ef22d9c689513',
                 'Birmex, informe del auditor independiente sobre los estados financieros 2025 (Cuenta Pública 2025, tomo VII)',
                 CP + 'VII/12NEF.05.DAR.pdf'),
    'asf_pm08': ('asf-historico/IR2008_T9V2.pdf',
                 '25b0b1cd4958ec6e5a12753c8730e59fa65e688380da3233749981f1e27ef509',
                 'ASF, Informe del Resultado CP 2008, tomo IX, vol. 2, auditoría de desempeño 957: Plataforma México',
                 ASF + 'IR2008i/Tomos/T9V2.pdf'),
    'asf_pm11': ('asf-historico/2011_0016_a.pdf',
                 'dc1556b2979510721539d0c11111494e6afb588d6447200613b0c29ec95fdf99',
                 'ASF, Cuenta Pública 2011, auditoría 16, SSP: Plataforma México. Servicios de telecomunicaciones y bienes informáticos',
                 ASF + 'IR2011i/Grupos/Gobierno/2011_0016_a.pdf'),
}

# Miles de pesos, tal como los publican los documentos.
OLMECA = {
    'aportaciones': 42696652.3, 'erogaciones': 41998275.1, 'serv_admin': 15609.0,
    'obra_proceso': 357887290.0, 'iva_devuelto': 14463214.0, 'contratos': 192,
}
CEFEDIS = {'inversion': 3948638498, 'om': 10806429459, 'otros': 992816086, 'total': 17635763330}
BIRMEX_INV25 = 10083.8
PM08 = {'instalaciones': 432678.8, 'sistema': 14277786.3, 'ejercido08': 1188506.4}
PM11 = {'ejercido': 1898114.6, 'recuperaciones': 14116.3}


def mdp(miles):
    return round(miles / 1000, 1)


def tx(n):
    return '$' + format(n, ',.1f') + ' mdp'


def main():
    for arch, sha, _, _ in FUENTES.values():
        h = hashlib.sha256(open(os.path.join(INV, arch), 'rb').read()).hexdigest()
        if h != sha:
            sys.exit('La huella de %s no coincide: %s' % (arch, h))
    obra = mdp(OLMECA['obra_proceso'])
    assert obra == 357887.3
    ceo = {k: round(v / 1e6, 1) for k, v in CEFEDIS.items()}
    sin_detalle = round(ceo['total'] - ceo['inversion'] - ceo['om'] - ceo['otros'], 1)
    assert sin_detalle == 1888.0

    raw = open(DB, 'rb').read().decode('utf-8')
    i = raw.index('"simulador_megaobras": {')
    j = raw.index('{', i)
    prof = 0
    for k in range(j, len(raw)):
        if raw[k] == '{':
            prof += 1
        elif raw[k] == '}':
            prof -= 1
            if prof == 0:
                break
    sim = json.loads(raw[j:k + 1])
    ver = sim['verificacion']
    for clave, (_, sha, doc, url) in FUENTES.items():
        ver['fuentes'][clave] = {'doc': doc, 'url': url, 'sha256': sha}
    obras = {o['id']: o for o in sim['obras']}
    ctx = sim['operacion_oficial'].setdefault('contexto_entidad', {})

    # 1. Olmeca: la inversión real con la obra en proceso que documenta la ASF.
    db = obras['dos-bocas']
    db['inversion_real_mdp'] = obra
    db['sobrecosto_pct'] = round((obra / db['inversion_presupuestada_mdp'] - 1) * 100, 1)
    db['estado_campos'] = {'inversion_presupuestada_mdp': 'pendiente', 'inversion_real_mdp': 'oficial', 'sobrecosto_pct': 'pendiente'}
    v = ver['obras']['dos-bocas']
    v['campos'] = dict(db['estado_campos'])
    v['definiciones'] = {
        'inversion_presupuestada_mdp': 'Pendiente: los $160,000 mdp que trae la ficha no tienen documento en mano. La refinería no está en la cartera de Hacienda y su presupuesto original no aparece en la Cuenta Pública.',
        'inversion_real_mdp': 'Obra en proceso que PTI Infraestructura de Desarrollo, la filial de Pemex que construye la refinería, registró al 31-12-2024: $357,887,290.0 miles de pesos, que según la ASF «corresponde a lo registrado para construcción» de la refinería, en 6 paquetes y 17 plantas (CP 2024, auditoría 247, p. 8). Es lo acumulado en libros, sin IVA, hasta ese día: no incluye lo gastado desde 2025.',
        'sobrecosto_pct': 'No se puede afirmar: compara la obra en proceso documentada contra un presupuesto original que no tiene documento.',
    }
    v['asfHist'] = [
        {'dato': 'Obra en proceso de la refinería al 31-12-2024', 'valor': tx(obra), 'estado': 'oficial', 'pagina': '8 (CP 2024, aud. 247)'},
        {'dato': 'Aportaciones de Pemex al capital de la filial en 2024', 'valor': tx(mdp(OLMECA['aportaciones'])), 'estado': 'oficial', 'pagina': '1 y 7 (CP 2024, aud. 247)'},
        {'dato': 'Erogaciones de la filial en 2024, sin IVA, por %d contratos' % OLMECA['contratos'], 'valor': tx(mdp(OLMECA['erogaciones'])), 'estado': 'oficial', 'pagina': '1 y 11 (CP 2024, aud. 247)'},
        {'dato': 'Devoluciones de IVA que recibió la filial en 2024', 'valor': tx(mdp(OLMECA['iva_devuelto'])), 'estado': 'oficial', 'pagina': '13 (CP 2024, aud. 247)'},
        {'dato': 'Crudo procesado, septiembre de 2025 a junio de 2026 (promedio)', 'valor': '188 mil barriles diarios', 'estado': 'oficial', 'pagina': '378 (Segundo Informe)'},
        {'dato': 'Mejor mes: diciembre de 2025', 'valor': '263 mil barriles diarios, 77 % de su capacidad', 'estado': 'oficial', 'pagina': '378 (Segundo Informe) y 55 (Pemex, CP 2025)'},
    ]
    v['hallazgo'] = ('En la Cuenta Pública 2024 la ASF revisó lo que entró y salió de la filial de la refinería: Pemex le aportó $42,696.7 mdp y ella erogó $41,998.3 mdp sin IVA '
                     'por 192 contratos. Pagó 122 contratos con atrasos de 1 a 454 días y firmó tres contratos para reconocer trabajos hechos antes de formalizarlos, '
                     'sin reglas para ello. Promovió 3 recomendaciones, sin montos por aclarar ni recuperaciones (pp. 7-14).')
    v['fuentes'] = ['opa', 'asf24', 'asf_olmeca24', 'pemex_ef25', 'informe26']
    ctx['dos-bocas'] = {
        'texto': ('Lo más cercano en un documento oficial: en 2024 Pemex aportó $42,696.7 mdp al capital de PTI Infraestructura de Desarrollo, la filial que construye la refinería, '
                  'y la filial pagó $41,998.3 mdp sin IVA por 192 contratos (ASF, CP 2024, auditoría 247). Son pagos de construcción y arranque, no de operación. '
                  'La refinería se arrienda a Pemex, que la opera: el primer tren de crudo entró en operación en febrero de 2025 y el segundo en mayo (Pemex, Cuenta Pública 2025). '
                  'De septiembre de 2025 a junio de 2026 procesó en promedio 188 mil barriles diarios; su mejor mes fue diciembre de 2025, con 263 mil, el 77 % de su capacidad '
                  '(Segundo Informe de Gobierno 2026, p. 378). Desde 2025 Pemex consolida a la filial sin publicar sus estados por separado, así que lo que cuesta operar la refinería '
                  'y lo que deja siguen sin documento.'),
        'desglose_titulo': 'Lo que pagó en 2024 la filial que construye la refinería (ASF)',
        'desglose_estado': 'oficial',
        'desglose': [
            {'rubro': 'Pagos a proveedores y contratistas, sin IVA (el total de la ASF menos los servicios administrativos)', 'mdp': mdp(OLMECA['erogaciones'] - OLMECA['serv_admin']), 'icono': '🏗️'},
            {'rubro': 'Servicios administrativos: contabilidad, impuestos y tesorería', 'mdp': mdp(OLMECA['serv_admin']), 'icono': '🧾'},
        ],
    }

    # 2. CEFEDIS: el costo que Birmex registró ante Hacienda, renglón por renglón.
    mf = ctx['megafarmacia']
    mf['nota'] = ('Es el resultado de toda la empresa, que además de la Megafarmacia compra, produce y distribuye vacunas y medicamentos. La Cuenta Pública no separa lo de la Megafarmacia, '
                  'así que su pérdida sigue pendiente y esta cifra no entra en la suma. Para 2025 el auditor externo de Birmex volvió a abstenerse de opinar (dictamen del 20-03-2026): '
                  'sin balanzas mensuales confiables, no pudo validar cuentas por cobrar, inventarios, almacenes ni activo fijo.')
    mf['extra'] = ('En la cartera de Hacienda (corte 4T 2025) Birmex registró un costo total del proyecto de %s: %s de inversión, %s de operación y mantenimiento en 32 años y %s de otros costos; '
                   'la cartera no detalla los %s restantes (resta de Auditavisión). En 2025 no ejerció nada bajo esa clave, y toda la inversión física de Birmex ese año fue de %s '
                   '(Segundo Informe de Gobierno 2026, anexo estadístico).') % (
        tx(ceo['total']), tx(ceo['inversion']), tx(ceo['om']), tx(ceo['otros']), tx(sin_detalle), tx(mdp(BIRMEX_INV25)))
    mf['desglose_titulo'] = 'Costo del proyecto que Birmex registró ante Hacienda (cartera, corte 4T 2025)'
    mf['desglose_estado'] = 'oficial'
    mf['desglose'] = [
        {'rubro': 'Inversión', 'mdp': ceo['inversion'], 'icono': '🏗️'},
        {'rubro': 'Operación y mantenimiento previstos en 32 años', 'mdp': ceo['om'], 'icono': '🔧'},
        {'rubro': 'Otros costos', 'mdp': ceo['otros'], 'icono': '📄'},
        {'rubro': 'Costo total del proyecto', 'mdp': ceo['total'], 'icono': '🧾'},
    ]
    vm = ver['obras']['megafarmacia']
    vm['asfHist'] = [a for a in vm['asfHist'] if not a['dato'].startswith(('Otros costos', 'Costo total del proyecto', 'Ejercido en 2025'))]
    vm['asfHist'] += [
        {'dato': 'Otros costos previstos', 'valor': tx(ceo['otros']), 'estado': 'oficial', 'pagina': 'cartera, corte 4T 2025'},
        {'dato': 'Costo total del proyecto registrado', 'valor': tx(ceo['total']), 'estado': 'oficial', 'pagina': 'cartera, corte 4T 2025'},
        {'dato': 'Ejercido en 2025 bajo la clave', 'valor': '$0.0 mdp', 'estado': 'oficial', 'pagina': 'cartera, corte 4T 2025'},
    ]
    if 'birmex25' not in vm['fuentes']:
        vm['fuentes'].append('birmex25')

    # 3. Búnker: lo más cercano que documenta la ASF; el edificio sigue pendiente.
    vb = ver['obras']['bunker-garcia-luna']
    vb['definiciones']['inversion_real_mdp'] = (
        'Pendiente: los $3,346 mdp que trae la ficha no tienen documento. Del contrato de obra civil se habían erogado $206,027.9 miles de pesos más IVA en agosto de 2010 '
        '(ASF, CP 2009, p. 2). Lo más cercano a un costo total: la ASF estimó $432,678.8 miles para construir y equipar las instalaciones de Plataforma México de 2007 a 2009 '
        '(CP 2008, auditoría 957, pp. 89-90), con el presupuesto aprobado de 2009 y no con lo ejercido, y sin decir qué parte es este edificio.')
    vb['asfHist'] = [a for a in vb['asfHist'] if 'aud. 957' not in a['pagina'] and 'aud. 16)' not in a['pagina']]
    vb['asfHist'] += [
        {'dato': 'Construcción de instalaciones y equipamiento de Plataforma México, 2007-2009 (estimación de la ASF)', 'valor': tx(mdp(PM08['instalaciones'])), 'estado': 'oficial', 'pagina': '89-90 (CP 2008, aud. 957)'},
        {'dato': 'Costo del sistema Plataforma México, 2007-2012 (estimación de la ASF)', 'valor': tx(mdp(PM08['sistema'])), 'estado': 'oficial', 'pagina': '89 (CP 2008, aud. 957)'},
        {'dato': 'Ejercido en acciones de Plataforma México en 2008 (federal, estados y municipios)', 'valor': tx(mdp(PM08['ejercido08'])), 'estado': 'oficial', 'pagina': '88 (CP 2008, aud. 957)'},
        {'dato': 'Ejercido por la Coordinación General de Plataforma México en 2011', 'valor': tx(mdp(PM11['ejercido'])), 'estado': 'oficial', 'pagina': '1 (CP 2011, aud. 16)'},
        {'dato': 'Recuperaciones probables en telecomunicaciones y equipo informático, 2011', 'valor': tx(mdp(PM11['recuperaciones'])), 'estado': 'oficial', 'pagina': '23 (CP 2011, aud. 16)'},
    ]
    for f in ('asf_pm08', 'asf_pm11'):
        if f not in vb['fuentes']:
            vb['fuentes'].append(f)

    t = sim['totales_consolidados']
    lista = sim['obras']
    t['inversion_total_mdp'] = round(sum(o['inversion_real_mdp'] for o in lista), 1)
    t['inversion_presupuestada_total_mdp'] = round(sum(o['inversion_presupuestada_mdp'] for o in lista), 1)
    t['sobrecosto_conjunto_pct'] = round((t['inversion_total_mdp'] / t['inversion_presupuestada_total_mdp'] - 1) * 100, 1)

    nuevo = json.dumps(sim, ensure_ascii=False, indent=2)
    nuevo = nuevo[:-1] + raw[raw.rfind('\n', 0, k) + 1:k] + '}'
    raw = raw[:j] + nuevo.replace('\n', '\r\n') + raw[k + 1:]

    # 4. Costo en vivo: textos de lo que falta, con lo nuevo.
    a = raw.index('"costo_vivo_megaobras"')
    c = raw.index('{', a)
    prof = 0
    for e in range(c, len(raw)):
        if raw[e] == '{':
            prof += 1
        elif raw[e] == '}':
            prof -= 1
            if prof == 0:
                break
    cv = json.loads(raw[c:e + 1])
    for clave, (_, sha, doc, url) in FUENTES.items():
        cv['fuentes'][clave] = {'doc': doc, 'url': url, 'sha256': sha}
    d = cv['obras']['dos-bocas']
    d['contexto'] = d['contexto'].replace('$7,018.9 mdp', '$7,019.0 mdp')
    d['falta'] = [{'limitacion': 'sin_desglose', 'texto': (
        'Los estados de PTI Infraestructura son de toda la filial y vienen condensados: no separan depreciación, intereses ni mantenimiento de la refinería, y la filial también lleva '
        'la reconfiguración de Salina Cruz (ASF, CP 2024, auditoría 247, pp. 8-9). Desde 2025 Pemex la consolida sin estados propios (estados financieros consolidados 2025, p. 35).'),
        'fuente': 'pemex_ef25'}]
    m = cv['obras']['megafarmacia']['falta']
    m[:] = [x for x in m if x.get('fuente') != 'birmex25']
    m.insert(1, {'limitacion': 'dictamen', 'texto': (
        'Tampoco hay opinión sobre 2025: el auditor externo volvió a abstenerse (dictamen del 20-03-2026) porque los saldos iniciales no tenían soporte y no hubo balanzas mensuales '
        'confiables; no pudo validar inventarios, almacenes ni activo fijo, ni saber si se solventó lo observado en 2024 (pp. 3 y 5 del PDF).'), 'fuente': 'birmex25'})
    cv['obras']['bunker-garcia-luna']['falta'] = [{'limitacion': 'no_localizado', 'texto': (
        'No encontramos el costo total del edificio ni de su equipo. La ASF revisó el contrato de obra civil (CP 2009) y estimó $432.7 mdp para construir y equipar las '
        'instalaciones de todo Plataforma México de 2007 a 2009 (CP 2008, auditoría 957, pp. 89-90), sin separar este inmueble. Tampoco sabemos cuánto del programa se gasta en él.'),
        'fuente': 'asf_pm08'}]
    nuevo = json.dumps(cv, ensure_ascii=False, indent=2).replace('\n', '\n  ')
    raw = raw[:c] + nuevo.replace('\r\n', '\n').replace('\n', '\r\n') + raw[e + 1:]

    open(DB, 'wb').write(raw.encode('utf-8'))
    print(json.dumps({'dos-bocas': [db['inversion_presupuestada_mdp'], obra, db['sobrecosto_pct']],
                      'cefedis': ceo, 'sin_detalle': sin_detalle,
                      'totales': {x: t[x] for x in ('inversion_total_mdp', 'inversion_presupuestada_total_mdp', 'sobrecosto_conjunto_pct')}}, ensure_ascii=False))


if __name__ == '__main__':
    main()
