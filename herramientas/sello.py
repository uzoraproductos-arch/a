#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sube el sello de version de Auditavision.

GitHub Pages sirve cada archivo con cache-control: max-age=600. Sin un sello
en la direccion, el navegador del lector puede seguir enseñando la hoja de
estilos o el motor de hace un rato, y un cambio publicado y correcto parece
no haber ocurrido. Y sin un sello visible al pie no hay manera de saber si
quien reporta un problema esta viendo lo que acabamos de publicar o una copia
guardada: la respuesta deja de ser conjetura y pasa a ser un dato que el
lector puede leer en voz alta.

Uso:
    python3 herramientas/sello.py            # dice cual es el sello de hoy
    python3 herramientas/sello.py 20260923a  # lo sube a ese

Toca las cinco dependencias de index.html y el renglon del pie. Ejecutalo en
todo cambio que toque assets/; si no tocaste assets/, no hace falta.
Preserva los saltos de linea CRLF del archivo, que es la convencion del
proyecto.
"""
import os
import re
import sys
from datetime import date

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA = os.path.join(RAIZ, 'index.html')

ARCHIVOS = [
    ('href', 'assets/css/auditavision.css'),
    ('src', 'assets/js/mexico-states-geo.js'),
    ('src', 'assets/js/audit-database.js'),
    ('src', 'assets/js/municipios-efipem.js'),
    ('src', 'assets/js/audit-engine.js'),
]

VISIBLE = re.compile(r'<span class="footer-sello">[\s\S]*?</span>')


def sello_actual(d):
    m = re.search(r'id="selloVersion">([0-9a-z]+)<', d)
    return m.group(1) if m else None


def siguiente(actual):
    """El de hoy. Si ya hay uno de hoy, la letra que sigue."""
    hoy = date.today().strftime('%Y%m%d')
    if actual and actual.startswith(hoy):
        letra = actual[8:] or 'a'
        return hoy + chr(ord(letra[0]) + 1)
    return hoy + 'a'


def main():
    d = open(RUTA, 'rb').read().decode('utf-8')
    actual = sello_actual(d)

    if len(sys.argv) < 2:
        print('sello actual : %s' % (actual or 'ninguno'))
        print('sugerido     : %s' % siguiente(actual))
        print('para subirlo : python3 herramientas/sello.py %s' % siguiente(actual))
        return 0

    nuevo = sys.argv[1]
    if not re.fullmatch(r'\d{8}[a-z]?', nuevo):
        print('uso: sello.py AAAAMMDD[letra]   (por ejemplo 20260923a)')
        return 2

    cr_antes = len(re.findall(r'\r(?!\n)', d))

    for atributo, archivo in ARCHIVOS:
        pat = re.compile(r'%s="%s(\?v=[0-9a-z]+)?"' % (atributo, re.escape(archivo)))
        n = len(pat.findall(d))
        if n != 1:
            print('ERROR: %s aparece %d veces en index.html, se esperaba 1' % (archivo, n))
            return 1
        d = pat.sub('%s="%s?v=%s"' % (atributo, archivo, nuevo), d)

    renglon = ('<span class="footer-sello">Versión publicada: '
               '<b id="selloVersion">%s</b></span>' % nuevo)
    if VISIBLE.search(d):
        d = VISIBLE.sub(renglon, d)
    else:
        print('ERROR: no se encontro el renglon del pie (span.footer-sello)')
        return 1

    cr_despues = len(re.findall(r'\r(?!\n)', d))
    if cr_despues != cr_antes:
        print('ERROR: los CR sueltos pasaron de %d a %d' % (cr_antes, cr_despues))
        return 1
    if d.count('?v=' + nuevo) != 5 or d.count('id="selloVersion"') != 1:
        print('ERROR: el conteo final no cuadra')
        return 1

    open(RUTA, 'wb').write(d.encode('utf-8'))
    print('sello %s -> %s' % (actual or 'ninguno', nuevo))
    print('5 dependencias y el pie visible | CRLF intactos')
    return 0


if __name__ == '__main__':
    sys.exit(main())
