#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integra el Directorio de Proveedores y Contratistas Sancionados de la
Secretaría Anticorrupción y Buen Gobierno en assets/auditor/data/sancionados.js
(window.AUDIT_SANCIONADOS).

Reglas (AGENTS.md §2 y §2 bis):
- Solo se publican con nombre y RFC las personas morales (RFC de 12 caracteres).
  Las personas físicas (RFC de 13 caracteres) solo cuentan en el total estadístico,
  sin nombre ni RFC.
- Aparecer en el Directorio y tener contratos en ComprasMX no prueba que la
  empresa haya sido contratada estando inhabilitada: el contrato pudo firmarse
  antes del inicio de la inhabilitación o bajo suspensión provisional/definitiva
  en juicio de nulidad o amparo. Siempre se muestra la fecha inicial y final de
  la sanción para comparar contra la fecha del contrato.

Uso:
    python3 herramientas/anclar_sancionados.py [sancionados_raw.json]
"""
import collections
import hashlib
import json
import pathlib
import re
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SALIDA = RAIZ / 'assets' / 'auditor' / 'data' / 'sancionados.js'
CMX_INDICE = RAIZ / 'assets' / 'auditor' / 'data' / 'comprasmx' / 'indice.js'
SAT_69B = RAIZ / 'assets' / 'auditor' / 'data' / 'sat-69b.js'

URL_PORTAL = 'https://directoriosancionados.buengobierno.gob.mx/'
URL_API = 'https://kong-servicios-estrategico.buengobierno.gob.mx/particularesSancionadosPro'
CORTE = '2026-11-17'
SHA_ESPERADO = '023e410ce88855490eb885b9a024a9c6bb16c63176b1c3b8dcde823933788bc9'

QUERY = {
    "query": """query {
      results(filtros: {}) {
        numero_expediente
        rfc
        nombre_razon_social
        institucion_dependencia { nombre clave_dependencia }
        fecha_notificacion
        multa { monto monto_cf }
        plazo { fecha_inicial fecha_final plazo_inha }
        leyes_infringidas
        causa_motivo_hechos
        autoridad_sancionadora
        fecha_dof
      }
    }"""
}


def _ley_corta(s):
    s = (s or '').upper()
    if 'LAASSP' in s or 'ADQUISICIONES' in s:
        return 'LAASSP'
    if 'LOPSRM' in s or 'OBRAS' in s:
        return 'LOPSRM'
    if 'ASOCIACIONES' in s or 'LAPP' in s:
        return 'LAPP'
    if 'ANTICORRUPCI' in s or 'LFAACP' in s:
        return 'LFAACP'
    if 'RESPONSABILIDADES' in s or 'LGRA' in s:
        return 'LGRA'
    return (s[:24] + '…') if len(s) > 24 else (s or '—')


def main():
    if len(sys.argv) >= 2:
        raw = pathlib.Path(sys.argv[1]).read_bytes()
    else:
        p = subprocess.run(['curl.exe', '-sL', '-X', 'POST', URL_API,
                            '-H', 'Content-Type: application/json', '-d', json.dumps(QUERY)],
                           capture_output=True, check=True)
        raw = p.stdout
    sha = hashlib.sha256(raw).hexdigest()
    d = json.loads(raw.decode('utf-8'))
    res = (d.get('data') or {}).get('results') or []
    if not res:
        sys.exit('anclar_sancionados: el API no devolvió registros')

    t_cmx = CMX_INDICE.read_text(encoding='utf-8')
    d_cmx = json.loads(t_cmx[t_cmx.index('{'):t_cmx.rindex('}') + 1])
    idx_cmx = {r[0]: r[1] for r in d_cmx['r']}

    t_sat = SAT_69B.read_text(encoding='utf-8')
    sat_rows = json.loads(t_sat[t_sat.index('"r": [') + 5:].rstrip().rstrip(';').rstrip('}').rstrip())
    sat_rfcs = {r[0]: r[2] for r in sat_rows}

    por_rfc = collections.defaultdict(list)
    nombres = {}
    pf_count = 0
    sin_rfc = 0
    multa_tot = 0.0
    multa_pm = 0.0

    for r in res:
        rfc = re.sub(r'\s+', '', (r.get('rfc') or '')).upper()
        nom = re.sub(r'\s+', ' ', (r.get('nombre_razon_social') or '')).strip()
        try:
            m = round(float((r.get('multa') or {}).get('monto') or 0.0), 2)
        except ValueError:
            m = 0.0
        multa_tot += m
        if len(rfc) == 12:
            multa_pm += m
            nombres.setdefault(rfc, nom)
            inst = ((r.get('institucion_dependencia') or {}).get('nombre') or r.get('autoridad_sancionadora') or '').strip()
            plz = r.get('plazo') or {}
            por_rfc[rfc].append([
                (r.get('numero_expediente') or '').strip(),
                inst,
                _ley_corta(r.get('leyes_infringidas')),
                (plz.get('fecha_inicial') or '').strip(),
                (plz.get('fecha_final') or '').strip(),
                (plz.get('plazo_inha') or '').strip(),
                m,
                (r.get('fecha_dof') or '').strip(),
            ])
        elif len(rfc) == 13:
            pf_count += 1
        else:
            sin_rfc += 1

    cruce_cmx = []
    for rfc in sorted(por_rfc):
        if rfc in idx_cmx:
            exps = por_rfc[rfc]
            e0 = exps[0]
            cruce_cmx.append([
                rfc,
                idx_cmx[rfc],
                len(exps),
                e0[2],
                e0[1],
                e0[3],
                e0[4],
                round(sum(x[6] for x in exps), 2),
                e0[0],
            ])
    cruce_69b = [[rfc, nombres[rfc], sat_rfcs[rfc], len(por_rfc[rfc])]
                 for rfc in sorted(por_rfc) if rfc in sat_rfcs]

    salida_obj = {
        'corte': CORTE,
        'fuente': 'Secretaría Anticorrupción y Buen Gobierno, Directorio de Proveedores y Contratistas Sancionados',
        'url': URL_PORTAL,
        'api': URL_API,
        'sha256': sha,
        'nota': ('Solo incluye personas morales (RFC de 12 caracteres). Las personas físicas sancionadas '
                 'se cuentan en el resumen estadístico pero no se publican con nombre ni RFC (AGENTS.md §2 bis). '
                 'Aparecer en el Directorio y tener contratos en ComprasMX no prueba que se haya contratado '
                 'durante la inhabilitación: hay que comparar la fecha del contrato con la vigencia de la sanción.'),
        'resumen': {
            'expedientes': len(res),
            'expedientesMorales': sum(len(v) for v in por_rfc.values()),
            'empresasUnicas': len(por_rfc),
            'personasFisicasOcultas': pf_count,
            'sinRfcMoral': sin_rfc,
            'multasMdp': round(multa_tot / 1e6, 1),
            'multasMoralesMdp': round(multa_pm / 1e6, 1),
            'enComprasMx': len(cruce_cmx),
            'enSat69b': len(cruce_69b),
        },
        'campos': ['expediente', 'institucion', 'ley', 'inicio', 'fin', 'plazo', 'multa', 'dof'],
        'cruceComprasMx': cruce_cmx,
        'cruceSat69b': cruce_69b,
        'n': {rfc: nombres[rfc] for rfc in sorted(por_rfc)},
        'r': {rfc: por_rfc[rfc] for rfc in sorted(por_rfc)},
    }
    js = ('/* Generado por herramientas/anclar_sancionados.py. No editar a mano. */\n'
          'window.AUDIT_SANCIONADOS = ' + json.dumps(salida_obj, ensure_ascii=False, separators=(',', ':')) + ';\n')
    SALIDA.write_text(js, encoding='utf-8', newline='\n')
    r = salida_obj['resumen']
    print('sancionados.js: %d expedientes (%d de %d empresas morales, %d PF ocultas); multas $%s mdp; %d en ComprasMX y %d en 69-B' % (
        r['expedientes'], r['expedientesMorales'], r['empresasUnicas'], r['personasFisicasOcultas'],
        format(r['multasMdp'], ',.1f'), r['enComprasMx'], r['enSat69b']))


if __name__ == '__main__':
    main()
