#!/usr/bin/env python3
"""El padrón de contribuyentes del SAT (19-11-2026).

Pedido del autor: «¿podemos obtener información de cuántos contribuyentes
están registrados en el SAT, cuántas personas morales… diferentes regímenes
fiscales…?». El SAT lo publica en sus datos abiertos (Datos Abiertos ›
Padrón), en cinco hojas de Excel con una serie mensual desde 2010:

  PorTipoContribuyente.xls   activos por tipo (físicas, asalariados, morales, grandes)
  PorSitRFC21.xls            activos, suspendidos y cancelados
  PadronPorRegimen2.xls      activos por régimen fiscal
  PorEntFed.xls              activos por entidad federativa (domicilio fiscal)
  SectorActEco.xls           activos por sector de actividad (trimestral)

Uso:
    python3 herramientas/anclar_padron_sat.py            # descarga los cinco
    python3 herramientas/anclar_padron_sat.py <carpeta>  # usa los ya bajados

Escribe docs/sat/padron-sat.json con la huella SHA-256 de cada archivo, su
corte y las series. Lo leen padron_sat.py (las páginas de Datos y el chat) y
planisferio.py (las lentes del padrón).

Se detiene sin escribir nada si:
  - una hoja cambia sus columnas;
  - los cinco tipos no suman el total que el SAT da en cada mes;
  - el total por tipo no es el número de activos de la hoja por situación;
  - en los últimos 12 meses las entidades no suman el total (en enero y
    febrero de 2010 el propio SAT no cuadra por 234: se anota, no se corrige);
  - los sectores del último trimestre no suman los activos de su mes;
  - las cinco hojas no traen el mismo último mes.
Necesita xlrd (las hojas son .xls de Excel 97).
"""
import datetime
import hashlib
import json
import os
import sys
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, 'docs', 'sat', 'padron-sat.json')
PAGINA = 'https://www.sat.gob.mx/minisitio/DatosAbiertos/padron.html'
BASE = 'https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Cifras_SAT/Documents/'
MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
TRIM = {'Primero': 3, 'Segundo': 6, 'Tercero': 9, 'Cuarto': 12}

# Las columnas tal como las encabeza el SAT, con nuestra clave corta.
TIPO = [('pf', 'Personas Físicas'), ('gpf', 'Grandes Contribuyentes (PF)'), ('asal', 'Asalariados (PF)'),
        ('pm', 'Personas Morales'), ('gpm', 'Grandes Contribuyentes (PM)'), ('total', 'Total')]
SIT = [('act', 'Activos'), ('sus', 'Suspendidos'), ('can', 'Cancelados')]
REGIMEN = [
    ('rg_pm', 'Régimen general de Ley personas morales'),
    ('simp_pm', 'Régimen simplificado de Ley personas morales'),
    ('nolucro', 'Personas morales con fines no lucrativos'),
    ('repecos', 'Régimen de pequeños contribuyentes'),
    ('sueldos', 'Régimen de sueldos y salarios e ingresos asimilados a salarios'),
    ('arrend', 'Régimen de arrendamiento'),
    ('enaj', 'Régimen de enajenación o adquisición de bienes'),
    ('demas', 'Régimen de los demás ingresos'),
    ('consol', 'Régimen de consolidación'),
    ('extranj', 'Régimen residentes en el extranjero sin establecimiento permanente en México'),
    ('divid', 'Régimen de ingresos por dividendos (socios y accionistas)'),
    ('aepf', 'Régimen de las personas físicas con actividades empresariales y profesionales'),
    ('interm', 'Régimen intermedio de las personas físicas con actividades empresariales'),
    ('interes', 'Régimen de los ingresos por intereses'),
    ('premios', 'Régimen de los ingresos por obtención de premios'),
    ('sinobl', 'Sin obligaciones fiscales'),
    ('pemex', 'Pemex'),
    ('simp_pf', 'Régimen simplificado de ley personas físicas'),
    ('prest', 'Ingresos por la obtención de préstamos'),
    ('coop', 'Sociedades cooperativas de producción que optan por diferir sus ingresos.'),
    ('rif', 'Régimen de incorporación fiscal'),
    ('agro', 'Régimen de actividades agrícolas, ganaderas, silvícolas y pesqueras'),
    ('grupos', 'Régimen opcional para grupos de sociedades'),
    ('coord', 'Régimen de los coordinados'),
    ('plataf', 'Actividades Empresariales con ingresos a través de Plataformas Tecnológicas'),
    ('resico', 'Régimen Simplificado de Confianza'),
]
ENTIDADES = ['Aguascalientes', 'Baja California', 'Baja California Sur', 'Campeche', 'Chiapas', 'Chihuahua', 'Coahuila', 'Colima',
             'Ciudad de México', 'Durango', 'Estado de México', 'Guanajuato', 'Guerrero', 'Hidalgo', 'Jalisco', 'Michoacán', 'Morelos',
             'Nayarit', 'Nuevo León', 'Oaxaca', 'Puebla', 'Querétaro', 'Quintana Roo', 'San Luis Potosí', 'Sinaloa', 'Sonora', 'Tabasco',
             'Tamaulipas', 'Tlaxcala', 'Veracruz', 'Yucatán', 'Zacatecas', 'No especificado']
