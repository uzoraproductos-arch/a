# -*- coding: utf-8 -*-
"""Integra al auditor lo que la ASF documentó de cinco megaobras anteriores
a 2018 (cotejado el 28-09-2026):

- Estela de Luz: Informe sobre la fiscalización superior del monumento
  Estela de Luz 2009-2011 (informe especial).
- Refinería Bicentenario (Tula): auditoría 315 de la Cuenta Pública 2014.
- Agronitrogenados y Fertinal: auditorías 498 (CP 2015) y 468 (CP 2016).
- Enciclomedia: auditoría 584 de la Cuenta Pública 2005 (tomo VI, vol. 2).
- FARAC: auditoría 96 de la Cuenta Pública 2017 (Fonadin).

Uso:  python3 herramientas/integrar_megaobras_asf_historico.py <carpeta>
<carpeta> guarda los seis PDF con el nombre de ARCHIVOS; se comprueba su
huella SHA-256 antes de escribir. Solo toca simulador_megaobras en
assets/auditor/js/audit-database.js (la Enciclopedia no se toca).
Idempotente: vuelve a escribir los mismos valores.
"""
import hashlib
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'audit-database.js')

ARCHIVOS = {
    'Estela_Luz_Nv.pdf': '91cef08bd1cfdc16e91f4a40a5c46885d058b2083d77d3611b33709af89056f8',
    '2014_0315_a.pdf': '370607a9b7c055cf1c58a9455ea467730063e2276ff4e5078d3dddb787be02c4',
    '2015_0498_a.pdf': '906989b1266ac701aa6ff639be499afac9d670f501ed7aa57c5e58470eebe041',
    '2016_0468_a.pdf': '7028e6acd9ba71064179ce42229b6ad06dfcb36b349c2370d0626608bb340af3',
    'T6V2.pdf': 'e668164a96e169ee16b5b5b78a3e875a43dc0a780d482c70bcd750e7fc8e380b',
    '2017_0096_a.pdf': 'aef6346d39a48e59bd0666415965d83bf7da0cda69d84eba69de357c2d3581f8',
}

FUENTES = {
    'asf_estela': {
        'doc': 'ASF, Informe sobre la fiscalización superior del monumento Estela de Luz 2009-2011 (informe especial)',
        'url': 'https://www.asf.gob.mx/uploads/56_Informes_especiales_de_auditoria/Estela_Luz_Nv.pdf',
        'sha256': ARCHIVOS['Estela_Luz_Nv.pdf'],
    },
    'asf_tula14': {
        'doc': 'ASF, Cuenta Pública 2014, auditoría 315, Pemex Refinación: Calidad de Combustibles, Fase Gasolinas, de la Refinería «Miguel Hidalgo» y Revisión de la Cancelación de la Construcción de la Refinería Bicentenario',
        'url': 'https://www.asf.gob.mx/Trans/Informes/IR2014i/Documentos/Auditorias/2014_0315_a.pdf',
        'sha256': ARCHIVOS['2014_0315_a.pdf'],
    },
    'asf_agro15': {
        'doc': 'ASF, Cuenta Pública 2015, auditoría 498-DE, Petróleos Mexicanos: Gestión Financiera para la Adquisición de Agro Nitrogenados',
        'url': 'https://www.asf.gob.mx/Trans/Informes/IR2015i/Documentos/Auditorias/2015_0498_a.pdf',
        'sha256': ARCHIVOS['2015_0498_a.pdf'],
    },
    'asf_fert16': {
        'doc': 'ASF, Cuenta Pública 2016, auditoría 468-DE, Pemex Fertilizantes: Gestión Financiera (compra de Grupo Fertinal)',
        'url': 'https://www.asf.gob.mx/Trans/Informes/IR2016ii/Documentos/Auditorias/2016_0468_a.pdf',
        'sha256': ARCHIVOS['2016_0468_a.pdf'],
    },
    'asf_encic05': {
        'doc': 'ASF, Informe del Resultado de la Cuenta Pública 2005, tomo VI, vol. 2, auditoría 584, SEP: Egresos Presupuestales Asignados al Proyecto Enciclomedia',
        'url': 'https://www.asf.gob.mx/Trans/Informes/ir2005i/Tomos/T6V2.pdf',
        'sha256': ARCHIVOS['T6V2.pdf'],
    },
    'asf_farac17': {
        'doc': 'ASF, Cuenta Pública 2017, auditoría 96, Banobras: Fideicomiso Fondo Nacional de Infraestructura (deuda del rescate carretero)',
        'url': 'https://www.asf.gob.mx/Trans/Informes/IR2017c/Documentos/Auditorias/2017_0096_a.pdf',
        'sha256': ARCHIVOS['2017_0096_a.pdf'],
    },
}

