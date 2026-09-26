#!/usr/bin/env python3
"""Matriz de Datos Básicos (MDB) de la ASF, Cuenta Pública 2024, entregas
primera, segunda y tercera (consolidado, corte febrero de 2026).

Uso:
    python3 herramientas/extraer_mdb_asf.py MDB_Consolidado.pdf

Fuente: https://www.asf.gob.mx/Trans/Informes/IR2024c/Documentos/Matriz/MDB_Consolidado.pdf

Lee dos cuadros del documento:
  - páginas 11 a 14: resumen por rubro, grupo funcional y sector;
  - páginas 19 a 23: gasto federalizado por entidad federativa
    (gobierno del estado, municipios y otros).
Los montos del documento vienen en miles de pesos; aquí se guardan en pesos.
Escribe investigaciones/asf-mdb-2024.json; integrar_cuenta_publica.py lo lee.
"""
import hashlib
import json
import logging
import pathlib
import re
import sys

import pypdf

logging.disable(logging.WARNING)
RAIZ = pathlib.Path(__file__).resolve().parent.parent
SALIDA = RAIZ / 'investigaciones' / 'asf-mdb-2024.json'

NUM = r'(-?[\d,]+(?:\.\d+)?%?)'
CAMPOS = ['auditorias', 'universo', 'muestra', 'representatividad', 'solventadas', 'conAcciones',
          'R', 'RD', 'PEFCF', 'SA', 'PRAS', 'PO', 'acciones', 'sugerencias', 'recuperaciones', 'porAclarar']
ESTADOS = ['Aguascalientes', 'Baja California', 'Baja California Sur', 'Campeche', 'Chiapas', 'Chihuahua',
           'Ciudad de México', 'Coahuila de Zaragoza', 'Colima', 'Durango', 'Guanajuato', 'Guerrero', 'Hidalgo',
           'Jalisco', 'México', 'Michoacán de Ocampo', 'Morelos', 'Nayarit', 'Nuevo León', 'Oaxaca', 'Puebla',
           'Querétaro', 'Quintana Roo', 'San Luis Potosí', 'Sinaloa', 'Sonora', 'Tabasco', 'Tamaulipas',
           'Tlaxcala', 'Veracruz de Ignacio de la Llave', 'Yucatán', 'Zacatecas']


def numeros(tokens):
    """Convierte la cola numerica de un renglon; admite que falte el % cuando
    el universo es cero (el documento deja la celda vacia)."""
    v = [t for t in tokens]
    if len(v) == 15:
        v.insert(3, '')
    if len(v) != 16:
        return None
    d = {}
    for k, t in zip(CAMPOS, v):
        if t == '':
            d[k] = None
        elif t.endswith('%'):
            d[k] = float(t[:-1].replace(',', ''))
        elif k in ('universo', 'muestra', 'recuperaciones', 'porAclarar'):
            d[k] = round(float(t.replace(',', '')) * 1000, 2)   # miles -> pesos
        else:
            d[k] = int(t.replace(',', ''))
    return d


def cola(linea):
    linea = ' ' + linea
    m = re.search(r'((?:\s+' + NUM + r'){15,16})\s*$', linea)
    if not m:
        return None, linea
    return m.group(1).split(), linea[:m.start()]


def sectores(r):
    grupos = []
    actual = {'grupo': None, 'sectores': []}
    orden = ['Ingreso', 'Deuda', 'Gobierno', 'Desarrollo Social', 'Desarrollo Económico', 'Gasto Federalizado']
    total = None
    pend = []
    for i in range(10, 14):
        txt = r.pages[i].extract_text()
        for linea in txt.split('\n'):
            tk, pref = cola(linea)
            if tk is None:
                if re.search(r'AUDITOR|MATRIZ|Grupo|Funcional|PEFCF|Universo|Seleccionado|Muestra|Auditada|Representatividad|Observaci|Solventada|Acciones|Rubro|Finanzas|Públicas|^Sector( |$)|torías|Alcance|Resultados|Suge-|rencias|Cuantificaci|Miles|Total$|Recuperaciones|Operadas|Durante|auditoría|Tema|Federalizado PO|Montos|proceso|seguimiento|PRASRD|Gasto$|^\d+$|Notas|^-', linea.strip()) or not linea.strip():
                    pend = []
                else:
                    pend.append(linea.strip())
                continue
            nombre = ' '.join(pend + [pref.strip()]).strip()
            pend = []
            d = numeros(tk)
            if d is None:
                continue
            if nombre == 'Total':
                total = d
                continue
            if nombre.startswith('Subtotal'):
                if actual['grupo'] is None and len(grupos) < len(orden):
                    actual['grupo'] = orden[len(grupos)]
                actual['subtotal'] = d
                grupos.append(actual)
                actual = {'grupo': None, 'sectores': []}
                continue
            d['nombre'] = re.sub(r'\s+', ' ', nombre)
            actual['sectores'].append(d)
    # el ultimo "Subtotal" del cuadro es el del rubro Gasto completo
    gasto = None
    if len(grupos) == 7:
        gasto = grupos.pop()['subtotal']
    for g, n in zip(grupos, orden):
        g['grupo'] = n
    return total, grupos, gasto


