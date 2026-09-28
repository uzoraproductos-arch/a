# -*- coding: utf-8 -*-
"""Datos de las vistas del simulador «Un año de cuentas en veinte segundos»
(módulo 5) que no estaban en la base: los Poderes de la Unión, la obra
pública por sector y el huachicol fiscal (28-09-2026).

- Poderes y obra pública: se suman del CSV de datos abiertos del PEF 2026
  (Transparencia Presupuestaria), cuya huella se comprueba. La obra pública
  es la columna «Tipo de gasto 3: Gasto de obra pública» agrupada por ramo
  y unidad responsable; el Ejecutivo es el gasto neto total del decreto
  menos los Poderes Legislativo y Judicial y los órganos autónomos.
- Huachicol: la única cifra oficial es la del Segundo Informe de Gobierno
  (1-09-2026), p. 260 impresa / 284 del PDF: 109.4 millones de litros no
  declarados y $4,600 mdp de recaudación asociada de IVA e IEPS entre el
  1-09-2025 y el 30-06-2026. Los $600,000 mdp quedan como pendiente, con la
  aclaración oficial del 9-10-2025.

Uso:  python3 herramientas/integrar_ritmo_vistas.py <PEF_2026.csv>
Escribe la colección ritmo_vistas en assets/auditor/js/audit-database.js
(solo el auditor) y corrige la fecha de la aclaración en la estimación
«pff» del huachicol. Idempotente.
"""
import collections
import csv
import hashlib
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'audit-database.js')
CSV_SHA = '6dec5f3ad52126c3257a74e7e177eada0c591ed8109d861becf767e959c86c03'
GASTO_NETO = 10193683.7  # panoramaErario.totalPEF, decreto del PEF 2026

AUTONOMOS = {22: 'INE', 35: 'CNDH', 40: 'INEGI', 49: 'FGR'}


def mdp(x):
    return round(x / 1e6, 1)


def leer(ruta):
    h = hashlib.sha256(open(ruta, 'rb').read()).hexdigest()
    if h != CSV_SHA:
        sys.exit('La huella del CSV no coincide: ' + h)
    ramo = collections.defaultdict(float)
    obra = collections.defaultdict(float)
    obra_ur = collections.defaultdict(float)
    fais_mun = 0.0
    for x in csv.DictReader(open(ruta, encoding='utf-8-sig')):
        m = float(x['MONTO_PEF_2026'])
        k = int(x['ID_RAMO'])
        ramo[k] += m
        if x['ID_TIPOGASTO'] == '3':
            obra[k] += m
            obra_ur[(k, x['DESC_UR'])] += m
        if k == 33 and x['ID_PP'] == '4':
            fais_mun += m
    return ramo, obra, obra_ur, fais_mun


