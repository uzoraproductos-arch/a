#!/usr/bin/env python3
"""Revisión semanal de la plataforma (Bloque 3 del plan, 27-10-2026).

Dos preguntas, cada lunes (.github/workflows/semanal.yml) o cuando quieras:

1. ¿Se cayó algún enlace a una fuente? Revisa cada enlace externo de las
   páginas publicadas (sin las fuentes tipográficas ni el propio sitio).
   Los portales de gobierno fallan seguido por unas horas: un enlace roto
   aquí es un aviso para revisarlo a mano, no una prueba de que el
   documento desapareció. Si de verdad ya no está, se busca su nueva
   dirección o se recurre a su copia en la bóveda (docs/boveda/).
2. ¿Ya salió un dato que esperamos? Los «vigías» de abajo: documentos con
   fecha de entrega por ley que la plataforma debe integrar en cuanto
   aparezcan. Al integrarlo, se cambia el vigía por el del periodo siguiente.

No cambia nada de la plataforma: escribe un reporte (docs/SEMANAL.md, y en
GitHub, el resumen de la ejecución). Termina con error solo si un vigía ya
salió, para que el aviso no pase de largo.

    python3 herramientas/semanal.py
    python3 herramientas/semanal.py --sin-enlaces     # solo los vigías

Corrección del 11-11-2026. El reporte del 09-11 dijo «13,937 enlaces
externos, 13,398 no abrieron» y no cupo en el resumen de GitHub: 13,304 de
esos enlaces van a un solo portal (la estadística judicial del CJF), que
dejó de contestar al recibir doce peticiones a la vez. Desde entonces:

- a cada portal se le pide de uno en uno, con pausa, y un enlace que falla
  se intenta una segunda vez;
- de un portal con más de MUESTRA enlaces se revisa una muestra repartida
  (se dice cuántos de cuántos): que conteste la muestra dice que el portal
  vive; no prueba cada enlace;
- el reporte agrupa por portal y se recorta para caber en el resumen;
- se suman los dos vigías que solo existen en la rama de trabajo (la lista
  69-B del SAT y las leyes citadas), en modo de solo lectura: GitHub
  programa las tareas desde `main`, y sus flujos propios no están ahí.
"""
import argparse
import concurrent.futures
import glob
import os
import re
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUERA = ('fonts.googleapis.com', 'fonts.gstatic.com', 'uzoraproductos-arch.github.io', 'auditavision.com.mx')

# Documentos que esperamos: (qué es, dirección donde aparecerá, qué hacer).
# Ojo: la ASF ya tiene en esa dirección un PDF de una página que dice
# «Próximamente se publicará el informe…» (155 KB, revisado el 27-10-2026):
# que el archivo exista no basta. Solo cuenta como publicado si pesa más de
# MIN_BYTES; el informe de marzo de 2026 trae 648 páginas.
MIN_BYTES = 1000000
MUESTRA = 40            # de un portal con más enlaces que esto se revisa una muestra
PAUSA = 0.4             # segundos entre dos peticiones al mismo portal
TOPE_RESUMEN = 900000   # GitHub corta el resumen de una ejecución en 1,024 KB
TOPE_LISTA = 400        # renglones de enlaces caídos que se escriben uno por uno

# Vigías que viven en su propio flujo (.github/workflows/vigia-*.yml). Esos
# flujos solo se programan si están en `main`; mientras no lleguen ahí, la
# revisión semanal (que sí está en `main`) los corre aquí, sin escribir nada.
VIGIAS_PROPIOS = [
# El último dato dice si un cambio termina la revisión con error: el del SAT
# sí (es raro y toca al Vigía de proveedores); el legislativo trae hallazgos
# casi cada día y solo se reporta, para que el aviso no se vuelva costumbre.
    ('Lista 69-B del SAT', ['vigia_69b.py'], os.path.join('docs', 'sat69b', 'bandeja.json'), True),
    ('Leyes y reglamentos citados', ['vigia_legislativo.py'], os.path.join('docs', 'legislativo', 'bandeja.json'), False),
]
VIGIAS = [
    # El de corte al 30 de septiembre de 2026 se integró el 11-11-2026.
    ('Informe semestral de la ASF con corte al 31 de marzo de 2027 (art. 38 de la LFRCF, a más tardar el 1 de mayo de 2027)',
     'https://www.asf.gob.mx/uploads/56_Informes_especiales_de_auditoria/IS_31_03_2027.pdf',
     'Cambiar DOC y ANT de herramientas/informe_semestral.py con sus cifras nuevas (y las de pendientes.py e informe_sancion.py que las citan), registrarlo en la bóveda y cambiar este vigía por el del corte al 30 de septiembre de 2027.'),
]


