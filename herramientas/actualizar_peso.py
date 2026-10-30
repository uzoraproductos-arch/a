#!/usr/bin/env python3
"""Pone al día «El peso en el tiempo» con Banxico (pedido del autor,
30-10-2026: «lo que necesitamos de INEGI y de Banxico es llenar nuestra base de
datos para que nuestro chat responda a través de nuestra base»).

Banxico sirve para llenar la base, no para que el chat le pregunte en cada
plática: este programa trae del Sistema de Información Económica (SIE) las
mismas series que ya están en `finanzas_sexenales.peso` de audit-database.js
y las escribe ahí. Al regenerar (sello.py), el chat, el Radar y la máquina del
tiempo del peso leen la cifra nueva de la base.

    BANXICO_TOKEN=... python3 herramientas/actualizar_peso.py

Series (las mismas que se cotejaron el 10-10-2026):
  SP1      INPC general, mensual, desde 1988           (peso.inpc)
  SF329    pesos por dólar, promedio mensual, desde 1988 (peso.usd)
  SF57923  pesos por euro, mensual, desde 2000          (peso.eur)
  SF43718  FIX, el dato más reciente                   (peso.hoy.usd)
  SF46410  euro, el dato más reciente                  (peso.hoy.eur)

El cotejo: cada mes que ya estaba en la base tiene que venir igual de Banxico.
Si uno cambió, o una serie llega con huecos, el programa se detiene sin
escribir nada (se revisa a mano: no entra una cifra sin cotejo). Solo agrega
los meses nuevos y el dato del día. La llave va en la variable de entorno,
nunca en un archivo.
"""
import datetime
import json
import os
import re
import sys
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'audit-database.js')
API = 'https://www.banxico.org.mx/SieAPIRest/service/v1/series/'
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
MENSUALES = {'inpc': ('SP1', '1988-01-01'), 'usd': ('SF329', '1988-01-01'), 'eur': ('SF57923', '2000-01-01')}


def pide(ruta, token):
    r = urllib.request.Request(API + ruta, headers={'Bmx-Token': token, 'Accept': 'application/json'})
    with urllib.request.urlopen(r, timeout=60) as x:
        return json.loads(x.read().decode('utf-8'))['bmx']['series']


def numero(t):
    t = str(t).replace(',', '').strip()
    return None if t in ('', 'N/E') else float(t)


def mensual(datos):
    """{'1988': [ene, feb, …]} a partir de [{'fecha': 'dd/mm/aaaa', 'dato': '…'}]."""
    m = {}
    for x in datos:
        v = numero(x['dato'])
        if v is None:
            continue
        _, mes, anio = x['fecha'].split('/')
        m.setdefault(anio, {})[int(mes)] = v
    out = {}
    for anio, meses in sorted(m.items()):
        if sorted(meses) != list(range(1, len(meses) + 1)):
            raise SystemExit('actualizar_peso: la serie trae huecos en %s (meses %s): se revisa a mano' % (anio, sorted(meses)))
        out[anio] = [meses[i] for i in range(1, len(meses) + 1)]
    return out


def mes_texto(anio, n):
    return '%s de %s' % (MESES[n - 1], anio)


def fecha_texto(d):
    return '%d de %s de %d' % (d.day, MESES[d.month - 1], d.year)


def cotejar(nombre, viejo, nuevo):
    """Lo que ya estaba tiene que venir igual. Devuelve los meses nuevos."""
    nuevos = 0
    for anio, vals in viejo.items():
        nv = nuevo.get(anio, [])
        for i, v in enumerate(vals):
            if i >= len(nv) or abs(nv[i] - v) > 1e-9 * max(1, abs(v)):
                raise SystemExit('actualizar_peso: %s de %s cambió en Banxico (%s → %s): se revisa a mano antes de escribir'
                                 % (nombre, mes_texto(anio, i + 1), v, nv[i] if i < len(nv) else 'sin dato'))
    for anio, nv in nuevo.items():
        nuevos += len(nv) - len(viejo.get(anio, []))
    return nuevos


def main():
    token = os.environ.get('BANXICO_TOKEN', '').strip()
    if not token:
        raise SystemExit('actualizar_peso: falta BANXICO_TOKEN (va en los secretos, nunca en un archivo)')
    raw = open(DB, 'rb').read().decode('utf-8')
    a = raw.index('"peso": {', raw.index('"finanzas_sexenales"')) + len('"peso": ')
    P, b = json.JSONDecoder().raw_decode(raw, a)
    hoy = datetime.date.today().isoformat()

    cambios = []
    for clave, (serie, desde) in MENSUALES.items():
        s = pide('%s/datos/%s/%s' % (serie, desde, hoy), token)[0]
        nuevo = mensual(s.get('datos') or [])
        n = cotejar(clave, P[clave]['mensual'], nuevo)
        if n:
            P[clave]['mensual'] = nuevo
            cambios.append('%s: %d mes(es) nuevo(s)' % (serie, n))
    # El último mes de cada serie, para los textos de sus fuentes.
    ult = {k: (max(P[k]['mensual']), len(P[k]['mensual'][max(P[k]['mensual'])])) for k in MENSUALES}

    dia = {x['idSerie']: x['datos'][0] for x in pide('SF43718,SF46410/datos/oportuno', token) if x.get('datos')}
    if 'SF43718' in dia and 'SF46410' in dia:
        f1 = datetime.datetime.strptime(dia['SF43718']['fecha'], '%d/%m/%Y').date()
        f2 = datetime.datetime.strptime(dia['SF46410']['fecha'], '%d/%m/%Y').date()
        if f1 == f2 and f1.isoformat() > P['hoy']['iso']:
            viejo_dia = P['hoy']['fecha']
            P['hoy'].update(fecha=fecha_texto(f1), iso=f1.isoformat(), usd=numero(dia['SF43718']['dato']), eur=numero(dia['SF46410']['dato']))
            F = P['fuentes']['BX_DIARIO']
            F['corto'] = F['corto'].replace(viejo_dia, P['hoy']['fecha'])
            F['doc'] = F['doc'].replace('Dato del ' + viejo_dia, 'Dato del ' + P['hoy']['fecha'])
            cambios.append('FIX y euro del %s' % P['hoy']['fecha'])

    if not cambios:
        print('actualizar_peso: sin cambios; la base ya tiene lo último de Banxico')
        return 0

    viejo_mes = P['hoy']['inpc_mes']
    P['hoy']['inpc_mes'] = mes_texto(*ult['inpc'])
    for k, f in (('inpc', 'BX_INPC'), ('usd', 'BX_USD'), ('eur', 'BX_EUR')):
        d = P['fuentes'][f]['doc']
        P['fuentes'][f]['doc'] = re.sub(r' a [a-z]+ de \d{4}\.', ' a %s.' % mes_texto(*ult[k]), d, count=1)
    P['consulta'] = fecha_texto(datetime.date.today())

    txt = json.dumps(P, ensure_ascii=False, indent=2)
    txt = '\n    '.join(txt.split('\n')).replace('\n', '\r\n')
    raw = raw[:a] + txt + raw[b:]
    # La nota del Radar dice con qué INPC se pasa a pesos de hoy.
    raw = raw.replace('por el INPC de %s entre el INPC promedio' % viejo_mes, 'por el INPC de %s entre el INPC promedio' % P['hoy']['inpc_mes'])
    open(DB, 'wb').write(raw.encode('utf-8'))
    print('actualizar_peso: ' + '; '.join(cambios) + ' (INPC hasta %s)' % P['hoy']['inpc_mes'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
