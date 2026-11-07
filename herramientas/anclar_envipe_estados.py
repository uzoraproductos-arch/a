#!/usr/bin/env python3
"""Ancla la ENVIPE 2026 por entidad para la dimensión penal del Planisferio
(pedido del autor, 05-11-2026: «una dimensión de penal»).

Se corre a mano, con poppler (pdftotext) instalado:

    python3 herramientas/anclar_envipe_estados.py <carpeta con envipe2026_<ent>.pdf y envipe2026_presentacion_nacional.pdf>

Los PDF se bajan de https://www.inegi.org.mx/contenidos/programas/envipe/2026/doc/
(uno por entidad: envipe2026_ags.pdf … envipe2026_zac.pdf). De cada uno se
toma, del texto del propio INEGI:

- la cifra oculta del estado («La cifra oculta en el estado de X corresponde a N %»);
- la tasa de fraude por cada 100 mil habitantes, cuando la ficha la dice en su
  texto («el delito de fraude en el estado de X representó una tasa de N
  delitos»). En las entidades donde el delito más frecuente fue otro, la ficha
  da la tasa de fraude solo en una gráfica (imagen): se queda vacía y la
  dimensión la dice pendiente, nunca se lee a ojo;
- el delito que la ficha destaca en su página de tipos de delito.

Escribe docs/seguridad/envipe-2026-entidades.json con la huella SHA-256 de
cada PDF. Si falta una entidad o una cifra oculta, se detiene.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, 'docs', 'seguridad', 'envipe-2026-entidades.json')
URL = 'https://www.inegi.org.mx/contenidos/programas/envipe/2026/doc/envipe2026_%s.pdf'
# Clave del archivo del INEGI → clave de la plataforma (la de DB.estados).
CLAVES = {'ags': 'AGS', 'bc': 'BC', 'bcs': 'BCS', 'camp': 'CAM', 'coah': 'COAH', 'col': 'COL', 'chis': 'CHIS', 'chih': 'CHIH',
          'cdmx': 'CDMX', 'dgo': 'DGO', 'gto': 'GTO', 'gro': 'GRO', 'hgo': 'HGO', 'jal': 'JAL', 'mex': 'MÉX', 'mich': 'MICH',
          'mor': 'MOR', 'nay': 'NAY', 'nl': 'NL', 'oax': 'OAX', 'pue': 'PUE', 'qro': 'QRO', 'qroo': 'QROO', 'slp': 'SLP',
          'sin': 'SIN', 'son': 'SON', 'tab': 'TAB', 'tamps': 'TAM', 'tlax': 'TLAX', 'ver': 'VER', 'yuc': 'YUC', 'zac': 'ZAC'}


def texto(ruta):
    t = subprocess.run(['pdftotext', '-layout', ruta, '-'], capture_output=True, check=True).stdout.decode('utf-8')
    return re.sub(r'\s+', ' ', t)


def sha(ruta):
    with open(ruta, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def main(carpeta):
    estados = {}
    for c, a in CLAVES.items():
        ruta = os.path.join(carpeta, 'envipe2026_%s.pdf' % c)
        if not os.path.exists(ruta):
            sys.exit('Falta %s' % ruta)
        t = texto(ruta)
        oc = re.search(r'La cifra oculta en (?:el estado de |la )?[^.]{2,40}? corresponde a ([\d.]+) %', t)
        if not oc:
            sys.exit('%s: no encontré su cifra oculta' % c)
        fr = re.search(r'el delito de fraude1/ en [^.]{2,40}? representó una tasa de ([\d ]+) delitos por cada 100 mil habitantes', t)
        de = re.search(r'TIPOS DE DELITO \d+ La ENVIPE estima que el delito de (.{3,80}?) en (?:el estado de |la |Ciudad de México)', t)
        estados[a] = {'oculta': float(oc.group(1)),
                      'fraude': int(fr.group(1).replace(' ', '')) if fr else None,
                      'destaca': de.group(1).replace('1/', '').strip() if de else None,
                      'url': URL % c, 'sha': sha(ruta)}
    nac = os.path.join(carpeta, 'envipe2026_presentacion_nacional.pdf')
    if not os.path.exists(nac):
        sys.exit('Falta %s' % nac)
    tn = texto(nac)
    # La presentación nacional: tasa de fraude 2024 y 2025 en la gráfica de los
    # delitos más frecuentes, y la cifra oculta 2025 en su serie.
    if '8 290' not in tn or '93.4' not in tn:
        sys.exit('La presentación nacional cambió: revisa la tasa de fraude y la cifra oculta antes de seguir')
    doc = {'fuente': 'INEGI, Encuesta Nacional de Victimización y Percepción sobre Seguridad Pública (ENVIPE) 2026, datos de 2025: '
                     'principales resultados por entidad federativa',
           'nacional': {'fraude': 8290, 'fraude2024': 7574, 'oculta': 93.4,
                        'url': URL % 'presentacion_nacional', 'sha': sha(nac)},
           'estados': estados}
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write('\n')
    sin = sorted(a for a, x in estados.items() if x['fraude'] is None)
    print('%d entidades; tasa de fraude en el texto de %d; solo en gráfica: %s' % (len(estados), 32 - len(sin), ', '.join(sin)))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
