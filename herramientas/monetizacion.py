#!/usr/bin/env python3
"""La operación para cobrar, lista y apagada (pedido del autor, 07-11-2026:
«instalar toda la operación para que al momento en que te diga "ya"… lancemos
la monetización»).

Aquí viven, en un solo lugar:

- el interruptor `MONETIZACION` (apagado) y el canal de pago `CANAL_PAGO`;
- los planes (`PLANES`), que son los de docs/CATALOGO-SERVICIOS.md §3;
- «¿Cómo nos sostenemos?» (`SOSTEN` y `NUNCA`), que se lee en servicios.html;
- los contadores de la base (`contadores()`), que se cuentan de los archivos
  al generar y nunca se escriben a mano (AGENTS.md §2);
- la lista para lanzar (`LISTA`), con lo que decide el autor.

Mientras `MONETIZACION` esté en False, servicios.html no muestra planes ni
precios. Al ponerlo en True, `revisar()` detiene la generación si un plan de
pago no tiene precio o si falta el canal de pago: no se abre a medias.

    python3 herramientas/monetizacion.py          # la lista para lanzar
    python3 herramientas/monetizacion.py --prueba
"""
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# El interruptor. Solo el autor lo enciende («ya»).
MONETIZACION = False
# La dirección de la pasarela de pago (o de la página de pago), cuando exista.
CANAL_PAGO = ''

# Los planes (docs/CATALOGO-SERVICIOS.md §3). precio: pesos sin IVA, o None
# mientras no haya pilotos (§2: no se inventa). periodo: 'mes', 'año' o
# 'encargo'. Sus ids deben ser los mismos de la migración de Supabase.
PLANES = [
    {'id': 'gratis', 'nombre': 'Gratis', 'para': 'Cualquier persona.', 'periodo': None, 'precio': 0,
     'agrega': ['Toda la consulta: Enciclopedia, Planisferio, Noticiero y el Auditor',
                'Buscar un RFC en la lista 69-B', 'Leer facturas y estados de resultados en tu navegador']},
    {'id': 'profesional', 'nombre': 'Profesional', 'para': 'Una empresa con su cartera de proveedores.', 'periodo': 'mes', 'precio': None,
     'agrega': ['Vigía de proveedores: tu cartera contra la 69-B cada semana, con aviso por correo',
                'Tu cartera guardada por nosotros, no solo en tu navegador',
                'Carta de corrección al proveedor, con cada señal y su artículo']},
    {'id': 'despacho', 'nombre': 'Despacho', 'para': 'Despachos contables y jurídicos con varios clientes.', 'periodo': 'mes', 'precio': None,
     'agrega': ['Lo del plan Profesional para cada cliente', 'Revisión de facturas por lote, con informe',
                'Expediente de materialidad con tarifa preferente']},
    {'id': 'encargo', 'nombre': 'Por encargo', 'para': 'Quien necesita una respuesta por escrito.', 'periodo': 'encargo', 'precio': None,
     'agrega': ['Ficha de debida diligencia de un proveedor', 'Expediente de investigación o del ente', 'Revisión documental y diagnóstico financiero']},
    {'id': 'institucion', 'nombre': 'Institución', 'para': 'Universidades, órganos de control y medios.', 'periodo': 'año', 'precio': None,
     'agrega': ['Licencia del Auditor Virtual', 'Talleres, como «Documentar para sancionar»', 'Entrega de datos en tu formato, con aviso de cambios']},
]

# ¿Cómo nos sostenemos? (idea tomada de getquin, «How does getquin make
# money?», docs/FRAUDE-MERCADO-Y-HOSPEDAJE.md §3.4).
SOSTEN = [
    ('🤝', 'Servicios por encargo', 'Revisiones, expedientes y talleres que se cotizan por escrito antes de empezar.', '#oferta'),
    ('📡', 'Planes para quien necesita aviso y memoria', 'El Vigía de tus proveedores y los planes para despachos e instituciones. Se abren con el lanzamiento.', '#modulos'),
    ('🐷', 'Donaciones', 'De quien quiere sostener la consulta gratuita, a la vista de todos.', 'donaciones.html'),
]
NUNCA = [
    'Publicidad: no vendemos espacios ni menciones.',
    'Tus datos: no los vendemos ni los compartimos, y tus archivos no se suben.',
    'La información: consultar una cifra, una ley o la lista 69-B es gratis y lo seguirá siendo.',
    'Lo que publicamos: ningún pago retira, suaviza ni retrasa una publicación.',
]
HOY = ('Hoy todavía no entra dinero: no hay pagos abiertos. Cuando los haya, publicaremos cada año cuánto entró por cada vía.')

