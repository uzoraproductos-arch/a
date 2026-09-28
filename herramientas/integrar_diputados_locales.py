# -*- coding: utf-8 -*-
"""Diputadas y diputados locales: lo que pagan los congresos con documento
de 2026 (28-09-2026).

Cuatro de 32, cada uno con su archivo oficial (huellas comprobadas):

- Guanajuato: tabulador de sueldos y prestaciones 2026 del Congreso,
  nivel 20 (investigaciones/entregas/). Percepción mensual bruta
  $224,437.56 y neta $144,097.16, tal como las publica.
- Jalisco: nómina de la primera quincena de septiembre de 2026 del
  Congreso (sistema de nómina de su portal de transparencia). Los 38
  diputados, $54,534.88 brutos por quincena; ISR $13,310.23 y pensiones
  $6,271.51. Mensual = 2 quincenas («derivado»).
- Tabasco: «Integración de la remuneración mensual del puesto de elección
  popular diputados del año 2026», Periódico Oficial núm. 8590, suplemento
  C, 8-11-2025, p. 3. Bruta $68,577.90 y neta $50,000.00.
- Querétaro: formato de remuneraciones (art. 66, fr. VII), 2.º trimestre
  de 2026. Los 25 diputados, dieta bruta $89,774 y neta $56,885.72, sin
  percepciones adicionales.

No se promedian ni se extrapolan: cada congreso paga con conceptos
distintos. La tarjeta muestra el rango neto y la lista de los cuatro.

Uso:  python3 herramientas/integrar_diputados_locales.py
Solo toca assets/auditor/js/audit-database.js. Idempotente.
"""
import hashlib
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'audit-database.js')
LOC = os.path.join(RAIZ, 'investigaciones', 'congresos-locales')
ENT = os.path.join(RAIZ, 'investigaciones', 'entregas')

ARCHIVOS = {
    'GTO': (os.path.join(ENT, 'Guanajuato_Congreso_Tabulador2026.pdf'), 'e83c076abe51397de41eef1703435b3793c50ace5f9f813085ae93b132ff86e0'),
    'JAL': (os.path.join(LOC, 'Jalisco_Nomina_1aQuincenaSep2026.pdf'), '30a139e7b9791af0a773ba5d2bfbd3ed21c432a887e5806c96e97a482ed79dcc'),
    'TAB': (os.path.join(LOC, 'Tabasco_PO_8590C_2025-11-08.pdf'), '877d5a4e06f63df6a4e7e28b4106852b921e34db71efa44d06df39aab9862a7b'),
    'QRO': (os.path.join(LOC, 'Queretaro_A66FVII_2T2026.xlsx'), '0975a9fe2badfb5b34a1bb33c25245ff76deb665ab8816947b3bcd14cadd095b'),
}
FUENTES = {
    'GTO': {'corto': 'Congreso de Guanajuato, tabulador 2026',
            'doc': 'H. Congreso del Estado de Guanajuato, Tabulador de sueldos y prestaciones 2026 del Poder Legislativo',
            'url': 'https://congreso-gto.s3.amazonaws.com/transparencia/TABULADOR_DE_SUELDOS_2026.pdf'},
    'JAL': {'corto': 'Congreso de Jalisco, nómina 1.ª quincena de septiembre de 2026',
            'doc': 'H. Congreso del Estado de Jalisco, Sistema de nómina, primera quincena de septiembre de 2026 (PDF de la quincena)',
            'url': 'https://transparencia.congresojal.gob.mx/modulos/nomina/impresion_quincena.php?id=260901'},
    'TAB': {'corto': 'Periódico Oficial de Tabasco, 8-11-2025',
            'doc': 'Periódico Oficial del Estado de Tabasco, núm. 8590, suplemento C, 8 de noviembre de 2025: tabuladores 2026 del H. Congreso del Estado',
            'url': 'https://publicacionperiodico.tabasco.gob.mx/documento/7667/firmado_qr.pdf'},
    'QRO': {'corto': 'Legislatura de Querétaro, remuneraciones 2.º trim. 2026',
            'doc': 'Legislatura del Estado de Querétaro, formato LTAIPEQArt66FraccVII (remuneraciones brutas y netas), segundo trimestre de 2026',
            'url': 'http://site.legislaturaqueretaro.gob.mx/CloudPLQ/Transparencia/Art66/Fracc_07/2026/LTAIPEQArt66FraccVIIA_2o_Tri_2026.xlsx'},
}

