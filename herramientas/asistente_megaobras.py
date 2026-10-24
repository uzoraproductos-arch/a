# -*- coding: utf-8 -*-
"""Inversión y Megaobras, dentro del chat del Auditor Virtual (pedido del
autor, 24-10-2026: «que toda la información y contenido que obra en la
herramienta de inversión y obra se pueda programar con el auditor
virtual, así como sus vinculaciones directas hacia los portales
correspondientes, visualizaciones de los mapas, salud financiera,
cuestiones de los presidentes»).

No hay una sola cifra nueva. Cada obra sale de simulador_megaobras con lo
mismo que pintan las aplicaciones de la herramienta:

- Aprobado, costo real y sobrecosto: los campos de la obra ya corregidos
  con los documentos oficiales (mo_sector.obras_oficiales), con su estado,
  su rango si lo tiene y su «de dónde sale» (verificacion.definiciones).
- Gana o pierde al año: la medida única de la herramienta (mo_base).
- Lo que dijo la ASF y los documentos de cada obra (verificacion).
- Los seis sexenios con sus obras y sus sumas (mo_tabla._datos), cada uno
  ligado al estado de cuenta de su presidente (radar-estado-de-cuenta.html).
- Las cinco aplicaciones, para abrirlas en el marco del chat como las del
  Modo Inspector (asistente.js las suma a su catálogo).

La dependencia a cargo de cada obra (para abrir su salud financiera en el
Auditor de entes) solo se pone si sus propios documentos la nombran: si
la palabra no aparece en ellos, la generación se detiene.

Los textos de cifra se escriben aquí con los mismos formatos de las
páginas (mo_pulso.mdp y sim_mdp), para que se lean igual en el chat.
"""
import html
import json
import os
import re

import apartados
import mo_base
import mo_pulso
import mo_sector
import mo_tabla

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPIDE = 'radar-estado-de-cuenta.html'


def limpio(t):
    return html.unescape(re.sub(r'\s+', ' ', re.sub('<[^>]+>', '', str(t or '')))).strip()


# Como se dice cada obra en la calle. Se comparan en minúsculas y sin acentos.
ALIAS = {
    'tren-maya': ['tren maya'],
    'megafarmacia': ['megafarmacia', 'mega farmacia', 'cefedis', 'farmacia del bienestar'],
    'dos-bocas': ['dos bocas', 'refineria olmeca', 'olmeca', 'refineria de dos bocas', 'refineria de paraiso'],
    'aifa-texcoco': ['aifa', 'felipe angeles', 'aeropuerto felipe angeles', 'naim', 'naicm', 'texcoco', 'aeropuerto de texcoco',
                     'aeropuerto de santa lucia', 'santa lucia', 'nuevo aeropuerto'],
    'tren-toluca': ['tren toluca', 'tren mexico toluca', 'tren interurbano', 'el insurgente', 'tren insurgente', 'tren de toluca'],
    'agronitrogenados': ['agronitrogenados', 'agro nitrogenados', 'plantas chatarra'],
    'fertinal': ['fertinal', 'grupo fertinal'],
    'estela-luz': ['estela de luz', 'suavicrema'],
    'bunker-garcia-luna': ['bunker', 'garcia luna', 'plataforma mexico'],
    'refineria-tula': ['refineria de tula', 'refineria bicentenario', 'barda de tula', 'barda perimetral', 'tula'],
    'enciclomedia': ['enciclomedia'],
    'fobaproa': ['fobaproa', 'ipab', 'rescate bancario'],
    'farac-carretero': ['farac', 'rescate carretero'],
}

# La dependencia a cargo, solo si sus documentos la nombran (la segunda
# columna es la palabra que debe aparecer en ellos).
ENTE = {
    'tren-maya': ('defensa', 'Defensa'),
    'aifa-texcoco': ('defensa', 'Defensa'),
    'dos-bocas': ('pemex', 'Pemex'),
    'refineria-tula': ('pemex', 'Pemex'),
    'agronitrogenados': ('pemex', 'Petróleos Mexicanos'),
    'fertinal': ('pemex', 'Pemex'),
    'megafarmacia': ('salud', 'Salud'),
    'enciclomedia': ('sep', 'SEP'),
    'bunker-garcia-luna': ('sspc', 'SSPC'),
}


