# -*- coding: utf-8 -*-
"""Lector de facturas CFDI (encargo del autor, 05-11-2026: implementar en la
plataforma el código que lee una factura y cruzarla contra la lista 69-B).

Es la versión de Python de la aplicación «Lector de facturas CFDI» del Modo
Inspector (herramienta-inspector-factura.html, que hace lo mismo en el
navegador con assets/auditor/js/insp-factura.js). Sirve para dos cosas:

1. Como herramienta: lee uno o varios XML y escribe una tabla CSV con lo
   principal de cada factura y su cruce con la lista 69-B del SAT.
2. Como material de aprendizaje: cada paso dice por qué se hace así.

    python3 herramientas/lector_cfdi.py factura1.xml factura2.xml > tabla.csv
    python3 herramientas/lector_cfdi.py carpeta/*.xml --salida tabla.csv
    python3 herramientas/lector_cfdi.py carpeta/*.xml --proveedores   # resumen por emisor
    python3 herramientas/lector_cfdi.py --prueba      # con la factura ficticia de docs/ejemplos/

Reglas (AGENTS.md §2 y §2 bis):
- Lo que dice la lista 69-B es «oficial»: el SAT lo publicó con su oficio y
  su fecha. Lo que sale de comparar fechas o de rehacer la cuenta es
  «derivado» y se rotula «señal para revisar», nunca «irregularidad».
  Desvirtuado y sentencia favorable son resultados A FAVOR del contribuyente.
- El RFC de una persona física (13 caracteres) no se escribe completo en la
  tabla: es un dato personal. La factura es del lector; la tabla, también.
- Nada se manda a ningún lado: el script solo lee archivos de tu equipo.
"""
import csv
import datetime
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LISTA_69B = os.path.join(RAIZ, 'assets', 'auditor', 'data', 'sat-69b.js')
EJEMPLO = os.path.join(RAIZ, 'docs', 'ejemplos', 'factura-ficticia-cfdi40.xml')

# Los «espacios de nombres» del XML. Una factura escribe <cfdi:Comprobante>,
# pero «cfdi:» es solo un apodo: lo que cuenta es la dirección a la que apunta
# (xmlns:cfdi="http://www.sat.gob.mx/cfd/4"). ElementTree trabaja con la
# dirección completa entre llaves: {http://www.sat.gob.mx/cfd/4}Comprobante.
# Por eso se busca por dirección y no por apodo: un emisor puede llamarlo
# distinto y seguiría siendo un CFDI válido.
NS = {
    '4.0': 'http://www.sat.gob.mx/cfd/4',
    '3.3': 'http://www.sat.gob.mx/cfd/3',
}
TFD = 'http://www.sat.gob.mx/TimbreFiscalDigital'

TIPOS = {'I': 'Ingreso', 'E': 'Egreso', 'T': 'Traslado', 'N': 'Nómina', 'P': 'Pago'}
# El complemento para recepción de pagos (REP): 2.0 con el CFDI 4.0 y 1.0 con el 3.3.
PAGOS_NS = ('http://www.sat.gob.mx/Pagos20', 'http://www.sat.gob.mx/Pagos')
GENERICOS = ('XAXX010101000', 'XEXX010101000')   # público en general y extranjero: no son personas

