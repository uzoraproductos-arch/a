#!/usr/bin/env python3
"""Ancla las reclamaciones por posible fraude que la CONDUSEF dio a nivel
nacional en sus comunicados de 2026, para «El fraude en números» (pedido del
autor, 07-11-2026: «continúa con las reclamaciones de la CONDUSEF»).

Se corre a mano:

    python3 -I herramientas/anclar_condusef_fraude.py <com081.html> <com090.html> <com096.html>

Los tres archivos son las páginas de los comunicados en gob.mx (`COMUNICADOS`,
abajo), guardadas tal cual. La página trae fichas de sesión, así que la huella
SHA-256 se toma del **texto del comunicado** (el cuerpo de la nota, sin
etiquetas y con los espacios juntados). Se detiene si un texto ya no dice su
número de comunicado o alguna de las cifras que se toman de él:

- 081 (28-05-2026): de enero a marzo de 2026, 22,199 reclamaciones recibidas a
  nivel nacional; el 37.4 % por posible fraude, y de ellas el 94 % de la banca
  múltiple.
- 090 (18-06-2026): de enero a mayo de 2026, «más de 35 mil» reclamaciones por
  posible fraude; en la banca múltiple, 18 % más que en el mismo periodo de
  2025, y cerca de 49 % más en Sofipos y Sofomes.
- 096 (09-07-2026): de enero a junio de 2026, 43,871 «asuntos relacionados con
  posibles afectaciones financieras». **No dice que sean fraudes**, aunque la
  prensa los repita así: se ancla para que conste qué dice.

Lo que los comunicados **no** dicen, y por eso no se escribe: el total de 2025,
cuánto dinero se reclamó o se devolvió, ni si el 081 y el 090 cuentan lo mismo
(el 37.4 % de 22,199 da unas 8,300 en tres meses, y el 090 da más de 35 mil en
cinco). El Informe de Autoevaluación anual 2025 que dio un buscador no se pudo
abrir (07-11-2026) y, abierto desde México, la página dice que no existe.

Escribe docs/seguridad/condusef-fraude-2026.json.
"""
import hashlib
import html
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, 'docs', 'seguridad', 'condusef-fraude-2026.json')
BASE = 'https://www.gob.mx/condusef/prensa/'
COMUNICADOS = [
    ('081', '2026-05-28', 'condusef-alerta-sobre-incremento-de-fraudes-y-llama-a-fortalecer-la-educacion-financiera',
     'CONDUSEF alerta sobre incremento de fraudes y llama a fortalecer la educación financiera',
     'Comunicado 081', 'enero-marzo de 2026',
     [('reclamaciones', r'de las ([\d,]+) ?reclamaciones recibidas en CONDUSEF a nivel nacional'),
      ('fraude_pct', r'el ([\d.]+)% estuvieron relacionadas con un posible fraude'),
      ('banca_pct', r'de éstas, el (\d+)% corresponden a Banca Múltiple')]),
    ('090', '2026-06-18', 'condusef-y-seproban-unen-esfuerzos-para-fortalecer-el-combate-al-fraude-financiero-y-proteger-a-las-personas-usuarias-428880',
     'CONDUSEF y SEPROBAN unen esfuerzos para fortalecer el combate al fraude financiero y proteger a las personas usuarias',
     'Comunicado_90', 'enero-mayo de 2026',
     [('fraude_mas_de_mil', r'Más de (\d+) mil reclamaciones por posible fraude financiero se registraron entre enero y mayo de 2026'),
      ('banca_cambio_pct', r'aumentaron (\d+)% en la banca múltiple respecto al mismo periodo del año anterior'),
      ('sofi_cambio_pct', r'el incremento fue cercano al (\d+)%')]),
    ('096', '2026-07-09', 'mas-coordinacion-mas-prevencion-uif-y-condusef-firman-convenio-para-fortalecer-la-seguridad-del-sistema-financiero',
     'Más coordinación, más prevención: UIF y CONDUSEF firman convenio para fortalecer la seguridad del sistema financiero',
     'Comunicado 096', 'enero-junio de 2026',
     [('asuntos', r'la CONDUSEF registró (\d+) mil (\d{3}) asuntos relacionados con posibles afectaciones financieras')]),
]


def texto(ruta, marca):
    with open(ruta, encoding='utf-8') as f:
        t = f.read()
    m = re.search(r'class="article-body"[^>]*>(.*?)</div>', t, re.S)
    if not m:
        sys.exit('%s: la página ya no trae el cuerpo del comunicado (article-body)' % ruta)
    if marca not in t:
        sys.exit('%s: la página ya no dice «%s»' % (ruta, marca))
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', m.group(1)))).strip()


def _num(g):
    if len(g) > 1:
        return int(''.join(g))
    return float(g[0]) if '.' in g[0] else int(g[0].replace(',', ''))


def main(rutas):
    doc = {'fuente': 'CONDUSEF, comunicados de prensa en gob.mx', 'comunicados': []}
    for ruta, (num, fecha, slug, titulo, marca, periodo, cifras) in zip(rutas, COMUNICADOS):
        t = texto(ruta, marca)
        d = {'numero': num, 'fecha': fecha, 'titulo': titulo, 'url': BASE + slug, 'periodo': periodo,
             'sha_texto': hashlib.sha256(t.encode('utf-8')).hexdigest()}
        for clave, rx in cifras:
            m = re.search(rx, t)
            if not m:
                sys.exit('El comunicado %s ya no dice la cifra «%s»' % (num, clave))
            d[clave] = _num(m.groups())
            # La oración completa: un punto seguido de espacio la cierra (el de «37.4» no).
            ini = [x.end() for x in re.finditer(r'\.\s', t[:m.start()])]
            fin = re.compile(r'\.(\s|$)').search(t, m.end())
            cita = t[ini[-1] if ini else 0:fin.start() + 1].strip()
            if cita not in d.setdefault('citas', []):
                d['citas'].append(cita)
        doc['comunicados'].append(d)
    c81 = doc['comunicados'][0]
    if c81['reclamaciones'] != 22199:
        sys.exit('El comunicado 081 cambió su total: %s' % c81['reclamaciones'])
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write('\n')
    for d in doc['comunicados']:
        print(d['numero'], d['periodo'], {k: v for k, v in d.items() if isinstance(v, (int, float))})


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(sys.argv[1:])
