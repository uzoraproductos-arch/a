#!/usr/bin/env python3
"""Ancla la ENVIPE 2026 por entidad para la dimensión penal del Planisferio
(pedido del autor, 05-11-2026: «una dimensión de penal»).

Se corre a mano, con poppler (pdftotext) instalado:

    python3 herramientas/anclar_envipe_estados.py <carpeta con envipe2026_<ent>.pdf y envipe2026_presentacion_nacional.pdf> <I_nivel_victimizacion_2026_est.xlsx>

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

La tasa de fraude de las entidades cuya ficha la da solo en gráfica se toma
del tabulado básico del INEGI «I. Nivel de victimización y delincuencia»,
cuadro 1.13 (tasa de incidencia por entidad de ocurrencia y los cinco delitos
más frecuentes), redondeada al entero como en las fichas. Se baja de
https://www.inegi.org.mx/contenidos/programas/envipe/2026/tabulados/ (pestaña
«Tabulados» de la ENVIPE 2026). Antes de usarlo se coteja: cada tasa que da el
texto de una ficha debe ser igual a la del cuadro, y la del país, 8 290; si
una no cuadra, se detiene. Se necesita openpyxl.

Escribe docs/seguridad/envipe-2026-entidades.json con la huella SHA-256 de
cada PDF y del tabulado, y en cada entidad de dónde salió su tasa de fraude
(«ficha» o «tabulado»). Si falta una entidad, una cifra oculta o una tasa de
fraude, se detiene.
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
URL_TAB = 'https://www.inegi.org.mx/contenidos/programas/envipe/2026/tabulados/I_nivel_victimizacion_2026_est.xlsx'
# Nombre de cada entidad en el tabulado del INEGI → clave de la plataforma.
NOMBRES = {'Aguascalientes': 'AGS', 'Baja California': 'BC', 'Baja California Sur': 'BCS', 'Campeche': 'CAM', 'Coahuila de Zaragoza': 'COAH',
           'Colima': 'COL', 'Chiapas': 'CHIS', 'Chihuahua': 'CHIH', 'Ciudad de México': 'CDMX', 'Durango': 'DGO', 'Guanajuato': 'GTO',
           'Guerrero': 'GRO', 'Hidalgo': 'HGO', 'Jalisco': 'JAL', 'México': 'MÉX', 'Michoacán de Ocampo': 'MICH', 'Morelos': 'MOR',
           'Nayarit': 'NAY', 'Nuevo León': 'NL', 'Oaxaca': 'OAX', 'Puebla': 'PUE', 'Querétaro': 'QRO', 'Quintana Roo': 'QROO',
           'San Luis Potosí': 'SLP', 'Sinaloa': 'SIN', 'Sonora': 'SON', 'Tabasco': 'TAB', 'Tamaulipas': 'TAM', 'Tlaxcala': 'TLAX',
           'Veracruz de Ignacio de la Llave': 'VER', 'Yucatán': 'YUC', 'Zacatecas': 'ZAC'}
DELITOS = ('Fraude', 'Extorsión', 'Amenazas', 'Robo', 'Lesiones', 'Otros delitos', 'Hostigamiento', 'Delitos sexuales')
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


def fraude_tabulado(ruta):
    """Cuadro 1.13 del tabulado: {clave: tasa de fraude sin redondear}, con
    'NAL' para el país. Cada entidad trae su total y debajo sus cinco delitos
    más frecuentes."""
    import openpyxl
    ws = openpyxl.load_workbook(ruta, read_only=True, data_only=True)['1.13']
    tit = ' '.join(str(c) for r in ws.iter_rows(min_row=1, max_row=4, values_only=True) for c in r if c)
    if 'cinco delitos más frecuentes' not in tit or 'Cuadro 1.13' not in tit:
        sys.exit('El cuadro 1.13 del tabulado cambió: revisa su título antes de seguir')
    out, cur = {}, None
    for r in ws.iter_rows(min_row=6, values_only=True):
        r = [c for c in r if c is not None]
        if len(r) != 2 or not isinstance(r[1], (int, float)):
            continue
        n = str(r[0]).strip()
        if n.startswith(DELITOS):
            if n.rstrip('0123456789') == 'Fraude':
                out[cur] = r[1]
        elif n == 'Estados Unidos Mexicanos':
            cur = 'NAL'
        elif n in NOMBRES:
            cur = NOMBRES[n]
        else:
            sys.exit('El cuadro 1.13 trae un renglón que no conozco: %s' % n)
    return out


def main(carpeta, tabulado):
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
                      'fraude_de': 'ficha' if fr else None,
                      'destaca': de.group(1).replace('1/', '').strip() if de else None,
                      'url': URL % c, 'sha': sha(ruta)}
    tab = fraude_tabulado(tabulado)
    if round(tab.get('NAL', 0)) != 8290:
        sys.exit('El cuadro 1.13 no da 8 290 fraudes por cada 100 mil en el país: revisa el tabulado')
    for a, x in estados.items():
        if x['fraude'] is not None and a in tab and round(tab[a]) != x['fraude']:
            sys.exit('%s: su ficha dice %d fraudes por cada 100 mil y el cuadro 1.13, %s' % (a, x['fraude'], round(tab[a])))
        if x['fraude'] is None and a in tab:
            x['fraude'], x['fraude_de'] = int(round(tab[a])), 'tabulado'
    sin = sorted(a for a, x in estados.items() if x['fraude'] is None)
    if sin:
        sys.exit('Sin tasa de fraude ni en su ficha ni en el cuadro 1.13: %s' % ', '.join(sin))
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
           'tabulado': {'titulo': 'Tabulados básicos, I. Nivel de victimización y delincuencia, cuadro 1.13: tasa de incidencia delictiva por '
                                  'entidad federativa de ocurrencia por cada cien mil habitantes y los cinco delitos más frecuentes, 2025',
                        'url': URL_TAB, 'sha': sha(tabulado)},
           'estados': estados}
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write('\n')
    tb = sorted(a for a, x in estados.items() if x['fraude_de'] == 'tabulado')
    print('%d entidades; tasa de fraude del texto de su ficha: %d; del cuadro 1.13 del tabulado: %s' % (len(estados), 32 - len(tb), ', '.join(tb)))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