PEND3 = {'inversion_presupuestada_mdp': 'pendiente', 'inversion_real_mdp': 'pendiente', 'sobrecosto_pct': 'pendiente'}

# Cada obra: valores que sustituyen a los del simulador, estado de cada campo,
# definiciones, hallazgo y la lista «asfHist» que pinta el panel lateral.
OBRAS = {
    'estela-luz': {
        'valores': {'inversion_presupuestada_mdp': 393.5, 'inversion_real_mdp': 1304.9, 'sobrecosto_pct': 192.0},
        'campos': {'inversion_presupuestada_mdp': 'oficial', 'inversion_real_mdp': 'oficial', 'sobrecosto_pct': 'oficial'},
        'definiciones': {
            'inversion_presupuestada_mdp': 'Monto del contrato de construcción firmado el 18-12-2009 entre el fideicomiso e I.I.I. Servicios: $393,490.0 miles de pesos (ASF, informe especial, p. 3).',
            'inversion_real_mdp': 'Costo final del proyecto, desde su concepción hasta su inauguración: $1,304,917.7 miles de pesos (ASF, informe especial, p. 13).',
            'sobrecosto_pct': 'La ASF calcula que el costo de la construcción se elevó 192.0 % respecto del contratado originalmente (p. 13). Mide solo la construcción; el costo final incluye además proyecto, supervisión y otros gastos.',
        },
        'hallazgo': 'La ASF documentó pagos improcedentes por $399.2 mdp incluidos en el costo final: $248.9 mdp por el acero (precio, peso, transporte y montaje) y $150.3 mdp por precios extraordinarios, cuarzo y otros conceptos, y presentó denuncias de hechos. Se inauguró el 7 de enero de 2012, más de 15 meses después de lo previsto.',
        'asfHist': [
            {'dato': 'Contrato de construcción original (18-12-2009)', 'valor': '$393.5 mdp', 'estado': 'oficial', 'pagina': '3'},
            {'dato': 'Total contratado tras cuatro convenios modificatorios', 'valor': '$1,146.4 mdp', 'estado': 'oficial', 'pagina': '3'},
            {'dato': 'Costo final del proyecto', 'valor': '$1,304.9 mdp', 'estado': 'oficial', 'pagina': '13'},
            {'dato': 'Pagos injustificados en el acero', 'valor': '$248.9 mdp', 'estado': 'oficial', 'pagina': '3'},
            {'dato': 'Otros pagos improcedentes', 'valor': '$150.3 mdp', 'estado': 'oficial', 'pagina': '4'},
        ],
        'fuentes': ['asf_estela'],
    },
    'refineria-tula': {
        'valores': {'inversion_presupuestada_mdp': 3714.0, 'inversion_real_mdp': 1127.6, 'sobrecosto_pct': 0},
        'campos': {'inversion_presupuestada_mdp': 'derivado', 'inversion_real_mdp': 'derivado', 'sobrecosto_pct': 'derivado'},
        'definiciones': {
            'inversion_presupuestada_mdp': 'Suma de lo que Hacienda autorizó a los dos proyectos de inversión de la nueva refinería: $1,475.2 mdp para estudios de preinversión (clave 0818T4M0023) y $2,238.8 mdp para acondicionar el terreno (clave 0918T4M0048). ASF, auditoría 315, CP 2014, pp. 10 y 11.',
            'inversion_real_mdp': 'Suma de lo ejercido en esos dos proyectos: $659.3 mdp en 17 contratos de estudios y $468.3 mdp en obras del terreno (pp. 10 y 11).',
            'sobrecosto_pct': 'No hubo sobrecosto: el proyecto se detuvo habiendo ejercido el 30.4 % de lo autorizado. Se dejaron de ejecutar $1,770.5 mdp de plataformas, urbanización, edificios y vialidades (p. 11).',
        },
        'hallazgo': 'La ASF constató que la nueva refinería no continuó: de $3,714.0 mdp autorizados a sus dos proyectos de inversión se ejercieron $1,127.6 mdp, y siete contratos se terminaron anticipadamente por «cambio de estrategia de negocios». La cifra de $12,400 mdp que traía el simulador no aparece en este documento.',
        'asfHist': [
            {'dato': 'Estudios de preinversión: autorizado / ejercido', 'valor': '$1,475.2 / $659.3 mdp', 'estado': 'oficial', 'pagina': '10'},
            {'dato': 'Acondicionamiento del terreno: autorizado / ejercido', 'valor': '$2,238.8 / $468.3 mdp', 'estado': 'oficial', 'pagina': '11'},
            {'dato': 'Obra que se dejó de ejecutar', 'valor': '$1,770.5 mdp', 'estado': 'oficial', 'pagina': '11'},
            {'dato': 'Total ejercido (suma)', 'valor': '$1,127.6 mdp', 'estado': 'derivado', 'pagina': '10-11'},
        ],
        'fuentes': ['asf_tula14'],
    },
    'agronitrogenados': {
        'valores': {},
        'campos': dict(PEND3),
        'definiciones': {
            'inversion_presupuestada_mdp': 'La ASF da estas cifras en dólares: el proyecto se autorizó en 475 millones de dólares (compra más rehabilitación) y subió a 760 millones. No hay en el documento un equivalente en pesos, así que la cifra en mdp sigue pendiente.',
            'inversion_real_mdp': 'Pendiente en pesos. En dólares: 760 millones por Agro Nitrogenados (ASF, CP 2015, p. 27) y 635 millones por Fertinal (ASF, CP 2016, p. 2). No se suman ni se convierten aquí: son compras distintas, de años distintos.',
            'sobrecosto_pct': 'En dólares, el costo total de Agro Nitrogenados pasó de 475 a 760 millones: 60.0 % más (cálculo de Auditavisión con las dos cifras de la ASF, p. 27). No incluye Fertinal.',
        },
        'hallazgo': 'La ASF concluyó que Pemex compró la planta de Agro Nitrogenados en 275 millones de dólares sin evaluar el estado de los bienes (llevaba 14 años sin operar) y que la rehabilitación subió de 200 a 485 millones, con lo que el proyecto pasó de 475 a 760 millones de dólares. De Fertinal, comprada en 635 millones de dólares, dictaminó que «no es un negocio rentable» para Pemex y que en 2016 registró una pérdida integral de 565.7 millones de dólares.',
        'asfHist': [
            {'dato': 'Agro Nitrogenados: precio de compra de la planta', 'valor': '275 millones de dólares', 'estado': 'oficial', 'pagina': '27 (CP 2015)'},
            {'dato': 'Agro Nitrogenados: costo total autorizado → final', 'valor': '475 → 760 millones de dólares', 'estado': 'oficial', 'pagina': '26-27 (CP 2015)'},
            {'dato': 'Aumento del costo total', 'valor': '60.0 %', 'estado': 'derivado', 'pagina': '27 (CP 2015)'},
            {'dato': 'Fertinal: inversión de compra (2016)', 'valor': '635 millones de dólares', 'estado': 'oficial', 'pagina': '2 (CP 2016)'},
            {'dato': 'Fertinal: pérdida integral de 2016', 'valor': '565.7 millones de dólares ($11,690.6 mdp)', 'estado': 'oficial', 'pagina': '31 (CP 2016)'},
        ],
        'fuentes': ['asf_agro15', 'asf_fert16'],
    },
    'enciclomedia': {
        'valores': {'inversion_presupuestada_mdp': 21398.3},
        'campos': {'inversion_presupuestada_mdp': 'oficial', 'inversion_real_mdp': 'pendiente', 'sobrecosto_pct': 'pendiente'},
        'definiciones': {
            'inversion_presupuestada_mdp': 'Recursos que Hacienda autorizó para el servicio multianual de Enciclomedia de 2005 a 2010: $21,398,300.0 miles de pesos para 125,562 aulas (ASF, CP 2005, tomo VI, vol. 2, p. 264).',
            'inversion_real_mdp': 'Falta un documento que sume lo pagado de 2004 a 2011. La ASF solo revisó 2005, cuando se ejercieron $478.3 mdp de los $2,105.0 mdp previstos (p. 270).',
            'sobrecosto_pct': 'No se puede calcular mientras falte lo pagado en total.',
        },
        'hallazgo': 'La ASF revisó el primer año del contrato multianual (2005): de $2,105.0 mdp asignados a Enciclomedia se ejercieron $478.3 mdp, porque el esquema cambió de compra de equipo a un servicio multianual de arrendamiento. Hacienda había autorizado $21,398.3 mdp para 2005 a 2010.',
        'asfHist': [
            {'dato': 'Autorizado para el servicio multianual 2005-2010', 'valor': '$21,398.3 mdp', 'estado': 'oficial', 'pagina': '264'},
            {'dato': 'Presupuesto original de 2005', 'valor': '$2,105.0 mdp', 'estado': 'oficial', 'pagina': '265'},
            {'dato': 'Ejercido en 2005', 'valor': '$478.3 mdp', 'estado': 'oficial', 'pagina': '270'},
        ],
        'fuentes': ['asf_encic05'],
    },
    'farac-carretero': {
        'valores': {},
        'campos': dict(PEND3),
        'definiciones': {
            'inversion_presupuestada_mdp': 'El rescate no tuvo un presupuesto de obra: sustituyó deuda bancaria de los concesionarios por deuda en bonos con aval federal. Lo que la ASF documenta es esa deuda (ver el panel).',
            'inversion_real_mdp': 'Pendiente: falta un documento que diga cuánto costó en total indemnizar a los concesionarios de las 23 autopistas.',
            'sobrecosto_pct': 'No aplica mientras no haya un costo original y uno final comparables.',
        },
        'hallazgo': 'La ASF (Cuenta Pública 2017) documentó que la deuda en bonos del rescate carretero pasó de $27,491.2 mdp en 1997 a $225,500.2 mdp en 2017, por nuevas emisiones, el aumento de la UDI y la capitalización de intereses; ese año se pagaron $10,368.6 mdp de intereses y lo que faltaba pagar de 2018 a 2033 se estimaba en $351,969.6 mdp.',
        'asfHist': [
            {'dato': 'Deuda en bonos del rescate, 1997', 'valor': '$27,491.2 mdp', 'estado': 'oficial', 'pagina': '6'},
            {'dato': 'Deuda en bonos neta, 31-12-2017', 'valor': '$225,500.2 mdp', 'estado': 'oficial', 'pagina': '5-6'},
            {'dato': 'Intereses pagados en 2017', 'valor': '$10,368.6 mdp', 'estado': 'oficial', 'pagina': '6'},
            {'dato': 'Capital e intereses por pagar 2018-2033 (estimado por la ASF, en UDIS valuadas a 2017)', 'valor': '$351,969.6 mdp', 'estado': 'oficial', 'pagina': '6'},
        ],
        'fuentes': ['asf_farac17'],
    },
}


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def patch():
    raw = open(DB, 'rb').read().decode('utf-8')
    i = raw.index('"simulador_megaobras": {')
    j = raw.index('{', i)
    prof = 0
    for k in range(j, len(raw)):
        c = raw[k]
        if c == '{':
            prof += 1
        elif c == '}':
            prof -= 1
            if prof == 0:
                break
    bloque = raw[j:k + 1]
    nl = '\r\n' if '\r\n' in bloque else '\n'
    sim = json.loads(bloque)
    ver = sim['verificacion']
    ver['fuentes'].update(FUENTES)

    for o in sim['obras']:
        v = OBRAS.get(o['id'])
        if not v:
            continue
        for campo, valor in v['valores'].items():
            o[campo] = valor
        pres, real = o['inversion_presupuestada_mdp'], o['inversion_real_mdp']
        # El sobrecosto oficial (Estela) o el derivado (Tula) ya viene
        # en valores; si no, se recalcula con las cifras que quedan.
        if 'sobrecosto_pct' not in v['valores'] and pres and real:
            o['sobrecosto_pct'] = round((real / pres - 1) * 100, 1)
        o['estado_campos'] = dict(v['campos'])
        o['hallazgo_asf'] = v['hallazgo']
        ver['obras'][o['id']] = {
            'campos': v['campos'],
            'definiciones': v['definiciones'],
            'hallazgo': v['hallazgo'],
            'asfHist': v['asfHist'],
            'fuentes': v['fuentes'],
        }

    t = sim['totales_consolidados']
    t['inversion_total_mdp'] = round(sum(o['inversion_real_mdp'] for o in sim['obras']), 1)
    t['inversion_presupuestada_total_mdp'] = round(sum(o['inversion_presupuestada_mdp'] for o in sim['obras']), 1)
    t['sobrecosto_conjunto_pct'] = round((t['inversion_total_mdp'] / t['inversion_presupuestada_total_mdp'] - 1) * 100, 1)

    nuevo = json.dumps(sim, ensure_ascii=False, indent=2)
    nuevo = nuevo[:-1] + raw[raw.rfind('\n', 0, k) + 1:k] + '}'
    raw = raw[:j] + nuevo.replace('\n', nl) + raw[k + 1:]
    open(DB, 'wb').write(raw.encode('utf-8'))
    return sim


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    for nombre, h in ARCHIVOS.items():
        real = sha(os.path.join(sys.argv[1], nombre))
        if real != h:
            sys.exit('La huella de %s no coincide: %s' % (nombre, real))
    print('Huellas verificadas (%d archivos).' % len(ARCHIVOS))
    sim = patch()
    for o in sim['obras']:
        if o['id'] in OBRAS:
            print('  %-18s presupuesto %10s  real %10s  sobrecosto %6s  %s' % (
                o['id'], o['inversion_presupuestada_mdp'], o['inversion_real_mdp'], o['sobrecosto_pct'], o['estado_campos']))
    print('Totales:', {k: sim['totales_consolidados'][k] for k in ('inversion_total_mdp', 'inversion_presupuestada_total_mdp', 'sobrecosto_conjunto_pct')})


if __name__ == '__main__':
    main()