def _anclas(archivo):
    s = open(os.path.join(RAIZ, archivo), encoding='utf-8').read()
    return set(re.findall(r'id="([^"]+)"', s))


def _cifra(o, campo, fmt, ver, pend):
    e = (o.get('estado_campos') or {}).get(campo) or 'pendiente'
    r = (o.get('rangos_campos') or {}).get(campo)
    x = {'v': o[campo], 'e': e, 'vt': fmt(o[campo])}
    if r:
        x['vt'] = 'entre %s y %s; punto medio %s' % (fmt(r['min']), fmt(r['max']), fmt(r['medio']))
        x['op'] = limpio(r.get('op'))
    d = ((ver or {}).get('definiciones') or {}).get(campo)
    if d:
        x['d'] = limpio(d)
    if e == 'pendiente':
        x['p'] = pend
    return x


def _pct(v):
    return ('+' if v > 0 else '') + format(v, '.1f') + ' %'


def datos(d):
    sm = d['simulador_megaobras']
    obras = mo_sector.obras_oficiales(d)
    res = mo_base.resultados(sm)
    V = (sm.get('verificacion') or {}).get('obras') or {}
    F = dict((d.get('costo_vivo_megaobras') or {}).get('fuentes') or {})
    F.update((sm.get('verificacion') or {}).get('fuentes') or {})
    OF = sm.get('operacion_oficial') or {}
    cuenta = (sm.get('cuenta') or {}).get('obras') or {}
    sectores = {s['id']: s for s in sm['sectores']}
    a_sector, a_cuenta, a_tabla = _anclas(mo_tabla.SECTOR), _anclas(mo_tabla.CUENTA), _anclas(mo_tabla.ARCHIVO)
    malos = [k for k in ALIAS if k not in {o['id'] for o in obras}]
    out = []
    for o in obras:
        oid = o['id']
        ver = V.get(oid)
        fu = [{'tx': limpio(F[k]['doc']), 'url': F[k]['url']} for k in (ver or {}).get('fuentes') or [] if k in F]
        r = res[oid]
        rr = {'tipo': r['tipo']}
        if r['tipo'] == 'dato':
            rr.update(v=r['v'], vt=mo_pulso.mdp(abs(r['v'])), anio=r['anio'], e=r['e'], op=limpio(r['op']), nota=limpio(r['nota']),
                      base=mo_tabla.BASE[r['base']], fu=[{'tx': limpio(x['doc']) + ((', ' + limpio(x['pag'])) if x.get('pag') else ''), 'url': x['url']}
                                                         for x in r['f']])
        else:
            rr['txt'] = limpio(r['txt'])
            if r['tipo'] == 'pendiente':
                rr['p'] = 'cuenta-' + oid
        # Lo que el lector puede leer para comprobar a quién le toca.
        textos = json.dumps([ver, cuenta.get(oid), o['nombre'], [F.get(k) for k in (ver or {}).get('fuentes') or []],
                             OF.get('fuentes', {}).get(((OF.get('obras') or {}).get(oid) or {}).get('fuente')),
                             OF.get('fuentes', {}).get(((OF.get('contexto_entidad') or {}).get(oid) or {}).get('fuente'))], ensure_ascii=False)
        ente = None
        if oid in ENTE:
            if ENTE[oid][1] not in textos:
                malos.append('%s: sus documentos no nombran a %s' % (oid, ENTE[oid][1]))
            ente = ENTE[oid][0]
        for a, ids in (('obra-' + oid, a_sector), ('cuenta-' + oid, a_cuenta), ('mt-' + oid, a_tabla)):
            if a not in ids:
                malos.append('#' + a)
        sec = sectores.get(o['sector_id']) or {}
        pend = 'obra-' + oid
        out.append({
            'id': oid, 'n': o['nombre'].split(' (')[0], 'nom': o['nombre'], 'ico': o['icono'], 'pres': o['presidente'],
            'per': o['periodo_sexenal'], 'sec': limpio(sec.get('nombre')), 'sico': sec.get('icono', ''), 'est': limpio(o.get('estatus')),
            'resc': 1 if o.get('tipo') == 'rescate' else 0, 'al': ALIAS.get(oid, []),
            'c': {'pres': _cifra(o, 'inversion_presupuestada_mdp', mo_pulso.mdp, ver, pend),
                  'real': _cifra(o, 'inversion_real_mdp', mo_pulso.mdp, ver, pend),
                  'sob': dict(_cifra(o, 'sobrecosto_pct', _pct, ver, pend), et=limpio(o.get('sobrecosto_etiqueta') or 'Sobrecosto'))},
            'res': rr, 'asf': limpio((ver or {}).get('hallazgo')) or None, 'fu': fu, 'ente': ente,
            'ir': {'ficha': mo_tabla.SECTOR + '#obra-' + oid, 'cuenta': mo_tabla.CUENTA + '#cuenta-' + oid,
                   'tabla': mo_tabla.ARCHIVO + '#mt-' + oid},
        })

    # Los seis sexenios, cada uno con el estado de cuenta de su presidente.
    s = open(os.path.join(RAIZ, EXPIDE), encoding='utf-8').read()
    adm = {a['n']: a['id'] for a in json.loads(re.search(r'id="rdDatos">(.*?)</script>', s, re.S).group(1))['admins']}
    _sm, _sec, _res, grupos, todos = mo_tabla._datos(d)
    sx = []
    for g in grupos:
        if g['nombre'] not in adm:
            malos.append('sin estado de cuenta: ' + g['nombre'])
        if 'mt-sx-' + g['clave'] not in a_tabla:
            malos.append('#mt-sx-' + g['clave'])
        sx.append({'k': g['clave'], 'n': g['corto'], 'nom': g['nombre'], 'a0': g['a0'], 'a1': g['a1'], 'adm': adm.get(g['nombre']),
                   'ids': [o['id'] for o in g['obras']], 'costo': g['costo'], 'costot': mo_pulso.sim_mdp(g['costo']),
                   'resc': g['rescates'], 'pcosto': 1 if g['pend_costo'] else 0, 'res': g['res'], 'rest': mo_pulso.mdp(abs(g['res'])),
                   'nres': g['n_res'], 'ir': mo_tabla.ARCHIVO + '#mt-sx-' + g['clave']})

    # Las cuatro cifras de la herramienta, como las dice su portada.
    solo = [o for o in obras if o.get('tipo') != 'rescate']
    real = sum(o['inversion_real_mdp'] for o in solo)
    presu = sum(o['inversion_presupuestada_mdp'] for o in solo)
    b = mo_base.balance(sm)
    tot = {'n': len(solo), 'nresc': len(obras) - len(solo), 'real': real, 'realt': mo_pulso.sim_mdp(real), 'presu': presu,
           'presut': mo_pulso.sim_mdp(presu), 'brecha': real - presu, 'brechat': mo_pulso.sim_mdp(real - presu),
           'neto': b['neto'], 'netot': mo_pulso.mdp(abs(b['neto'])), 'pierde': b['pierde'], 'pierdet': mo_pulso.mdp(abs(b['pierde'])),
           'gana': b['gana'], 'ganat': mo_pulso.mdp(b['gana']), 'ndato': b['n_dato'], 'npierde': b['n_pierde'], 'ngana': b['n_gana'],
           'npend': b['n_pend'], 'nna': b['n_na'], 'anios': b['anios'], 'medida': limpio(mo_base.medida_txt(sm))}

    # Las cinco aplicaciones, con su número y su página.
    h = next(x for x in apartados.HERRAMIENTAS if x[1] == 'obras')
    apps = []
    for i, t in enumerate(h[7]):
        url = apartados.modulo_archivo(h[0], t[0])
        if not os.path.exists(os.path.join(RAIZ, url)):
            malos.append(url)
        apps.append({'id': 'mo' + re.sub(r'^herramienta-megaobras-|\.html$|pulso-', '', t[0]), 'k': i + 1, 'ico': t[1], 'n': t[2],
                     'frase': t[3], 'desc': limpio(t[4]), 'url': url})

    # Los portales oficiales donde se sigue la inversión pública.
    portales = [{'tx': limpio(F[k]['doc']), 'url': F[k]['url']} for k in ('opa', 'cp', 'asf24') if k in F]
    if malos:
        raise SystemExit('asistente_megaobras: ' + '; '.join(malos))
    return {'obras': out, 'sx': sx, 'tot': tot, 'apps': apps, 'pagina': h[0], 'nombre': h[3], 'portales': portales,
            'pend': 'pendientes.html#tema-megaobras', 'expide': EXPIDE}
