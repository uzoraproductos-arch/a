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

# Ronda 24 (25-11-2026, decisión del autor): la tabla del Precio Fundador se publica en servicios.html. **Es el único lugar
# donde vive un monto de la plataforma**: lo leen servicios.html (#precio-fundador) y la Mesa de Trabajo del Auditor
# (auditor_bento.py), y apartados.pagina() detiene la generación si aparece un monto en MXN fuera de los bloques
# marcados con <!--precio-fundador-->. Los pagos en línea siguen apagados (MONETIZACION): hoy se opera con códigos
# piloto y promocionales; el cobro en línea entra con su pasarela (Ronda 27). Matiza la Ronda 10: los paquetes piloto
# (PAQUETES de apartados.py) siguen sin monto.
PRECIO_FUNDADOR = {
    'decision': '25-11-2026',
    'fundadores': 100,
    'libre': {'nombre': 'Libre', 'precio': 0, 'nota': 'Siempre, sin tarjeta', 'bienvenida': 5,
              'incluye': ['El Auditor, en sus cuatro modos', 'El Planisferio', 'El Noticiero y las Auditorías en imágenes',
                          'La consulta de un RFC en la lista 69-B', 'El simulador del predial']},
    'paquetes': [{'id': 't20', 'tokens': 20, 'precio': 149}, {'id': 't100', 'tokens': 100, 'precio': 499}],
    # (clave, qué, tokens): lo que gasta cada acción.
    'consumo': [('dictamen', 'Dictamen con huella SHA-256', 1), ('lote', 'Lote XML / CSV · Cero CIEC', 2),
                ('semaforo', 'Semáforo Patrimonial completo', 3)],
    'planes': [
        {'id': 'pro', 'nombre': 'Plan Pro', 'precio': 149, 'regular': 249, 'anual': 1490, 'tokens_mes': 30,
         'para': 'Personas, profesionales independientes y contadores.',
         'incluye': ['30 tokens al mes', 'Vigía semanal de hasta 25 RFC', 'Portafolio ampliado']},
        {'id': 'pyme', 'nombre': 'Plan PyME / Despacho', 'precio': 699, 'regular': 999, 'anual': 6990, 'tokens_mes': 200,
         'para': 'Empresas, despachos contables y áreas de cumplimiento.',
         'incluye': ['200 tokens al mes', 'Escudo Cero CIEC masivo', 'Vigía semanal de hasta 250 RFC', 'Dictámenes ilimitados']},
    ],
    'medida': {'nombre': 'Gobierno / Corporativo', 'desde': 2500,
               'incluye': ['Radiografías municipales', 'Entrega-recepción', 'Soporte dedicado']},
}


def pesos(n):
    """Un monto de la tabla del Precio Fundador, como se escribe en la página."""
    return '$%s MXN' % format(n, ',')


def consumo(clave):
    """Los tokens que gasta una acción de la tabla (detiene la generación si no existe)."""
    for k, _q, t in PRECIO_FUNDADOR['consumo']:
        if k == clave:
            return t
    raise SystemExit('monetizacion.py: el consumo «%s» no está en PRECIO_FUNDADOR' % clave)


def plan(pid):
    for p in PRECIO_FUNDADOR['planes']:
        if p['id'] == pid:
            return p
    raise SystemExit('monetizacion.py: el plan «%s» no está en PRECIO_FUNDADOR' % pid)


def revisa_fundador():
    """La tabla cuadra consigo misma: el anual son diez meses (dos gratis), el precio de fundador es menor al regular,
    los tokens de cada plan son los que dice su primera línea y nada es negativo."""
    F = PRECIO_FUNDADOR
    for p in F['planes']:
        if p['anual'] != p['precio'] * 10:
            raise SystemExit('monetizacion.py: el anual de %s no son diez meses (dos gratis)' % p['nombre'])
        if not 0 < p['precio'] < p['regular']:
            raise SystemExit('monetizacion.py: el Precio Fundador de %s no es menor al regular' % p['nombre'])
        if p['incluye'][0] != '%d tokens al mes' % p['tokens_mes']:
            raise SystemExit('monetizacion.py: %s no dice sus tokens al mes en su primera línea' % p['nombre'])
    if any(x['precio'] <= 0 or x['tokens'] <= 0 for x in F['paquetes']) or F['medida']['desde'] <= 0:
        raise SystemExit('monetizacion.py: un paquete o el plan a medida no tiene monto')
    if F['libre']['precio'] != 0 or any(t <= 0 for _k, _q, t in F['consumo']):
        raise SystemExit('monetizacion.py: el plan Libre cobra o una acción no gasta tokens')


# Los montos en MXN solo viven dentro de estos bloques (apartados.pagina() lo revisa).
MARCA_PRECIO = ('<!--precio-fundador-->', '<!--/precio-fundador-->')
_MONTO = re.compile(r'\$\s?\d[\d,.]*\s*MXN')