# Clave de cada entidad en la base (abbr de AUDIT_DB.estados), en el orden del SAT.
ABBR = ['AGS', 'BC', 'BCS', 'CAM', 'CHIS', 'CHIH', 'COAH', 'COL', 'CDMX', 'DGO', 'MÉX', 'GTO', 'GRO', 'HGO', 'JAL', 'MICH', 'MOR',
        'NAY', 'NL', 'OAX', 'PUE', 'QRO', 'QROO', 'SLP', 'SIN', 'SON', 'TAB', 'TAM', 'TLAX', 'VER', 'YUC', 'ZAC', None]
SECTOR = [
    ('gob', 'Actividades del gobierno y de organismos internacionales y extraterritoriales'),
    ('agro', 'Agricultura, ganadería, aprovechamiento forestal, pesca y caza'),
    ('mayor', 'Comercio al por mayor'), ('menor', 'Comercio al por menor'), ('constr', 'Construcción'),
    ('corp', 'Dirección de corporativos y empresas'),
    ('elec', 'Electricidad, agua y suministro de gas por ductos al consumidor final'),
    ('manuf', 'Industrias manufactureras'), ('info', 'Información en medios masivos'), ('mineria', 'Minería'), ('otros', 'Otros'),
    ('otserv', 'Otros servicios excepto actividades del gobierno'),
    ('aloj', 'Servicios de alojamiento temporal y de preparación de alimentos y bebidas'),
    ('apoyo', 'Servicios de apoyo a los negocios y manejo de desechos y servicios de remediación'),
    ('esparc', 'Servicios de esparcimiento culturales y deportivos, y otros servicios recreativos'),
    ('salud', 'Servicios de salud y de asistencia social'), ('educ', 'Servicios educativos'),
    ('finan', 'Servicios financieros y de seguros'),
    ('inmob', 'Servicios inmobiliarios y de alquiler de bienes muebles e intangibles'),
    ('prof', 'Servicios profesionales, científicos y técnicos'),
    ('transp', 'Transportes, correos y almacenamiento'),
]
HOJAS = {'tipo': ('PorTipoContribuyente.xls', TIPO), 'sit': ('PorSitRFC21.xls', SIT), 'reg': ('PadronPorRegimen2.xls', REGIMEN),
         'ent': ('PorEntFed.xls', [(e, e) for e in ENTIDADES]), 'sec': ('SectorActEco.xls', SECTOR)}


def _plano(s):
    return ' '.join(str(s).replace('\n', ' ').split()).rstrip('.').lower()


def leer(ruta, columnas):
    """Las filas de datos de una hoja, verificando su encabezado."""
    import xlrd
    s = xlrd.open_workbook(ruta).sheet_by_index(0)
    enc = None
    for r in range(min(12, s.nrows)):
        if str(s.cell_value(r, 1)).strip() == 'Año':
            enc = r
            break
    if enc is None:
        sys.exit('%s: no encontré el encabezado «Año».' % os.path.basename(ruta))
    H = [_plano(x) for x in s.row_values(enc)[3:3 + len(columnas)]]
    esperado = [_plano(n) for _, n in columnas]
    for h, e in zip(H, esperado):
        # El SAT recorta algunos nombres largos; basta con que empiecen igual.
        if not (h == e or (len(h) >= 30 and e.startswith(h)) or (len(e) >= 30 and h.startswith(e))):
            sys.exit('%s cambió sus columnas: «%s» en lugar de «%s». Revisar a mano.' % (os.path.basename(ruta), h, e))
    if len(H) != len(esperado) or str(s.cell_value(enc, 3 + len(columnas)) if s.ncols > 3 + len(columnas) else '').strip():
        sys.exit('%s trae otro número de columnas. Revisar a mano.' % os.path.basename(ruta))
    filas, notas = [], []
    for r in range(enc + 1, s.nrows):
        v = s.row_values(r)
        if isinstance(v[1], float) and v[1] > 2000:
            per = v[2].strip()
            mes = TRIM[per] if per in TRIM else MESES.index(per) + 1
            datos = [None if x in ('n.a.', '') else int(round(float(x))) for x in v[3:3 + len(columnas)]]
            filas.append([int(v[1]), mes] + datos)
        elif str(v[1]).strip():
            notas.append(' '.join(str(v[1]).split()))
    return filas, notas