# Catálogo c_RegimenFiscal del SAT: clave → (nombre, aplica a persona física,
# aplica a persona moral). Copiado del catálogo de CFDI 4.0 que publica el SAT
# en la página del Anexo 20 (catCFDI_V_4_20261106.xls, hoja c_RegimenFiscal,
# SHA-256 6249e37275ce164a1c4ac44e726dcd60858dac5c5604ff6c9ab06005a9199e1a,
# cotejado el 07-11-2026). Si el SAT agrega una clave, se agrega aquí.
REGIMENES = {
    '601': ('General de Ley Personas Morales', False, True),
    '603': ('Personas Morales con Fines no Lucrativos', False, True),
    '605': ('Sueldos y Salarios e Ingresos Asimilados a Salarios', True, False),
    '606': ('Arrendamiento', True, False),
    '607': ('Régimen de Enajenación o Adquisición de Bienes', True, False),
    '608': ('Demás ingresos', True, False),
    '610': ('Residentes en el Extranjero sin Establecimiento Permanente en México', True, True),
    '611': ('Ingresos por Dividendos (socios y accionistas)', True, False),
    '612': ('Personas Físicas con Actividades Empresariales y Profesionales', True, False),
    '614': ('Ingresos por intereses', True, False),
    '615': ('Régimen de los ingresos por obtención de premios', True, False),
    '616': ('Sin obligaciones fiscales', True, False),
    '620': ('Sociedades Cooperativas de Producción que optan por diferir sus ingresos', False, True),
    '621': ('Incorporación Fiscal', True, False),
    '622': ('Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras', False, True),
    '623': ('Opcional para Grupos de Sociedades', False, True),
    '624': ('Coordinados', False, True),
    '625': ('Régimen de las Actividades Empresariales con ingresos a través de Plataformas Tecnológicas', True, False),
    '626': ('Régimen Simplificado de Confianza', True, True),
}

# La revisión contra la ley (07-11-2026, pedido del autor tras leer la página
# de WiseCricket: «lo que puede hacer… lo podemos hacer nosotros»). Cada regla
# con su fundamento, cotejado ese día contra el documento vigente:
# - Guía de llenado del CFDI, Anexo 20 del SAT (Anexo_20_Guia_de_llenado_CFDI.pdf,
#   SHA-256 70e0c92df44b4f36975e4a0a5b1f0609f83c62deb029eda440fe4df6e2265a25).
# - CFF, última reforma DOF 09-04-2026;
# - LIVA, última reforma DOF 12-11-2021, y su Reglamento (RLIVA, DOF 25-09-2014).
# Todo lo que sale de aquí es «derivado» y se dice «señal para revisar»: el XML
# no dice qué se compró de verdad ni si ya se corrigió. La lee también la
# página (insp_factura.py la pasa a insp-factura.js): el texto vive aquí.
GUIA20 = 'http://omawww.sat.gob.mx/tramitesyservicios/Paginas/documentos/Anexo_20_Guia_de_llenado_CFDI.pdf'
ANEXO20 = 'http://omawww.sat.gob.mx/tramitesyservicios/Paginas/anexo_20.htm'
CFF_PDF = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/CFF.pdf'
LIVA_PDF = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LIVA.pdf'
RLIVA_PDF = 'https://www.diputados.gob.mx/LeyesBiblio/regley/Reg_LIVA_250914.pdf'
REGLAS = {
    'regimen': {'t': 'Régimen fiscal y tipo de persona',
                'f': 'Catálogo c_RegimenFiscal del SAT (Anexo 20): cada régimen dice si es para persona física, moral o las dos',
                'u': ANEXO20},
    'forma99': {'t': 'Método y forma de pago',
                'f': 'Guía de llenado del CFDI (Anexo 20), campo FormaPago: si el pago no se recibe al emitir, '
                     'la forma es «99» (Por definir) y el método «PPD»',
                'u': GUIA20},
    'rep': {'t': 'Complemento de pago (REP)',
            'f': 'Código Fiscal, art. 29-A, fracción VII, inciso b): si no se paga en una sola exhibición, '
                 'se expide un CFDI por cada pago que se reciba',
            'u': CFF_PDF},
    'ret_iva': {'t': 'Retención de IVA a personas físicas',
                'f': 'Ley del IVA, art. 1o.-A, fracción II, inciso a), y su Reglamento, art. 3, fracción I: la persona moral '
                     'retiene dos terceras partes del IVA por servicios personales independientes, comisiones o arrendamiento '
                     'que le presta una persona física',
                'u': LIVA_PDF, 'u2': RLIVA_PDF},
}
SITUACION = {'P': 'Presunto', 'D': 'Desvirtuado', 'F': 'Definitivo', 'S': 'Sentencia favorable'}
TOLERANCIA = 0.01   # un centavo: el CFDI redondea a dos decimales