def montos_fuera(texto):
    """Los montos en MXN que aparecen fuera de los bloques del Precio Fundador (debe ser una lista vacía)."""
    a, b = (re.escape(x) for x in MARCA_PRECIO)
    return _MONTO.findall(re.sub(a + '.*?' + b, '', texto, flags=re.S))


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
    # El padrón de contrapartes y el Registro Público Único (18-11-2026): lo
    # nuevo que ya se revisa, contado de sus archivos como lo demás.
    pm = _js('assets/auditor/data/padron/meta.js')
    rpu = _js('assets/auditor/data/deuda-rpu.js', '{"meta"')['meta']
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
        ('padron', pm['rfc'], 'RFC en las listas del SAT de los arts. 69, 17-H Bis y 69-B Bis',
         'RFC distintos en %d listas del SAT, con la OFAC y la ONU aparte' % len(pm['orden']),
         'SAT, datos abiertos: contribuyentes publicados', pm['sat'][pm['orden'][0]]['pagina'], 'herramienta-inspector-padron.html'),
        ('rpu', rpu['n'], 'créditos y obligaciones de estados y municipios, uno por uno',
         'renglones del Registro Público Único al %s' % rpu['corteTxt'], 'SHCP, Registro Público Único', rpu['pagina'], 'planisferio.html?d=deuda'),
    ] + _mas()


def _mas():
    """Ronda 7 (22-11-2026, pedido del autor: «La base, al día» con todo lo que ya tiene la base). Cada número se cuenta o se lee
    de su archivo al generar, nunca a mano."""
    import subprocess
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    S = _js('assets/auditor/data/sancionados.js')
    I = _js('assets/auditor/data/sanciones-int.js')
    F = _js('assets/auditor/js/municipios-fraude.js')
    with open(os.path.join(RAIZ, 'docs', 'salud', 'issste-anuario-2025.json'), encoding='utf-8') as f:
        A = json.load(f)
    with open(os.path.join(RAIZ, 'docs', 'vivienda', 'shf-precios-vivienda.json'), encoding='utf-8') as f:
        H = json.load(f)
    js = ("global.window={};require(%s);require(%s);var E=window.AUDIT_MUNICIPIOS.ent,n=0;"
          "Object.keys(E).forEach(function(k){E[k].lista.forEach(function(r){if(+r[0]<990)n++;});});"
          "var c=window.AUDIT_DB.cuenta_publica_asf.cp2024;process.stdout.write(JSON.stringify([n,c.total.auditorias,c.corte]));"
          % (json.dumps(os.path.join(RAIZ, 'assets', 'auditor', 'js', 'municipios-efipem.js')),
             json.dumps(os.path.join(RAIZ, 'assets', 'auditor', 'js', 'audit-database.js'))))
    nmun, asf, asf_corte = json.loads(subprocess.run(['node', '-e', js], check=True, capture_output=True, text=True).stdout)
    import cc_predial
    pred = cc_predial.MUNICIPIOS
    nent = len({m['ent'] for m in pred})
    ofac = sum(1 for r in I['r'] if r[0] == 'ofac')
    return [
        ('sancionados', len(S['r']), 'empresas proveedoras y contratistas sancionadas, con su expediente',
         'personas morales del Directorio al %s (las personas físicas solo se cuentan)' % S['corte'], S['fuente'], S['url'], 'herramienta-inspector-padron.html'),
        ('municipios', nmun, 'municipios y alcaldías con su ficha: su cuenta, su gente y sus carpetas por fraude',
         'claves del padrón municipal del INEGI (sin «No especificado»), con el Censo 2020 y el SESNSP (%s y %s)' % (F['corte2025'], F['corte2026']),
         'INEGI y SESNSP', F['pagina'], 'planisferio.html'),
        ('predial', len(pred), 'municipios y alcaldías con su predial cotejado contra su ley, en %d entidades' % nent,
         'renglones del simulador del predial (cc_predial.py), cada uno con su ley y su huella', 'Leyes de Ingresos y de Hacienda municipales 2026',
         'herramienta-calculadora-predial.html', 'herramienta-calculadora-predial.html'),
        ('issste', A['totales']['derechohabientes'], 'derechohabientes del ISSSTE en su Anuario 2025, estado por estado, junto a la Memoria del IMSS',
         'cifra del Anuario Estadístico 2025 del ISSSTE (oficial), recuadrada con sus 32 entidades', A['fuente'], A['url'], 'planisferio.html?d=salud'),
        ('shf', len(H['municipios']), 'municipios con el precio de la vivienda del Índice SHF (%s)' % H['corte'],
         'municipios del Índice SHF de Precios de la Vivienda, además de las 32 entidades', 'Sociedad Hipotecaria Federal', H['pagina'], 'herramienta-calculadora-predial.html'),
        ('asf', asf, 'auditorías de la ASF a la Cuenta Pública 2024, con lo que quedó por aclarar',
         'auditorías de la Matriz de Datos Básicos de la ASF (corte %s)' % asf_corte, 'Auditoría Superior de la Federación', 'https://www.asf.gob.mx/', 'herramienta-inspector-asf.html'),
        ('ofac-onu', len(I['r']), 'registros de las listas de sanciones de la OFAC y la ONU',
         '%s de la OFAC y %s de la ONU, en sanciones-int.js' % (format(ofac, ','), format(len(I['r']) - ofac, ',')), 'OFAC (EE. UU.) y Consejo de Seguridad de la ONU',
         'https://sanctionslist.ofac.treas.gov/', 'herramienta-inspector-padron.html'),
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
    revisa_fundador()
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
    revisa_fundador()
    assert montos_fuera('a $149 MXN b') == ['$149 MXN'] and not montos_fuera(MARCA_PRECIO[0] + '$149 MXN' + MARCA_PRECIO[1])
    c = contadores()
    assert len(c) == 13 and all(isinstance(x[1], int) and x[1] > 0 for x in c), c
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
