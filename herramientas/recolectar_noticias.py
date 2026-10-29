# -*- coding: utf-8 -*-
"""Mesa de redaccion: junta titulares de finanzas publicas para alimentar la
base (pedido del autor, 28-10-2026: «jalando noticias para ir alimentando
nuestra base de datos»).

Lee los buscadores de noticias (Bing Noticias y, de respaldo, Google
Noticias) con las busquedas de noticias.MESA y escribe docs/noticias/
bandeja.json, que la seccion «Mesa de redaccion» de noticias-relevantes.html
muestra rotulada «sin verificar». De cada nota guarda solo el titular, el
medio, la fecha, la liga, el tema y el dia en que la vimos; nunca su texto.
Lo que se verifica despues entra a columnas.js por integrar_al_momento.py.

    python3 herramientas/recolectar_noticias.py            # baja y guarda
    python3 herramientas/recolectar_noticias.py --prueba   # sin red, con un RSS de ejemplo

Corre a mano o desde GitHub (.github/workflows/mesa-de-redaccion.yml).
"""
import datetime
import email.utils
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

import noticias

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, noticias.BANDEJA)
MAXIMO = 400        # notas que se conservan en la bandeja
POR_TEMA = 15       # titulares nuevos por tema en cada corrida
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre',
         'noviembre', 'diciembre']


def bing(q):
    return 'https://www.bing.com/news/search?' + urllib.parse.urlencode({'q': q, 'format': 'rss', 'setlang': 'es-MX', 'cc': 'MX'})


def google(q):
    return 'https://news.google.com/rss/search?' + urllib.parse.urlencode({'q': q, 'hl': 'es-419', 'gl': 'MX', 'ceid': 'MX:es-419'})


def bajar(url):
    pet = urllib.request.Request(url, headers={'User-Agent': 'Auditavision-mesa/1.0 (+https://github.com/uzoraproductos-arch/a)'})
    with urllib.request.urlopen(pet, timeout=30) as r:
        return r.read()


def liga_real(u):
    """Bing envuelve la liga (apiclick.aspx?...&url=...): se saca la del medio."""
    if 'bing.com' in u:
        q = urllib.parse.parse_qs(urllib.parse.urlparse(u).query)
        if q.get('url'):
            return q['url'][0]
    return u


def fecha_txt(d):
    return '%d de %s de %d' % (d.day, MESES[d.month - 1], d.year)


def leer(xml, tema):
    raiz = ET.fromstring(xml)
    out = []
    for it in raiz.iter('item'):
        tit = (it.findtext('title') or '').strip()
        medio = (it.findtext('source') or '').strip()
        if not medio:
            for h in it:
                if h.tag.lower().endswith('source'):
                    medio = (h.text or '').strip()
        if medio and tit.endswith(' - ' + medio):
            tit = tit[:-(len(medio) + 3)]
        elif not medio and re.search(r' - [^-]+$', tit):
            tit, medio = tit.rsplit(' - ', 1)
        url = liga_real((it.findtext('link') or '').strip())
        if not tit or not re.match(r'https?://', url):
            continue
        f = ''
        try:
            d = email.utils.parsedate_to_datetime(it.findtext('pubDate') or '')
            f = fecha_txt(d)
        except (TypeError, ValueError):
            pass
        out.append({'titulo': tit, 'medio': medio, 'fecha': f, 'url': url, 'tema': tema})
    return out


EJEMPLO = b'''<?xml version="1.0"?><rss xmlns:News="https://www.bing.com/news/search?q=&amp;format=rss"><channel>
<item><title>Hacienda presenta el informe trimestral</title><link>https://www.bing.com/news/apiclick.aspx?ref=FexRss&amp;url=https%3a%2f%2fejemplo.mx%2fnota&amp;c=1</link>
<pubDate>Wed, 28 Oct 2026 15:00:00 GMT</pubDate><News:Source>Medio de ejemplo</News:Source></item>
<item><title>La ASF entrega auditorias - Otro medio</title><link>https://ejemplo.mx/otra</link><pubDate>Tue, 27 Oct 2026 10:00:00 GMT</pubDate></item>
</channel></rss>'''


def main():
    prueba = '--prueba' in sys.argv
    hoy = fecha_txt(datetime.date.today())
    try:
        previa = json.load(open(SALIDA, encoding='utf-8'))
    except (OSError, ValueError):
        previa = {}
    viejas = previa.get('notas') or []
    vistas = {n['url'] for n in viejas} | {n['titulo'].lower() for n in viejas}
    nuevas, fallas = [], []
    for tema, _t, q in noticias.MESA:
        lista = []
        for fuente in ([lambda: EJEMPLO] if prueba else [lambda: bajar(bing(q)), lambda: bajar(google(q))]):
            try:
                lista = leer(fuente(), tema)
            except Exception as e:  # red caida o RSS roto: se prueba el respaldo
                fallas.append('%s: %s' % (tema, e))
                continue
            if lista:
                break
        k = 0
        for n in lista:
            if n['url'] in vistas or n['titulo'].lower() in vistas or k >= POR_TEMA:
                continue
            vistas.update([n['url'], n['titulo'].lower()])
            n['visto'] = hoy
            nuevas.append(n)
            k += 1
    datos = {'actualizado': hoy if nuevas or not previa.get('actualizado') else previa['actualizado'],
             'nota': 'Titulares que junta herramientas/recolectar_noticias.py, sin verificar. Solo titular, medio, fecha y liga; nunca el texto de la nota.',
             'notas': (nuevas + viejas)[:MAXIMO]}
    if prueba:
        print(json.dumps(datos['notas'][:2], ensure_ascii=False, indent=1))
        return 0 if len(nuevas) >= 2 and nuevas[0]['url'] == 'https://ejemplo.mx/nota' and nuevas[1]['medio'] == 'Otro medio' else 1
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('mesa de redaccion: %d titulares nuevos, %d en la bandeja%s' % (
        len(nuevas), len(datos['notas']), ('; fallas: ' + '; '.join(fallas)) if fallas else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())
