#!/usr/bin/env python3
"""Extrae de los datos abiertos de Hacienda lo que gastaron el Congreso y el
Poder Judicial: el cierre de 2025 (Cuenta Pública) y el avance de 2026.

Uso:
    python3 herramientas/extraer_ejercicio_poderes.py CP2025.csv AVANCE_2T_2026.csv

Los dos CSV se bajan de Transparencia Presupuestaria, Datos Abiertos:
  - Cuenta Pública 2025 (ramos administrativos, generales y autónomos):
    /work/models/PTP/DatosAbiertos/BD_Cuenta_Publica/CSV/cuenta_publica_2025_gf_ecd_epe.csv
  - Avance del gasto (AC01) al segundo trimestre de 2026:
    /work/models/PTP/DatosAbiertos/Bases_de_datos_presupuesto/CSV/pef_ac01_avance_2t_2026.csv
El servidor manda una cadena de certificados incompleta: curl necesita el
intermedio YR1 de Let's Encrypt en su paquete de confianza (--cacert), nunca
desactivar la verificación.

Escribe investigaciones/ejercicio-poderes.json; integrar_poderes.py lo lee.
"""
import collections
import csv
import hashlib
import io
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SALIDA = RAIZ / 'investigaciones' / 'ejercicio-poderes.json'
HOST = 'https://www.transparenciapresupuestaria.gob.mx'
URL_CP = HOST + '/work/models/PTP/DatosAbiertos/BD_Cuenta_Publica/CSV/cuenta_publica_2025_gf_ecd_epe.csv'
URL_AV = HOST + '/work/models/PTP/DatosAbiertos/Bases_de_datos_presupuesto/CSV/pef_ac01_avance_2t_2026.csv'
RAMOS = {'1': '01', '3': '03'}
CAPITULOS = {
    '1': 'Servicios personales', '2': 'Materiales y suministros', '3': 'Servicios generales',
    '4': 'Transferencias, asignaciones, subsidios y otras ayudas',
    '5': 'Bienes muebles, inmuebles e intangibles', '6': 'Inversión pública',
    '7': 'Inversiones financieras y otras provisiones',
}


def num(x):
    x = (x or '').strip().replace(',', '')
    if x in ('', '-'):
        return 0.0
    return float(x)


def texto(ruta):
    raw = pathlib.Path(ruta).read_bytes()
    try:
        return raw.decode('utf-8-sig'), hashlib.sha256(raw).hexdigest()
    except UnicodeDecodeError:
        return raw.decode('latin-1'), hashlib.sha256(raw).hexdigest()


def cuenta_publica(ruta):
    t, sha = texto(ruta)
    r = csv.reader(io.StringIO(t))
    cab = [c.strip() for c in next(r)]
    i = {c: cab.index(c) for c in cab}
    uni = collections.OrderedDict()
    caps = collections.defaultdict(lambda: collections.defaultdict(float))
    for f in r:
        ramo = f[i['R']].strip()
        if ramo not in RAMOS:
            continue
        clave = (RAMOS[ramo], f[i['UR']].strip())
        u = uni.setdefault(clave, {'ramo': clave[0], 'ur': clave[1], 'nombre': f[i['UR_DESC']].strip(),
                                   'original': 0.0, 'modificado': 0.0, 'devengado': 0.0,
                                   'pagado': 0.0, 'ejercido': 0.0})
        for campo, col in (('original', 'Original_Bruto'), ('modificado', 'Modificado_Bruto'),
                           ('devengado', 'Devengado'), ('pagado', 'Pagado'), ('ejercido', 'Ejercido_Bruto')):
            u[campo] += num(f[i[col]])
        if clave[0] == '01':
            caps[clave[1]][f[i['PTDA']].strip()[:1] + '000'] += num(f[i['Ejercido_Bruto']])
    unidades = [dict(u, **{k: round(v, 2) for k, v in u.items() if isinstance(v, float)}) for _, u in sorted(uni.items())]
    capitulos = {ur: [{'cap': c, 'concepto': CAPITULOS[c[0]], 'ejercido': round(v, 2)}
                      for c, v in sorted(d.items()) if round(v, 2)] for ur, d in caps.items()}
    return {'fuente': 'CP2025', 'sha256': sha, 'unidades': unidades, 'capitulosLegislativo': capitulos}


def avance(ruta):
    t, sha = texto(ruta)
    r = csv.DictReader(io.StringIO(t))
    uni = collections.OrderedDict()
    for f in r:
        ramo = f['ID_RAMO'].strip()
        if ramo not in RAMOS:
            continue
        clave = (RAMOS[ramo], f['ID_UR'].strip())
        u = uni.setdefault(clave, {'ramo': clave[0], 'ur': clave[1], 'nombre': f['DESC_UR'].strip(),
                                   'aprobado': 0.0, 'modificado': 0.0, 'pagado': 0.0})
        u['aprobado'] += num(f['MONTO_APROBADO'])
        u['modificado'] += num(f['MONTO_MODIFICADO'])
        u['pagado'] += num(f['MONTO_PAGADO'])
    unidades = [dict(u, **{k: round(v, 2) for k, v in u.items() if isinstance(v, float)}) for _, u in sorted(uni.items())]
    return {'fuente': 'AV2T2026', 'sha256': sha, 'corte': '30 de junio de 2026', 'unidades': unidades}


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    datos = {'cp2025': cuenta_publica(sys.argv[1]), 'avance2026': avance(sys.argv[2]),
             'urls': {'CP2025': URL_CP, 'AV2T2026': URL_AV}}
    SALIDA.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding='utf-8')
    for k in ('cp2025', 'avance2026'):
        for u in datos[k]['unidades']:
            print(k, u['ramo'], u['ur'], u['nombre'], {c: v for c, v in u.items() if isinstance(v, float)})


if __name__ == '__main__':
    main()
