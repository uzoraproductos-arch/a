#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Respaldo de la base de datos de Supabase en CSV (paso 2.10 del plan v2,
27-10-2026).

Una plataforma de transparencia no puede depender de que un proveedor siga
existiendo: este script baja cada tabla a un CSV y escribe un manifiesto con
la huella SHA-256 de cada archivo, para comprobar después que el respaldo no
se tocó.

Dos modos:
    python3 herramientas/respaldo_base.py CARPETA
        Respaldo completo, con la llave de servicio. Trae datos personales
        (correos de quien aceptó el aviso de privacidad): la carpeta va FUERA
        del repositorio y se guarda cifrada.
    python3 herramientas/respaldo_base.py CARPETA --publico
        Solo lo público (erratas publicadas, evidencias, búsquedas en internet
        y donaciones), con la llave pública: sirve como datos abiertos.

Lee SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY (o SUPABASE_ANON_KEY con
--publico) del entorno; ninguna llave se escribe en un archivo. Solo Python
estándar: corre igual en Windows.
"""
import argparse
import csv
import datetime
import hashlib
import io
import json
import os
import sys
import urllib.request

# Todas las tablas de supabase/migrations/. Si una migración agrega una
# tabla, va aquí: main() compara esta lista con las migraciones y se detiene.
TABLAS = ['administradores', 'alertas', 'busquedas_web', 'consultas_ia', 'donaciones', 'envios', 'evidencias',
          'foro_hilos', 'foro_mensajes', 'limites', 'perfiles', 'portales_cache', 'preguntas_bot', 'suscripciones']
PUBLICAS = ['envios_publicos', 'evidencias', 'busquedas_web', 'donaciones']
PAGINA = 1000
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tablas_en_migraciones():
    import glob
    import re
    t = set()
    for f in glob.glob(os.path.join(RAIZ, 'supabase', 'migrations', '*.sql')):
        t |= set(re.findall(r'^create table public\.(\w+)', open(f, encoding='utf-8').read(), re.M))
    return t


def bajar(base, llave, tabla):
    filas, desde = [], 0
    while True:
        req = urllib.request.Request('%s/rest/v1/%s?select=*' % (base, tabla), headers={
            'apikey': llave, 'Authorization': 'Bearer ' + llave, 'Accept': 'application/json',
            'Range-Unit': 'items', 'Range': '%d-%d' % (desde, desde + PAGINA - 1)})
        with urllib.request.urlopen(req, timeout=120) as r:
            lote = json.loads(r.read().decode('utf-8'))
        filas += lote
        if len(lote) < PAGINA:
            return filas
        desde += PAGINA


def a_csv(filas):
    cols = sorted({k for f in filas for k in f})
    s = io.StringIO()
    w = csv.writer(s, lineterminator='\n')
    w.writerow(cols)
    for f in filas:
        w.writerow([json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else ('' if v is None else v)
                    for v in (f.get(c) for c in cols)])
    return s.getvalue()


def main(argv=None):
    ap = argparse.ArgumentParser(description='Respaldo de la base de Auditavisión en CSV')
    ap.add_argument('carpeta')
    ap.add_argument('--publico', action='store_true', help='solo lo público, con la llave pública')
    a = ap.parse_args(argv)
    falta = tablas_en_migraciones() - set(TABLAS)
    if falta:
        raise SystemExit('respaldo_base.py: hay tablas sin respaldo: %s (agrégalas a TABLAS)' % ', '.join(sorted(falta)))
    base = (os.environ.get('SUPABASE_URL') or '').rstrip('/')
    llave = os.environ.get('SUPABASE_ANON_KEY' if a.publico else 'SUPABASE_SERVICE_ROLE_KEY') or ''
    if not (base.startswith('https://') or base.startswith('http://127.0.0.1')) or not llave:
        raise SystemExit('respaldo_base.py: faltan SUPABASE_URL y %s en el entorno'
                         % ('SUPABASE_ANON_KEY' if a.publico else 'SUPABASE_SERVICE_ROLE_KEY'))
    dentro = os.path.abspath(a.carpeta).startswith(RAIZ + os.sep)
    if dentro and not a.publico:
        raise SystemExit('respaldo_base.py: el respaldo completo trae datos personales; guárdalo fuera del repositorio')
    sello = datetime.datetime.now().strftime('%Y%m%d-%H%M')
    dest = os.path.join(a.carpeta, 'respaldo-%s%s' % (sello, '-publico' if a.publico else ''))
    os.makedirs(dest, exist_ok=True)
    manifiesto = {'creado': sello, 'modo': 'público' if a.publico else 'completo', 'origen': base, 'tablas': {}}
    for t in (PUBLICAS if a.publico else TABLAS):
        filas = bajar(base, llave, t)
        datos = a_csv(filas).encode('utf-8')
        open(os.path.join(dest, t + '.csv'), 'wb').write(datos)
        manifiesto['tablas'][t] = {'renglones': len(filas), 'sha256': hashlib.sha256(datos).hexdigest()}
        print('  %-16s %6d renglones' % (t, len(filas)))
    with open(os.path.join(dest, 'manifiesto.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(manifiesto, f, ensure_ascii=False, indent=1)
    print('respaldo: %d tablas en %s' % (len(manifiesto['tablas']), dest))
    return 0


if __name__ == '__main__':
    sys.exit(main())