def num(v):
    """El importe viene como texto («11600.00»): se vuelve número. Si falta, 0."""
    try:
        return float(v or 0)
    except ValueError:
        return 0.0


def leer(xml_bytes):
    """Lee una factura y devuelve un diccionario con lo principal.

    ET.fromstring recibe los bytes tal cual: el propio XML dice su
    codificación en la primera línea, y ElementTree la respeta."""
    raiz = ET.fromstring(xml_bytes)
    # raiz.tag es «{dirección}Comprobante»: se separa la dirección del nombre.
    m = re.match(r'\{([^}]+)\}(\w+)$', raiz.tag)
    if not m or m.group(2) != 'Comprobante':
        raise ValueError('no es un CFDI: el elemento raíz no es Comprobante')
    version = next((v for v, ns in NS.items() if ns == m.group(1)), None)
    if not version:
        raise ValueError('espacio de nombres desconocido: %s' % m.group(1))
    ns = {'c': NS[version], 't': TFD}

    emisor = raiz.find('c:Emisor', ns)
    receptor = raiz.find('c:Receptor', ns)
    # Ojo: hay <cfdi:Impuestos> dentro de cada concepto y otro, el del total,
    # colgado directo del Comprobante. find('c:Impuestos') sin más busca solo
    # entre los hijos directos, que es el que queremos.
    imp = raiz.find('c:Impuestos', ns)
    # El IVA (impuesto «002») del total, trasladado y retenido.
    iva = lambda ruta: sum(num(x.attrib.get('Importe')) for x in raiz.findall('c:Impuestos/' + ruta, ns)
                           if x.attrib.get('Impuesto') == '002')
    # El timbre va dentro de <cfdi:Complemento>; «.//» busca a cualquier profundidad.
    timbre = raiz.find('.//t:TimbreFiscalDigital', ns)
    conceptos = raiz.findall('c:Conceptos/c:Concepto', ns)

    a = raiz.attrib.get   # atajo: a('Total') es raiz.attrib.get('Total')
    f = {
        'version': version,
        'uuid': (timbre.attrib.get('UUID') if timbre is not None else '') or '',
        'fecha': a('Fecha', ''),
        'timbrado': timbre.attrib.get('FechaTimbrado', '') if timbre is not None else '',
        'serie_folio': ('%s %s' % (a('Serie', ''), a('Folio', ''))).strip(),
        'tipo': TIPOS.get(a('TipoDeComprobante', ''), a('TipoDeComprobante', '')),
        'moneda': a('Moneda', ''),
        'emisor_rfc': (emisor.attrib.get('Rfc', '') if emisor is not None else '').upper(),
        'emisor_nombre': emisor.attrib.get('Nombre', '') if emisor is not None else '',
        'emisor_regimen': emisor.attrib.get('RegimenFiscal', '') if emisor is not None else '',
        'receptor_rfc': (receptor.attrib.get('Rfc', '') if receptor is not None else '').upper(),
        'receptor_nombre': receptor.attrib.get('Nombre', '') if receptor is not None else '',
        'uso': receptor.attrib.get('UsoCFDI', '') if receptor is not None else '',
        'subtotal': num(a('SubTotal')),
        'descuento': num(a('Descuento')),
        'trasladados': num(imp.attrib.get('TotalImpuestosTrasladados')) if imp is not None else 0.0,
        'retenidos': num(imp.attrib.get('TotalImpuestosRetenidos')) if imp is not None else 0.0,
        'total': num(a('Total')),
        'metodo': a('MetodoPago', ''),
        'forma': a('FormaPago', ''),
        'receptor_regimen': receptor.attrib.get('RegimenFiscalReceptor', '') if receptor is not None else '',
        'iva_trasladado': iva('c:Traslados/c:Traslado'),
        'iva_retenido': iva('c:Retenciones/c:Retencion'),
        # Si es un complemento de pago: a qué facturas (UUID) paga y cuánto.
        'pagos': [((d.attrib.get('IdDocumento') or '').upper(), num(d.attrib.get('ImpPagado')))
                  for pns in PAGOS_NS for d in raiz.iter('{%s}DoctoRelacionado' % pns)],
        'conceptos': [{'descripcion': c.attrib.get('Descripcion', ''), 'cantidad': num(c.attrib.get('Cantidad')),
                       'importe': num(c.attrib.get('Importe'))} for c in conceptos],
    }
    return f