def pide(url, metodo='HEAD', tam=False):
    req = urllib.request.Request(url, method=metodo, headers={'User-Agent': 'Mozilla/5.0 (revision semanal de Auditavision)'})
    try:
        with urllib.request.urlopen(req, timeout=30, context=ssl.create_default_context()) as r:
            return (r.status, int(r.headers.get('Content-Length') or 0)) if tam else r.status
    except urllib.error.HTTPError as e:
        # Hay portales que no contestan HEAD: se intenta una vez con GET.
        if metodo == 'HEAD' and e.code in (403, 405, 501):
            return pide(url, 'GET', tam)
        return (e.code, 0) if tam else e.code
    except Exception as e:  # red, certificado, tiempo
        return (type(e).__name__, 0) if tam else type(e).__name__


def enlaces():
    usos = {}
    for f in sorted(glob.glob(os.path.join(RAIZ, '*.html'))):
        for u in re.findall(r'href="(https?://[^"#]+)', open(f, encoding='utf-8', errors='ignore').read()):
            u = u.replace('&amp;', '&')
            if not any(d in u for d in FUERA):
                usos.setdefault(u, set()).add(os.path.basename(f))
    return usos


def portal(u):
    return urlparse(u).netloc.lower()


def muestra(urls):
    """Los enlaces que de verdad se piden: todos, salvo en los portales con
    más de MUESTRA, donde se toma una muestra repartida y siempre la misma."""
    por = {}
    for u in sorted(urls):
        por.setdefault(portal(u), []).append(u)
    out = {}
    for h, us in por.items():
        if len(us) > MUESTRA:
            paso = len(us) / float(MUESTRA)
            us = [us[int(i * paso)] for i in range(MUESTRA)]
        out[h] = us
    return por, out


def revisa_portal(us):
    """Un portal, de uno en uno y con pausa; lo que falla se intenta otra vez."""
    res = {}
    for u in us:
        s = pide(u)
        if not (isinstance(s, int) and s < 400):
            time.sleep(2)
            s = pide(u)
        res[u] = s
        time.sleep(PAUSA)
    return res


