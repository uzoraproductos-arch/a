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

Toca las siete dependencias de index.html y el renglon del pie. Ejecutalo en
todo cambio que toque assets/; si no tocaste assets/, no hace falta.
Preserva los saltos de linea CRLF del archivo, que es la convencion del
proyecto.
"""
import os
import re
import sys
from datetime import date

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Solo index.html y sus copias en assets/auditor/. La Enciclopedia es un proyecto
# aparte (decisión del autor, 27-09-2026): ni ella ni los archivos que carga
# (assets/css, assets/js, assets/data) se tocan sin que el autor lo pida.
RUTAS = [os.path.join(RAIZ, 'index.html')]

ARCHIVOS = [
    ('href', 'assets/auditor/css/auditavision.css'),
    ('href', 'assets/auditor/css/civico.css'),
    ('href', 'assets/auditor/css/puerta.css'),
    ('src', 'assets/auditor/js/mexico-states-geo.js'),
    ('src', 'assets/auditor/js/audit-database.js'),
    ('src', 'assets/auditor/js/municipios-efipem.js'),
    ('src', 'assets/auditor/js/municipios-rendicion.js'),
    ('src', 'assets/auditor/js/audit-engine.js'),
    ('src', 'assets/auditor/js/comunidad.js'),
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
        # Despues de la z sigue za, zb...: el dia no se acaba con el alfabeto.
        if letra == 'z':
            return hoy + 'za'
        return hoy + letra[:-1] + chr(ord(letra[-1]) + 1)
    return hoy + 'a'


def main():
    d_first = open(RUTAS[0], 'rb').read().decode('utf-8')
    actual = sello_actual(d_first)

    if len(sys.argv) < 2:
        print('sello actual : %s' % (actual or 'ninguno'))
        print('sugerido     : %s' % siguiente(actual))
        print('para subirlo : python3 herramientas/sello.py %s' % siguiente(actual))
        return 0

    nuevo = sys.argv[1]
    if not re.fullmatch(r'\d{8}[a-z]{0,2}', nuevo):
        print('uso: sello.py AAAAMMDD[letra]   (por ejemplo 20260923a)')
        return 2

    for ruta in RUTAS:
        nombre = os.path.basename(ruta)
        d = open(ruta, 'rb').read().decode('utf-8')
        cr_antes = len(re.findall(r'\r(?!\n)', d))

        for atributo, archivo in ARCHIVOS:
            pat = re.compile(r'%s="%s(\?v=[0-9a-z]+)?"' % (atributo, re.escape(archivo)))
            n = len(pat.findall(d))
            if n != 1:
                print('ERROR: %s aparece %d veces en %s, se esperaba 1' % (archivo, n, nombre))
                return 1
            d = pat.sub('%s="%s?v=%s"' % (atributo, archivo, nuevo), d)

        renglon = ('<span class="footer-sello">Versión publicada: '
                   '<b id="selloVersion">%s</b></span>' % nuevo)
        if VISIBLE.search(d):
            d = VISIBLE.sub(renglon, d)
        else:
            print('ERROR: no se encontro el renglon del pie (span.footer-sello) en %s' % nombre)
            return 1

        cr_despues = len(re.findall(r'\r(?!\n)', d))
        if cr_despues != cr_antes:
            print('ERROR: los CR sueltos pasaron de %d a %d en %s' % (cr_antes, cr_despues, nombre))
            return 1
        if d.count('?v=' + nuevo) != len(ARCHIVOS) or d.count('id="selloVersion"') != 1:
            print('ERROR: el conteo final no cuadra en %s' % nombre)
            return 1

        open(ruta, 'wb').write(d.encode('utf-8'))
        print('sello %s -> %s en %s (%d dependencias y pie visible | CRLF intactos)' % 
              (actual or 'ninguno', nuevo, nombre, len(ARCHIVOS)))
    # Las paginas de apartado (herramientas.html, aprende.html...) llevan el
    # mismo sello: se regeneran con el nuevo.
    import apartados
    return apartados.generar(nuevo)


if __name__ == '__main__':
    sys.exit(main())
