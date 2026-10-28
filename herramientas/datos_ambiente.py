# -*- coding: utf-8 -*-
"""Datos → Medio ambiente (pedido del autor, 22-10-2026).

La cuarta tarjeta de Datos. Reune la parte informativa que vivia dentro de
la herramienta Costo Ambiental: la basura, lo que se gasta en proteger, el
presupuesto del sector, la huella de las megaobras, las leyes, quien lo mide,
el PIB que no alcanza y sus puntos ciegos. La herramienta se quedo con lo que
el lector calcula (su ticket, el reloj, los simuladores, el auditor y las
investigaciones).

No se reescribe ninguna cifra: cada pagina toma su bloque del HTML que ya
arman am_basura.construir() y am_pib._completo() (am_cortes.bloque), con sus
estilos y su JS. Los dos scripts toleran que falten las demas secciones.

Lo llama apartados.generar() (paginas()).
"""
import am_basura
import am_cortes
import am_pib

PORTADA = 'datos-medio-ambiente.html'
NOMBRE = 'Medio ambiente'
ICONO = '🌎'
HERRAMIENTA = 'herramienta-ambiente.html'

GRUPOS = {'dano': '📉 Lo que cuesta el daño', 'basura': '🗑️ Lo que se tira',
          'dinero': '🏛️ El dinero y las obras', 'reglas': '⚖️ Las reglas y quién mide'}

# (id, archivo, icono, titulo, de que trata, origen, bloques, grupo)
# origen: 'ab' (am_basura) o 'ap' (am_pib); bloques: ids de <section> o
# (origen, clase, etiqueta) para los que no tienen id: la procedencia de las
# cuentas ecologicas (de am_pib) cierra la pagina de quien lo mide.
PARTES = [
    ('pib', 'datos-ambiente-pib.html', '📉', 'El PIB que no alcanza',
     'Lo que el país anunció haber producido, menos lo que costó a la naturaleza: la resta paso a paso',
     'ap', [('ap', 'ap-arranque', 'section'), 'apCascada'], 'dano'),
    ('desglose', 'datos-ambiente-desglose.html', '🌫️', 'Qué se acabó y qué se ensució',
     'El costo ambiental en sus dos partes, el agotamiento y la degradación, renglón por renglón',
     'ap', ['apDesglose'], 'dano'),
    ('proteger', 'datos-ambiente-proteger.html', '💸', 'Lo que se gasta en proteger',
     'El gasto público en proteger el ambiente frente al costo del daño, con su calculadora',
     'ab', ['abProteger'], 'dano'),
    ('basura', 'datos-ambiente-basura.html', '🗑️', 'La basura',
     'Un servicio municipal sin dinero federal: lo que se genera, lo que se recolecta y a dónde va',
     'ab', ['abBasura'], 'basura'),
    ('presupuesto', 'datos-ambiente-presupuesto.html', '🏛️', 'El presupuesto ambiental',
     'El Ramo 16 en 2026 y el proyecto 2027, órgano por órgano, con su tabla en CSV',
     'ab', ['abPresupuesto'], 'dinero'),
    ('megaobras', 'datos-ambiente-megaobras.html', '🏗️', 'La huella de las megaobras',
     'El mapa de México con las megaobras e infraestructura por estado, su gasto federalizado y su alerta ambiental',
     'ab', ['abMegaobras'], 'dinero'),
    ('leyes', 'datos-ambiente-leyes.html', '⚖️', 'Las leyes que aplican',
     'Tu derecho a un medio ambiente sano, la basura, las obras y el clima, con su texto vigente',
     'ab', ['abLeyes'], 'reglas'),
    ('ciegos', 'datos-ambiente-puntos-ciegos.html', '🔦', 'Puntos ciegos y consecuencias',
     'Lo que el indicador que se anuncia no dice, y por qué el daño con precio oficial obliga',
     'ap', ['apCiegos'], 'reglas'),
    ('quien', 'datos-ambiente-quien-lo-mide.html', '🔎', 'Quién lo mide y de dónde sale',
     'Las instituciones que cambiaron con las reformas, los documentos y lo que todavía falta',
     'ab', ['abQuien', ('ap', 'ap-aviso', 'aside')], 'reglas'),
]

# Anclas de las paginas viejas de la herramienta (herramienta-ambiente-basura
# redirige aqui conservando el ancla).
ANCLAS = {'abBasura': 'basura', 'abProteger': 'proteger', 'abPresupuesto': 'presupuesto', 'abMegaobras': 'megaobras',
          'abLeyes': 'leyes', 'abQuien': 'quien', 'apCascada': 'pib', 'apDesglose': 'desglose', 'apCiegos': 'ciegos'}