def cuadra(f):
    """Rehace la cuenta de la factura (derivado):
    subtotal − descuento + impuestos trasladados − impuestos retenidos = total.
    También revisa que los conceptos sumen el subtotal. Devuelve la lista de
    diferencias (vacía si todo cuadra)."""
    out = []
    calc = f['subtotal'] - f['descuento'] + f['trasladados'] - f['retenidos']
    if abs(calc - f['total']) > TOLERANCIA:
        out.append('el total dice %.2f y la cuenta da %.2f' % (f['total'], calc))
    if f['conceptos']:
        suma = sum(c['importe'] for c in f['conceptos'])
        if abs(suma - f['subtotal']) > TOLERANCIA:
            out.append('los conceptos suman %.2f y el subtotal dice %.2f' % (suma, f['subtotal']))
    return out


def pagos_del_lote(leidas):
    """Junta los complementos de pago del lote: UUID de la factura → [suma
    pagada, cuántos pagos]. None si el lote no trae ningún complemento (así no
    se dice «sin complemento» de lo que el lector no cargó)."""
    pg, hay = {}, False
    for _n, f in leidas:
        for uuid, imp in f.get('pagos') or []:
            hay = True
            x = pg.setdefault(uuid, [0.0, 0])
            x[0] += imp
            x[1] += 1
    return pg if hay else None


def revisar(f, pagos=None):
    """La revisión contra la ley (REGLAS). Devuelve [(id de regla, 'senal' o
    'nota', texto)]. Todo es derivado: «señal para revisar», nunca irregularidad."""
    out = []
    for rol, rfc, reg in (('emisor', f['emisor_rfc'], f['emisor_regimen']), ('receptor', f['receptor_rfc'], f.get('receptor_regimen', ''))):
        if not reg or rfc in GENERICOS or len(rfc) not in (12, 13):
            continue
        r = REGIMENES.get(reg)
        if not r:
            out.append(('regimen', 'senal', 'El régimen %s del %s no está en el catálogo c_RegimenFiscal del SAT.' % (reg, rol)))
        elif not (r[1] if es_fisica(rfc) else r[2]):
            out.append(('regimen', 'senal', 'El %s tiene RFC de persona %s y su régimen es %s (%s), que el catálogo del SAT da solo a personas %s.'
                        % (rol, 'física' if es_fisica(rfc) else 'moral', reg, r[0], 'morales' if es_fisica(rfc) else 'físicas')))
    ingreso = f['tipo'] == 'Ingreso'
    metodo, forma = f.get('metodo', ''), f.get('forma', '')
    if ingreso and metodo == 'PPD' and forma and forma != '99':
        out.append(('forma99', 'senal', 'Dice pago en parcialidades o diferido (PPD) con forma de pago %s; con PPD, la forma debe ser «99» (Por definir).' % forma))
    if ingreso and metodo == 'PUE' and forma == '99':
        out.append(('forma99', 'senal', 'Dice pago en una sola exhibición (PUE) con forma «99» (Por definir); si ya se pagó, la forma es la que se usó.'))
    if ingreso and metodo == 'PPD':
        p = (pagos or {}).get((f['uuid'] or '').upper())
        if pagos is None:
            out.append(('rep', 'nota', 'Es PPD: cada pago que reciba necesita su complemento de pago. Si cargas los complementos junto con la factura, los empato.'))
        elif not p:
            out.append(('rep', 'senal', 'Es PPD y ninguno de los complementos de pago que cargaste la cita. Si ya se pagó, falta su complemento.'))
        else:
            falta = f['total'] - p[0]
            out.append(('rep', 'nota', '%d complemento%s de pago la cita%s por $%s en total%s.' % (
                p[1], '' if p[1] == 1 else 's', '' if p[1] == 1 else 'n', format(round(p[0], 2), ',.2f'),
                (', y le quedan $%s según el total de la factura' % format(round(falta, 2), ',.2f')) if falta > TOLERANCIA else '')))
    emf, rem = f['emisor_rfc'], f['receptor_rfc']
    if (ingreso and es_fisica(emf) and emf not in GENERICOS and len(rem) == 12 and rem not in GENERICOS
            and f.get('iva_trasladado', 0) > TOLERANCIA and f.get('iva_retenido', 0) <= TOLERANCIA):
        dos = round(f['iva_trasladado'] * 2 / 3, 2)
        out.append(('ret_iva', 'senal', 'Una persona física le factura a una persona moral IVA por $%s sin IVA retenido. Si es un servicio '
                    'profesional, una comisión o un arrendamiento, la persona moral retiene dos terceras partes: $%s (IVA × 2 ÷ 3). '
                    'Si es venta de bienes, no aplica.' % (format(f['iva_trasladado'], ',.2f'), format(dos, ',.2f'))))
    return out