def bajar(carpeta):
    os.makedirs(carpeta, exist_ok=True)
    for nombre, _ in HOJAS.values():
        destino = os.path.join(carpeta, nombre)
        req = urllib.request.Request(BASE + nombre, headers={'User-Agent': 'Mozilla/5.0 (Auditavision; datos abiertos)'})
        with urllib.request.urlopen(req, timeout=90) as r, open(destino, 'wb') as f:
            f.write(r.read())


def main():
    if len(sys.argv) > 1:
        carpeta = sys.argv[1]
    else:
        import tempfile
        carpeta = tempfile.mkdtemp(prefix='padron-sat-')
        bajar(carpeta)
    D, archivos, notas = {}, {}, {}
    for k, (nombre, cols) in HOJAS.items():
        ruta = os.path.join(carpeta, nombre)
        archivos[k] = {'archivo': nombre, 'url': BASE + nombre, 'sha256': hashlib.sha256(open(ruta, 'rb').read()).hexdigest()}
        D[k], notas[k] = leer(ruta, cols)

    tipo = D['tipo']
    for f in tipo:
        if sum(f[2:7]) != f[7]:
            sys.exit('Por tipo: %s-%02d los cinco tipos suman %s y el total dice %s.' % (f[0], f[1], sum(f[2:7]), f[7]))
    total = {(f[0], f[1]): f[7] for f in tipo}
    for f in D['sit']:
        if total.get((f[0], f[1])) != f[2]:
            sys.exit('Por situación: %s-%02d dice %s activos y por tipo, %s.' % (f[0], f[1], f[2], total.get((f[0], f[1]))))
    desc_ent = []
    for i, f in enumerate(D['ent']):
        s = sum(f[2:])
        if s != total[(f[0], f[1])]:
            if i >= len(D['ent']) - 12:
                sys.exit('Por entidad: %s-%02d las entidades suman %s y el total es %s.' % (f[0], f[1], s, total[(f[0], f[1])]))
            desc_ent.append({'periodo': '%d-%02d' % (f[0], f[1]), 'suma': s, 'total': total[(f[0], f[1])]})
    ult_sec = D['sec'][-1]
    if sum(ult_sec[2:]) != total[(ult_sec[0], ult_sec[1])]:
        sys.exit('Por sector: el trimestre %s-%02d suma %s y los activos de su mes son %s.' % (ult_sec[0], ult_sec[1], sum(ult_sec[2:]), total[(ult_sec[0], ult_sec[1])]))
    cortes = {k: tuple(D[k][-1][:2]) for k in ('tipo', 'sit', 'reg', 'ent')}
    if len(set(cortes.values())) != 1:
        sys.exit('Las hojas no traen el mismo último mes: %s' % cortes)
    anio, mes = cortes['tipo']

    out = {
        'que': 'Padrón de contribuyentes del SAT, datos abiertos',
        'pagina': PAGINA,
        'descarga': datetime.date.today().isoformat(),
        'corte': {'anio': anio, 'mes': mes, 'texto': '%s de %d' % (MESES[mes - 1].lower(), anio)},
        'corte_sector': {'anio': ult_sec[0], 'mes': ult_sec[1]},
        'nota': 'Cifras preliminares (SAT). Contribuyentes activos al cierre de cada mes.',
        'archivos': archivos,
        'notas': notas,
        'descuadres_historicos': {'ent': desc_ent},
        'tipo': {'cols': [c for c, _ in TIPO], 'nombres': [n for _, n in TIPO], 'serie': tipo},
        'sit': {'cols': [c for c, _ in SIT], 'nombres': [n for _, n in SIT], 'serie': D['sit']},
        'reg': {'cols': [c for c, _ in REGIMEN], 'nombres': [n.rstrip('.') for _, n in REGIMEN], 'serie': D['reg']},
        'ent': {'cols': ENTIDADES, 'abbr': ABBR, 'serie': D['ent']},
        'sec': {'cols': [c for c, _ in SECTOR], 'nombres': [n for _, n in SECTOR], 'serie': D['sec']},
    }
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    viejo = open(SALIDA, encoding='utf-8').read() if os.path.exists(SALIDA) else ''
    nuevo = json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '\n'
    # La fecha de descarga sola no es novedad: si los archivos son los mismos, no se toca.
    if viejo:
        v = json.loads(viejo)
        v.pop('descarga', None)
        if v == {k: x for k, x in out.items() if k != 'descarga'}:
            print('Padrón del SAT: mismos archivos (corte %s); sin cambios.' % out['corte']['texto'])
            return
    open(SALIDA, 'w', encoding='utf-8').write(nuevo)
    t = tipo[-1]
    print('Padrón del SAT, corte de %s: %s activos (%s personas morales, %s asalariados). Escrito %s.' % (
        out['corte']['texto'], format(t[7], ','), format(t[5] + t[6], ','), format(t[4], ','), os.path.relpath(SALIDA, RAIZ)))


if __name__ == '__main__':
    main()
