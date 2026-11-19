#!/usr/bin/env python3
"""Lo que cada modo del Auditor suma a la respuesta de un servicio (19-11-2026).

Las respuestas de los servicios (`srv_<id>`, `srv_fam_*`, `srv_perfil_*`,
`srv_catalogo`) las arma servicios_fichas.py. Aquí solo se les agrega:

- **Quién puede pedirlo hoy** (`SERVICIOS_OPERAN` de apartados.py, decisión del
  autor, 19-11-2026: los Servicios operan para quien tiene un código de acceso
  vigente). El servidor revisa lo mismo (`SERVICIOS_CON_CODIGO` de
  supabase/functions/recibir-formulario): si no dicen lo mismo, la generación
  se detiene.
- **Los datos de la capa de cada modo** (`svCapa()` de asistente.js): la
  familia, lo que se hace gratis hoy (de `hace` de servicios_fichas.FICHAS), el
  compromiso de independencia de su familia y lo que un encargo no es.

Reglas (AGENTS.md §0 quater y §2): nunca un monto, y nunca se dice que la
plataforma evita el fraude ni que cumple por el cliente.
"""

import html
import os

import apartados as A

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# El compromiso de la política de independencia que el modo Periodista pone a
# la vista en cada familia, y lo que un encargo no es (modo Inspector). Se
# buscan por el principio de su título en apartados.INDEPENDENCIA.
IND_FAMILIA = {'electoral': 'En campaña', 'investigacion': 'Quien encarga', 'prevencion': 'Lo que no está en venta', 'formacion': 'Lo que no está en venta'}
IND_NO_ES = 'Es investigación documental'


def _ind(prefijo):
    x = [c for c in A.INDEPENDENCIA if c[0].startswith(prefijo)]
    if len(x) != 1:
        raise SystemExit('asistente_servicios.py: no encuentro en INDEPENDENCIA el compromiso «%s…»' % prefijo)
    return list(x[0])


def abre():
    """Quién puede pedir un servicio hoy, cotejado contra el servidor."""
    with open(os.path.join(RAIZ, 'supabase', 'functions', 'recibir-formulario', 'index.ts'), encoding='utf-8') as f:
        srv = 'const SERVICIOS_CON_CODIGO = true;' in f.read()
    if srv != (A.SERVICIOS_OPERAN == 'codigo'):
        raise SystemExit('asistente_servicios.py: SERVICIOS_OPERAN de apartados.py y SERVICIOS_CON_CODIGO de recibir-formulario no dicen lo mismo')
    return ('Ya opera para quien tiene un código de acceso vigente: arma tu solicitud, ve cómo queda y envíala; te respondemos por escrito.'
            if A.SERVICIOS_OPERAN else
            'Los servicios se abren con el lanzamiento: ya puedes armar tu solicitud y ver cómo queda antes de mandarla.')


def enriquece(t):
    """Agrega a las respuestas srv_<id> de D.san.t el aviso de quién puede pedirlas
    y los datos de svCapa(). Cambia `t` en su lugar y lo devuelve."""
    import servicios_fichas as sf
    fam = {x[0] for x in A.LINEAS}
    if fam - set(IND_FAMILIA):
        raise SystemExit('asistente_servicios.py: estas familias no tienen su compromiso en IND_FAMILIA: %s' % ', '.join(sorted(fam - set(IND_FAMILIA))))
    a = '<p><b>Quién puede pedirlo:</b> %s</p>' % html.escape(abre(), quote=False)
    noes = _ind(IND_NO_ES)
    for sid, _ico, _n, _q, _r, _p, linea in A.SERVICIOS:
        k = 'srv_' + sid
        if k not in t:
            raise SystemExit('asistente_servicios.py: el servicio «%s» no tiene su respuesta %s en el chat' % (sid, k))
        x = t[k]
        x['h'] = x['h'].replace('<p><a href="%s">' % (sf.PAGINA % sid), a + '<p><a href="%s">' % (sf.PAGINA % sid), 1)
        if a not in x['h']:
            raise SystemExit('asistente_servicios.py: no encuentro dónde poner el aviso en %s' % k)
        gr = [[lg, tit] for _i, tit, _tx, lg, et in sf.FICHAS[sid]['hace'] if et in ('Gratis', 'Nuevo')][:3]
        x.update({'fam': linea, 'gr': gr, 'ind': _ind(IND_FAMILIA[linea]), 'noes': noes})
    return t


if __name__ == '__main__':
    print('asistente_servicios.py:', abre())
