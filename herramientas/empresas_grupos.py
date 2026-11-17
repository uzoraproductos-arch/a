# -*- coding: utf-8 -*-
"""Grupos empresariales y sus filiales, para el chat y para Contratos públicos
(pedido del autor, 17-11-2026: «le pregunté al chat por Grupo Prodi y no salió
información… quiero integrar a la base de datos toda la información necesaria
para responder esa clase de preguntas»).

El problema: muchos grupos no contratan con su nombre. Contrata una filial o
un consorcio, y quien busca al grupo no encuentra nada. Este módulo dice, de
cada grupo, **con qué empresas aparece en ComprasMX** y **qué falta cotejar**.

Reglas (AGENTS.md §2 y §2 bis):

- **Ninguna cifra se escribe aquí.** Los contratos se leen de ComprasMX
  (assets/auditor/data/comprasmx/) por el RFC de cada empresa: si el RFC no
  está en el catálogo, la generación se detiene.
- **El vínculo entre el grupo y la empresa necesita documento.** Mientras solo
  lo diga la prensa, va como `pendiente`, con su ficha en el Registro.
- **Contrato, concesión y permiso no son lo mismo** (FIGURAS): ComprasMX trae
  contratos; una concesión se acredita con su título. Lo que la prensa cuenta
  y aún no cotejamos va en `cotejar`, con el portal donde debe estar su
  documento, **sin montos**.
- **A las personas no se les nombra** (dueños, socios, familiares): la que
  contrata con el gobierno es la empresa.
- **No se dice el partido de un gobierno.** Los documentos dicen qué gobierno
  firmó y en qué año; las mismas reglas valen para todos.

Un grupo nuevo necesita su renglón en GRUPOS y su pregunta en
preguntas_auditor.json.
"""
import html
import json
import os
import re
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CMX = os.path.join(RAIZ, 'assets', 'auditor', 'data', 'comprasmx')
PAGINA = 'contratos-publicos.html'
PLATAFORMA = 'Auditavisión: falta de la plataforma, que aún no coteja ese documento'

# Las tres figuras con que una empresa trabaja para un gobierno o usa un bien
# público. Cada una con su ley, cotejada contra el texto vigente de la Cámara
# de Diputados (LCPAF, última reforma DOF 14-11-2025; LGBN).
FIGURAS = [
    {'id': 'contrato', 'n': 'Contrato de obra o de compra',
     'tx': 'El gobierno paga a la empresa por construir, vender o dar un servicio. Es lo que trae ComprasMX.',
     'ley': 'Art. 134 de la Constitución · Ley de Obras Públicas y Servicios Relacionados con las Mismas'},
    {'id': 'concesion', 'n': 'Concesión',
     'tx': ('El gobierno no paga: da a la empresa el derecho de construir, operar y explotar un bien o un servicio público '
            '(una autopista, por ejemplo) por un plazo, y la empresa cobra a quien lo usa. Se acredita con su título de concesión, '
            'no con un contrato de ComprasMX.'),
     'ley': 'Art. 6o. de la Ley de Caminos, Puentes y Autotransporte Federal (hasta 30 años) · arts. 16 y 73 de la Ley General de Bienes Nacionales (hasta 50 años)'},
    {'id': 'permiso', 'n': 'Permiso',
     'tx': ('Una autorización para usar un bien público por un tiempo, que la autoridad puede revocar. Lo regula la ley de cada gobierno; '
            'se acredita con el permiso mismo.'),
     'ley': 'Art. 16 de la Ley General de Bienes Nacionales (no crea derechos reales) y la ley patrimonial de cada entidad'},
]

