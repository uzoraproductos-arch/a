# -*- coding: utf-8 -*-
"""Diputadas y diputados locales: lo que pagan los congresos con documento
de 2026 (28-09-2026).

Doce de 32, cada uno con su archivo oficial (huellas comprobadas):

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
- Colima: acuerdo parlamentario con el tabulador 2026 del Poder Legislativo,
  Periódico Oficial «El Estado de Colima», 21-02-2026, supl. 2, pp. 9-10.
  Quincenal: dieta $38,738.30 + previsión social $7,500 = $46,238.30; neto
  $33,556.84. Mensual = 2 quincenas («derivado»).
- Tlaxcala: Presupuesto de Egresos 2026 (P.O. núm. 50, 5.ª secc.,
  10-12-2025), Anexo 42, analítico de plazas del Poder Legislativo, p. 469:
  25 diputados «de $111,243 hasta $135,923». El decreto no dice la
  periodicidad; es mensual porque la partida 1111 Dietas ($33,669,060,
  Anexo 8) entre 25 y 12 da $112,230 («derivado»).
- Nayarit: formato art. 33 fr. VIII del 1.er trimestre de 2026. Los 30
  diputados: sueldo $32,651 bruto ($26,397.46 neto) y dieta $78,406.64
  bruta mensual, cuyo neto no se reporta. Bruto = suma («derivado»).
- Guerrero: formato 08A-VIIIA del 1.er trimestre de 2026. 45 de 46
  diputados, $50,060 brutos y $40,188 netos; sin dietas ni compensaciones.
- Sinaloa: Manual de Remuneraciones del Poder Legislativo 2026-2027,
  Anexo 4, p. 23. Sueldo $28,234.20 + compensación a legisladores
  $112,707.14 = $140,941.34 de percepciones ordinarias mensuales.
- Oaxaca: formato LGTA70FVIIIA 2026 (1.er y 2.º trimestres). Los 42
  diputados, $51,448.51 brutos y $42,000 netos.
- Campeche: Ley de Presupuesto de Egresos 2026, Anexo 19 (tabuladores):
  dieta $61,952 y, en el analítico, 35 diputados con sueldo bruto mensual
  de $61,952.
- Yucatán: Presupuesto 2026, tomo de los poderes y organismos autónomos
  (Diario Oficial núm. 35,878, 29-12-2025), Congreso, p. 187: sueldo base
  $44,880 + despensa $6,000 = $50,880 de percepciones mensuales.

Sin neto publicado: Tlaxcala, Nayarit (la dieta), Sinaloa, Campeche y
Yucatán; su neto queda «pendiente» y no entra en el rango neto.

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
    'COL': (os.path.join(LOC, 'Colima_PO_2026-02-21_Sup02_TabuladorLegislativo.pdf'), '06e9d12e1e4d1893c88a1bdd6a7e3fc969792ba6bd511878581a618db16b7a95'),
    'TLX': (os.path.join(LOC, 'Tlaxcala_PO50_5aSecc_2025-12-10_PresupuestoEgresos2026.pdf'), '6db5994001400bfdfb87f14d7291f996c78cfe120109f48d4623a495bdb588a0'),
    'NAY': (os.path.join(LOC, 'Nayarit_A33FVIII_1T2026.xlsx'), '6a45b470e405dc35e89e4cd403055fabbe65189d5966ce53b0e3df1d9acff5d4'),
    'GRO': (os.path.join(LOC, 'Guerrero_08A-VIIIA_1T2026.xlsx'), 'b5dafc47a00bcdca3ad9aff953e6d3066008a3046a851a4db1932e8095ede7e6'),
    'SIN': (os.path.join(LOC, 'Sinaloa_ManualRemuneraciones_2026-2027.pdf'), '3bd782d48affe4fdd6d2634939795c5309836caaa3b1887e335ca6ae061f7ff5'),
    'OAX': (os.path.join(LOC, 'Oaxaca_LGTA70FVIIIA_2026.xlsx'), 'bdd2c652811fecdf91d97dd778019e01072570ad34987c87f73e141204157a38'),
    'CAM': (os.path.join(LOC, 'Campeche_LPE2026_Anexo19_Tabuladores.docx'), '627801e7d40f26fc8753b0c90d394a1ae75a5441069a0fa60322c81dca4e6dc2'),
    'YUC': (os.path.join(LOC, 'Yucatan_DO35878_2025-12-29_TomoPoderesAutonomos.pdf'), '471275a3c4391ccb018e9e41d99897f3557d6b5e3f4c5010ae9501fa34291834'),
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
    'COL': {'corto': 'Periódico Oficial de Colima, 21-02-2026',
            'doc': 'Periódico Oficial «El Estado de Colima», 21 de febrero de 2026, suplemento 2: acuerdo parlamentario que aprueba el tabulador de remuneraciones del Poder Legislativo para el ejercicio fiscal 2026',
            'url': 'https://periodicooficial.col.gob.mx/p/21022026/sup02/226022101.pdf'},
    'TLX': {'corto': 'Presupuesto de Egresos de Tlaxcala 2026',
            'doc': 'Periódico Oficial del Estado de Tlaxcala núm. 50, 5.ª sección, 10 de diciembre de 2025: Presupuesto de Egresos del Estado de Tlaxcala para el ejercicio fiscal 2026 (Anexos 8 y 42)',
            'url': 'https://sefintlax.gob.mx/DocsSF/2026/admin/enero/PRESUPUESTO_EGRESOS_TLAXCALA_2026.pdf'},
    'NAY': {'corto': 'Congreso de Nayarit, remuneraciones 1.er trim. 2026',
            'doc': 'H. Congreso del Estado de Nayarit, formato LTAIPEN art. 33 fr. VIII (remuneración bruta y neta), primer trimestre de 2026, con su tabla de dietas',
            'url': 'https://congresonayarit.gob.mx/wp-content/uploads/TRANSPARENCIA/art_33/08/2026/08_a_remuneracion_bruta_y_neta_primer_trimestre_2026.xlsx'},
    'GRO': {'corto': 'Congreso de Guerrero, remuneraciones 1.er trim. 2026',
            'doc': 'H. Congreso del Estado de Guerrero, formato 08A-VIIIA (remuneración bruta y neta), primer trimestre de 2026',
            'url': 'https://congresogro.gob.mx/transparencia/2026/08A-VIIIA-2026-1.xlsx'},
    'SIN': {'corto': 'Congreso de Sinaloa, manual de remuneraciones 2026-2027',
            'doc': 'H. Congreso del Estado de Sinaloa, Manual de Remuneraciones del Poder Legislativo del Estado de Sinaloa 2026-2027, Anexo 4 (catálogo de sueldos por categoría)',
            'url': 'https://www.congresosinaloa.gob.mx/images/estructura-y-normatividad/MANUAL_DE_REMUNERACIONES_DEL_PODER_LEGISLATIVO_DEL_2026-2027_.pdf'},
    'OAX': {'corto': 'Congreso de Oaxaca, remuneraciones 2026',
            'doc': 'H. Congreso del Estado de Oaxaca, formato LGTA70FVIIIA (remuneración bruta y neta), primer y segundo trimestres de 2026',
            'url': 'https://www.congresooaxaca.gob.mx/docs66.congresooaxaca.gob.mx/transparencia/2026/ART70/FVIII/LGTA70FVIIIA_2026.xlsx'},
    'CAM': {'corto': 'Presupuesto de Egresos de Campeche 2026, Anexo 19',
            'doc': 'Ley de Presupuesto de Egresos del Estado de Campeche para el ejercicio fiscal 2026, Anexo 19: tabuladores (incluye el Poder Legislativo y su analítico de plazas)',
            'url': 'https://legislacion.congresocam.gob.mx/index.php/leyes-focalizadas/paquete-fiscal/2026/649-anexos-de-la-ley-de-presupuesto-de-egresos-del-estado-de-campeche-para-el-ejercicio-fiscal-2026/file'},
    'YUC': {'corto': 'Diario Oficial de Yucatán, 29-12-2025',
            'doc': 'Diario Oficial del Gobierno del Estado de Yucatán núm. 35,878, 29 de diciembre de 2025, edición especial: Presupuesto de Egresos 2026, tomo de los poderes y organismos autónomos (Congreso del Estado)',
            'url': 'https://www.yucatan.gob.mx/docs/diario_oficial/diarios/2025/2025-12-29_5.pdf'},
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
    {'nombre': 'Colima', 'bruto': 2 * 46238.30, 'brutoEstado': 'derivado', 'neto': 2 * 33556.84, 'netoEstado': 'derivado',
     'concepto': 'Por quincena: dieta $38,738.30 más previsión social $7,500 = $46,238.30 brutos; menos ISR ($10,780.71) y pensiones ($1,900.75), $33,556.84 netos. Mensual: la quincena por dos. Una segunda fila del tabulador retiene más de pensiones y deja $33,285.30 netos.',
     'fuente': 'COL', 'pagina': 'pp. 9-10'},
    {'nombre': 'Tlaxcala', 'bruto': 111243.0, 'brutoHasta': 135923.0, 'brutoEstado': 'derivado', 'neto': None, 'netoEstado': 'pendiente',
     'concepto': 'Los 25 diputados, remuneración «de $111,243 hasta $135,923» en el analítico de plazas. El decreto no dice la periodicidad: es mensual porque la partida de dietas ($33,669,060 al año, Anexo 8) entre 25 diputados y 12 meses da $112,230. No publica el neto.',
     'fuente': 'TLX', 'pagina': 'Anexo 42, p. 469'},
    {'nombre': 'Nayarit', 'bruto': 32651.0 + 78406.64, 'brutoEstado': 'derivado', 'neto': None, 'netoEstado': 'pendiente',
     'concepto': 'Los 30 diputados: sueldo de $32,651 brutos ($26,397.46 netos) más dieta de $78,406.64 brutos al mes, cuyo neto el formato no reporta. Bruto: la suma de ambos.',
     'fuente': 'NAY', 'pagina': 'tabla de dietas'},
    {'nombre': 'Guerrero', 'bruto': 50060.0, 'brutoEstado': 'oficial', 'neto': 40188.0, 'netoEstado': 'oficial',
     'concepto': '45 de los 46 diputados (a uno le quedan $28,130 netos). El formato no registra dietas, bonos ni compensaciones; aparte, aguinaldo de $62,575 al año.',
     'fuente': 'GRO', 'pagina': 'enero a marzo de 2026'},
    {'nombre': 'Sinaloa', 'bruto': 140941.34, 'brutoEstado': 'oficial', 'neto': None, 'netoEstado': 'pendiente',
     'concepto': 'Sueldo de $28,234.20 más «compensación a legisladores» de $112,707.14: total de percepciones ordinarias mensuales. El manual no publica el neto.',
     'fuente': 'SIN', 'pagina': 'Anexo 4, p. 23'},
    {'nombre': 'Oaxaca', 'bruto': 51448.51, 'brutoEstado': 'oficial', 'neto': 42000.0, 'netoEstado': 'oficial',
     'concepto': 'Los 42 diputados, igual en el primero y el segundo trimestres; las percepciones adicionales aparecen como «no disponible».',
     'fuente': 'OAX', 'pagina': 'enero a junio de 2026'},
    {'nombre': 'Campeche', 'bruto': 61952.0, 'brutoEstado': 'oficial', 'neto': None, 'netoEstado': 'pendiente',
     'concepto': 'Dieta de los 35 diputados; el analítico de plazas la registra como sueldo bruto mensual. No publica el neto.',
     'fuente': 'CAM', 'pagina': 'tabulador del Poder Legislativo'},
    {'nombre': 'Yucatán', 'bruto': 50880.0, 'brutoEstado': 'oficial', 'neto': None, 'netoEstado': 'pendiente',
     'concepto': 'Los 35 diputados: sueldo base de $44,880 más despensa de $6,000 al mes; aparte, aguinaldo de $59,840 al año. No publica el neto.',
     'fuente': 'YUC', 'pagina': 'p. 187'},
]
ENTIDADES.sort(key=lambda e: -e['bruto'])
for e in ENTIDADES:
    e['bruto'] = round(e['bruto'], 2)
    if e['neto'] is not None:
        e['neto'] = round(e['neto'], 2)


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
    con_neto = [e for e in ENTIDADES if e['neto'] is not None]
    netos = [e['neto'] for e in con_neto]
    mayor = max(con_neto, key=lambda e: e['neto'])
    menor = min(con_neto, key=lambda e: e['neto'])
    n = len(ENTIDADES)
    brutos = [e['bruto'] for e in ENTIDADES]
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
        'mensualConcepto': ('Neto mensual: del congreso que menos paga (%s) al que más (%s), entre los %d que publican el neto. '
                            'En bruto, los %d con documento van de $%s a $%s al mes' % (menor['nombre'], mayor['nombre'], len(con_neto), n,
                                                                                         format(min(brutos), ',.2f'), format(max(brutos), ',.2f'))),
        'anual': round(12 * mayor['neto'], 2),
        'anualEstado': 'derivado',
        'anualOperacion': '12 × $%s, el neto mensual más alto documentado (%s); sin aguinaldo ni prima vacacional' % (format(mayor['neto'], ',.2f'), mayor['nombre']),
        'parcial': True,
        'fuente': mayor['fuente'],
        'pagina': mayor['pagina'],
        'entidades': ENTIDADES,
        'nota': ('Cada congreso fija su pago con conceptos distintos: unos pagan solo la dieta, otros la reparten en apoyos, compensaciones y gratificaciones. '
                 'Por eso no se promedia ni se extrapola a los %d que faltan. De los que faltan, Ciudad de México, Nuevo León, Chiapas, Quintana Roo y Tamaulipas '
                 'solo tienen años anteriores en su portal, y Baja California Sur y Zacatecas llegan a 2025. Durango publica para 2026 un rango '
                 '($78,890.56 a $113,285) sin decir si es mensual, así que no lo usamos. Michoacán lo publica en un dominio que no pudimos consultar. '
                 'Los demás no los localizamos todavía; suelen estar en la Plataforma Nacional de Transparencia, que no pudimos consultar desde nuestro entorno.') % (32 - n),
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
