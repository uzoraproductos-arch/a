# -*- coding: utf-8 -*-
"""Población, padrón y huachicol en aduanas con los originales de la entrega
del 28-09-2026 (investigaciones/entregas/).

- Población: CONAPO, proyecciones a mitad de 2026. La suma de las 32
  entidades, todas las edades y ambos sexos, es 134,407,258 personas
  (CONAPO_Poblacion2026_derivada.csv, reproducible con derivar_poblacion.py
  sobre el original 00_Pob_Mitad_1950_2070.csv). Queda como «derivado».
- Padrón: SAT, datos abiertos del padrón por situación del RFC. Último
  corte publicado en el archivo: abril de 2026, 88,085,311 contribuyentes
  activos. Sustituye los 63.2 millones que no tenían fuente. «Oficial».
- Huachicol: Segundo Informe de Gobierno (1-09-2026), cotejado en el PDF.
  Los 3,109 son casos de clasificación arancelaria incorrecta (p. 46
  impresa, 70 del PDF), no decomisos; los $4,600 mdp son recaudación
  asociada a 109.4 millones de litros no declarados (p. 260 impresa, 284
  del PDF), no evasión. «Oficial».

Uso:  python3 herramientas/integrar_poblacion_padron_anam.py
Solo toca assets/auditor/js/audit-database.js. Idempotente.
"""
import csv
import hashlib
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'audit-database.js')
ENT = os.path.join(RAIZ, 'investigaciones', 'entregas')
HUELLAS = {
    'CONAPO_Poblacion2026_derivada.csv': '23700b367c585f6791ba6d47e7dc140cf3623593831a58d73321d8517846a36a',
    'SAT_PadronSituacionRFC.csv': '062847fd0a575b02411487438018e36ce8bd3927789760954a1426938589a6a5',
    'SAT_PadronPorTipoContribuyente.csv': '5be8c25ace814cb9af43cfba0ebbe303b613dfecbd0f5ff04575e18c33fc7e5a',
    'Presidencia_SegundoInformeGobierno2026.pdf': 'cc95e5ade7cb306b734e9dc1e61e1defcba14c444e5705de24be6ca6e115fa9d',
}
CONAPO_URL = 'https://repodatos.atdt.gob.mx/CONAPO/proyecciones/00_Pob_Mitad_1950_2070.csv'
CONAPO_SHA = '89db6adc7930965fb5b5c01ad3a98765ed90afa6a151c2cfb913acc2b9e0cac6'
SAT_URL = 'https://repodatos.atdt.gob.mx/api_update/sat/padron/porsitrfc21.csv'
IG2_URL = 'https://www.segundoinformedegobierno.gob.mx/gmx_media/2-ig-informe-consolidado-final_01_09_2026'


def ruta(nombre):
    r = os.path.join(ENT, nombre)
    h = hashlib.sha256(open(r, 'rb').read()).hexdigest()
    if h != HUELLAS[nombre]:
        sys.exit('La huella de %s no coincide: %s' % (nombre, h))
    return r


def leer_csv(nombre):
    return list(csv.DictReader(open(ruta(nombre), encoding='utf-8-sig', newline='')))


def bloque(raw, clave, desde=0):
    i = raw.index('"' + clave + '": {', desde)
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


def volcar(raw, a, b, obj):
    """Sustituye raw[a:b] por obj conservando sangría y escapes del bloque."""
    viejo = raw[a:b]
    nl = '\r\n'
    lineas = viejo.split(nl)
    sang = len(lineas[-1]) - len(lineas[-1].lstrip(' '))
    asc = '\\u00' in viejo
    txt = json.dumps(obj, ensure_ascii=asc, indent=2)
    txt = ('\n' + ' ' * sang).join(txt.split('\n')).replace('\n', nl)
    return raw[:a] + txt + raw[b:]