# La lista para lanzar: (clave, qué, quién lo decide o lo hace). hecho() dice
# si ya está, leyendo el repositorio cuando se puede.
LISTA = [
    ('forma', 'Forma jurídica (persona física con actividad empresarial o sociedad)', 'El autor'),
    ('cfdi', 'Emitir CFDI propio (RFC con la actividad y un proveedor de facturación)', 'El autor'),
    ('canal', 'Canal de pago (CANAL_PAGO de este archivo)', 'El autor elige la pasarela; se pega aquí'),
    ('precios', 'Precio de cada plan de pago (PLANES), con 3 a 5 pilotos', 'El autor'),
    ('aviso', 'Aviso de privacidad: qué guarda el Vigía (RFC de la cartera y correo)', 'El autor lo aprueba'),
    ('base', 'Migración de Supabase escrita y probada (clientes, contrataciones, cartera, avisos, pagos)', 'Hecho: prueba_base_datos.py'),
    ('base_sub', 'Esa migración aplicada en el proyecto de Supabase', 'Flujo «Sube la base de datos»'),
    ('candado', 'Quitar el candado (CANDADO de acceso.py) para que Google vea la plataforma', 'El autor'),
    ('interruptor', 'Encender MONETIZACION', 'El autor dice «ya»'),
]
MIGRACION = os.path.join(RAIZ, 'supabase', 'migrations', '20261107000001_monetizacion.sql')


def _js(ruta, inicio='{'):
    with open(os.path.join(RAIZ, ruta), encoding='utf-8') as f:
        t = f.read()
    return json.loads(t[t.index(inicio):t.rindex('}') + 1])


def contadores():
    """(clave, valor, etiqueta, operación, fuente, url de la fuente, liga interna).
    Todos son conteos de los archivos de la plataforma: chip «derivado»."""
    s = _js('assets/auditor/data/sat-69b.js', '{"meta"')
    c = _js('assets/auditor/data/comprasmx/indice.js')['meta']
    with open(os.path.join(RAIZ, 'docs', 'boveda', 'evidencias.json'), encoding='utf-8') as f:
        b = json.load(f)
    copiados = sum(1 for e in b['evidencias'].values() if e.get('estado') == 'copiado')
    contratos = sum(a['contratos'] for a in c['archivos'])
    anios = sorted(a['anio'] for a in c['archivos'])
    return [
        ('69b', len(s['r']), 'RFC de la lista 69-B del SAT, con su situación',
         'renglones de la copia del %s (corte del SAT: %s)' % (s['meta']['descarga'], s['meta']['corte']),
         'SAT, listado del art. 69-B', s['meta']['url'], 'herramienta-inspector-efos.html'),
        ('contratos', contratos, 'contratos públicos de ComprasMX, %s' % ' y '.join(anios),
         'suma de los contratos de %d archivos de Datos Abiertos' % len(c['archivos']),
         'ComprasMX, Datos Abiertos', c['url'], 'contratos-publicos.html'),
        ('proveedores', c['proveedores'], 'proveedores del gobierno que puedes revisar',
         'proveedores distintos en esos contratos', 'ComprasMX, Datos Abiertos', c['url'], 'contratos-publicos.html'),
        ('boveda', copiados, 'documentos oficiales guardados con su huella SHA-256',
         'documentos de la bóveda con copia', 'Bóveda de evidencias de Auditavisión', 'pilares.html#base', 'pilares.html#base'),
    ]


def planes_migracion():
    with open(MIGRACION, encoding='utf-8') as f:
        t = f.read()
    t = t[t.index('insert into public.planes'):]
    t = t[:t.index(';')]
    return re.findall(r"\('([a-z]+)', '[^']+', '(?:mes|año|encargo|gratis)'", t)


def revisar():
    """Detiene la generación si el interruptor está encendido y algo falta, o si
    los planes de aquí y los de la base no coinciden."""
    ids = [p['id'] for p in PLANES]
    if planes_migracion() != ids:
        raise SystemExit('monetizacion.py: los planes de PLANES (%s) no son los de la migración (%s)'
                         % (', '.join(ids), ', '.join(planes_migracion())))
    if not MONETIZACION:
        return
    sin = [p['nombre'] for p in PLANES if p['precio'] is None and p['periodo'] != 'encargo']
    if sin:
        raise SystemExit('monetizacion.py: MONETIZACION está encendida y no tienen precio: %s' % ', '.join(sin))
    if not CANAL_PAGO:
        raise SystemExit('monetizacion.py: MONETIZACION está encendida y falta CANAL_PAGO')


def hecho():
    """Lo que se puede saber del repositorio. Lo demás lo marca el autor."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import acceso
    return {
        'canal': bool(CANAL_PAGO),
        'precios': all(p['precio'] is not None or p['periodo'] == 'encargo' for p in PLANES),
        'base': os.path.exists(MIGRACION),
        'candado': not acceso.CANDADO,
        'interruptor': MONETIZACION,
    }


def prueba():
    revisar()
    c = contadores()
    assert len(c) == 4 and all(isinstance(x[1], int) and x[1] > 0 for x in c), c
    assert [p['id'] for p in PLANES][0] == 'gratis' and PLANES[0]['precio'] == 0
    print('monetizacion: prueba bien (%s)' % ', '.join('%s %s' % (x[0], format(x[1], ',')) for x in c))


def main(argv):
    if '--prueba' in argv:
        return prueba()
    revisar()
    h = hecho()
    print('Monetización: %s\n' % ('ENCENDIDA' if MONETIZACION else 'apagada (lista para encender)'))
    for k, que, quien in LISTA:
        est = {True: '✅', False: '⬜'}.get(h.get(k), '❓')
        print('%s %s  · %s' % (est, que, quien))
    print('\n✅ hecho · ⬜ falta · ❓ lo confirma el autor')


if __name__ == '__main__':
    main(sys.argv[1:])