GRUPOS = [
    {'id': 'prodi', 'n': 'Grupo PRODI',
     'al': ['grupo prodi', 'prodi', 'mota engil', 'mota engil mexico', 'motaengil'],
     'que': ('La plataforma no encuentra contratos a nombre de «Grupo PRODI» en ComprasMX. La prensa lo describe como socio de '
             '<b>Mota-Engil México</b>, que es la empresa que sí aparece contratando.'),
     'emp': ['MME100125RS6'],
     'vin': {'id': 'grupo-prodi-vinculo',
             'que': 'El documento que acredite que Grupo PRODI es socio de Mota-Engil México, y con qué parte',
             'porque': ('La prensa lo reporta citando el informe anual de la empresa matriz, Mota-Engil. La plataforma aún no coteja '
                        'ese informe ni el Registro Público de Comercio, así que no lo afirma. No es omisión de una dependencia.'),
             'url': 'https://www.mota-engil.com/', 'url_txt': 'Mota-Engil: informes anuales de la empresa'},
     'asf': [(2022, 111, 'Tren Maya, Tramo 1 (Palenque-Escárcega)')],
     'cotejar': [
         {'id': 'grupo-prodi-tultepec', 'fig': 'concesion',
          'que': 'Autopista Tultepec-AIFA-Pirámides: el título de concesión, qué gobierno lo otorgó, en qué fecha y por cuántos años',
          'porque': ('Proyectos México la tiene registrada como proyecto de un gobierno estatal adjudicado a Mota-Engil México. '
                     'Falta cotejar el título de concesión y su publicación oficial.'),
          'url': 'https://www.proyectosmexico.gob.mx/proyecto_inversion/0900-autopista-tultepec-aeropuerto-internacional-felipe-angeles-piramides/',
          'url_txt': 'Proyectos México: ficha de la autopista'},
         {'id': 'grupo-prodi-aztlan', 'fig': 'permiso',
          'que': 'Parque Aztlán (Chapultepec, Ciudad de México): el permiso para operar el parque, su plazo y lo que la empresa paga por él',
          'porque': ('La prensa lo describe como un permiso temporal y revocable, no como una concesión. La plataforma no ha localizado '
                     'el permiso ni su publicación en la Gaceta Oficial de la Ciudad de México.'),
          'url': 'https://data.consejeria.cdmx.gob.mx/index.php/gaceta', 'url_txt': 'Gaceta Oficial de la Ciudad de México'},
     ],
     'prensa': [
         ('El Universal', 'Mota Engil gana contrato para el primer tramo del Tren Maya',
          'https://www.eluniversal.com.mx/cartera/mota-engil-gana-contrato-para-el-primer-tramo-del-tren-maya/'),
         ('El Mañana', 'Ganadores del Tren Maya: ayer eran favorecidos por Peña Nieto y hoy, por la 4T',
          'https://www.elmanana.com/ganadores-del-tren-maya-ayer-eran-favorecidos-por-pena-nieto-y-hoy-por-la-4t/5090443'),
         ('Dinero en Imagen', 'Mota-Engil opera parque Aztlán, sus contratos van del Tren Maya hasta Pemex',
          'https://www.dineroenimagen.com/jose-yuste/mota-engil-opera-parque-aztlan-sus-contratos-van-del-tren-maya-hasta-pemex/162851'),
         ('Excélsior', 'Para desarrollar Ciudad UDG, pactan compromisos gobierno, universidad y Grupo Prodi',
          'https://www.excelsior.com.mx/finanzas/para-desarrollar-ciudad-udg-pactan-compromisos-gobierno-universidad-y-grupo-prodi'),
     ]},
]

NOTA = ('Tener contratos, concesiones o permisos no es una irregularidad. Los documentos dicen qué gobierno firmó y en qué año, '
        'no un partido: las mismas reglas valen para todos los gobiernos.')


def plano(t):
    t = unicodedata.normalize('NFD', str(t or ''))
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn').lower()
    return re.sub(r'[^a-z0-9ñ]+', ' ', t).strip()


def _indice():
    t = open(os.path.join(CMX, 'indice.js'), encoding='utf-8').read()
    d = json.loads(t[t.index('{'):t.rindex('}') + 1])
    return {r[0]: r[1] for r in d['r']}


def _asf_map():
    d = json.load(open(os.path.join(RAIZ, 'investigaciones', 'expedientes-asf.json'), encoding='utf-8'))
    return {(x['cp'], x['num']): x for x in d['informes']}