def entidades(r):
    filas = []
    for i in range(18, 23):
        txt = r.pages[i].extract_text(extraction_mode='layout')
        for linea in txt.split('\n'):
            tk, pref = cola(linea)
            m = re.search(r'(Gobierno del Estado|Municipios|Alcaldías|Otros)\s*$', pref or '')
            if tk is None:
                if linea.strip() and len(linea) - len(linea.lstrip()) > 20 and len(linea.strip()) < 30:
                    filas.append(('texto', linea.strip()))
                continue
            d = numeros(tk)
            if d is None:
                continue
            if not m:
                if pref.strip() == 'Total':
                    filas.append(('total', d))
                elif 'No aplicable' in pref:
                    # * auditorias a dependencias federales coordinadoras de fondos
                    filas.append(('federal', d))
                continue
            d['ente'] = m.group(1)
            filas.append(('fila', d, pref[:m.start()].strip()))
    # Cada estado ocupa tres renglones (estado, municipios o alcaldias, otros);
    # su nombre va en el renglon de en medio, a veces cortado ("Coahuila de").
    total = None
    federal = None
    estados = []
    bloque = []
    for f in filas:
        if f[0] == 'total':
            total = f[1]
        elif f[0] == 'federal':
            federal = f[1]
        elif f[0] == 'fila':
            bloque.append(f)
            if len(bloque) == 3:
                txt = ' '.join(w for w in bloque[1][2].split() if w not in ('Gasto', 'Federalizado'))
                estados.append({'filas': [x[1] for x in bloque], 'txt': txt})
                bloque = []
    assert len(estados) == 32, len(estados)
    salida = []
    for e in estados:
        txt = 'México' if e['txt'] == 'Estado de México' else e['txt']
        cand = [n for n in ESTADOS if n == txt] or [n for n in ESTADOS if n.startswith(txt)]
        assert len(cand) >= 1, e['txt']
        nombre = min(cand, key=len)
        suma = {k: sum((x[k] or 0) for x in e['filas']) for k in ('auditorias', 'universo', 'muestra', 'acciones', 'PO', 'PRAS', 'recuperaciones', 'porAclarar')}
        salida.append({'entidad': nombre, 'total': {k: round(v, 2) for k, v in suma.items()},
                       'desglose': [{'ente': x['ente'], 'auditorias': x['auditorias'], 'porAclarar': x['porAclarar'],
                                     'recuperaciones': x['recuperaciones'], 'acciones': x['acciones']} for x in e['filas']]})
    assert len({x['entidad'] for x in salida}) == 32
    return total, salida, federal


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    r = pypdf.PdfReader(sys.argv[1])
    total, grupos, gasto = sectores(r)
    totGF, est, fed = entidades(r)
    # controles: los renglones suman lo que dice el documento
    assert sum(g['subtotal']['auditorias'] for g in grupos) == total['auditorias'], 'grupos'
    assert sum(e['total']['auditorias'] for e in est) + fed['auditorias'] == totGF['auditorias'], 'entidades'
    assert abs(sum(e['total']['porAclarar'] for e in est) + fed['porAclarar'] - totGF['porAclarar']) < 1000, 'por aclarar'
    datos = {
        'cuenta': 2024, 'corte': 'febrero de 2026', 'entregas': 'primera, segunda y tercera (consolidado)',
        'total': total, 'grupos': grupos, 'gasto': gasto,
        'federalizadoTotal': totGF, 'entidades': est,
        'federalizadoCoordinadoras': fed,
        'sha256': hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest(),
    }
    SALIDA.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding='utf-8')
    print('total', {k: total[k] for k in ('auditorias', 'acciones', 'recuperaciones', 'porAclarar')})
    for g in grupos:
        print(g['grupo'], g['subtotal']['auditorias'], g['subtotal']['porAclarar'], len(g['sectores']))
    for e in sorted(est, key=lambda e: -e['total']['porAclarar'])[:6]:
        print(e['entidad'], e['total'])


if __name__ == '__main__':
    main()