ENTRADA = ('El deterioro del ambiente también es gasto público: lo pagamos en agua, aire, suelo y basura. Aquí están las cifras '
           'de referencia, cada una con su documento: cuánto le cuesta al país el daño, cuánto se gasta en protegerlo, a dónde '
           'va la basura, cuánto recibe el sector ambiental y qué dicen las leyes. Lo que resuelve la PROFEPA con su dinero (denuncias, rezago y multas) '
           'está en <a href="datos-justicia-ambiental.html">Justicia ambiental</a>. Para hacer tus propias cuentas, '
           've a la herramienta <a href="%s">Costo Ambiental</a>.' % HERRAMIENTA)

HACER = ('<p class="apartado-nota">🧮 ¿Quieres hacer tus cuentas? En la herramienta <a href="%s">Costo Ambiental</a> '
         'sacas tu estado de cuenta ambiental, simulas el crecimiento real y la inversión ambiental, y auditas a cada órgano del sector.</p>' % HERRAMIENTA)


def _archivo(id_):
    return next(p[1] for p in PARTES if p[0] == id_)


def _pagina_bloque(htmls, origen, bloques):
    html = htmls[origen]
    trozos = []
    for b in bloques:
        if isinstance(b, tuple):
            t = am_cortes.bloque(htmls[b[0]], clase=b[1], etiqueta=b[2])
        else:
            t = am_cortes.bloque(html, id_=b)
        trozos.append(t)
    cuerpo = ''.join(trozos)
    if any(isinstance(b, tuple) and b[0] == 'ap' for b in bloques) or origen == 'ap':
        cuerpo = am_cortes.sin_numeros(cuerpo, 'ap-n')
        # Fuera de la herramienta, el arranque no lleva su indice ni su
        # rotulo de aplicacion, y el aviso no manda a las demas aplicaciones.
        cuerpo = _sin(cuerpo, '\n    <ol class="ap-indice"', '</ol>')
        cuerpo = _sin(cuerpo, '\n    <p class="ap-kicker">', '</p>')
        cuerpo = _sin(cuerpo, '\n    <p class="ap-hermanas">', '</p>')
    if origen == 'ap':
        return '<div class="ap" id="apRaiz">' + cuerpo + am_cortes.guion(html, 'apDatos') + '\n</div>'
    return '<div class="ab" id="abRaiz">' + cuerpo + am_cortes.guion(html, 'abDatos') + '\n</div>'


def _sin(html, inicio, fin):
    i = html.find(inicio)
    if i < 0:
        return html
    return html[:i] + html[html.index(fin, i) + len(fin):]


def _enlaces(html):
    """Los enlaces internos que apuntaban a las paginas viejas de la
    herramienta llevan a su pagina de Datos."""
    return (html.replace('href="herramienta-ambiente-pib.html"', 'href="%s"' % _archivo('pib'))
                .replace('href="herramienta-ambiente-basura.html"', 'href="%s"' % PORTADA))


def paginas(base, ref):
    """La portada y una pagina por parte, como las de datos_paginas()."""
    import apartados as ap
    html = {'ab': am_basura.construir(base, ref), 'ap': am_pib._completo(base, ref)}
    estilos = {'ab': ['am-basura.css'], 'ap': ['am-pib.css']}
    scripts = {'ab': ['am-basura.js'], 'ap': ['am-pib.js']}
    out = [{
        'archivo': PORTADA, 'menu': NOMBRE, 'menu_archivo': 'descarga-los-datos.html',
        'padre': ('descarga-los-datos.html', 'Datos'),
        'icono': ICONO, 'titulo': NOMBRE, 'lema': 'El costo del daño ambiental, con sus documentos',
        'entrada': ENTRADA, 'antes': '      ' + HACER,
        'pestanas': True, 'pista': 'Cada tarjeta abre su propia página.',
        'hash_a_pagina': dict([(p[0], p[1]) for p in PARTES] + [(k, _archivo(v)) for k, v in ANCLAS.items()]),
        'secciones': [dict({'id': p[0], 'pagina': p[1], 'pestana': (p[2], p[3], p[4])},
                           **({'grupo': GRUPOS[p[7]]} if i == 0 or PARTES[i - 1][7] != p[7] else {}))
                      for i, p in enumerate(PARTES)],
    }]
    for id_, archivo, ico, titulo, frase, origen, bloques, grupo in PARTES:
        out.append({
            'archivo': archivo, 'menu': titulo, 'menu_archivo': 'descarga-los-datos.html',
            'padre': ('descarga-los-datos.html', 'Datos'), 'padre2': (PORTADA, NOMBRE),
            'icono': ico, 'titulo': titulo, 'lema': '%s · %s' % (NOMBRE, GRUPOS[grupo][2:].strip()),
            'entrada': frase + '.',
            'estilos': estilos[origen] + [e for b in bloques if isinstance(b, tuple) and b[0] != origen for e in estilos[b[0]]],
            'scripts': scripts[origen],
            'pie_extra': ap.partes_nav(NOMBRE, PORTADA, ICONO, PARTES, archivo),
            'secciones': [{'id': id_ + '-pag', 'titulo': titulo, 'texto': '', 'sin_cab': True, 'tarjetas': [],
                           'bloque': _enlaces(_pagina_bloque(html, origen, bloques))}],
        })
    return out
