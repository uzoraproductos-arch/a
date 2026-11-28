#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""La base fiscal 2026-2027 (Ola 1, Ronda 38): cuatro JSON maestros en
docs/fiscal-2027/ y su validador. Aquí no se escribe ninguna cifra: se lee
de los JSON y se coteja contra el texto de su documento oficial.

Cada dato lleva `estado` (oficial / auditada / pendiente), su `fuente` (una
clave de fuentes.json), su artículo y su `cita`: el fragmento textual del
documento. El validador busca esa cita, palabra por palabra, en el archivo
de la fuente (los textos del DOF de investigaciones/fiscal-2027/ y los PDF de
investigaciones/leyes/), y revisa que cada valor numérico esté dentro de su
cita. Un dato `auditada` dice su `operacion`, y las que el validador sabe
rehacer las rehace. Un `pendiente` dice su motivo y la liga oficial donde
debe estar.

    python3 herramientas/fiscal_2027.py --prueba

Los PDF se leen con pdftotext (poppler). Donde no está instalado (la
revisión de GitHub), sus citas se saltan y se dice cuántas; las huellas de
los archivos, la estructura, las tarifas y los cuadres se revisan siempre.
"""
import calendar
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(RAIZ, 'docs', 'fiscal-2027')
MAESTROS = ['tarifas-y-topes.json', 'reforma-2027.json', 'fiscalizacion-y-plazos.json', 'calendario-y-pendientes-2027.json']
ESTADOS = ('oficial', 'auditada', 'pendiente')
OFICIALES = ('dof.gob.mx', 'www.diputados.gob.mx', 'www.sat.gob.mx', 'sjf2.scjn.gob.mx', 'www.inegi.org.mx', 'www.gob.mx', 'www.banxico.org.mx')
CAB = re.compile(r'CÁMARA DE DIPUTADOS DEL H\. CONGRESO|^\s*Secretaría General\s*$|Secretaría de Servicios Parlamentarios|^\s*\d+ de \d+\s*$'
                 r'|^\s*(LEY|CÓDIGO|REGLAMENTO) [A-ZÁÉÍÓÚÑ ,]+$|(Última [Rr]eforma|Nueva Ley|Nuevo Reglamento)( publicada)? DOF')


def norma(t, pdf=False):
    """El texto en una línea. De un PDF de la Cámara se quitan antes los encabezados de página."""
    if pdf:
        t = '\n'.join(l for l in t.split('\n') if not CAB.search(l))
    return re.sub(r'\s+', ' ', t).strip()


def sha(ruta):
    return hashlib.sha256(open(ruta, 'rb').read()).hexdigest()


def texto(ruta):
    """El texto normalizado de una fuente, o None si es un PDF y no hay pdftotext."""
    if ruta.endswith('.pdf'):
        if not shutil.which('pdftotext'):
            return None
        return norma(subprocess.run(['pdftotext', '-layout', ruta, '-'], capture_output=True, check=True).stdout.decode('utf-8'), True)
    return norma(open(ruta, encoding='utf-8').read())


def carga(nombre):
    return json.load(open(os.path.join(DIR, nombre), encoding='utf-8'))


# ---- Días hábiles (CFF, art. 12): la misma cuenta que usa el calendario.
def _lunes(anio, mes, n):
    d = datetime.date(anio, mes, 1)
    d += datetime.timedelta(days=(7 - d.weekday()) % 7)
    return d + datetime.timedelta(days=7 * (n - 1))


def inhabiles(anio):
    """Los días que el art. 12 del CFF no cuenta, además de sábados y domingos."""
    return {datetime.date(anio, 1, 1), _lunes(anio, 2, 1), _lunes(anio, 3, 3), datetime.date(anio, 5, 1), datetime.date(anio, 5, 5),
            datetime.date(anio, 9, 16), _lunes(anio, 11, 3), datetime.date(anio, 12, 25)}


def siguiente_habil(d):
    """Si el plazo vence en día inhábil, se recorre al siguiente hábil (CFF, art. 12)."""
    while d.weekday() >= 5 or d in inhabiles(d.year):
        d += datetime.timedelta(days=1)
    return d


def tramos(filas):
    """Una tarifa es continua si cada límite inferior es el superior anterior más un centavo."""
    errores = []
    for i, f in enumerate(filas):
        if i and round(f['inferior'] - filas[i - 1]['superior'], 2) != 0.01:
            errores.append('tramo %d: %s no sigue a %s' % (i + 1, f['inferior'], filas[i - 1]['superior']))
        if i and f['tasa'] <= filas[i - 1]['tasa']:
            errores.append('tramo %d: la tasa no sube' % (i + 1))
        if i:  # la cuota fija es la del tramo anterior más su ancho por su tasa
            a = filas[i - 1]
            esperado = a['cuota'] + (a['superior'] - a['inferior']) * a['tasa'] / 100
            if abs(esperado - f['cuota']) > 0.06:
                errores.append('tramo %d: cuota fija %s y sale %.2f' % (i + 1, f['cuota'], esperado))
    if filas and filas[-1]['superior'] is not None:
        errores.append('el último tramo debe ser «en adelante»')
    return errores


def _datos(nodo, ruta=''):
    """Todos los datos (objetos con `estado`) de un JSON maestro, con su ruta."""
    if isinstance(nodo, dict):
        if 'estado' in nodo and 'id' in nodo:
            yield ruta, nodo
        for k, v in nodo.items():
            yield from _datos(v, ruta + '/' + k)
    elif isinstance(nodo, list):
        for i, v in enumerate(nodo):
            yield from _datos(v, '%s[%d]' % (ruta, i))


def _numeros(v):
    """Los valores numéricos de un dato, para buscarlos en su cita."""
    if isinstance(v, bool):
        return
    if isinstance(v, (int, float)):
        yield v
    elif isinstance(v, dict):
        for x in v.values():
            yield from _numeros(x)
    elif isinstance(v, list):
        for x in v:
            yield from _numeros(x)


def _formas(n):
    """Cómo puede venir escrito un número en el documento."""
    f = set()
    for dec in (0, 1, 2, 4):
        if round(n, dec) == n:
            f.add(format(n, ',.%df' % dec))
            f.add(format(n, '.%df' % dec))
    return f


def revisa():
    errores, avisos = [], []
    fu = carga('fuentes.json')['fuentes']
    textos, sin_pdf = {}, 0
    for k, f in fu.items():
        if not any(f['url'].startswith('https://' + h + '/') for h in OFICIALES):
            errores.append('fuente %s: su liga no es de un portal oficial (%s)' % (k, f['url']))
        if 'www.dof.gob.mx' in f['url']:
            errores.append('fuente %s: el DOF se liga sin «www.»' % k)
        if not f.get('archivo'):
            if not f.get('sin_archivo'):
                errores.append('fuente %s: sin archivo y sin decir por qué' % k)
            continue
        ruta = os.path.join(RAIZ, f['archivo'])
        if not os.path.isfile(ruta):
            errores.append('fuente %s: falta %s' % (k, f['archivo']))
            continue
        if sha(ruta) != f['sha256']:
            errores.append('fuente %s: la huella de %s cambió; vuelve a cotejar sus citas' % (k, f['archivo']))
        textos[k] = texto(ruta)
    ids, cuenta = set(), {e: 0 for e in ESTADOS}
    for nombre in MAESTROS:
        doc = carga(nombre)
        for ruta, d in _datos(doc):
            donde = '%s%s (%s)' % (nombre, ruta, d['id'])
            if d['id'] in ids:
                errores.append('%s: id repetido' % donde)
            ids.add(d['id'])
            if d['estado'] not in ESTADOS:
                errores.append('%s: estado «%s»' % (donde, d['estado']))
                continue
            cuenta[d['estado']] += 1
            if not d.get('concepto'):
                errores.append('%s: sin concepto' % donde)
            if d['estado'] == 'pendiente':
                if not d.get('motivo') or not d.get('url') or not d.get('quien'):
                    errores.append('%s: un pendiente dice su motivo, quién lo debe y su liga oficial' % donde)
                elif not any(d['url'].startswith('https://' + h + '/') for h in OFICIALES):
                    errores.append('%s: la liga del pendiente no es oficial' % donde)
                continue
            if d['estado'] == 'auditada' and not d.get('operacion'):
                errores.append('%s: un dato auditado dice su operación' % donde)
            for c in d.get('citas') or []:
                if c['fuente'] not in fu:
                    errores.append('%s: fuente desconocida «%s»' % (donde, c['fuente']))
                    continue
                if not c.get('articulo') or not c.get('cita'):
                    errores.append('%s: cada cita lleva su artículo y su texto' % donde)
                    continue
                t = textos.get(c['fuente'])
                if t is None:
                    sin_pdf += 1
                elif norma(c['cita']) not in t:
                    errores.append('%s: la cita no está en %s: «%s…»' % (donde, fu[c['fuente']]['archivo'], c['cita'][:70]))
            if not d.get('citas'):
                errores.append('%s: sin cita' % donde)
            elif d['estado'] == 'oficial' and 'valor' in d and not d.get('tabla'):
                junto = ' '.join(c['cita'] for c in d['citas'])
                if d.get('en_letra'):  # el documento escribe la cantidad con letra
                    for x in d['en_letra']:
                        if x not in junto:
                            errores.append('%s: «%s» no aparece en su cita' % (donde, x))
                else:
                    for n in _numeros(d['valor']):
                        if not any(x in junto for x in _formas(n)):
                            errores.append('%s: el valor %s no aparece en su cita' % (donde, n))
            if d.get('vigencia_desde') and not re.match(r'^\d{4}-\d{2}-\d{2}$', d['vigencia_desde']):
                errores.append('%s: vigencia_desde va como AAAA-MM-DD' % donde)
    errores += _cuadres()
    if sin_pdf:
        avisos.append('%d citas de leyes en PDF no se cotejaron: aquí no hay pdftotext (sus huellas sí se revisaron)' % sin_pdf)
    return errores, avisos, cuenta


def _por_id():
    return {d['id']: d for n in MAESTROS for _, d in _datos(carga(n))}


def _cuadres():
    """Las cuentas que el validador rehace con los propios datos."""
    e, D = [], _por_id()

    def cerca(a, b, que, tol=0.005):
        if abs(a - b) > tol:
            e.append('cuadre: %s da %s y el dato dice %s' % (que, round(a, 4), b))
    uma = D['uma-2026']['valor']
    cerca(uma['diaria'] * 30.4, uma['mensual'], 'UMA diaria × 30.4')
    cerca(uma['mensual'] * 12, uma['anual'], 'UMA mensual × 12')
    for i, veces, base in (('exencion-aguinaldo', 30, 'diaria'), ('exencion-prima-vacacional', 15, 'diaria'), ('exencion-ptu', 15, 'diaria'),
                           ('exencion-prima-dominical', 1, 'diaria'), ('tope-deducciones-personales', 5, 'anual'),
                           ('tope-aportaciones-retiro', 5, 'anual'), ('tope-gastos-funerales', 1, 'anual')):
        cerca(veces * uma[base], D[i]['valor']['pesos'], '%s = %d UMA' % (i, veces))
    cerca(uma['mensual'] * D['subsidio-empleo-2026']['valor']['porcentaje_uma_mensual'] / 100, D['subsidio-empleo-mensual-pesos']['valor']['pesos'], 'subsidio = UMA mensual × porcentaje')
    for i in ('isr-tarifa-mensual-2026', 'isr-tarifa-anual-2026'):
        e += ['%s: %s' % (i, x) for x in tramos(D[i]['tabla'])]
    m, a = D['isr-tarifa-mensual-2026']['tabla'], D['isr-tarifa-anual-2026']['tabla']
    if [f['tasa'] for f in m] != [f['tasa'] for f in a]:
        e.append('las tarifas mensual y anual del ISR no tienen las mismas tasas')
    for i in ('resico-pf-mensual-2026', 'resico-pf-anual-2026', 'resico-pf-mensual-2027', 'resico-pf-anual-2027'):
        t = D[i]['tabla']
        if any(t[k]['hasta'] <= t[k - 1]['hasta'] or t[k]['tasa'] <= t[k - 1]['tasa'] for k in range(1, len(t))):
            e.append('%s: sus tramos no suben' % i)
    for anio in ('2026', '2027'):
        tope = D['resico-pf-tope-' + anio]['valor']['pesos']
        if D['resico-pf-anual-' + anio]['tabla'][-1]['hasta'] != tope or D['resico-pf-mensual-' + anio]['tabla'][-1]['hasta'] != tope:
            e.append('RESICO %s: el último tramo de sus tablas no es su tope' % anio)
        if [round(f['hasta'] * 12, 0) for f in D['resico-pf-mensual-' + anio]['tabla'][:-1]] != [f['hasta'] for f in D['resico-pf-anual-' + anio]['tabla'][:-1]]:
            e.append('RESICO %s: la tabla mensual × 12 no da la anual' % anio)
    iva = D['iva-opcional-resico-equilibrio']['valor']
    cerca((16 - D['iva-opcional-resico-7']['valor']['tasa']) / 16 * 100, iva['porcentaje'], 'punto de equilibrio del IVA opcional = (16 − 7) ÷ 16', 0.0001)
    cerca(D['recargos-prorroga-2027']['valor']['tasa_mensual'] * 1.5, D['recargos-mora-2027']['valor']['tasa_mensual'], 'recargos por mora = prórroga × 1.5')
    cerca(D['recargos-prorroga-2026']['valor']['tasa_mensual'] * 1.5, D['recargos-mora-2026']['valor']['tasa_mensual'], 'recargos por mora 2026 = prórroga × 1.5')
    for f in D['calendario-dia-17']['fechas']:
        y, mth = map(int, f['periodo_de_pago'].split('-'))
        d = siguiente_habil(datetime.date(y, mth, 17))
        if d.isoformat() != f['vence']:
            e.append('calendario: el 17 de %s recorre a %s y el dato dice %s' % (f['periodo_de_pago'], d, f['vence']))
    for i in ('calendario-anual-pm-2026', 'calendario-anual-pf-2026'):
        f = D[i]['valor']
        if siguiente_habil(datetime.date.fromisoformat(f['fecha_de_ley'])).isoformat() != f['vence']:
            e.append('%s: su vencimiento no es el siguiente día hábil' % i)
    return e


def main():
    if '--prueba' not in sys.argv:
        print(__doc__)
        return
    errores, avisos, cuenta = revisa()
    for a in avisos:
        print('fiscal_2027: aviso:', a)
    if errores:
        for x in errores:
            print('fiscal_2027: ERROR:', x)
        sys.exit(1)
    print('fiscal_2027: %d oficiales, %d auditadas y %d pendientes; citas, huellas, tarifas y cuadres en orden' % (cuenta['oficial'], cuenta['auditada'], cuenta['pendiente']))


if __name__ == '__main__':
    main()
