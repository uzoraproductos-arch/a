# -*- coding: utf-8 -*-
"""Cortes de las paginas de Costo Ambiental (pedido del autor, 22-10-2026).

Las aplicaciones am_basura y am_pib escriben su pagina completa; desde que la
parte informativa se mudo a Datos → Medio ambiente (datos_ambiente.py) y la
herramienta se quedo solo con lo que el lector calcula, cada pagina toma de
ese HTML solo los bloques que le tocan. Asi las cifras, sus fuentes y sus
chips se escriben en un solo lugar.
"""
import re


def bloque(html, id_=None, clase=None, etiqueta='section'):
    """El bloque <etiqueta ...> con ese id (o esa clase) hasta su cierre, que
    va en su propio renglon con dos espacios de sangria."""
    if id_:
        m = re.search(r'\n  <%s [^>]*id="%s"' % (etiqueta, re.escape(id_)), html)
    else:
        m = re.search(r'\n  <%s class="%s[ "]' % (etiqueta, re.escape(clase)), html)
    if not m:
        raise ValueError('No encontré el bloque %s' % (id_ or clase))
    fin = html.index('\n  </%s>' % etiqueta, m.start()) + len('\n  </%s>' % etiqueta)
    return html[m.start():fin]


def guion(html, id_):
    """El <script type="application/json" id="..."> con los datos del JS."""
    m = re.search(r'\n  <script type="application/json" id="%s">.*?</script>' % re.escape(id_), html, re.S)
    if not m:
        raise ValueError('No encontré los datos %s' % id_)
    return m.group(0)


def sin_numeros(html, clase):
    """Quita los numeros de capitulo (<span class="ap-n">1</span>) de los
    titulos: fuera de su pagina original ya no siguen un orden."""
    return re.sub(r'<span class="%s">\d+</span> ' % re.escape(clase), '', html)
