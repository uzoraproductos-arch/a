#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Agente de busqueda de la fiscalizacion (pedido del autor, 21-10-2026).

Da una vuelta por las direcciones oficiales que lista fiscalizadores.py:

- cada entrega de la ASF de las Cuentas Publicas 2024 a 2027, en la
  direccion donde la ASF las publica (IR<año><a|b|c>/index.html); si la
  pagina ya existe, cuenta cuantos informes individuales enlaza;
- el portal de cada autoridad fiscalizadora.

No escribe cifras en la base: un dato nuevo solo entra a la plataforma
cuando alguien lo extrae de su documento oficial (extraer_mdb_asf.py,
integrar_cuenta_publica.py) con su huella. Lo que hace es decir, con fecha,
que ya esta publicado y falta integrarlo, que aun no aparece aunque la ley
ya lo exigia, o que el portal no respondio.

    python3 herramientas/agente_fiscalizacion.py          # da la vuelta
    python3 herramientas/agente_fiscalizacion.py --ver    # solo muestra el ultimo reporte

Escribe investigaciones/agente-fiscalizacion.json; sello.py pinta la pagina
con lo que diga ese archivo. Respeta el proxy y los certificados del
sistema: si un portal no se deja verificar, se reporta como «no respondio»;
nunca se desactiva la verificacion.
"""
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fiscalizadores as fz  # noqa: E402

AGENTE = 'Auditavision-agente-fiscalizacion/1.0 (+https://auditavision.com.mx/)'


def consultar(url):
    """(codigo HTTP, cuerpo) o (0, '') si no hubo respuesta verificable."""
    req = urllib.request.Request(url, headers={'User-Agent': AGENTE})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read(2_000_000).decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, ''
    except Exception:
        return 0, ''


def vuelta():
    hoy = datetime.date.today().isoformat()
    rep = {'fecha': hoy, 'entregas': {}, 'portales': {}}
    for e in fz.ENTREGAS:
        if not e[6]:
            continue
        http, cuerpo = consultar(e[6])
        r = {'http': http}
        if http == 200:
            n = len(set(re.findall(r'Documentos/Auditorias/[^"\']+\.pdf', cuerpo)))
            if n:
                r['informes'] = n
        rep['entregas'][e[0]] = r
    for a in fz.AUTORIDADES:
        if a[7]:
            rep['portales'][a[0]] = {'http': consultar(a[7])[0]}
    os.makedirs(os.path.dirname(fz.REPORTE), exist_ok=True)
    with open(fz.REPORTE, 'w', encoding='utf-8') as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
        f.write('\n')
    return rep


def mostrar(rep):
    hall = rep.get('entregas', {})
    print('Vuelta del %s' % rep['fecha'])
    for e in fz.ENTREGAS:
        st = fz.estado_entrega(e, hall, rep['fecha'])
        h = hall.get(e[0]) or {}
        print('  CP%d  %-42s %s  %-14s %s' % (e[1], e[3], e[4], st, ('%d informes' % h['informes']) if h.get('informes') else ''))
    for k, p in rep.get('portales', {}).items():
        print('  portal %-6s %s' % (k, p['http'] or 'sin respuesta'))
    nuevas = [e[0] for e in fz.ENTREGAS if fz.estado_entrega(e, hall, rep['fecha']) == 'publicada']
    if nuevas:
        print('\nPor integrar: %s' % ', '.join(nuevas))


if __name__ == '__main__':
    mostrar(fz.reporte() if '--ver' in sys.argv else vuelta())