def es_fisica(rfc):
    """RFC de 13 caracteres = persona física; de 12 = persona moral (empresa)."""
    return len(rfc) == 13


def tapa(rfc):
    """El RFC de una persona física no se muestra completo (§2 bis): se dejan
    las 4 letras del nombre y la homoclave, y se tapa la fecha de nacimiento."""
    return rfc[:4] + '••••••' + rfc[10:] if es_fisica(rfc) else rfc


def cargar_69b(ruta=LISTA_69B):
    """La lista 69-B ya integrada (actualizar_69b.py). Es un archivo .js para
    el navegador: «window.SAT_69B = {…};». Se corta de la primera llave a la
    última y lo de en medio es JSON puro."""
    t = open(ruta, encoding='utf-8').read()
    d = json.loads(t[t.index('{'):t.rindex('}') + 1])
    return d['meta'], {r[0]: r for r in d['r']}


def fecha_iso(f):
    """«28/06/2018» (como la da el SAT) → date(2018, 6, 28). Vacía → None."""
    if not f:
        return None
    d, m, a = f.split('/')
    return datetime.date(int(a), int(m), int(d))


def cruce(rfc, fecha_factura, lista):
    """Lo que dice la lista 69-B de un RFC, separado en dos:
    - «oficial»: lo que el SAT publicó (situación, oficio, fecha).
    - «senales»: lo que sale de comparar fechas (derivado, para revisar)."""
    r = lista.get(rfc)
    if not r:
        return {'oficial': '', 'senales': []}
    sit = SITUACION[r[2]]
    oficial = '%s · oficio %s del %s (%s)' % (sit, r[3], r[4], r[5])
    senales = []
    # La fecha del CFDI viene como «2026-03-15T10:30:00» (formato ISO): los
    # primeros 10 caracteres son el día, y date.fromisoformat los entiende.
    ff = None
    try:
        ff = datetime.date.fromisoformat(fecha_factura[:10])
    except ValueError:
        pass
    fp = fecha_iso(r[6]) if len(r) > 6 else None
    fd = fecha_iso(r[7]) if len(r) > 7 else None
    if r[2] in ('D', 'S'):
        senales.append('A favor del contribuyente: %s.' % ('desvirtuó la presunción ante el SAT' if r[2] == 'D' else 'un tribunal le dio la razón'))
    else:
        if ff and fd and ff >= fd:
            senales.append('Señal para revisar: la factura es del %s, posterior a su publicación como definitivo (%s).' % (ff.isoformat(), r[7]))
        elif ff and fp and ff >= fp:
            senales.append('Señal para revisar: la factura es del %s, cuando ya estaba publicado como presunto (%s).' % (ff.isoformat(), r[6]))
        if r[2] == 'F':
            senales.append('El art. 69-B del CFF (párrafo quinto) dice que las operaciones de los comprobantes de quien está en el '
                           'listado definitivo no producen ni produjeron efecto fiscal alguno; quien la recibió tiene 30 días tras la '
                           'publicación para acreditar la operación o corregir su situación (párrafo octavo).')
    return {'oficial': oficial, 'senales': senales}


