#!/usr/bin/env python3
"""La pobreza de cada estado, de las infografías del INEGI (04-11-2026).

Dimensión social del Planisferio (pedido del autor, 04-11-2026). Desde 2025
la medición de la pobreza la hace el INEGI, con la metodología del CONEVAL
(que se extinguió). El INEGI publica una infografía por entidad
(«Pobreza multidimensional, 2024», pm_infog_<clave>_2024.pdf) y una
presentación nacional de resultados (pm_presentacion_2024.pdf).

Uso (se corre a mano, con las 33 infografías y la presentación bajadas):

    python3 herramientas/anclar_pobreza_estados.py <carpeta con pm_infog_XX_2024.pdf o XX.pdf> <pm_presentacion_2024.pdf>

Escribe docs/social/pobreza-entidades-2024.json con la huella SHA-256 de
cada archivo. Se detiene si:
  - una infografía no trae alguna de sus cifras o su título no es su estado;
  - la pobreza moderada más la extrema de un estado se aleja más de 0.15
    puntos de la pobreza que la presentación nacional da para ese estado;
  - las personas en pobreza (porcentaje × población) se alejan más de 0.2 %
    de la población de lo que da la presentación, en miles;
  - la suma de las 32 poblaciones o de las 32 personas en pobreza no da la
    del país (infografía 00).
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, 'docs', 'social', 'pobreza-entidades-2024.json')
URL = 'https://www.inegi.org.mx/contenidos/desarrollosocial/pm/doc/pm_infog_%s_2024.pdf'
URL_PRES = 'https://www.inegi.org.mx/contenidos/desarrollosocial/pm/doc/pm_presentacion_2024.pdf'
# Las claves del INEGI, en su orden, con la abreviatura de la base.
CLAVES = ['AGS', 'BC', 'BCS', 'CAM', 'COAH', 'COL', 'CHIS', 'CHIH', 'CDMX', 'DGO', 'GTO', 'GRO', 'HGO', 'JAL', 'MÉX', 'MICH',
          'MOR', 'NAY', 'NL', 'OAX', 'PUE', 'QRO', 'QROO', 'SLP', 'SIN', 'SON', 'TAB', 'TAM', 'TLAX', 'VER', 'YUC', 'ZAC']
CARENCIAS = [('rez', 'rezago educativo'),
             ('sal', 'carencia por acceso a los servicios de salud'),
             ('seg', 'carencia por acceso a la seguridad social'),
             ('viv', 'carencia por calidad y espacios de la vivienda'),
             ('bas', 'carencia por acceso a los servicios básicos en la vivienda'),
             ('ali', 'carencia por acceso a la alimentación nutritiva y de calidad')]

CLAVE_CAR = {'rez': 'rezago', 'sal': 'servicios de salud', 'seg': 'seguridad social', 'viv': 'calidad y espacios',
             'bas': 'servicios básicos', 'ali': 'alimentación'}

# Los renglones de la p. 32 de la presentación que pdftotext no deja en una
# sola línea (el nombre y la cifra salen separados), copiados a mano de esa
# página. Cada uno se coteja igual que los demás: moderada + extrema no debe
# alejarse más de 0.15 puntos (las dos vienen redondeadas a un decimal).
TRANSCRITO = {'CHIS': 66.0, 'GRO': 58.1, 'OAX': 51.6, 'VER': 44.5, 'PUE': 43.4, 'TLAX': 40.8, 'TAB': 34.8,
              'SLP': 30.4, 'YUC': 26.6, 'QROO': 17.7, 'SON': 14.1}
PAIS = 29.6  # «Estados Unidos Mexicanos», p. 32 de la presentación y comunicado 118/25


def llano(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s.upper()) if unicodedata.category(c) != 'Mn')


def sha(ruta):
    return hashlib.sha256(open(ruta, 'rb').read()).hexdigest()


def texto(ruta, layout=True, pag=None):
    a = ['pdftotext'] + (['-layout'] if layout else []) + (['-f', str(pag), '-l', str(pag)] if pag else []) + [ruta, '-']
    return subprocess.run(a, capture_output=True, text=True, check=True).stdout


def infografia(ruta):
    t = texto(ruta)
    lin = [re.sub(r'\s{2,}', '  ', x).strip() for x in t.split('\n')]
    titulo = lin[0].split('  ')[0]
    m = next((re.match(r'^2024  ([\d.]+)  100  2024  ([\d.]+)$', x) for x in lin if re.match(r'^2024  [\d.]+  100  2024  [\d.]+$', x)), None)
    if not m:
        raise SystemExit('anclar_pobreza: %s no trae la pobreza moderada' % ruta)
    mod, ing = float(m.group(1)), float(m.group(2))
    k = next(i for i, x in enumerate(lin) if re.search(r'Pobreza  2024  [\d.]+$', x))
    ingx = float(lin[k].rsplit('  ', 1)[1])
    m = re.match(r'^2024  ([\d.]+)$', lin[k + 1])
    if not m:
        raise SystemExit('anclar_pobreza: %s no trae la pobreza extrema' % ruta)
    ext = float(m.group(1))
    m = re.search(r'2024 (\d{1,3}(?: \d{3})+)', t)
    pob = int(m.group(1).replace(' ', ''))
    plano = re.sub(r'\s+', ' ', texto(ruta, layout=False))
    plano = re.sub(r'(\d)\. (\d) %', r'\1.\2 %', plano)
    plano = re.sub(r'([a-záéíóú])- ([a-záéíóú])', r'\1\2', plano)
    # Las seis frases «X % de la población de … presentó …» van siempre en el
    # mismo orden; las gráficas a veces se meten a media frase, así que se
    # toman en orden y se coteja que lo primero que nombra cada una sea su
    # carencia.
    frases = list(re.finditer(r'([\d.]+) % de la población (?:de|del) ', plano))
    if len(frases) != len(CARENCIAS):
        raise SystemExit('anclar_pobreza: %s trae %d frases de carencias, no %d' % (ruta, len(frases), len(CARENCIAS)))
    car = {}
    for (c, clave), m in zip(CARENCIAS, frases):
        tramo = plano[m.end():m.end() + 400].lower()
        primera = min((tramo.find(k), cc) for cc, k in CLAVE_CAR.items() if tramo.find(k) >= 0)[1]
        if primera != c:
            raise SystemExit('anclar_pobreza: %s: la frase %s nombra primero %s' % (ruta, c, primera))
        car[c] = float(m.group(1))
    return {'titulo': titulo, 'mod': mod, 'ext': ext, 'ing': ing, 'ingx': ingx, 'pob': pob, 'car': car}


def presentacion(ruta):
    """La pobreza de cada estado en la presentación nacional (p. 32): los
    renglones que se leen limpios, nombre y cifra en el mismo renglón."""
    out = subprocess.run(['pdftotext', '-f', '32', '-l', '32', '-bbox', ruta, '-'], capture_output=True, text=True, check=True).stdout
    W = [(float(a), float(b), float(c), float(d), w) for a, b, c, d, w in
         re.findall(r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)<', out)]
    res = {}
    for clave, (lo, hi) in (('pct', (0, 330)), ('mil', (330, 700))):
        filas = {}
        for x0, y0, x1, y1, w in W:
            if lo <= x0 < hi and y0 > 90:
                filas.setdefault(round((y0 + y1) / 6), []).append((x0, w))
        for ws in filas.values():
            s = ' '.join(w for _, w in sorted(ws))
            m = re.match(r'^(.*?[a-zé])\s+(\d{1,2}(?: \d{3})?\.\d)$' if clave == 'mil' else r'^(.*?[a-zé])\s+(\d{1,2}\.\d)$', s)
            if m:
                res.setdefault(llano(m.group(1)), {})[clave] = float(m.group(2).replace(' ', ''))
    return res


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    carpeta, pres = sys.argv[1], sys.argv[2]

    def ruta(c):
        for n in ('pm_infog_%s_2024.pdf' % c, '%s.pdf' % c):
            if os.path.exists(os.path.join(carpeta, n)):
                return os.path.join(carpeta, n)
        raise SystemExit('anclar_pobreza: falta la infografía %s' % c)
    P = presentacion(pres)
    nac = infografia(ruta('00'))
    est, cotejos = {}, 0
    for i, a in enumerate(CLAVES, 1):
        c = '%02d' % i
        r = ruta(c)
        x = infografia(r)
        x['sha'] = sha(r)
        x['url'] = URL % c
        x['clave'] = c
        nombre = llano(x['titulo'])
        p = P.get(nombre) or next((v for k, v in P.items() if k.startswith(nombre + ' ')), None)
        if a in TRANSCRITO:
            p = dict(p or {}, pct=TRANSCRITO[a])
        if not p or 'pct' not in p:
            raise SystemExit('anclar_pobreza: %s no tiene su pobreza de la presentación' % a)
        if p and 'pct' in p:
            if abs(x['mod'] + x['ext'] - p['pct']) > 0.15:
                raise SystemExit('anclar_pobreza: %s: moderada %.1f + extrema %.1f no da la pobreza de la presentación (%.1f)' % (a, x['mod'], x['ext'], p['pct']))
            x['pobPres'] = p['pct']
            cotejos += 1
        if p and 'mil' in p:
            calc = (x['mod'] + x['ext']) / 100 * x['pob']
            if abs(calc - p['mil'] * 1000) > 0.002 * x['pob']:
                raise SystemExit('anclar_pobreza: %s: las personas en pobreza (%.0f) no dan las de la presentación (%.1f mil)' % (a, calc, p['mil']))
            x['milPres'] = p['mil']
            cotejos += 1
        est[a] = x
    suma = sum(x['pob'] for x in est.values())
    if abs(suma - nac['pob']) > 0.0005 * nac['pob']:
        raise SystemExit('anclar_pobreza: las 32 poblaciones (%d) no suman la del país (%d)' % (suma, nac['pob']))
    pobres = sum((x['mod'] + x['ext']) / 100 * x['pob'] for x in est.values())
    if abs(pobres - (nac['mod'] + nac['ext']) / 100 * nac['pob']) > 0.005 * nac['pob']:
        raise SystemExit('anclar_pobreza: las personas en pobreza de los 32 no dan las del país')
    if cotejos < 25:
        raise SystemExit('anclar_pobreza: solo %d cotejos contra la presentación; revisa la lectura' % cotejos)
    if abs(nac['mod'] + nac['ext'] - PAIS) > 0.15:
        raise SystemExit('anclar_pobreza: la pobreza del país no cuadra')
    nac['pobPres'] = PAIS
    nac.update({'sha': sha(ruta('00')), 'url': URL % '00'})
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, 'w', encoding='utf-8') as f:
        json.dump({'fuente': 'INEGI, Pobreza multidimensional 2024 (con base en la ENIGH 2024 y la metodología del CONEVAL), infografías por entidad federativa',
                   'presentacion': {'url': URL_PRES, 'sha': sha(pres)}, 'cotejos': cotejos, 'nacional': nac, 'estados': est},
                  f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('anclar_pobreza: %s con las 32 entidades; %d cotejos contra la presentación; país %.1f %% en pobreza' % (
        os.path.relpath(SALIDA, RAIZ), cotejos, nac['pobPres']))


if __name__ == '__main__':
    main()
