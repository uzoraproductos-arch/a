#!/usr/bin/env python3
"""El valor de la UDI, de Banxico (19-11-2026).

Lo usa el simulador de venta de un inmueble (cc_inmueble.py): la casa
habitación está exenta del ISR hasta 700,000 unidades de inversión (LISR,
art. 93, fr. XIX, inciso a). Banxico publica la UDI de cada día por
adelantado en su cuadro CP150 del Sistema de Información Económica, que se
lee sin llave.

Uso:
    python3 herramientas/anclar_udi.py              # consulta el cuadro
    python3 herramientas/anclar_udi.py <cuadro.html>

Escribe docs/sat/udi.json con el último valor publicado y su fecha. Se
detiene si el cuadro no trae tantas fechas como valores, o si el valor sale
de un rango sensato (de 1 a 50 pesos), señal de que cambió el formato.
"""
import datetime
import json
import os
import re
import sys
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, 'docs', 'sat', 'udi.json')
URL = 'https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?sector=8&accion=consultarCuadro&idCuadro=CP150&locale=es'


def main():
    if len(sys.argv) > 1:
        h = open(sys.argv[1], encoding='utf-8', errors='replace').read()
    else:
        req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0 (Auditavision; datos abiertos)'})
        h = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', errors='replace')
    i = h.index('tdObservacion') if 'tdObservacion' in h else -1
    if i < 0:
        sys.exit('El cuadro CP150 de Banxico no trae valores: revisar a mano.')
    cab = h[:i]
    fechas = re.findall(r'^\s*(\d\d/\d\d/20\d\d)\s*$', cab, re.M)
    valores = re.findall(r'tdObservacion[^>]*>\s*([\d.]+)\s*<', h)
    if not valores or len(fechas) < len(valores):
        sys.exit('El cuadro trae %d fechas y %d valores: revisar a mano.' % (len(fechas), len(valores)))
    fechas = fechas[-len(valores):]
    f, v = fechas[-1], float(valores[-1])
    if not 1 < v < 50:
        sys.exit('Valor de UDI fuera de rango: %s' % v)
    d, m, a = f.split('/')
    out = {'que': 'Valor de la unidad de inversión (UDI), pesos por UDI', 'fecha': '%s-%s-%s' % (a, m, d), 'valor': v,
           'serie': [['%s-%s-%s' % tuple(reversed(x.split('/'))), float(y)] for x, y in zip(fechas, valores)],
           'fuente': 'Banco de México, Sistema de Información Económica, cuadro CP150 «Valores de UDIS» (serie SP68257)', 'url': URL,
           'consulta': datetime.date.today().isoformat()}
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    if os.path.exists(SALIDA):
        viejo = json.load(open(SALIDA, encoding='utf-8'))
        if viejo.get('fecha') == out['fecha'] and viejo.get('valor') == v:
            print('UDI: sin cambio (%s, %s).' % (out['fecha'], v))
            return
    open(SALIDA, 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    print('UDI del %s: %s pesos. Escrito %s.' % (out['fecha'], v, os.path.relpath(SALIDA, RAIZ)))


if __name__ == '__main__':
    main()