COLUMNAS = ['archivo', 'version', 'uuid', 'fecha', 'tipo', 'emisor_rfc', 'emisor_nombre', 'receptor_rfc', 'receptor_nombre',
            'subtotal', 'trasladados', 'retenidos', 'total', 'moneda', 'cuenta', 'lista_69b_emisor', 'senales', 'revision']


def renglon(nombre, f, lista, pagos=None):
    """Una fila de la tabla. Las personas físicas van con el RFC tapado y sin nombre."""
    c = cruce(f['emisor_rfc'], f['fecha'], lista)
    dif = cuadra(f)
    fila = dict(f, archivo=nombre, cuenta='cuadra' if not dif else 'no cuadra: ' + '; '.join(dif),
                lista_69b_emisor=c['oficial'] or 'no aparece', senales=' | '.join(c['senales']),
                revision=' | '.join(('Señal para revisar: ' if k == 'senal' else '') + t for _r, k, t in revisar(f, pagos)))
    for k in ('emisor', 'receptor'):
        if es_fisica(fila[k + '_rfc']):
            fila[k + '_rfc'] = tapa(fila[k + '_rfc'])
            fila[k + '_nombre'] = '(persona física: nombre oculto)'
    for k in ('subtotal', 'trasladados', 'retenidos', 'total'):
        fila[k] = '%.2f' % fila[k]
    return {k: fila[k] for k in COLUMNAS}


PROV_COLUMNAS = ['emisor_rfc', 'emisor_nombre', 'facturas', 'total', 'monedas', 'no_cuadran', 'lista_69b', 'senales', 'revision']
ORDEN_69B = {'F': 0, 'P': 1, 'S': 2, 'D': 3}


def por_proveedor(leidas, lista):
    """Facturas por lote (entrega B de «Mi Auditavisión», 05-11-2026): el
    resumen por emisor. leidas es [(nombre, factura)]. Primero los que están en
    la lista 69-B (definitivo, presunto…) y luego por monto. La suma es de los
    totales tal como vienen, sin convertir monedas (derivado)."""
    g = {}
    pagos = pagos_del_lote(leidas)
    for _nombre, f in leidas:
        rfc = f['emisor_rfc']
        x = g.setdefault(rfc, {'rfc': rfc, 'nombre': f['emisor_nombre'], 'facturas': 0, 'total': 0.0, 'monedas': set(),
                               'no_cuadran': 0, 'senales': 0, 'revision': 0})
        x['facturas'] += 1
        x['total'] += f['total']
        x['monedas'].add(f['moneda'] or 'MXN')
        x['no_cuadran'] += 1 if cuadra(f) else 0
        x['senales'] += sum(1 for s in cruce(rfc, f['fecha'], lista)['senales'] if s.startswith('Señal'))
        x['revision'] += sum(1 for _r, k, _t in revisar(f, pagos) if k == 'senal')
    out = []
    for rfc, x in g.items():
        r = lista.get(rfc)
        out.append({'emisor_rfc': tapa(rfc) if es_fisica(rfc) else rfc,
                    'emisor_nombre': '(persona física: nombre oculto)' if es_fisica(rfc) else x['nombre'],
                    'facturas': x['facturas'], 'total': '%.2f' % x['total'], 'monedas': ', '.join(sorted(x['monedas'])),
                    'no_cuadran': x['no_cuadran'], 'senales': x['senales'], 'revision': x['revision'],
                    'lista_69b': cruce(rfc, '', lista)['oficial'] or 'no aparece', '_o': (ORDEN_69B.get(r[2], 9) if r else 9, -x['total'])})
    out.sort(key=lambda x: x.pop('_o'))
    return out


