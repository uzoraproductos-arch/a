#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Investigación 23 de «Auditoría en imágenes»: el Seguro Popular
(pedido del autor, 28-10-2026: «integra lo del Seguro Popular como una
auditoría en imagen… resaltar el éxito que fue»).

Escribe `auditorias_actuales['seguro-popular']` en window.AUDIT_DB y su
diapositiva en index.html. Cada cifra viene de tres documentos ya leídos
completos y guardados en la bóveda (CONTEXT.md, 28-10-2026):
  - ASF, Marco de Referencia MR-Seguro Popular, Cuenta Pública 2018.
  - INEGI, comunicado 118/25, Pobreza multidimensional 2024 (cuadro 1).
  - INEGI, Pobreza multidimensional 2024, presentación de resultados.
El logro se dice con sus números y, junto a él, lo que la ASF le observó:
las mismas reglas para todos los gobiernos (pilares.html).

Se puede correr otra vez: reemplaza la entrada y no duplica la diapositiva.
"""
import json
import os
import sys
from urllib.parse import quote

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'audit-database.js')
IDX = os.path.join(RAIZ, 'index.html')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from integrar_costo_vivo_megaobras import bloque_json  # noqa: E402

ASF = 'https://www.asf.gob.mx/Trans/Informes/IR2018b/Documentos/Auditorias/2018_MR-SEGURO%20POPULAR_a.pdf'
PM = 'https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2025/pm/pm2025_08.pdf'
PMP = 'https://www.inegi.org.mx/contenidos/desarrollosocial/pm/doc/pm_presentacion_2024.pdf'
LGS = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LGS.pdf'
PEND = 'red-seguro-popular-51-millones-2'

ID = 'seguro-popular'
IMG = 'assets/auditor/img/showcase_seguro_popular.jpg'
ALT = ('Ilustración de un centro de salud con personas en la sala de espera, una póliza de afiliación '
       'y una gráfica de la gente sin acceso a la salud de 2016 a 2024')
BADGE = '🏥 Salud pública · Seguro Popular, INSABI e IMSS-Bienestar (2004–2024)'
PREGUNTA = ('¿A cuántas personas llegó a cubrir el Seguro Popular, cuántas se quedaron sin acceso a la salud '
            'después y qué le observó la ASF?')

# Personas con carencia por acceso a los servicios de salud (INEGI,
# comunicado 118/25, cuadro 1): año, millones, porcentaje, qué operaba.
SERIE = [
    (2016, 18.8, 15.6, 'Seguro Popular en operación'),
    (2018, 20.1, 16.2, 'Seguro Popular: último año medido antes del cambio'),
    (2020, 35.7, 28.2, 'INSABI desde el 1 de enero de 2020 (y la pandemia)'),
    (2022, 50.4, 39.1, 'INSABI: el punto más alto de la serie'),
    (2024, 44.5, 34.2, 'IMSS-Bienestar desde el decreto del 29 de mayo de 2023'),
]

# Lo que la ASF observó en 2018, por tipo de irregularidad (MR-Seguro
# Popular, p. 25 y 26). Suman los 928.7 mdp del monto observado total.
OBSERVADO = [
    ('Falta de documentación justificativa o comprobatoria del gasto', 333.1,
     '9 entidades, entre ellas Campeche, Chihuahua, Ciudad de México y Tabasco · 35.9 % de lo observado'),
    ('Recursos o rendimientos no ejercidos, devengados o sin reintegrar a la TESOFE', 236.2,
     '22 entidades · 25.4 % de lo observado'),
    ('Transferencia de recursos a otras cuentas bancarias', 80.4,
     'Chiapas, Sinaloa y Tamaulipas · 8.7 %'),
    ('Pago de sueldos, prestaciones o estímulos por encima de lo autorizado', 77.6,
     'Guerrero, Jalisco, Quintana Roo y Yucatán · 8.4 %'),
    ('Gasto en conceptos que no cumplen los objetivos del programa', 50.6,
     'Campeche, Chiapas, Morelos y Quintana Roo · 5.4 %'),
    ('Bienes pagados a precios superiores a los contratados', 24.9,
     'Chiapas y Quintana Roo · 2.7 %'),
    ('Conceptos de nómina no autorizados', 21.7,
     'Hidalgo, Jalisco y Oaxaca · 2.3 %'),
    ('Otros: personal sin el perfil, medicinas fuera del CAUSES, penas no aplicadas, bienes no localizados', 104.2,
     '11.2 % de lo observado'),
]


def entrada():
    assert round(sum(v for _, v, _ in OBSERVADO), 1) == 928.7
    s18, s24 = SERIE[1][1], SERIE[4][1]
    return {
        'ente': 'Comisión Nacional de Protección Social en Salud (Secretaría de Salud) y los Regímenes Estatales de Protección Social en Salud',
        'quien': ('La Comisión Nacional de Protección Social en Salud, de la Secretaría de Salud, operaba el Sistema de Protección Social en Salud y '
                  'transfería el dinero a los Regímenes Estatales de las 32 entidades, que daban el servicio. La Auditoría Superior de la Federación '
                  'revisó su gasto (33 auditorías de la Cuenta Pública 2018). El Congreso aprobó en 2019 su sustitución por el INSABI y en 2023 el '
                  'paso al IMSS-Bienestar. El INEGI mide cuánta gente no tiene acceso a servicios de salud.'),
        'que': ('El Seguro Popular fue el brazo del Sistema de Protección Social en Salud para quien no tenía IMSS ni ISSSTE. Su logro está medido: '
                'pasó de 5.3 millones de personas afiliadas en 2004 a 53.5 millones en 2017, y en 2018 las 32 entidades acordaron mantener esa '
                'cobertura (ASF). Mientras operó, la gente sin acceso a servicios de salud se mantuvo en 18.8 millones en 2016 y 20.1 millones en '
                '2018, el 16.2 % de la población. Tras su sustitución por el INSABI subió a 35.7 millones en 2020 y a 50.4 millones en 2022; en '
                '2024, ya con el IMSS-Bienestar, eran 44.5 millones (INEGI): {dif} millones más que en 2018. También tuvo sus fallas, y la ASF las '
                'documentó: en 2018 observó $928.7 millones, el 1.7 % de lo que revisó, sobre todo gasto sin comprobar y dinero no ejercido; '
                '$892.3 millones seguían por aclarar al cerrar la revisión. Un monto observado no es un daño probado: es lo que la entidad no '
                'comprobó a tiempo.').replace('{dif}', '%.1f' % (s24 - s18)),
        'falta': ('Cuántas personas afiliadas recibieron atención de verdad: las consultas y servicios venían en los informes de resultados del '
                  'Sistema de Protección Social en Salud, que la plataforma aún no integra. Tampoco están todavía aquí las auditorías de la ASF al '
                  'INSABI y al IMSS-Bienestar, ni cuánto de los $892.3 millones por aclarar se aclaró después.'),
        'pendiente_id': PEND,
        'caja': '2004–2024 · ASF e INEGI',
        'cont': [
            {'ico': '📈', 'tit': 'Afiliados, de 2004 a 2017', 'txt': '5.3 → 53.5 millones',
             'etq': 'personas con Seguro Popular; en 2018 las 32 entidades acordaron mantener la cobertura · ASF, CP 2018', 'est': 'oficial'},
            {'ico': '🩺', 'tit': 'Sin acceso a la salud en 2018', 'txt': '20.1 millones',
             'etq': 'el 16.2 % de la población, con el Seguro Popular en operación · INEGI, comunicado 118/25', 'est': 'oficial'},
            {'ico': '📉', 'tit': 'Sin acceso a la salud en 2024', 'txt': '44.5 millones',
             'etq': 'el 34.2 %; el máximo fue 50.4 millones en 2022 · INEGI, comunicado 118/25', 'est': 'oficial'},
            {'ico': '🔍', 'tit': 'Observado por la ASF (2018)', 'v': 928.7, 'f': 'mdp1',
             'etq': 'en 33 auditorías, el 1.7 % de lo revisado; $892.3 mdp seguían por aclarar', 'est': 'oficial'},
            {'ico': '➕', 'tit': 'De más frente a 2018', 'txt': '+%.1f millones' % (s24 - s18),
             'etq': 'personas sin acceso a servicios de salud. Operación: 44.5 − 20.1', 'est': 'derivado'},
            {'ico': '💰', 'tit': 'Ejercido en 2018', 'v': 68148.4, 'f': 'mdp1',
             'etq': 'el 3.5 % del gasto federalizado de la Cuenta Pública 2018 · ASF', 'est': 'oficial'},
            {'ico': '⏳', 'tit': 'Atenciones de verdad', 'txt': 'Sin integrar',
             'etq': 'cuántas consultas y servicios dio a sus afiliados', 'est': 'pendiente', 'pend': PEND},
        ],
        'serieTit': 'La línea del tiempo: personas sin acceso a servicios de salud, 2016–2024',
        'serieTxt': ('Millones de personas con «carencia por acceso a los servicios de salud» (INEGI). Ojo: la encuesta mide si la persona dice estar '
                     'afiliada o tener derecho a una institución, no si la atendieron ni si había medicinas. Con el INSABI desapareció el padrón de '
                     'afiliados y cambió también la forma de declarar, y 2020 fue el año de la pandemia: la serie se lee con esas dos notas.'),
        'serie': [{'k': str(a), 'v': v, 'pct': p, 'sub': s, 'est': 'oficial', 'url': PM} for a, v, p, s in SERIE],
        'rastroTit': 'Lo que la ASF observó en el Seguro Popular en 2018, por tipo de irregularidad ($928.7 mdp)',
        'rastroEst': 'oficial',
        'rastro': [{'k': k, 'sub': sub, 'v': v, 'url': ASF, 'est': 'oficial'} for k, v, sub in OBSERVADO],
        'fuentes': [
            {'doc': 'ASF, Marco de Referencia «Recursos federales transferidos a través del Acuerdo de Coordinación (Seguro Popular)», Cuenta Pública 2018', 'url': ASF},
            {'doc': 'INEGI, comunicado de prensa 118/25, Pobreza multidimensional 2024, cuadro 1 (13-08-2025)', 'url': PM},
            {'doc': 'INEGI, Pobreza multidimensional 2024, presentación de resultados', 'url': PMP},
            {'doc': 'Ley General de Salud, transitorios de los decretos del 29-11-2019 y del 29-05-2023', 'url': LGS},
        ],
    }


def a_db():
    raw = open(DB, 'rb').read().decode('utf-8')
    a, b = bloque_json(raw, 'auditorias_actuales')
    datos = json.loads(raw[a:b])
    datos[ID] = entrada()
    nl = '\r\n'
    txt = json.dumps(datos, ensure_ascii=False, indent=2)
    txt = '\n  '.join(txt.split('\n')).replace('\n', nl)
    raw = raw[:a] + txt + raw[b:]
    open(DB, 'wb').write(raw.encode('utf-8'))
    bb = raw.encode('utf-8')
    print('audit-database.js: %s integrado (CR sueltos: %d)' % (ID, bb.count(b'\r') - bb.count(b'\r\n')))


def a_portada():
    raw = open(IDX, 'rb').read().decode('utf-8')
    href = 'auditoria-%s.html' % ID
    if 'data-caso="%s"' % href in raw:
        print('index.html: la diapositiva ya estaba')
        return
    nl = '\r\n'
    q = 'herramienta-inspector-pregunta.html?p=' + quote(PREGUNTA)
    slide = nl.join([
        '',
        '          <!-- Slide 23: %s -->' % href,
        '          <a class="showcase-slide" href="%s" data-caso="%s">' % (q, href),
        '            <img src="%s" alt="%s" loading="lazy">' % (IMG, ALT),
        '            <span class="showcase-ia">Ilustración provisional</span>',
        '            <div class="showcase-slide-gradient"></div>',
        '            <div class="showcase-slide-content">',
        '              <span class="showcase-slide-badge">%s</span>' % BADGE,
        '              <h3 class="showcase-slide-q">%s</h3>' % PREGUNTA,
        '              <div class="showcase-click-cue">',
        '                <span>💬 Pregúntale al Auditor</span> ➔',
        '              </div>',
        '            </div>',
        '          </a>',
    ])
    fin = nl + '        </div>' + nl + nl + '        <!-- Flechas de navegación del carrusel -->'
    assert raw.count(fin) == 1, 'no encuentro el final del carrusel'
    raw = raw.replace(fin, slide + fin, 1)
    dot = '        <button type="button" class="showcase-dot" onclick="window.AuditEngine.showcaseGoTo(21)" aria-label="Ir a FARAC (Rescate Carretero de 1997)"></button>'
    assert raw.count(dot) == 1, 'no encuentro el último punto del carrusel'
    raw = raw.replace(dot, dot + nl + '        <button type="button" class="showcase-dot" onclick="window.AuditEngine.showcaseGoTo(22)" '
                      'aria-label="Ir a Seguro Popular: el logro, el cambio y lo que observó la ASF"></button>', 1)
    open(IDX, 'wb').write(raw.encode('utf-8'))
    bb = raw.encode('utf-8')
    print('index.html: diapositiva 23 agregada (CR sueltos: %d)' % (bb.count(b'\r') - bb.count(b'\r\n')))


if __name__ == '__main__':
    a_db()
    a_portada()