def main():
    pob = leer_csv('CONAPO_Poblacion2026_derivada.csv')
    nac = pob[0]
    assert nac['CVE_GEO'] == '00' and len(pob) == 33
    total = int(nac['POBLACION'])
    assert total == sum(int(x['POBLACION']) for x in pob[1:]) == 134407258

    sit = leer_csv('SAT_PadronSituacionRFC.csv')
    ult = sit[-1]
    assert (ult['ejercicio'], ult['mes']) == ('2026', 'Abril')
    activos = int(float(ult['activos']))
    tipo = leer_csv('SAT_PadronPorTipoContribuyente.csv')[-1]
    assert (tipo['ejercicio'], tipo['mes']) == ('2026', 'Abril') and int(float(tipo['total'])) == activos == 88085311
    asal = int(float(tipo['asalariados_pf']))
    ruta('Presidencia_SegundoInformeGobierno2026.pdf')

    raw = open(DB, 'rb').read().decode('utf-8')

    # 1. Parámetros de la calculadora cívica.
    c0, _ = bloque(raw, 'calculadora_civica')
    a, b = bloque(raw, 'poblacion', c0)
    raw = volcar(raw, a, b, {
        'millones': round(total / 1e6, 1),
        'personas': total,
        'fuente': 'CONAPO · Proyecciones de la Población de México y de las Entidades Federativas 2020-2070, población a mitad de 2026',
        'url': CONAPO_URL,
        'sha256': CONAPO_SHA,
        'estado': 'derivado',
        'como': 'Suma de las 32 entidades, las 110 edades y ambos sexos del año 2026 en el archivo de datos abiertos del CONAPO: %s personas. El archivo no trae una fila nacional; por eso la cifra es derivada.' % format(total, ','),
    })
    a, b = bloque(raw, 'padron', c0)
    raw = volcar(raw, a, b, {
        'millones': round(activos / 1e6, 1),
        'personas': activos,
        'corte': 'abril de 2026',
        'fuente': 'SAT · Padrón de contribuyentes por situación del RFC, datos abiertos, corte de abril de 2026',
        'url': SAT_URL,
        'sha256': HUELLAS['SAT_PadronSituacionRFC.csv'],
        'estado': 'oficial',
        'como': '%s contribuyentes con RFC activo en abril de 2026, el último mes publicado en el archivo. %s son asalariados: su impuesto lo retiene el patrón. Es el número de inscritos con RFC activo, no el de quienes pagaron impuestos ese mes. Se usa para repartir entre quienes tienen obligaciones con el SAT, no entre todos los habitantes.' % (format(activos, ','), format(asal, ',')),
    })

    # 2. Catálogo macro: el mismo padrón.
    viejo = '"padronContribuyentes": 63.2,'
    if viejo in raw:
        raw = raw.replace(viejo, '"padronContribuyentes": %s,' % round(activos / 1e6, 1), 1)
    assert '"padronContribuyentes": 88.1,' in raw

    # 3. Huachicol: ANAM y aduanas, cotejado en el Segundo Informe.
    h0, h1 = bloque(raw, 'huachicol_fiscal')
    H = json.loads(raw[h0:h1])
    H['fuentes']['informe2'] = {
        'doc': 'Presidencia de la República, Segundo Informe de Gobierno 2025-2026, informe consolidado (1-09-2026)',
        'url': IG2_URL,
        'sha256': HUELLAS['Presidencia_SegundoInformeGobierno2026.pdf'],
    }
    H['anam'] = {
        'estado': 'oficial',
        'fuente': 'informe2',
        'periodo': '1 de septiembre de 2025 al 30 de junio de 2026',
        'casos': 3109,
        'casos_texto': 'En colaboración con el SAT, la Agencia Nacional de Aduanas detectó 3,109 casos de clasificación arancelaria incorrecta en productos petrolíferos e hidrocarburos, «propiciando su regularización». No son decomisos: es mercancía declarada con una fracción que no le corresponde.',
        'casos_pagina': '46 (70 del PDF)',
        'litros_millones': 109.4,
        'recaudacion_mdp': 4600,
        'sellos_cancelados': 3434,
        'denuncias': 118,
        'pagina': '260 (284 del PDF)',
        'texto': 'Con sistemas de revisión no intrusiva en las 50 aduanas se detectaron 109.4 millones de litros de hidrocarburos no declarados, con una recaudación asociada de $4,600 mdp de IVA e IEPS. Aparte, herramientas de trazabilidad permitieron a «las autoridades competentes» cancelar 3,434 sellos digitales para facturar y presentar 118 denuncias penales.',
        'limites': 'Son diez meses, no un año. Los $4,600 mdp son lo que se cobró por lo detectado, no lo que se evade. El Informe no atribuye los sellos ni las denuncias solo a la Agencia de Aduanas.',
    }
    raw = volcar(raw, h0, h1, H)

    open(DB, 'wb').write(raw.encode('utf-8'))
    print(json.dumps({'poblacion': total, 'padron': activos, 'asalariados': asal}, ensure_ascii=False))


if __name__ == '__main__':
    main()