def todos():
    """El catálogo, validado: cada RFC existe en ComprasMX y nada se repite."""
    idx, figs, vistos, ids, amap = _indice(), {f['id'] for f in FIGURAS}, {}, set(), _asf_map()
    out = []
    for g in GRUPOS:
        emp = []
        for rfc in g['emp']:
            if rfc not in idx:
                raise SystemExit('empresas_grupos: el RFC %s de «%s» no está en el catálogo de ComprasMX.' % (rfc, g['n']))
            if len(rfc) != 12:
                raise SystemExit('empresas_grupos: %s no es el RFC de una persona moral; las personas físicas no se publican.' % rfc)
            emp.append({'rfc': rfc, 'n': idx[rfc]})
        for a in g['al']:
            if a != plano(a):
                raise SystemExit('empresas_grupos: la frase «%s» de %s debe ir en minúsculas y sin acentos.' % (a, g['n']))
            if a in vistos:
                raise SystemExit('empresas_grupos: «%s» está en %s y en %s' % (a, vistos[a], g['id']))
            vistos[a] = g['id']
        for c in g['cotejar']:
            if c['fig'] not in figs:
                raise SystemExit('empresas_grupos: «%s» trae una figura desconocida: %s' % (c['id'], c['fig']))
        for x in [g['vin']] + g['cotejar']:
            if x['id'] in ids or not (x['que'] and x['porque'] and x['url']):
                raise SystemExit('empresas_grupos: el pendiente «%s» está repetido o le falta su porqué o su enlace (AGENTS.md §2).' % x['id'])
            ids.add(x['id'])
        asf_items = []
        for cp, num, etq in g.get('asf', []):
            inf = amap.get((cp, num))
            if not inf or not inf.get('extractos'):
                raise SystemExit('empresas_grupos: falta la auditoría (%s, %s) o sus extractos en expedientes-asf.json' % (cp, num))
            ext = inf['extractos']
            asf_items.append({
                'etq': etq, 'cp': cp, 'num': num, 'clave': inf['claveAuditoria'], 'ente': inf['ente'],
                'contrato': ext['contrato'], 'fecha': ext['fechaContrato'],
                'consorcio': ext['consorcio'], 'integrantes': ext['integrantes'],
                'orig_mdp': round(ext['tramo1Original'] / 1e6, 1),
                'conv_mdp': round(ext['tramo1Convenios'] / 1e6, 1),
                'tot_mdp': round(ext['tramo1Total'] / 1e6, 1),
                'ej22_mdp': round(ext['tramo1Ejercido2022'] / 1e6, 1),
                'aclarar_mdp': round((inf.get('porAclarar') or 0) / 1e6, 1),
                'url': inf['url'], 'sha': inf['sha256'][:12],
            })
        out.append(dict(g, emp=emp, asf_items=asf_items))
    return out


def ancla(g):
    return 'grupo-' + g['id']


def datos():
    """Lo que lee el chat (D.gru). Sin cifras escritas aquí: los contratos los carga de ComprasMX y las auditorías de expedientes-asf.json."""
    fn = {f['id']: f['n'] for f in FIGURAS}
    return {
        'g': [{'id': g['id'], 'n': g['n'], 'al': g['al'], 'que': g['que'], 'emp': [x['rfc'] for x in g['emp']], 'ir': PAGINA + '#' + ancla(g),
               'vin': {'tx': g['vin']['que'], 'x': g['vin']['porque'], 'p': g['vin']['id'], 'url': g['vin']['url'], 'ut': g['vin']['url_txt']},
               'asf': g['asf_items'],
               'cot': [{'tx': c['que'], 'x': c['porque'], 'fig': fn[c['fig']], 'p': c['id'], 'url': c['url'], 'ut': c['url_txt']} for c in g['cotejar']],
               'pr': [{'m': m, 't': t, 'u': u} for m, t, u in g['prensa']]} for g in todos()],
        'fig': [{'n': f['n'], 'tx': f['tx'], 'ley': f['ley']} for f in FIGURAS], 'nota': NOTA, 'pag': PAGINA + '#grupos'}


def pendientes():
    """Para el Registro de pendientes (pendientes.py)."""
    out = []
    for g in todos():
        ap = [(PAGINA + '#' + ancla(g), 'Contratos públicos · Grupos y filiales: ' + g['n'])]
        for x in [g['vin']] + g['cotejar']:
            out.append({'id': x['id'], 'tema': 'Grupos empresariales y sus filiales', 'que': x['que'], 'porque': x['porque'],
                        'responsable': PLATAFORMA, 'enlace': x['url'], 'enlace_txt': x['url_txt'], 'aparece': ap})
    return out


