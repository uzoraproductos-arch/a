# -*- coding: utf-8 -*-
"""Genera UNA pagina de aplicacion del Modo Inspector, para probarla sin
regenerar todo el sitio (12-10-2026).

    python3 herramientas/insp_vista.py inspefos

Usa el sello vigente de index.html. sello.py sigue siendo el que genera
todo el sitio.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apartados as ap  # noqa: E402
import auditorias  # noqa: E402


def main(clave):
    d = open(os.path.join(ap.RAIZ, 'index.html'), 'rb').read().decode('utf-8')
    sello = re.search(r'id="selloVersion">([0-9a-z]+)<', d).group(1)
    base = auditorias.db()
    refs = {r['id']: r for r in base['referencias_legales']}

    def ref(rid):
        r = refs[rid]
        return ap.nota_ref(rid, r['num'], re.sub('<[^>]+>', '', r['cita_apa'])[:160].replace('"', '&quot;'))
    rubro = next(x[1] for x in ap.HERRAMIENTAS if clave in [t[0] for t in x[7]])
    n, h = next((k, x) for k, x in enumerate(ap.HERRAMIENTAS, 1) if x[1] == rubro)
    i = [t[0] for t in h[7]].index(clave)
    m = ap.insp_nativa(ap.herramienta_modulo(h, n, i), clave, base, ref)
    texto = ap.pagina(m, sello).replace('\r\n', '\n').replace('\n', '\r\n')
    open(os.path.join(ap.RAIZ, m['archivo']), 'wb').write(texto.encode('utf-8'))
    print('generada', m['archivo'])


if __name__ == '__main__':
    main(sys.argv[1])