def prueba():
    """La revisa revision.py: la factura ficticia se lee, cuadra y se cruza con
    una lista de mentiras (nunca con un contribuyente real)."""
    fallas = []
    f = leer(open(EJEMPLO, 'rb').read())
    if (f['version'], f['emisor_rfc'], f['total'], f['trasladados'], len(f['conceptos'])) != ('4.0', 'AAA010101AAA', 11600.0, 1600.0, 2):
        fallas.append('lectura: %r' % f)
    if cuadra(f):
        fallas.append('la factura ficticia debería cuadrar: %r' % cuadra(f))
    malo = dict(f, total=11700.0)
    if not cuadra(malo):
        fallas.append('un total alterado debería no cuadrar')
    # CFDI 3.3: el mismo XML con el espacio de nombres viejo se lee igual.
    viejo = open(EJEMPLO, 'rb').read().replace(b'http://www.sat.gob.mx/cfd/4', b'http://www.sat.gob.mx/cfd/3')
    if leer(viejo)['version'] != '3.3':
        fallas.append('no reconoce el CFDI 3.3')
    # Lista de mentiras: el emisor ficticio como definitivo publicado el 01-02-2026.
    falsa = {'AAA010101AAA': ['AAA010101AAA', 'EMPRESA FICTICIA', 'F', '000-00-0000-0', '01/02/2026', 'DOF', '01/10/2025', '01/02/2026']}
    c = cruce('AAA010101AAA', f['fecha'], falsa)
    if not c['oficial'].startswith('Definitivo') or not any('posterior a su publicación como definitivo' in s for s in c['senales']):
        fallas.append('cruce definitivo: %r' % c)
    c = cruce('AAA010101AAA', '2025-12-01T00:00:00', falsa)
    if not any('ya estaba publicado como presunto' in s for s in c['senales']):
        fallas.append('cruce presunto: %r' % c)
    falsa['AAA010101AAA'][2] = 'S'
    if not cruce('AAA010101AAA', f['fecha'], falsa)['senales'][0].startswith('A favor'):
        fallas.append('sentencia favorable debe decirse a favor')
    fila = renglon('ejemplo.xml', f, {})
    if fila['receptor_rfc'] != 'XAXX••••••000' or 'oculto' not in fila['receptor_nombre'] or fila['lista_69b_emisor'] != 'no aparece':
        fallas.append('renglón: %r' % fila)
    # Facturas por lote: dos del emisor ficticio (una alterada) y una de otro.
    otro = dict(f, emisor_rfc='BBB010101BBB', emisor_nombre='OTRA FICTICIA', total=500.0, subtotal=500.0, trasladados=0.0, conceptos=[])
    falsa['AAA010101AAA'][2] = 'F'
    pv = por_proveedor([('a.xml', f), ('b.xml', malo), ('c.xml', otro)], falsa)
    if [(x['emisor_rfc'], x['facturas'], x['no_cuadran']) for x in pv] != [('AAA010101AAA', 2, 1), ('BBB010101BBB', 1, 0)] \
            or pv[0]['total'] != '23300.00' or not pv[0]['lista_69b'].startswith('Definitivo') or pv[0]['senales'] != 2:
        fallas.append('por proveedor: %r' % pv)
    # La revisión contra la ley (07-11-2026). La ficticia (PUE, forma 03, emisor
    # moral en 601, receptor genérico) no da ninguna.
    if (f['metodo'], f['forma'], f['receptor_regimen'], f['iva_trasladado'], f['iva_retenido'], f['pagos']) != ('PUE', '03', '616', 1600.0, 0.0, []) \
            or revisar(f):
        fallas.append('revisión de la ficticia: %r' % (revisar(f),))
    ids = lambda g, p=None: [(r, k) for r, k, _t in revisar(g, p)]
    if ids(dict(f, receptor_rfc='BBB010101BBB', receptor_regimen='612')) != [('regimen', 'senal')]:
        fallas.append('régimen de persona física con RFC de moral')
    if ids(dict(f, emisor_regimen='699')) != [('regimen', 'senal')]:
        fallas.append('régimen fuera del catálogo')
    if ids(dict(f, metodo='PPD', forma='03')) != [('forma99', 'senal'), ('rep', 'nota')]:
        fallas.append('PPD con forma distinta de 99: %r' % ids(dict(f, metodo='PPD', forma='03')))
    if ids(dict(f, forma='99')) != [('forma99', 'senal')]:
        fallas.append('PUE con forma 99')
    ppd = dict(f, metodo='PPD', forma='99')
    if ids(ppd, {'OTRO': [1.0, 1]}) != [('rep', 'senal')] or ids(ppd, {f['uuid']: [11600.0, 2]}) != [('rep', 'nota')] \
            or 'le quedan $6,600.00' not in revisar(ppd, {f['uuid']: [5000.0, 1]})[0][2]:
        fallas.append('empate de complementos de pago')
    pf = dict(f, emisor_rfc='AAAA010101AA1', emisor_regimen='612', receptor_rfc='BBB010101BBB', receptor_regimen='601')
    r = revisar(pf)
    if [(x[0], x[1]) for x in r] != [('ret_iva', 'senal')] or '$1,066.67' not in r[0][2] or revisar(dict(pf, iva_retenido=1066.67)):
        fallas.append('retención de IVA: %r' % r)
    # Un complemento de pago se lee: el mismo XML con un DoctoRelacionado.
    rep = open(EJEMPLO, 'rb').read().replace(b'<cfdi:Complemento>', b'<cfdi:Complemento><pago20:Pagos xmlns:pago20="http://www.sat.gob.mx/Pagos20" Version="2.0">'
                                              b'<pago20:Pago><pago20:DoctoRelacionado IdDocumento="aaaaaaaa-0000-4000-8000-000000000009" ImpPagado="500.00"/>'
                                              b'</pago20:Pago></pago20:Pagos>')
    if pagos_del_lote([('p.xml', leer(rep)), ('f.xml', f)]) != {'AAAAAAAA-0000-4000-8000-000000000009': [500.0, 1]} \
            or pagos_del_lote([('f.xml', f)]) is not None:
        fallas.append('lectura del complemento de pago')
    # Y que la lista real tenga las fechas por etapa que necesita el cruce.
    meta, lista = cargar_69b()
    if len(next(iter(lista.values()))) < 8:
        fallas.append('sat-69b.js no trae las fechas de presunto y definitivo: corre actualizar_69b.py')
    for x in fallas:
        print('lector CFDI: FALLA', x)
    print('lector CFDI: prueba %s' % ('bien' if not fallas else 'con fallas'))
    return 1 if fallas else 0


def main(args):
    if '--prueba' in args:
        return prueba()
    salida = None
    if '--salida' in args:
        i = args.index('--salida')
        salida = args[i + 1]
        args = args[:i] + args[i + 2:]
    if not args:
        print(__doc__)
        return 1
    _meta, lista = cargar_69b()
    prov = '--proveedores' in args
    args = [a for a in args if a != '--proveedores']
    out = open(salida, 'w', newline='', encoding='utf-8-sig') if salida else sys.stdout   # utf-8-sig: Excel lee bien los acentos
    w = csv.DictWriter(out, fieldnames=PROV_COLUMNAS if prov else COLUMNAS)
    w.writeheader()
    leidas = []
    for ruta in args:
        try:
            leidas.append((os.path.basename(ruta), leer(open(ruta, 'rb').read())))
        except (ValueError, ET.ParseError) as e:
            print('%s: no se pudo leer (%s)' % (ruta, e), file=sys.stderr)
    pagos = pagos_del_lote(leidas)
    for fila in (por_proveedor(leidas, lista) if prov else [renglon(n, f, lista, pagos) for n, f in leidas]):
        w.writerow(fila)
    if salida:
        out.close()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