def vigias_propios():
    """Corre los vigías de la rama y dice si su bandeja cambió. No guarda nada:
    al terminar deja la bandeja como estaba."""
    out, avisos = [], 0
    for que, cmd, bandeja, falla in VIGIAS_PROPIOS:
        ruta = os.path.join(RAIZ, bandeja)
        antes = open(ruta, 'rb').read() if os.path.exists(ruta) else None
        try:
            p = subprocess.run([sys.executable, os.path.join(RAIZ, 'herramientas', cmd[0])] + cmd[1:], cwd=RAIZ,
                               capture_output=True, text=True, timeout=900)
            salida, codigo = (p.stdout + p.stderr).strip().splitlines()[-3:], p.returncode
        except Exception as e:  # tiempo, red
            salida, codigo = [type(e).__name__], -1
        despues = open(ruta, 'rb').read() if os.path.exists(ruta) else None
        cambio = despues != antes
        if antes is None:
            if os.path.exists(ruta):
                os.remove(ruta)
        else:
            open(ruta, 'wb').write(antes)
        avisos += cambio and falla
        out.append('- %s **%s**: %s. Última línea del vigía: `%s`' % (
            '🆕' if cambio else ('⚠️' if codigo else '✅'),
            'HAY CAMBIOS' if cambio else ('no pudo correr' if codigo else 'sin cambios'), que,
            (salida[-1] if salida else 'sin salida').replace('`', "'")[:300]))
        if cambio:
            out.append('  Qué hacer: correr `python3 herramientas/%s` en la rama de trabajo, revisar `%s` e integrarlo.' % (cmd[0], bandeja))
    return out, avisos


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--sin-enlaces', action='store_true', help='solo revisa los vigías')
    ap.add_argument('--sin-propios', action='store_true', help='no corre los vigías de la rama (69-B y leyes)')
    a = ap.parse_args()
    out = ['# Revisión semanal', '', 'La escribe `herramientas/semanal.py`. No cambia nada de la plataforma.', '', '## Vigías: datos que esperamos', '']
    salieron = 0
    for que, url, hacer in VIGIAS:
        st, n = pide(url, tam=True)
        ya = st == 200 and n > MIN_BYTES
        aviso = st == 200 and not ya
        salieron += ya
        out.append('- %s **%s**: %s. %s' % ('🆕' if ya else '⏳', 'YA SALIÓ' if ya else 'todavía no' + (' (solo está el aviso de «próximamente», %d KB)' % (n // 1000) if aviso else ''),
                                           que, ('Qué hacer: ' + hacer) if ya else '[Dónde aparecerá](%s).' % url))
    if not a.sin_enlaces:
        usos = enlaces()
        por, pedir = muestra(usos)
        estado = {}
        with concurrent.futures.ThreadPoolExecutor(12) as ex:   # doce portales a la vez; cada portal, de uno en uno
            for res in ex.map(revisa_portal, pedir.values()):
                estado.update(res)
        rotos = sorted(u for u, s in estado.items() if not (isinstance(s, int) and s < 400))
        out += ['', '## Enlaces a fuentes', '',
                '%d enlaces externos en %d portales; se pidieron %d y %d no abrieron.' % (len(usos), len(por), len(estado), len(rotos)), '']
        muestreados = sorted((h for h in por if len(por[h]) > MUESTRA), key=lambda h: -len(por[h]))
        if muestreados:
            out += ['Portales revisados por muestra (%d enlaces repartidos de cada uno):' % MUESTRA, '']
            out += ['- `%s`: %d enlaces, %d de la muestra no abrieron' % (h, len(por[h]), sum(u in rotos for u in pedir[h])) for h in muestreados]
            out.append('')
        caidos = sorted(set(portal(u) for u in rotos), key=lambda h: -sum(portal(u) == h for u in rotos))
        if caidos:
            out += ['Por portal:', ''] + ['- `%s`: %d de %d pedidos no abrieron' % (h, sum(portal(u) == h for u in rotos), len(pedir[h])) for h in caidos] + ['']
        out += ['- `%s` → %s (en %s)' % (estado[u], u, ', '.join(sorted(usos[u])[:4]) + ('…' if len(usos[u]) > 4 else '')) for u in rotos[:TOPE_LISTA]]
        if len(rotos) > TOPE_LISTA:
            out.append('- … y %d más (la lista completa sale al correrlo en tu copia: `docs/SEMANAL.md`).' % (len(rotos) - TOPE_LISTA))
        print('semanal: %d enlaces externos, %d pedidos, %d no abrieron' % (len(usos), len(estado), len(rotos)))
    propios, avisos = ([], 0) if a.sin_propios else vigias_propios()
    if propios:
        out += ['', '## Vigías de la rama de trabajo (solo lectura)', '',
                'Sus flujos (`vigia-69b.yml`, `vigia-legislativo.yml`) no están en `main`, así que GitHub no los programa. '
                'Aquí se corren sin guardar nada: si hay cambios, toca integrarlos a mano.', ''] + propios
    texto = '\n'.join(out) + '\n'
    if len(texto.encode('utf-8')) > TOPE_RESUMEN:
        texto = texto.encode('utf-8')[:TOPE_RESUMEN].decode('utf-8', 'ignore') + '\n\n… (reporte recortado para caber en el resumen)\n'
    open(os.path.join(RAIZ, 'docs', 'SEMANAL.md'), 'w', encoding='utf-8').write(texto)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8').write(texto)
    print('semanal: %d de %d vigías ya salieron; %d vigías de la rama piden integrarse' % (salieron, len(VIGIAS), avisos))
    return 1 if (salieron or avisos) else 0


if __name__ == '__main__':
    raise SystemExit(main())