def seccion():
    """La sección «Grupos y filiales» de contratos-publicos.html."""
    e = html.escape
    pe = '<span class="est-chip est-pendiente" data-pend="%s">pendiente</span>'
    of = '<span class="est-chip est-oficial">oficial</span>'
    fn = {f['id']: f['n'] for f in FIGURAS}
    figs = ''.join('<li><b>%s.</b> %s <small>(%s)</small></li>' % (e(f['n']), e(f['tx']), e(f['ley'])) for f in FIGURAS)
    grupos = []
    for g in todos():
        emp = ''.join('<li><a href="%s?q=%s"><b>%s</b></a> <small>(RFC %s)</small>: sus contratos de ComprasMX, con el importe y la liga de cada uno.</li>'
                      % (PAGINA, x['rfc'], e(x['n']), x['rfc']) for x in g['emp'])
        asf_li = ''.join(
            '<li><b>%s</b> (contrato <code>%s</code>, firmado el %s con <b>%s</b>, integrado por %s): '
            'importe original <b>$%s mdp</b> %s, convenios modificatorios por <b>+$%s mdp</b>, '
            'total contratado <b>$%s mdp</b> %s (%s ejercidos en %d) y <b>$%s mdp</b> pendientes por aclarar en la '
            '<a href="%s" target="_blank" rel="noopener">Auditoría %d de la Cuenta Pública %d (%s) ↗</a> <small>(sha256 %s…)</small>.</li>'
            % (e(a['etq']), e(a['contrato']), e(a['fecha']), e(a['consorcio']), e(a['integrantes']),
               format(a['orig_mdp'], ',.1f'), of, format(a['conv_mdp'], ',.1f'), format(a['tot_mdp'], ',.1f'), of,
               '$%s mdp' % format(a['ej22_mdp'], ',.1f'), a['cp'], format(a['aclarar_mdp'], ',.1f'),
               e(a['url']), a['num'], a['cp'], e(a['clave']), e(a['sha']))
            for a in g['asf_items'])
        asf_bloque = ('          <p><b>Lo que auditó la ASF (contratos de años anteriores a ComprasMX 2025-2026):</b></p>\n          <ul>%s</ul>\n' % asf_li) if asf_li else ''
        cot = ''.join('<li><b>%s.</b> %s %s<br><small>%s Dónde debe estar: <a href="%s" target="_blank" rel="noopener">%s ↗</a></small></li>'
                      % (e(fn[c['fig']]), e(c['que']), pe % c['id'], e(c['porque']), e(c['url']), e(c['url_txt'])) for c in g['cotejar'])
        pr = ''.join('<li><a href="%s" target="_blank" rel="noopener">%s ↗</a> <small>(%s, sin verificar)</small></li>' % (e(u), e(t), e(m))
                     for m, t, u in g['prensa'])
        grupos.append(
            '<h3 id="%s">%s</h3>\n          <p>%s</p>\n'
            '          <p><b>El vínculo:</b> %s %s<br><small>%s</small></p>\n'
            '          <p><b>Con qué empresas aparece en ComprasMX:</b></p>\n          <ul>%s</ul>\n'
            '%s'
            '          <p><b>Lo que falta cotejar</b> (sin montos hasta tener el documento):</p>\n          <ul>%s</ul>\n'
            '          <p><b>Cómo lo contó la prensa</b> (solo titular y liga; una nota no es fuente):</p>\n          <ul>%s</ul>\n'
            '          <p><small>Pregúntale al Auditor: «%s».</small></p>'
            % (ancla(g), e(g['n']), g['que'], e(g['vin']['que']), pe % g['vin']['id'], e(g['vin']['porque']), emp, asf_bloque, cot, pr, e(g['n'])))
    return {
        'id': 'grupos', 'titulo': 'Grupos y filiales: quién está detrás del nombre',
        'texto': ('Muchos grupos no contratan con su nombre: contrata una filial o un consorcio. Aquí decimos con qué empresas aparece '
                  'cada grupo en ComprasMX y qué falta cotejar.'),
        'tarjetas': [],
        'bloque': ('<div class="cmx-metodo">\n'
                   '          <h3>Contrato, concesión y permiso no son lo mismo</h3>\n          <ul>%s</ul>\n          %s\n'
                   '          <p><small>⚖️ %s</small></p>\n        </div>' % (figs, '\n          '.join(grupos), e(NOTA)))}


if __name__ == '__main__':
    for g in todos():
        print(g['n'], '→', ', '.join('%s (%s)' % (x['n'], x['rfc']) for x in g['emp']), '· ASF:', len(g['asf_items']), '· pendientes:', 1 + len(g['cotejar']))
