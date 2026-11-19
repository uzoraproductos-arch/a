#!/usr/bin/env python3
"""Las donatarias autorizadas, de las estadísticas del SAT (19-11-2026).

Pedido del autor: cuántas personas morales, asociaciones religiosas y
«diferentes regímenes fiscales». Las donatarias autorizadas (organizaciones
civiles y fideicomisos que pueden recibir donativos deducibles del ISR) las
publica el SAT en el Anexo 14 de la Resolución Miscelánea Fiscal (DOF) y las
resume en «Estadísticos Donatarias Autorizadas», un PDF de su micrositio:

  - cuántas hubo cada ejercicio desde 2020, y cuántas para recibir donativos
    del extranjero (convenio con EE. UU.);
  - las de 2026 por entidad federativa y por tipo de actividad (las claves
    A a L del Anexo 14);
  - revocaciones (LISR, art. 82-Quáter), cancelaciones a petición propia y
    autorizaciones que perdieron su vigencia.

Uso:
    python3 herramientas/anclar_donatarias.py            # descarga el PDF
    python3 herramientas/anclar_donatarias.py <archivo.pdf>

Escribe docs/sat/donatarias.json con la huella SHA-256 del PDF. Se detiene si
las entidades o los tipos de actividad no suman el total del año, o si el
total del año no es el del renglón de su ejercicio. Necesita pdftotext
(poppler-utils). Se corre a mano cada año, cuando el SAT publica el Anexo 14
de enero (fuentes.py, renglón «donatarias»).
"""
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, 'docs', 'sat', 'donatarias.json')
URL = 'https://www.sat.gob.mx/minisitio/DonatariasAutorizadas/documentos/padron_donatarias/EstadisticosDonatariasAutorizadas2026.pdf'
MICRO = 'https://www.sat.gob.mx/minisitio/DonatariasAutorizadas/index.html'
# Cómo escribe el SAT cada entidad en el PDF → clave de la base.
ENT = {'Aguascalientes': 'AGS', 'Baja California': 'BC', 'Baja California Sur': 'BCS', 'Campeche': 'CAM', 'Chiapas': 'CHIS',
       'Chihuahua': 'CHIH', 'Ciudad de México': 'CDMX', 'Coahuila de Zaragoza': 'COAH', 'Colima': 'COL', 'Durango': 'DGO',
       'Estado de México': 'MÉX', 'Guanajuato': 'GTO', 'Guerrero': 'GRO', 'Hidalgo': 'HGO', 'Jalisco': 'JAL',
       'Michoacán de Ocampo': 'MICH', 'Morelos': 'MOR', 'Nayarit': 'NAY', 'Nuevo Leon': 'NL', 'Nuevo León': 'NL', 'Oaxaca': 'OAX',
       'Puebla': 'PUE', 'Querétaro': 'QRO', 'Quintana Roo': 'QROO', 'San Luis Potosí': 'SLP', 'Sinaloa': 'SIN', 'Sonora': 'SON',
       'Tabasco': 'TAB', 'Tamaulipas': 'TAM', 'Tlaxcala': 'TLAX', 'Veracruz de Ignacio de La Llave': 'VER',
       'Veracruz de Ignacio de la Llave': 'VER', 'Yucatán': 'YUC', 'Zacatecas': 'ZAC'}
TIPOS = {'A': 'Asistenciales', 'B': 'Educativas', 'C': 'Investigación científica o tecnológica', 'D': 'Culturales', 'E': 'Becantes',
         'F': 'Ecológicas', 'G': 'Reproducción de especies en protección y peligro de extinción',
         'H': 'Apoyo económico de Donatarias Autorizadas', 'I': 'Obras o servicios públicos', 'J': 'Bibliotecas privadas',
         'K': 'Museos privados', 'L': 'Desarrollo social'}


def _n(s):
    return int(s.replace(',', ''))


def texto(pdf):
    return subprocess.run(['pdftotext', '-layout', pdf, '-'], check=True, capture_output=True).stdout.decode('utf-8')


def seccion(t, desde, hasta):
    i = t.index(desde)
    return t[i:t.index(hasta, i + len(desde))]