Q_JAL, ISR_JAL, PEN_JAL = 54534.88, 13310.23, 6271.51
ENTIDADES = [
    {'nombre': 'Guanajuato', 'bruto': 224437.56, 'brutoEstado': 'oficial', 'neto': 144097.16, 'netoEstado': 'oficial',
     'concepto': 'Seis conceptos mensuales: sueldo nominal $55,295.23, cuotas de seguridad social, previsión social, ayuda por servicios, apoyo familiar y gratificación quincenal. Neto después de ISR y fondo de ahorro. Aparte, 45 días de aguinaldo ($336,656.34 brutos).',
     'fuente': 'GTO', 'pagina': 'nivel 20'},
    {'nombre': 'Jalisco', 'bruto': round(2 * Q_JAL, 2), 'brutoEstado': 'derivado', 'neto': round(2 * (Q_JAL - ISR_JAL - PEN_JAL), 2), 'netoEstado': 'derivado',
     'concepto': 'Los 38 diputados cobran $54,534.88 brutos por quincena, sin otras percepciones en la nómina. Neto: la quincena menos ISR ($13,310.23) y pensiones ($6,271.51), por dos.',
     'fuente': 'JAL', 'pagina': 'puesto «Diputado»'},
    {'nombre': 'Querétaro', 'bruto': 89774.0, 'brutoEstado': 'oficial', 'neto': 56885.72, 'netoEstado': 'oficial',
     'concepto': 'Los 25 diputados, dieta mensual; el formato no registra percepciones adicionales.',
     'fuente': 'QRO', 'pagina': 'abril a junio de 2026'},
    {'nombre': 'Tabasco', 'bruto': 68577.90, 'brutoEstado': 'oficial', 'neto': 50000.00, 'netoEstado': 'oficial',
     'concepto': 'Percepción ordinaria total mensual; el cuadro no asigna prestaciones adicionales en dinero o en especie.',
     'fuente': 'TAB', 'pagina': 'p. 3'},
]


def bloque(raw, clave):
    i = raw.index('"' + clave + '": {')
    j = raw.index('{', i)
    prof = 0
    for k in range(j, len(raw)):
        if raw[k] == '{':
            prof += 1
        elif raw[k] == '}':
            prof -= 1
            if prof == 0:
                return j, k + 1
    raise ValueError(clave)


def main():
    for clave, (ruta, sha) in ARCHIVOS.items():
        h = hashlib.sha256(open(ruta, 'rb').read()).hexdigest()
        if h != sha:
            sys.exit('La huella de %s no coincide: %s' % (ruta, h))
        FUENTES[clave]['sha256'] = sha

    raw = open(DB, 'rb').read().decode('utf-8')
    a, b = bloque(raw, 'comparador_salarial')
    C = json.loads(raw[a:b])
    C['fuentes'].update(FUENTES)
    netos = [e['neto'] for e in ENTIDADES]
    mayor = max(ENTIDADES, key=lambda e: e['neto'])
    menor = min(ENTIDADES, key=lambda e: e['neto'])
    n = len(ENTIDADES)
    cargo = next(c for c in C['cargos'] if c['id'] == 'diputado_local')
    cargo.clear()
    cargo.update({
        'id': 'diputado_local',
        'grupo': 'local',
        'cargo': 'Diputada o diputado local',
        'detalle': '%d de 32 congresos con documento de 2026' % n,
        'icono': '\U0001f5fa️',
        'mensual': {'min': min(netos), 'max': max(netos)},
        'mensualEstado': 'oficial',
        'mensualConcepto': 'Neto mensual: del congreso que menos paga (%s) al que más (%s), entre los %d con documento' % (menor['nombre'], mayor['nombre'], n),
        'anual': round(12 * mayor['neto'], 2),
        'anualEstado': 'derivado',
        'anualOperacion': '12 × $%s, el neto mensual más alto documentado (%s); sin aguinaldo ni prima vacacional' % (format(mayor['neto'], ',.2f'), mayor['nombre']),
        'parcial': True,
        'fuente': mayor['fuente'],
        'pagina': mayor['pagina'],
        'entidades': ENTIDADES,
        'nota': ('Cada congreso fija su pago con conceptos distintos: unos pagan solo la dieta, otros la reparten en apoyos y gratificaciones. '
                 'Por eso no se promedia ni se extrapola a los 28 que faltan. Faltan porque su documento de 2026 no está en su portal '
                 '(Ciudad de México, Nuevo León, Sinaloa, Chiapas y Tamaulipas publican años anteriores), porque su portal no respondió '
                 '(Michoacán lo publica en un dominio que no pudimos consultar). Los demás no los localizamos todavía en su portal; '
                 'estos datos suelen publicarse en la Plataforma Nacional de Transparencia, que no pudimos consultar desde nuestro entorno.'),
    })
    viejo = raw[a:b]
    sang = len(viejo.split('\r\n')[-1]) - len(viejo.split('\r\n')[-1].lstrip(' '))
    txt = json.dumps(C, ensure_ascii=True, indent=2)
    txt = ('\n' + ' ' * sang).join(txt.split('\n')).replace('\n', '\r\n')
    raw = raw[:a] + txt + raw[b:]
    open(DB, 'wb').write(raw.encode('utf-8'))
    print(json.dumps({e['nombre']: [e['bruto'], e['neto']] for e in ENTIDADES}, ensure_ascii=False))


if __name__ == '__main__':
    main()
