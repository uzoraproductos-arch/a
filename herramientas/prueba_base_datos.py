#!/usr/bin/env python3
"""Prueba la base de datos de Supabase en un PostgreSQL local, sin cuenta ni
red (pedido del autor, 24-10-2026: «se necesita construir la base de datos»).

Levanta un PostgreSQL temporal, le pone lo mínimo de Supabase
(supabase/pruebas/supabase_simulado.sql), corre todas las migraciones de
supabase/migrations/ en orden y luego supabase/pruebas/permisos.sql, que
comprueba la seguridad por renglón: qué ve y qué puede escribir el público,
una persona con cuenta y la administración. Al terminar borra todo.

    python3 herramientas/prueba_base_datos.py

Necesita PostgreSQL 14 o más nuevo (initdb, pg_ctl, psql). Se detiene con
error si una sola prueba falla.
"""
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SB = os.path.join(RAIZ, 'supabase')


def binario(nombre):
    for d in sorted(glob.glob('/usr/lib/postgresql/*/bin'), reverse=True):
        if os.path.exists(os.path.join(d, nombre)):
            return os.path.join(d, nombre)
    ruta = shutil.which(nombre)
    if not ruta:
        raise SystemExit('prueba_base_datos.py: falta %s (PostgreSQL)' % nombre)
    return ruta


def main():
    tmp = tempfile.mkdtemp(prefix='auditavision-db-')
    datos, sock = os.path.join(tmp, 'datos'), os.path.join(tmp, 'sock')
    os.mkdir(sock)
    env = dict(os.environ)
    # initdb no corre como root: si es el caso, se usa el usuario postgres.
    pre = []
    if os.geteuid() == 0:
        shutil.chown(tmp, 'postgres')
        shutil.chown(sock, 'postgres')
        pre = ['runuser', '-u', 'postgres', '--']
    try:
        subprocess.run(pre + [binario('initdb'), '-D', datos, '-U', 'postgres', '-A', 'trust', '-E', 'UTF8', '--locale=C.UTF-8'],
                       check=True, stdout=subprocess.DEVNULL, env=env)
        subprocess.run(pre + [binario('pg_ctl'), '-D', datos, '-o', '-k %s -c listen_addresses=""' % sock, '-w', '-l', os.path.join(tmp, 'log'), 'start'],
                       check=True, stdout=subprocess.DEVNULL, env=env)
        archivos = [os.path.join(SB, 'pruebas', 'supabase_simulado.sql')]
        archivos += sorted(glob.glob(os.path.join(SB, 'migrations', '*.sql')))
        archivos += [os.path.join(SB, 'pruebas', 'permisos.sql')]
        for a in archivos:
            r = subprocess.run([binario('psql'), '-h', sock, '-U', 'postgres', '-d', 'postgres', '-X', '-q',
                                '-v', 'ON_ERROR_STOP=1', '-f', a], capture_output=True, text=True, env=env)
            for linea in (r.stdout + r.stderr).splitlines():
                # Solo lo que dice la prueba (NOTICE, ERROR, el aviso final), sin las tablas de psql.
                if re.search(r'NOTICE|ERROR|FALLA|pasaron', linea):
                    print('   ' + re.sub(r'^psql:[^:]+:\d+: (NOTICE:  )?', '', linea))
            if r.returncode:
                raise SystemExit('prueba_base_datos.py: falló %s' % os.path.relpath(a, RAIZ))
            print('ok  %s' % os.path.relpath(a, RAIZ))
    finally:
        subprocess.run(pre + [binario('pg_ctl'), '-D', datos, '-m', 'immediate', 'stop'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
        shutil.rmtree(tmp, ignore_errors=True)
    print('prueba_base_datos: la migración carga y la seguridad por renglón se cumple')


if __name__ == '__main__':
    sys.exit(main())