def construir(ruta):
    ramo, obra, obra_ur, fais_mun = leer(ruta)
    leg, jud = mdp(ramo[1]), mdp(ramo[3])
    aut = {n: mdp(ramo[k]) for k, n in AUTONOMOS.items()}
    aut_tot = round(sum(aut.values()), 1)
    ejec = round(GASTO_NETO - leg - jud - aut_tot, 1)
    tren_maya = mdp(obra_ur[(7, 'Tren Maya, S.A. de C.V.')])
    sectores = [
        {'id': 'obra_energia', 'nom': 'Energía: Pemex y CFE', 'mdp': round(mdp(obra[52]) + mdp(obra[53]), 1),
         'como': 'Pemex $%s + CFE $%s mdp' % (format(mdp(obra[52]), ',.1f'), format(mdp(obra[53]), ',.1f'))},
        {'id': 'obra_transporte', 'nom': 'Trenes, carreteras y puertos', 'mdp': round(mdp(obra[9]) + tren_maya + mdp(obra[13]), 1),
         'como': 'SICT $%s + Tren Maya (Defensa) $%s + Marina (Tren Interoceánico y puertos) $%s mdp' % (
             format(mdp(obra[9]), ',.1f'), format(tren_maya, ',.1f'), format(mdp(obra[13]), ',.1f'))},
        {'id': 'obra_ramo33', 'nom': 'Obra de estados y municipios (Ramo 33)', 'mdp': mdp(obra[33]),
         'como': 'Aportaciones federales clasificadas como gasto de obra pública; el FAIS municipal suma $%s mdp' % format(round(fais_mun / 1e6, 1), ',.1f')},
        {'id': 'obra_agua', 'nom': 'Agua: Conagua', 'mdp': mdp(obra[16]), 'como': 'Ramo 16, Comisión Nacional del Agua'},
        {'id': 'obra_salud', 'nom': 'Hospitales: IMSS e ISSSTE', 'mdp': round(mdp(obra[50]) + mdp(obra[51]), 1),
         'como': 'IMSS $%s + ISSSTE $%s mdp' % (format(mdp(obra[50]), ',.1f'), format(mdp(obra[51]), ',.1f'))},
    ]
    resto = round(sum(obra.values()) / 1e6 - sum(s['mdp'] for s in sectores), 1)
    sectores.append({'id': 'obra_otros', 'nom': 'Defensa, Fiscalía y Poderes', 'mdp': resto,
                     'como': 'Lo demás: Ingenieros de la Defensa, Fiscalía General, Cámaras y Poder Judicial'})
    total_obra = mdp(sum(obra.values()))
    assert abs(sum(s['mdp'] for s in sectores) - total_obra) < 0.2

    return {
        'nota': 'Datos de las vistas del simulador «Un año de cuentas en veinte segundos» (módulo 5). Los escribe herramientas/integrar_ritmo_vistas.py desde el CSV de datos abiertos del PEF 2026.',
        'fuentes': {
            'pef26csv': {
                'doc': 'SHCP, Presupuesto de Egresos de la Federación 2026, datos abiertos (PEF_2026.csv), columna MONTO_PEF_2026',
                'url': 'https://www.transparenciapresupuestaria.gob.mx/work/models/PTP/DatosAbiertos/Bases_de_datos_presupuesto/CSV/PEF_2026.csv',
                'sha256': CSV_SHA,
            },
            'pef26dof': {
                'doc': 'Presupuesto de Egresos de la Federación 2026, DOF 21-11-2025: gasto neto total de $10,193,683.7 mdp',
                'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/PEF_2026.pdf',
            },
            'ig2': {
                'doc': 'Presidencia de la República, Segundo Informe de Gobierno 2025-2026, apartado «Acompañamiento técnico a la Administración Pública Federal», p. 260 (p. 284 del PDF)',
                'url': 'https://www.segundoinformedegobierno.gob.mx/gmx_media/2-ig-informe-consolidado-final_01_09_2026',
                'sha256': 'cc95e5ade7cb306b734e9dc1e61e1defcba14c444e5705de24be6ca6e115fa9d',
            },
            'presidencia0910': {
                'doc': 'Presidencia de la República, versión estenográfica de la conferencia de prensa del 9 de octubre de 2025',
                'url': 'https://www.gob.mx/presidencia/articulos/version-estenografica-conferencia-de-prensa-de-la-presidenta-claudia-sheinbaum-pardo-del-09-de-octubre-de-2025',
            },
        },
        'poderes': {
            'gasto_neto': GASTO_NETO,
            'ejecutivo': ejec,
            'legislativo': leg,
            'judicial': jud,
            'autonomos': aut_tot,
            'autonomos_desglose': aut,
            'operacion_ejecutivo': 'Gasto neto total del PEF 2026 ($10,193,683.7 mdp) menos el Poder Legislativo, el Poder Judicial y los órganos autónomos (INE, CNDH, INEGI y Fiscalía General). Incluye los ramos generales que administra el Ejecutivo: deuda, participaciones y aportaciones a estados y municipios, y pensiones.',
        },
        'obra': {
            'total': total_obra,
            'sectores': sectores,
            'definicion': 'Lo que el PEF 2026 clasifica como «gasto de obra pública» (tipo de gasto 3), agrupado por Auditavisión en sectores según el ramo o la entidad que lo ejerce. Es presupuesto aprobado para 2026, no lo ya pagado.',
        },
        'huachicol': {
            'recaudacion_mdp': 4600,
            'litros_millones': 109.4,
            'periodo': '1-09-2025 a 30-06-2026',
            'fuente': 'ig2',
            'texto': 'Con sistemas de revisión no intrusiva en las 50 aduanas se detectaron 109.4 millones de litros de hidrocarburos no declarados, con una recaudación asociada de $4,600 mdp de IVA e IEPS. Son diez meses, no un año, y es lo que se cobró, no lo que se evade.',
            'declarado_mdp': 600000,
            'declarado_texto': 'La cifra que la Procuradora Fiscal mencionó ante diputados el 2-10-2025. El 9-10-2025 la Presidenta aclaró en su conferencia que «no hay un dato de Secretaría de Hacienda oficial de cuánto recurso significa el contrabando de combustible» y que la cifra venía de un diputado. No es oficial ni anual.',
            'declarado_fuentes': ['pff25', 'presidencia0910'],
        },
    }