def main():
    if len(sys.argv) > 1:
        pdf = sys.argv[1]
    else:
        pdf = os.path.join(tempfile.mkdtemp(prefix='donatarias-'), 'estadisticos.pdf')
        req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0 (Auditavision; datos abiertos)'})
        with urllib.request.urlopen(req, timeout=90) as r, open(pdf, 'wb') as f:
            f.write(r.read())
    sha = hashlib.sha256(open(pdf, 'rb').read()).hexdigest()
    t = texto(pdf)

    def serie(desde, hasta):
        s = seccion(t, desde, hasta)
        return [(int(a), _n(b)) for a, b in re.findall(r'^\s+(20\d\d)\s*\d?\s+([\d,]+)(?:\s+-?[\d.]+)?\s*$', s, re.M)]

    anual = serie('Evolución del Padrón de Donatarias Autorizadas', 'Nota:')
    extranjero = serie('Donatarias Autorizadas para recibir donativos deducibles del extranjero', 'Donatarias Autorizadas 2026 por Entidad')
    anio = anual[-1][0]
    total = anual[-1][1]

    s = seccion(t, 'por Entidad federativa', 'Total general')
    por_ent = {}
    for nom, n in re.findall(r'^\s+([A-ZÁÉÍÓÚ][^\d\n]+?)\s{2,}([\d,]+)\s+[\d.]+%\s*$', s, re.M):
        nom = nom.strip()
        if nom not in ENT:
            sys.exit('Entidad que no reconozco en el PDF: «%s».' % nom)
        por_ent[ENT[nom]] = _n(n)
    tot_ent = _n(re.search(r'Total general\s+([\d,]+)', t).group(1))
    if len(por_ent) != 32 or sum(por_ent.values()) != tot_ent or tot_ent != total:
        sys.exit('Por entidad: %d entidades suman %s; el total general dice %s y el del ejercicio %d, %s.' % (
            len(por_ent), sum(por_ent.values()), tot_ent, anio, total))

    s = seccion(t, 'por Tipo de actividad', 'Nota:')
    por_tipo = {}
    for m in re.finditer(r'^\s+([A-L])\s+(?:[^\d\n]*?\s{2,})?([\d,]+)\s+[\d.]+%\s*$', s, re.M):
        por_tipo[m.group(1)] = _n(m.group(2))
    tot_tipo = _n(re.search(r'^\s+Total\s+([\d,]+)\s+100', s, re.M).group(1))
    if sorted(por_tipo) != sorted(TIPOS) or sum(por_tipo.values()) != tot_tipo or tot_tipo != total:
        sys.exit('Por tipo: claves %s suman %s; el total dice %s.' % (sorted(por_tipo), sum(por_tipo.values()), tot_tipo))

    def tabla(etq):
        """Revocaciones o cancelaciones: el renglón de años y el de cifras (el último año trae una llamada pegada)."""
        i = t.index(etq + ' por ejercicio fiscal')
        bloque = t[i:i + 1500]
        anios = re.search(r'^\s*Asunto\s*\n?((?:\s+20\d\d\d?)+)', bloque, re.M) or re.search(r'^((?:\s+20\d\d\d?){5,})\s*$', bloque, re.M)
        vals = re.search(r'^\s+' + etq + r'((?:\s+[\d,]+)+)\s*$', bloque, re.M)
        ys = [int(a[:4]) for a in anios.group(1).split()]
        vs = [_n(v) for v in vals.group(1).split()]
        if len(ys) != len(vs):
            sys.exit('%s: %d años y %d cifras.' % (etq, len(ys), len(vs)))
        return list(zip(ys, vs))

    revoc = tabla('Revocaciones')
    canc = tabla('Cancelaciones')
    s = seccion(t, 'Organizaciones cuya autorización perdió su vigencia', 'Al tratarse de una autorización')
    vig = [(int(a), _n(b), f) for a, b, f in re.findall(r'^\s+(20\d\d)\s+([\d,]+)\s+(\d\d/\d\d/20\d\d)\s*$', s, re.M)]
    corte_mov = re.search(r'Información con corte al ([0-9]+ de [a-z]+ (?:de )?20\d\d)', t)

    out = {
        'que': 'Donatarias autorizadas para recibir donativos deducibles del ISR (SAT, Estadísticos Donatarias Autorizadas)',
        'doc': {'tx': 'SAT, Estadísticos Donatarias Autorizadas %d (con base en el Anexo 14 de la RMF publicado en el DOF el 09-01-%d)' % (anio, anio),
                'url': URL, 'sha256': sha, 'micrositio': MICRO},
        'descarga': datetime.date.today().isoformat(),
        'anio': anio, 'total': total,
        'anual': anual, 'extranjero': extranjero,
        'por_entidad': por_ent,
        'por_tipo': por_tipo, 'tipos': TIPOS,
        'revocaciones': revoc, 'cancelaciones': canc,
        'corte_movimientos': corte_mov.group(1).replace(' 20', ' de 20').replace('de de', 'de') if corte_mov else None,
        'perdieron_vigencia': vig,
    }
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    open(SALIDA, 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    print('Donatarias %d: %s autorizadas; %s pueden recibir del extranjero; 32 entidades y 12 tipos cuadran. Escrito %s.' % (
        anio, format(total, ','), format(extranjero[-1][1], ','), os.path.relpath(SALIDA, RAIZ)))


if __name__ == '__main__':
    main()
