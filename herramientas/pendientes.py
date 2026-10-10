#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Registro publico de pendientes (decision del autor, 10-10-2026).

Todo lo que la plataforma marca como «pendiente» se explica aqui, en una
sola pagina, pendientes.html: que falta, por que, a quien le toca
publicarlo y el enlace oficial donde deberia estar. Es la prueba de
transparencia civica: lo que no sabemos tambien se dice, con nombre.

Se arma solo con window.AUDIT_DB (los registros con estado «pendiente») mas
la lista PROPIOS de este archivo, para los pendientes que el motor escribe
en su codigo. Si un pendiente no trae su porque, su enlace o su
responsable, la generacion se detiene: ninguno se publica sin explicacion.

Regla del responsable (AGENTS.md, §2): se nombra a la dependencia solo si
de verdad debia publicarlo. Si el documento existe y la plataforma aun no
lo integra, se dice «falta de la plataforma». Si el dato es historico y no
hay dependencia que responda, se dice asi.

Lo llama apartados.generar(), asi que sello.py la regenera con el sello.
"""
import json
import os
import re

from apartados import RAIZ, pagina

ARCHIVO = 'pendientes.html'
PLATAFORMA = 'Falta de la plataforma: el documento existe y aún no lo integramos'
HISTORICO = 'Dato histórico: no hay dependencia que deba publicarlo hoy'
CP2024 = 'https://www.cuentapublica.hacienda.gob.mx/es/CP/2024'
TP = 'https://www.transparenciapresupuestaria.gob.mx/'


def db():
    s = open(os.path.join(RAIZ, 'assets', 'auditor', 'js', 'audit-database.js'), encoding='utf-8').read()
    return json.loads(s[s.index('{'):s.rindex('}') + 1])


def limpio(t):
    return re.sub(r'\s+', ' ', re.sub('<[^>]+>', '', str(t))).strip()


def e(id_, tema, que, porque, responsable, enlace, enlace_txt, aparece):
    return {'id': id_, 'tema': tema, 'que': que, 'porque': limpio(porque), 'responsable': responsable,
            'enlace': enlace, 'enlace_txt': enlace_txt, 'aparece': aparece}


# Pendientes que el motor escribe en su codigo (no viven como registro en la
# base). Cada uno: id, tema, que falta, por que, responsable, enlace oficial,
# texto del enlace, donde aparece.
PROPIOS = [
    ('asf-matriz-2018', 'Fiscalización', 'Matriz de Datos Básicos de la Cuenta Pública 2018',
     'La ASF no publicó en su portal la matriz de la Cuenta Pública 2018, como sí lo hizo con las demás. Sin ella, la serie de montos por aclarar tiene un hueco en ese año.',
     'Auditoría Superior de la Federación (ASF)', 'https://www.asf.gob.mx/Section/58_Informes_de_auditoria',
     'Informes de auditoría de la ASF', [('herramienta-inspector-asf.html', 'Qué encontró la ASF')]),
    ('municipios-sin-cuenta', 'Estados y municipios', 'Cuenta pública 2024 de los municipios que no la entregaron al INEGI',
     'De los 2,479 municipios del catálogo, 83 no reportaron sus finanzas de 2024 a la estadística del INEGI, y las 16 demarcaciones de la Ciudad de México no rinden cuenta municipal. Sin ese reporte no se sabe cuánto ingresaron ni en qué gastaron.',
     'Los ayuntamientos que no reportaron', 'https://www.inegi.org.mx/programas/finanzas/',
     'Estadística de finanzas públicas estatales y municipales (INEGI)',
     [('sigue-el-dinero.html#baja', 'Números · A dónde baja')]),
    ('alcaldes-inafed', 'Estados y municipios', 'Alcaldes sin registro en el padrón del INAFED',
     'Algunos municipios no tienen a su presidente municipal registrado en el padrón del Instituto Nacional para el Federalismo y el Desarrollo Municipal, o lo tienen sin partido.',
     'Instituto Nacional para el Federalismo y el Desarrollo Municipal (INAFED)', 'https://www.gob.mx/inafed',
     'INAFED', [('herramienta-inspector-entes.html', 'Auditor de entes públicos')]),
    ('huachicol-evasion', 'Ingresos', 'Cuánto se evade por huachicol fiscal',
     'Ni el SAT ni Hacienda han publicado una estimación oficial, con metodología, de cuánto IEPS y IVA se deja de cobrar por el contrabando de combustibles. Las cifras que circulan son de organismos civiles o se dijeron en tribuna sin documento.',
     'Servicio de Administración Tributaria (SAT) y Secretaría de Hacienda', 'https://www.sat.gob.mx/minisitio/DatosAbiertos/index.html',
     'Datos abiertos del SAT', [('auditoria-huachicol-fiscal.html', 'Huachicol fiscal')]),
    ('costo-unitario-megaobras', 'Megaobras', 'Costo por usuario de cada megaobra (por pasajero, por barril, por usuario)',
     'Ningún documento oficial publica el subsidio por usuario de las obras. La plataforma lo marca como pendiente hasta que la dependencia que opera cada obra publique su costo de operación y su número de usuarios.',
     'Las dependencias que operan cada obra (Sedena, Pemex, Fonatur, SICT)', 'https://www.transparenciapresupuestaria.gob.mx/Obra-Publica-Abierta',
     'Obra Pública Abierta (Hacienda)', [('herramienta-megaobras-sector.html', 'Megaobras · Sector e industria')]),
    ('estado-cuenta-pesos-2024', 'Cuenta Pública 2024', 'Pesos de 2024 en el Estado de Cuenta y el subejercicio de 2024',
     'Los Criterios Generales 2027 dan 2024 solo en por ciento del PIB. Los pesos y el subejercicio (modificado menos devengado) están en el Tomo II de la Cuenta Pública 2024, que la plataforma aún no coteja: el portal de Hacienda no se pudo abrir con conexión verificada.',
     PLATAFORMA, CP2024, 'Cuenta Pública 2024 (Hacienda)', [('estado-de-cuenta.html', 'Estado de Cuenta Cívico')]),
    ('radar-1989', 'Historia', 'Ingresos, gasto, inversión y costo financiero de 1989, el primer año de Salinas',
     'Las Estadísticas Oportunas de Hacienda, que usa el Radar, empiezan en 1990, y el Anexo Estadístico del 5.º Informe en 1995. '
     'La Cuenta Pública de 1989 existe, pero la plataforma aún no la integra. Mientras tanto, Salinas se mide con cinco de sus seis años '
     '(1990 a 1994) en % del PIB, y sus sumas en pesos quedan pendientes.',
     PLATAFORMA, 'https://www.cuentapublica.hacienda.gob.mx/', 'Cuenta Pública (Hacienda)', [('radar-tablero.html', 'Radar · El tablero'), ('radar-reloj.html', 'Radar · El reloj'), ('radar-duelo.html', 'Radar · Duelo de administraciones')]),
    ('asesores-congresos-locales', 'Remuneraciones', 'Remuneración de los asesores y del personal de apoyo de los 32 congresos locales',
     'Cada congreso debe publicar la remuneración bruta y la neta de todo su personal (Ley General de Transparencia, art. 65, fr. VII). '
     'La plataforma aún no integra esos tabuladores, así que el estado de cuenta de la diputación local no dice cuánto cobran sus asesores.',
     PLATAFORMA, 'https://www.plataformadetransparencia.org.mx/', 'Plataforma Nacional de Transparencia',
     [('radar-estado-de-cuenta.html#expide', 'Radar · Estado de cuenta de la diputación local')]),
    ('tren-maya-ficha', 'Megaobras', 'Ficha pericial del Tren Maya 2024',
     'Se retiró el 10-10-2026 porque sus cifras no se habían cotejado con el Tomo VII de la Cuenta Pública 2024 ni con la ASF. Volverá cuando cada cifra tenga su documento.',
     PLATAFORMA, CP2024, 'Cuenta Pública 2024, Tomo VII (Hacienda)', [('expedientes.html#exp-tren-maya', 'Expediente del Tren Maya')]),
]


PRESIDENTES = {'salinas': 'Salinas', 'zedillo': 'Zedillo', 'fox': 'Fox', 'calderon': 'Calderón', 'epn': 'Peña Nieto', 'amlo': 'López Obrador'}


def recolectar():
    d = db()
    out = []
    # 1. Cuenta Publica 2024 (Tomo II), agrupada.
    cf = d['cuentaFederal2024']
    pend = [c for c in cf['cifras'] if c['estado'] == 'pendiente']
    if pend:
        out.append(e('cp2024-tomo2', 'Cuenta Pública 2024', 'Estados financieros del Gobierno Federal 2024: ' +
                     ', '.join(c['concepto'].lower() for c in pend) + ' y la conciliación presupuestaria-contable',
                     pend[0]['motivo'], PLATAFORMA, pend[0]['url'], 'Cuenta Pública 2024, Tomo II (Hacienda)',
                     [('sigue-el-dinero.html?abrir=eb-cuenta-federal', 'Números · Estado de resultados'),
                      ('estado-de-cuenta.html', 'Estado de Cuenta Cívico')]))
    # 2. Programas sociales.
    for m in cf['evaluacion_social_mir']:
        if m['estado_montos'] == 'pendiente':
            out.append(e('prog-montos-' + ('imss-bienestar' if 'IMSS' in m['programa'] else m['clave'].lower()), 'Programas sociales', 'Aprobado y devengado 2024: ' + m['programa'],
                         m['motivo_montos'], PLATAFORMA, m.get('url'), 'Cuenta Pública 2024 (Hacienda)',
                         [('sigue-el-dinero.html?abrir=eb-cuenta-federal', 'Números · Resultados sociales'),
                          ('estado-de-cuenta.html#social', 'Estado de Cuenta · Social')]))
    out.append(e('prog-resultados', 'Programas sociales', 'Propósito, cobertura e impacto de los programas sociales: ' +
                 '; '.join(m['programa'] for m in cf['evaluacion_social_mir']),
                 cf['evaluacion_social_mir'][0]['motivo_resultados'], PLATAFORMA,
                 cf['evaluacion_social_mir'][0].get('url_resultados'), 'Transparencia Presupuestaria (Hacienda)',
                 [('estado-de-cuenta.html#social', 'Estado de Cuenta · Social')]))
    # 3. Huachicol fiscal: estimaciones sin documento de la autoridad.
    hf = d['huachicol_fiscal']
    for i, x in enumerate(hf.get('estimaciones', [])):
        if x.get('estado') == 'pendiente':
            f = hf['fuentes'].get(x.get('fuente'), {})
            out.append(e('huachicol-est-%d' % i, 'Ingresos', 'Cifra de %s mdp que circula sobre el huachicol fiscal: %s' % (
                format(x.get('total_mdp', 0), ','), f.get('doc', x.get('fuente')).split(',')[0]),
                x['por_que_pendiente'], 'Servicio de Administración Tributaria (SAT) y Secretaría de Hacienda',
                'https://www.sat.gob.mx/minisitio/DatosAbiertos/index.html', 'Datos abiertos del SAT',
                [('auditoria-huachicol-fiscal.html', 'Huachicol fiscal')]))
    # 4. Megaobras: campos sin documento, obra por obra.
    sim = d['simulador_megaobras']
    ver = sim['verificacion']
    nombres = {o['id']: o['nombre'] for o in sim['obras']}
    for oid, o in ver['obras'].items():
        campos = [k for k, v in (o.get('campos') or {}).items() if v == 'pendiente']
        if not campos:
            continue
        defs = o.get('definiciones') or {}
        porque = ' '.join(defs.get(k, '') for k in campos if defs.get(k)) or (
            'Ningún documento oficial publica el presupuesto original ni el costo total de la obra. ' + limpio(o.get('hallazgo', ''))[:300])
        quien = {'aifa-texcoco': 'Secretaría de la Defensa Nacional (Sedena)',
                 'dos-bocas': 'Pemex y su filial PTI Infraestructura de Desarrollo'}.get(oid, HISTORICO)
        fu = (o.get('fuentes') or ['opa'])[0]
        out.append(e('obra-' + oid, 'Megaobras', '%s: %s' % (nombres.get(oid, oid), ', '.join(
            {'inversion_presupuestada_mdp': 'presupuesto original', 'inversion_real_mdp': 'costo total',
             'sobrecosto_pct': 'sobrecosto'}[k] for k in campos)),
            porque, quien, ver['fuentes'].get(fu, {}).get('url'), ver['fuentes'].get(fu, {}).get('doc', 'Documento')[:80],
            [('herramienta-megaobras-sector.html', 'Megaobras · Sector e industria')]))
    # 5. Reloj de perdidas de las megaobras.
    for r in d['calculadora_civica']['relojes']['fuentes']:
        if r.get('estado') == 'pendiente':
            out.append(e('reloj-' + r['id'], 'Megaobras', r['nombre'], r.get('motivo', r.get('fuente')),
                         'Las dependencias que operan cada obra (Sedena, Pemex, Fonatur)', r.get('url'),
                         'Obra Pública Abierta (Hacienda)', [('herramienta-calculadora-reloj.html', 'El reloj de la deuda')]))
    # 6. Evaluacion sexenal: series historicas que no llegan tan atras.
    ev = d['evaluacion_sexenal']
    vistos = {}
    for fila in ev['filas']:
        for campo, v in fila.items():
            if isinstance(v, dict) and v.get('estado') == 'pendiente':
                vistos.setdefault((campo, v.get('motivo')), []).append(PRESIDENTES.get(fila.get('id'), fila.get('id')))
    urls = {'empleo': ev['fuentes'].get('PRES_5IG', {}).get('url'), 'recuperaciones': ev['fuentes'].get('ASF_IGE2022', {}).get('url'),
            'porAclarar': ev['fuentes'].get('ASF_MDB', {}).get('url')}
    nomb = {'empleo': 'Empleo formal (asegurados al IMSS)', 'recuperaciones': 'Recuperaciones de la ASF',
            'porAclarar': 'Monto por aclarar ante la ASF'}
    for (campo, motivo), quienes in vistos.items():
        out.append(e('sexenal-' + campo, 'Historia', '%s en los sexenios de %s' % (nomb.get(campo, campo), ', '.join(map(str, quienes))),
                     motivo, HISTORICO, urls.get(campo), 'Documento de la serie', [('herramienta-megaobras-sexenios.html', 'Las obras de cada sexenio')]))
    # 7. Remuneraciones netas no publicadas.
    cs = d['comparador_salarial']
    COLS = {c['id']: c['nombre'] for c in cs['prestaciones'].get('columnas', [])}
    for c in cs['cargos']:
        for en in c.get('entidades', []):
            if en.get('netoEstado') == 'pendiente':
                f = cs['fuentes'].get(en.get('fuente'), {})
                out.append(e('neto-%s-%s' % (c['id'], en['nombre'].lower().replace(' ', '-')), 'Remuneraciones',
                             'Remuneración neta de los diputados locales de %s' % en['nombre'],
                             'El documento oficial publica la remuneración bruta (%s) pero no la neta. La ley general de transparencia obliga a cada sujeto obligado a publicar la remuneración bruta y la neta.' % limpio(en.get('concepto', ''))[:220],
                             'Congreso del estado de %s' % en['nombre'], f.get('url'), f.get('corto', 'Documento del congreso'),
                             [('herramienta-calculadora-compara.html', 'Tú contra ellos')]))
    for fila in cs['prestaciones']['filas']:
        for col, cel in (fila.get('celdas') or {}).items():
            if isinstance(cel, dict) and cel.get('estado') == 'pendiente':
                f = cs['fuentes']['SEN'] if str(cel.get('ref', '')).startswith('Manual') else cs['fuentes']['PEF']
                out.append(e('prest-%s-%s' % (re.sub(r'[^a-z]+', '-', fila.get('concepto', 'f').lower()), col), 'Remuneraciones',
                             '%s de la %s (%s)' % (fila.get('concepto', 'Prestación'), COLS.get(col, col), cel.get('ref', '')),
                             cel.get('nota') or cel.get('tx'), {'sen': 'Senado de la República', 'pr': 'Presidencia de la República',
                                                                'dip': 'Cámara de Diputados', 'pjf': 'Poder Judicial de la Federación'}.get(col, 'La institución que paga la prestación'),
                             f.get('url'), f.get('corto', 'Documento'),
                             [('herramienta-calculadora-compara.html', 'Tú contra ellos')]))
    # 8. Poderes y ambiente: listas de pendientes de la base.
    pf = d['poderes']['fuentes']
    for k, url in (('judicial', pf['MANUAL']['url']), ('legislativo', pf['ASF_DIP']['url'])):
        for i, t in enumerate(d['poderes'][k].get('pendientes', [])):
            out.append(e('poderes-%s-%d' % (k, i), 'Poderes', t,
                         'No se calcula dividiendo el presupuesto entre el número de órganos o de personas: ese reparto no es un dato. '
                         'Hace falta que el poder publique el costo desglosado, o integrar el documento que lo trae.',
                         PLATAFORMA, url, 'Documento oficial del poder', [('index.html?ir=poderes', 'Lo que cuestan los Poderes')]))
    amb = d['ambiente']
    for i, t in enumerate(amb.get('pendientes', [])):
        quien = 'INEGI (publica cada diciembre)' if 'diciembre' in t else PLATAFORMA
        url = (amb['fuentes'].get('CNGMD') or {}).get('url') if 'Censo' in t else (
            'https://www.inegi.org.mx/temas/ee/' if 'Cuentas' in t else 'https://www.gob.mx/semarnat')
        out.append(e('ambiente-%d' % i, 'Ambiente', t.split(':')[0], t, quien, url, 'Fuente oficial',
                     [('herramienta-ambiente-basura.html', 'Basura y protección')]))
    # 9. Entidades sin fuente (CDMX en la estadistica del INEGI).
    fe = d['fiscalEntidades']['campos']
    sin = sorted({(tuple(v['sinFuente']), v['motivo']) for v in fe.values() if isinstance(v, dict) and v.get('sinFuente')})
    for ents, motivo in sin:
        out.append(e('entidades-' + '-'.join(ents).lower(), 'Estados y municipios',
                     'Convenios, recaudación propia y dependencia federal de 2024: ' + ', '.join(ents), motivo + '.',
                     'Gobierno de la Ciudad de México' if 'CDMX' in ents else PLATAFORMA,
                     'https://www.inegi.org.mx/programas/finanzas/', 'Finanzas públicas estatales (INEGI)',
                     [('sigue-el-dinero.html#baja', 'Números · A dónde baja')]))
    for p in PROPIOS:
        out.append(e(*p))
    # El estado de cuenta de diputados y de la Corte (Radar) los muestra.
    ec = ('radar-estado-de-cuenta.html#expide', 'Radar · Estado de cuenta')
    for x in out:
        if x['id'].startswith('neto-diputado_local-') or x['id'] in ('poderes-legislativo-0', 'poderes-judicial-1'):
            x['aparece'] = x['aparece'] + [ec]
    # Ninguno sin su porque, su responsable y su enlace oficial.
    faltan = [x['id'] for x in out if not (x['porque'] and x['responsable'] and x['enlace'])]
    if faltan:
        raise SystemExit('ERROR: pendientes sin porque, responsable o enlace: %s' % ', '.join(faltan))
    ids = [x['id'] for x in out]
    if len(ids) != len(set(ids)):
        raise SystemExit('ERROR: ids repetidos en el registro de pendientes')
    return out


def construir():
    items = recolectar()
    temas = []
    for x in items:
        if x['tema'] not in temas:
            temas.append(x['tema'])
    def tarjeta(x):
        tipo = 'plataforma' if x['responsable'] == PLATAFORMA else 'historico' if x['responsable'] == HISTORICO else 'dependencia'
        return ('<article class="pe-item pe-%s" id="%s">\n'
                '            <h3 class="pe-que"><span class="est-chip est-pendiente">pendiente</span> %s</h3>\n'
                '            <p class="pe-porque"><b>Por qué:</b> %s</p>\n'
                '            <p class="pe-quien"><b>%s</b> %s</p>\n'
                '            <p class="pe-donde"><a href="%s" target="_blank" rel="noopener">🔗 Dónde debería estar: %s ↗</a></p>\n'
                '            <p class="pe-aparece">Aparece en: %s · <a class="pe-ancla" href="#%s" aria-label="Enlace a este pendiente">#</a></p>\n'
                '          </article>') % (
            tipo, x['id'], x['que'], x['porque'],
            {'plataforma': '🧰 Responsable:', 'historico': '📜 Responsable:', 'dependencia': '🏛️ Debe publicarlo:'}[tipo],
            x['responsable'], x['enlace'], x['enlace_txt'],
            ' · '.join('<a href="%s">%s</a>' % a for a in x['aparece']), x['id'])
    resumen = {k: sum(1 for x in items if (x['responsable'] == PLATAFORMA) == (k == 'p') and (x['responsable'] == HISTORICO) == (k == 'h'))
               for k in ('p', 'h', 'd')}
    cab = ('<div class="pe-resumen">\n'
           '          <div><b>%d</b><span>pendientes registrados</span></div>\n'
           '          <div class="pe-r-d"><b>%d</b><span>🏛️ los debe publicar una dependencia</span></div>\n'
           '          <div class="pe-r-p"><b>%d</b><span>🧰 los debemos integrar nosotros</span></div>\n'
           '          <div class="pe-r-h"><b>%d</b><span>📜 son históricos, sin quien responda hoy</span></div>\n'
           '        </div>\n'
           '        <p class="pe-regla">Un dato pendiente no se estima ni se rellena: se dice que falta, por qué falta y dónde debería estar. '
           'Si la falta es de una dependencia obligada, la nombramos. Si el documento existe y aún no lo integramos, lo decimos: la falta es nuestra. '
           '¿Tienes el documento? <a href="comunidad.html#error" data-puerta="error">Cuéntanos y lo integramos</a>.</p>') % (
        len(items), resumen['d'], resumen['p'], resumen['h'])
    secciones = [{'id': 'resumen', 'titulo': 'Lo que falta, en números', 'texto': '', 'sin_cab': True, 'bloque': cab, 'tarjetas': []}]
    for t in temas:
        sid = 'tema-' + re.sub(r'[^a-z0-9]+', '-', t.lower().replace('ó', 'o').replace('í', 'i').replace('ú', 'u').replace('á', 'a').replace('é', 'e')).strip('-')
        secciones.append({'id': sid, 'titulo': t, 'texto': '', 'tarjetas': [],
                          'bloque': '<div class="pe-lista">\n          ' + '\n          '.join(tarjeta(x) for x in items if x['tema'] == t) + '\n        </div>'})
    return {
        'archivo': ARCHIVO, 'menu': 'Registro de pendientes', 'menu_archivo': 'indice.html',
        'padre': ('indice.html', 'Índice general'), 'icono': '⏳', 'titulo': 'Registro de pendientes',
        'lema': 'Lo que no sabemos también se dice',
        'entrada': ('Cada dato que la plataforma marca como <span class="est-chip est-pendiente">pendiente</span> está aquí, con su '
                    'explicación: qué falta, por qué falta, a quién le toca publicarlo y el enlace oficial donde debería estar. '
                    'Es nuestra rendición de cuentas: así puedes ir tú mismo a la fuente y exigirla.'),
        'secciones': secciones,
    }, items


def generar(sello):
    pag, items = construir()
    texto = pagina(pag, sello).replace('\r\n', '\n').replace('\n', '\r\n')
    open(os.path.join(RAIZ, ARCHIVO), 'wb').write(texto.encode('utf-8'))
    print('registro de pendientes: %s con %d pendientes, todos con porqué, responsable y enlace' % (ARCHIVO, len(items)))
    return 0