def bloque_json(raw, clave):
    i = raw.index('"' + clave + '": {')
    j = raw.index('{', i)
    prof = 0
    for k in range(j, len(raw)):
        c = raw[k]
        if c == '{':
            prof += 1
        elif c == '}':
            prof -= 1
            if prof == 0:
                return j, k + 1
    raise ValueError(clave)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    datos = construir(sys.argv[1])
    raw = open(DB, 'rb').read().decode('utf-8')
    nl = '\r\n'
    txt = json.dumps(datos, ensure_ascii=False, indent=2)
    txt = '\n  '.join(txt.split('\n')).replace('\n', nl)
    if '"ritmo_vistas": {' in raw:
        a, b = bloque_json(raw, 'ritmo_vistas')
        raw = raw[:a] + txt + raw[b:]
    else:
        fin = raw.rindex(nl + '};')
        raw = raw[:fin] + ',' + nl + '  "ritmo_vistas": ' + txt + raw[fin:]

    # Fecha de la aclaración: fue el 9 de octubre, en la conferencia (fuente oficial).
    a, b = bloque_json(raw, 'huachicol_fiscal')
    h = json.loads(raw[a:b])
    h['fuentes']['presidencia0910'] = datos['fuentes']['presidencia0910']
    for e in h['estimaciones']:
        if e.get('id') == 'pff':
            e['fuente2'] = 'presidencia0910'
            e['texto'] = e['texto'].replace(
                'El 10 de octubre la Presidenta la desmintió: dijo que la cifra venía de un diputado y que sin una base completa no se puede confirmar.',
                'El 9 de octubre, en su conferencia, la Presidenta aclaró que «no hay un dato de Secretaría de Hacienda oficial de cuánto recurso significa el contrabando de combustible» y que la cifra venía de un diputado; el secretario de Hacienda precisó que los $16,000 mdp son el saldo histórico de los casos querellados.')
    viejo = raw[a:b]
    # Se conserva el formato del bloque original (indent y escapes).
    asc = '\\u00' in viejo
    lineas = viejo.split(nl)
    sang = len(lineas[1]) - len(lineas[1].lstrip(' ')) - 2 if len(lineas) > 1 else 2
    nuevo = json.dumps(h, ensure_ascii=asc, indent=2)
    nuevo = ('\n' + ' ' * sang).join(nuevo.split('\n')).replace('\n', nl)
    raw = raw[:a] + nuevo + raw[b:]
    open(DB, 'wb').write(raw.encode('utf-8'))
    print(json.dumps({'poderes': {k: datos['poderes'][k] for k in ('ejecutivo', 'legislativo', 'judicial', 'autonomos')},
                      'obra': [(s['id'], s['mdp']) for s in datos['obra']['sectores']], 'total_obra': datos['obra']['total']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
