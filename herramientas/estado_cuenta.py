#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Estado de Cuenta Civico (entrega 3 de la propuesta de Astra, 10-10-2026).

Una pagina estatica, estado-de-cuenta.html, con las cifras escritas en el
HTML (se leen sin JavaScript y las indexan los buscadores) y su descarga en
CSV. Compara 2024 (observado), 2026 (aprobado y cierre estimado) y 2027
(propuesto) en las mismas unidades: por ciento del PIB, que es la medida que
permite comparar anos distintos. Los pesos de 2026 y 2027 van al lado.

Fuentes:
- investigaciones/estado-de-cuenta/cgpe2027-comparativo.json, que extrae
  herramientas/extraer_estado_cuenta.py del texto de los Criterios Generales
  de Politica Economica 2027 (cuadros de las pp. 52, 55 y 67).
- window.AUDIT_DB (assets/auditor/js/audit-database.js): la cuenta federal
  2024 corregida, las becas verificadas, la ASF, el INEGI y el Ramo 16.

Lo llama apartados.generar(), asi que sello.py la regenera con el sello.
"""
import csv
import io
import json
import os

from apartados import RAIZ, pagina

CGPE_URL = 'https://gaceta.diputados.gob.mx/PDF/66/2026/sep/20260908-C.pdf'
CGPE = 'SHCP, Criterios Generales de Política Económica 2027 (Gaceta Parlamentaria 7121, 8-09-2026)'
REVISION = '10-10-2026'
ARCHIVO = 'estado-de-cuenta.html'
CSV_ARCHIVO = 'estado-de-cuenta-2024-2027.csv'
COLUMNAS = [('2024', '2024', 'observado'), ('2026a', '2026', 'aprobado'),
            ('2026e', '2026', 'cierre estimado'), ('2027', '2027', 'propuesto')]


def db():
    s = open(os.path.join(RAIZ, 'assets', 'auditor', 'js', 'audit-database.js'), encoding='utf-8').read()
    return json.loads(s[s.index('{'):s.rindex('}') + 1])


def comparativo():
    return json.load(open(os.path.join(RAIZ, 'investigaciones', 'estado-de-cuenta', 'cgpe2027-comparativo.json'),
                          encoding='utf-8'))


def chip(e, pend='estado-cuenta-pesos-2024'):
    """Las etiquetas «pendiente» llevan a su ficha del Registro de pendientes."""
    e = e if e in ('oficial', 'pendiente') else 'derivado'
    extra = ' data-pend="%s"' % pend if e == 'pendiente' and pend else ''
    return '<span class="est-chip est-%s"%s>%s</span>' % (e, extra, e)


def pct(x):
    return ('%.1f%%' % x).replace('-', '−')


def mdp(x):
    return ('$%s' % format(abs(x), ',.1f')) if x >= 0 else '−$%s' % format(abs(x), ',.1f')


def doc(url, texto='Documento ↗'):
    return '<a href="%s" target="_blank" rel="noopener">%s</a>' % (url, texto)


def tabla(filas):
    cab = ''.join('<th>%s<br><small>%s</small></th>' % (a, b) for _, a, b in COLUMNAS)
    cuerpo = []
    for f in filas:
        celdas = []
        for k, _, _ in COLUMNAS:
            pesos = ('<small>%s mdp</small>' % mdp(f['mdp'][k])) if k in f['mdp'] else '<small>pesos: pendiente</small>'
            celdas.append('<td class="ec-num"><b>%s</b>%s</td>' % (pct(f['pib'][k]), pesos))
        cambio = f['pib']['2027'] - f['pib']['2024']
        cuerpo.append('<tr><th scope="row">%s<small>%s</small></th>%s<td class="ec-num ec-cambio">%s%s pp</td></tr>' % (
            f['concepto'], f['que'], ''.join(celdas), '+' if cambio > 0 else '', ('%.1f' % cambio).replace('-', '−')))
    return ('<div class="ec-tabla-w"><table class="ec-tabla"><thead><tr><th>Concepto<br><small>%% del PIB y millones de pesos</small></th>%s'
            '<th>Cambio<br><small>2024 → 2027 %s</small></th></tr></thead><tbody>\n%s\n</tbody></table></div>') % (
                cab, chip('derivado'), '\n'.join(cuerpo))


def barras(titulo, series, tope, nota):
    """series: [(etiqueta, clase, {col: valor})]. Barras horizontales en % del PIB."""
    grupos = []
    for k, anio, etapa in COLUMNAS:
        bs = ''.join('<span class="ec-barra %s" style="--v:%.1f%%"><span>%s %s</span></span>' % (
            clase, min(abs(v[k]) / tope * 100, 100), etq, pct(v[k])) for etq, clase, v in series)
        grupos.append('<div class="ec-grupo"><span class="ec-grupo-tit">%s <small>%s</small></span>%s</div>' % (anio, etapa, bs))
    return '<figure class="ec-grafica"><figcaption>%s</figcaption>%s<p class="ec-grafica-nota">%s</p></figure>' % (
        titulo, ''.join(grupos), nota)


def fuente_cgpe(paginas):
    return '%s %s, cuadros de las pp. %s. %s' % (chip('oficial'), CGPE, paginas, doc(CGPE_URL))


def construir():
    d = db()
    comp = {f['id']: f for f in comparativo()}
    cf = d['cuentaFederal2024']
    cif = {c['id']: c for c in cf['cifras']}
    eco = d['cuentas_ecologicas']
    asf = d['cuenta_publica_asf']
    amb = d['ambiente']
    soc = d['paquete_2027']['sociales']
    refs = {r['id']: r for r in d['referencias_legales'] if isinstance(r, dict)}
    pres = [comp[i] for i in ('ingresos', 'tributarios', 'petroleros', 'gasto', 'programable', 'participaciones', 'balance')]
    fin = [comp[i] for i in ('costofin', 'primario', 'shrfsp')]

    lectura = ('<div class="ec-lectura"><b>Cómo leer este estado de cuenta.</b> Los años se comparan en <b>por ciento del PIB</b>: '
               'un peso de 2024 no vale lo mismo que uno de 2027, y la economía también crece. Junto a cada porcentaje van los '
               'millones de pesos que publica Hacienda. Las columnas no son de la misma etapa: <b>2024 es lo observado</b>, '
               '<b>2026 trae lo aprobado y el cierre que Hacienda estima</b>, y <b>2027 es la propuesta</b> que la Cámara de '
               'Diputados todavía puede cambiar hasta el 15 de noviembre. Los pesos de 2024 están pendientes: los cuadros de los '
               'Criterios solo dan su porcentaje del PIB, y la Cuenta Pública 2024 aún no la cotejamos.</div>')

    presupuestaria = lectura + tabla(pres) + barras(
        'Lo que entra y lo que se paga, en % del PIB',
        [('Ingresos', 'ec-ing', comp['ingresos']['pib']), ('Gasto', 'ec-gas', comp['gasto']['pib'])], 30,
        'La distancia entre las dos barras es el déficit presupuestario de cada año. ' + chip('oficial')) + (
        '<p class="ec-fuente">%s Sector público presupuestario. 2024: cuadro «Ingresos y gasto del Sector Público» (p. 55). '
        '2026 y 2027: cuadro II.6 «Estimación de las finanzas públicas 2026-2027» (p. 67). El cambio se calcula restando el '
        'porcentaje de 2024 al de 2027.</p>' % fuente_cgpe('55 y 67')) + (
        '<p class="ec-fuente"><b>Para no confundir:</b> el presupuesto que aprobó la Cámara para 2024 fue de <b>%s mdp</b> de gasto neto '
        'total %s (%s). Es otra medida: lo autorizado, no lo pagado. %s</p>' % (
            mdp(cif['aprobado']['mdp']), chip('oficial'), 'Decreto del PEF 2024, art. 1', doc(cif['aprobado']['url'])))

    financiera = tabla(fin) + barras(
        'La deuda amplia (SHRFSP), en % del PIB',
        [('Deuda', 'ec-deu', comp['shrfsp']['pib'])], 60,
        'La deuda pasa de 51.9% del PIB en 2024 a 55.0% en la propuesta de 2027. ' + chip('oficial')) + (
        '<p class="ec-fuente">%s SHRFSP de 2024: cuadro de requerimientos financieros (p. 52). Lo demás: cuadros de las pp. 55 y 67.</p>'
        % fuente_cgpe('52, 55 y 67')) + (
        '<h3 class="ec-sub">La contabilidad del Gobierno Federal en 2024</h3>'
        '<table class="ec-tabla ec-mini"><tbody>%s</tbody></table>'
        '<p class="ec-fuente">%s</p>') % (
        ''.join('<tr><th scope="row">%s%s</th><td class="ec-num">%s</td><td>%s <small>%s %s</small></td></tr>' % (
            c['concepto'], ('<small>%s</small>' % c['nota']) if c.get('nota') else '',
            mdp(c['mdp']) + ' mdp' if c['mdp'] is not None else '—', chip(c['estado']),
            c['fuente'] if c['estado'] == 'oficial' else c['motivo'], doc(c['url']) if c.get('url') else '')
            for c in cf['cifras'] if c['vista'] == 'actividades'),
        'Estado de Actividades del Gobierno Federal, Tomo II de la Cuenta Pública 2024. Los intereses de aquí son solo del Gobierno '
        'Federal; el costo financiero de arriba es del sector público y suma otros conceptos.')

    becas = [m for m in cf['evaluacion_social_mir'] if m['estado_montos'] == 'oficial']
    social = (
        '<table class="ec-tabla ec-mini"><thead><tr><th>Programa</th><th>2024 aprobado</th><th>2024 devengado</th><th>Estado</th></tr></thead><tbody>%s%s</tbody></table>'
        '<p class="ec-fuente">%s</p>'
        '<h3 class="ec-sub">La propuesta de 2027</h3>'
        '<p>El proyecto de Presupuesto 2027 destina <b>%s mdp</b> a los programas sociales prioritarios, %s del PIB %s. Los cinco mayores:</p>'
        '<ul class="ec-lista">%s</ul>'
        '<p class="ec-fuente">%s Cuadro «Programas sociales prioritarios» (p. 33). No se compara renglón por renglón con 2024 porque los '
        'programas cambiaron de nombre y de diseño; esa comparación se hará cuando cada uno tenga su clave programática cotejada.</p>'
        '<div class="ec-pendiente">%s <b>Resultados de los programas:</b> propósito, cobertura e impacto son mediciones distintas. La Matriz '
        'de Indicadores para Resultados y las evaluaciones del CONEVAL existen; la plataforma aún no las coteja.</div>') % (
        ''.join('<tr><th scope="row">%s <small>%s · %s</small></th><td class="ec-num">%s</td><td class="ec-num">%s</td><td>%s</td></tr>' % (
            m['programa'], m['clave'], m['ramo'], mdp(m['aprobado_mdp']), mdp(m['devengado_mdp']), chip('oficial')) for m in becas),
        ''.join('<tr><th scope="row">%s</th><td>—</td><td>—</td><td>%s <small>%s</small></td></tr>' % (
            m['programa'], chip('pendiente', 'prog-montos-' + ('imss-bienestar' if 'IMSS' in m['programa'] else m['clave'].lower())),
            m['motivo_montos']) for m in cf['evaluacion_social_mir'] if m['estado_montos'] != 'oficial'),
        '%s %s' % (becas[0]['fuente_montos'], doc(becas[0]['url'])) if becas else '',
        mdp(soc['total']), pct(soc['pibPct']), chip('oficial'),
        ''.join('<li>%s: <b>%s mdp</b></li>' % (x['n'], mdp(x['m'])) for x in sorted(soc['filas'], key=lambda x: -x['m'])[:5]),
        fuente_cgpe('33'), chip('pendiente', 'prog-resultados'))

    p16 = amb['presupuesto']
    ceem = refs.get('ref-ceem-2024', {})
    ambiental = (
        '<table class="ec-tabla ec-mini"><tbody>'
        '<tr><th scope="row">Costos por agotamiento y degradación ambiental (2024)<small>Lo que costó al ambiente producir el PIB de 2024: '
        'agua, suelo, aire y bosques. Es una cuenta nacional, no un gasto del presupuesto.</small></th><td class="ec-num">%s mdp<br><small>%s del PIB</small></td><td>%s</td></tr>'
        '<tr><th scope="row">Gasto en protección ambiental del sector público (2024)</th><td class="ec-num">%s mdp<br><small>%s del PIB</small></td><td>%s</td></tr>'
        '<tr><th scope="row">Ramo 16, Medio Ambiente y Recursos Naturales: aprobado 2026</th><td class="ec-num">%s mdp</td><td>%s</td></tr>'
        '<tr><th scope="row">Ramo 16: propuesto 2027</th><td class="ec-num">%s mdp</td><td>%s</td></tr>'
        '</tbody></table>'
        '<p class="ec-fuente">INEGI, Cuentas Económicas y Ecológicas de México 2024 %s. Ramo 16: %s %s y %s %s.</p>'
        '<p>Por cada peso que el sector público gastó en proteger el ambiente en 2024, el país perdió <b>%.2f pesos</b> en agotamiento y '
        'degradación %s (%s ÷ %s).</p>') % (
        mdp(eco['ctada']['total_mdp']), pct(eco['ctada']['pct_pib']), chip(eco['ctada']['estado']),
        mdp(eco['gasto_proteccion_ambiental']['monto_mdp']), pct(eco['gasto_proteccion_ambiental']['pct_pib']),
        chip(eco['gasto_proteccion_ambiental']['estado']),
        mdp(p16['aprobado2026']['valor'] / 1e6), chip(p16['aprobado2026']['estado']),
        mdp(p16['proyecto2027']['valor'] / 1e6), chip(p16['proyecto2027']['estado']),
        doc(ceem.get('url', '#')), amb['fuentes']['PEF']['corto'], doc(amb['fuentes']['PEF']['url']),
        amb['fuentes']['PPEF2027']['corto'], doc(amb['fuentes']['PPEF2027']['url']),
        eco['ctada']['total_mdp'] / eco['gasto_proteccion_ambiental']['monto_mdp'], chip('derivado'),
        mdp(eco['ctada']['total_mdp']), mdp(eco['gasto_proteccion_ambiental']['monto_mdp']))

    t = asf['cp2024']['total']
    mdb = asf['fuentes']['MDB2024']
    renglones = (
        '<p>Estos renglones van aparte y <b>no se suman entre sí</b>: miden cosas de distinta naturaleza. Un déficit es dinero que '
        'falta y se cubre con deuda; un monto por aclarar es gasto que la ASF todavía no da por bueno; un daño ambiental es una pérdida '
        'de la nación que no pasa por el presupuesto. Sumarlos sería contar dos veces o mezclar peras con manzanas.</p>'
        '<div class="ec-renglones">'
        '<div class="ec-renglon ec-r-def"><span class="ec-r-tit">📉 Déficit presupuestario</span><b>%s · %s · %s</b>'
        '<span>2024 observado · 2026 cierre estimado · 2027 propuesto, en %% del PIB %s</span></div>'
        '<div class="ec-renglon ec-r-asf"><span class="ec-r-tit">🔍 Por aclarar ante la ASF (Cuenta Pública 2024)</span><b>%s mdp</b>'
        '<span>%s auditorías. Un monto por aclarar no es un desfalco comprobado: es gasto cuya justificación la ASF aún no acepta. %s %s, p. %s %s</span></div>'
        '<div class="ec-renglon ec-r-amb"><span class="ec-r-tit">🌎 Daño ambiental (2024)</span><b>%s mdp</b>'
        '<span>Agotamiento y degradación, %s del PIB. %s</span></div>'
        '<div class="ec-renglon ec-r-pen"><span class="ec-r-tit">⏳ Subejercicio (2024)</span><b>pendiente</b>'
        '<span>Se calcula con el modificado y el devengado de la Cuenta Pública 2024, que la plataforma aún no coteja. %s</span></div>'
        '</div>') % (
        pct(comp['balance']['pib']['2024']), pct(comp['balance']['pib']['2026e']), pct(comp['balance']['pib']['2027']), chip('oficial'),
        mdp(t['porAclarar'] / 1e6), format(t['auditorias'], ','), mdb['corto'], doc(mdb['url']), asf['cp2024']['pagina'], chip('oficial'),
        mdp(eco['ctada']['total_mdp']), pct(eco['ctada']['pct_pib']), chip('oficial'), chip('pendiente'))

    aportacion = [
        ('🧾', 'Tu estado de cuenta', 'Escribe lo que ganas y ve lo que pagas de ISR, IVA y predial, y a qué rubro del presupuesto llega cada peso.',
         'herramienta-calculadora-ticket.html', None, 'calculadora'),
        ('🌎', 'Tu ticket en negativo', 'Lo que ya te cargaron a tu nombre: tu parte de la deuda, de sus intereses y del daño ambiental.',
         'herramienta-ambiente-ticket.html', None, 'ambiente'),
    ]

    descarga = (
        '<p>El estado de cuenta completo, renglón por renglón, con su periodo, alcance, estado, fuente y página. Se abre en Excel.</p>'
        '<p><a class="ec-descarga" href="%s" download>⬇️ Descargar %s</a></p>'
        '<ul class="ec-lista"><li><b>Periodo:</b> 2024 observado; 2026 aprobado y cierre estimado; 2027 propuesto.</li>'
        '<li><b>Alcance:</b> sector público presupuestario (Gobierno Federal, organismos de control directo y empresas productivas del Estado), salvo donde el renglón dice otra cosa.</li>'
        '<li><b>Fecha de revisión:</b> %s.</li></ul>') % (CSV_ARCHIVO, CSV_ARCHIVO, REVISION)

    secciones = [
        ('aportacion', '👤 Tu aportación', 'Lo que tú pagas y a dónde va. Lo calcula la Calculadora Cívica con lo que ganas.', '', aportacion),
        ('presupuestaria', '📊 Dimensión presupuestaria', 'Lo que entra, lo que se gasta y lo que falta: 2024, 2026 y 2027.', presupuestaria, []),
        ('financiera', '🏦 Dimensión financiera', 'Lo que cuesta la deuda y cuánto se debe.', financiera, []),
        ('social', '🫂 Dimensión social', 'A dónde llegan los programas y qué se sabe de sus resultados.', social, []),
        ('ambiental', '🌱 Dimensión ambiental', 'Lo que se pierde del ambiente y lo que se gasta en protegerlo.', ambiental, []),
        ('renglones', '🧮 Renglones que no se suman', 'El déficit, lo que la ASF dejó por aclarar, el daño ambiental y el subejercicio.', renglones, []),
        ('descarga', '⬇️ Descarga y metodología', 'Periodo, alcance, fuentes y fecha de revisión.', descarga, []),
    ]
    filas_csv = []
    for f in comp.values():
        for k, anio, etapa in COLUMNAS:
            filas_csv.append([f['dimension'], f['concepto'], '% del PIB', anio, etapa, f['pib'][k], 'oficial', CGPE,
                              'p. %d' % (f['pagina_hist'] if k == '2024' else 67), CGPE_URL, REVISION])
            if k in f['mdp']:
                filas_csv.append([f['dimension'], f['concepto'], 'millones de pesos', anio, etapa, f['mdp'][k], 'oficial', CGPE,
                                  'p. 67', CGPE_URL, REVISION])
            else:
                filas_csv.append([f['dimension'], f['concepto'], 'millones de pesos', anio, etapa, '', 'pendiente',
                                  'Pendiente: está en el Tomo II de la Cuenta Pública 2024, que la plataforma aún no coteja', '', 'https://www.cuentapublica.hacienda.gob.mx/es/CP/2024', REVISION])
    for c in cf['cifras']:
        filas_csv.append(['contable 2024 (Gobierno Federal)', c['concepto'], 'millones de pesos', '2024',
                          'aprobado' if c['id'] == 'aprobado' else 'cuenta pública', '' if c['mdp'] is None else c['mdp'],
                          c['estado'], c.get('fuente', c.get('motivo', '')), '', c.get('url', ''), REVISION])
    for m in cf['evaluacion_social_mir']:
        filas_csv.append(['social', m['programa'], 'millones de pesos', '2024', 'devengado',
                          '' if m['devengado_mdp'] is None else m['devengado_mdp'], m['estado_montos'],
                          m.get('fuente_montos', m.get('motivo_montos', '')), '', m.get('url', ''), REVISION])
    filas_csv += [
        ['social', 'Programas sociales prioritarios (total)', 'millones de pesos', '2027', 'propuesto', soc['total'], 'oficial', CGPE, 'p. 33', CGPE_URL, REVISION],
        ['ambiental', 'Costos por agotamiento y degradación ambiental', 'millones de pesos', '2024', 'observado', eco['ctada']['total_mdp'], 'oficial',
         'INEGI, CEEM 2024', '', ceem.get('url', ''), REVISION],
        ['ambiental', 'Gasto en protección ambiental del sector público', 'millones de pesos', '2024', 'observado',
         eco['gasto_proteccion_ambiental']['monto_mdp'], 'oficial', 'INEGI, CEEM 2024', '', ceem.get('url', ''), REVISION],
        ['ambiental', 'Ramo 16 Medio Ambiente', 'millones de pesos', '2026', 'aprobado', round(p16['aprobado2026']['valor'] / 1e6, 1), 'oficial',
         amb['fuentes']['PEF']['corto'], p16['aprobado2026'].get('pagina', ''), amb['fuentes']['PEF']['url'], REVISION],
        ['ambiental', 'Ramo 16 Medio Ambiente', 'millones de pesos', '2027', 'propuesto', round(p16['proyecto2027']['valor'] / 1e6, 1), 'oficial',
         amb['fuentes']['PPEF2027']['corto'], '', amb['fuentes']['PPEF2027']['url'], REVISION],
        ['fiscalización', 'Monto por aclarar ante la ASF', 'millones de pesos', '2024', 'cuenta pública', round(t['porAclarar'] / 1e6, 1), 'oficial',
         mdb['corto'], 'p. %s' % asf['cp2024']['pagina'], mdb['url'], REVISION],
    ]
    return {
        'archivo': ARCHIVO, 'menu': 'Estado de Cuenta Cívico', 'menu_archivo': 'sigue-el-dinero.html',
        'padre': ('sigue-el-dinero.html', 'Números'), 'icono': '🧾', 'titulo': 'Estado de Cuenta Cívico',
        'lema': '2024, 2026 y 2027, en las mismas unidades',
        'entrada': ('Dos vistas de la misma cuenta. <b>Tu aportación</b>: lo que tú pagas y a dónde va. <b>La cuenta pública</b>: lo que '
                    'entra al gobierno, lo que gasta, lo que debe, lo que entrega y lo que se pierde del ambiente, comparando lo que pasó en '
                    '2024 con lo aprobado para 2026 y lo que se propone para 2027. Cada cifra trae su documento.'),
        # Enlace al estado de cuenta de cada administracion (10-10-2026).
        'antes': ('      <a class="apartado-nota" href="radar-estado-de-cuenta.html">🧾 ¿Buscas el de un sexenio? Expide el estado de cuenta '
                  'de cada administración, con su semáforo de salud financiera y sello de verificación</a>'),
        'secciones': [{'id': i, 'titulo': t_, 'texto': x, 'bloque': b, 'tarjetas': tj} for i, t_, x, b, tj in secciones],
    }, filas_csv


def generar(sello):
    pag, filas = construir()
    texto = pagina(pag, sello).replace('\r\n', '\n').replace('\n', '\r\n')
    open(os.path.join(RAIZ, ARCHIVO), 'wb').write(texto.encode('utf-8'))
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\r\n')
    w.writerow(['dimension', 'concepto', 'unidad', 'año', 'etapa', 'valor', 'estado', 'fuente', 'página', 'url', 'fecha_revision'])
    w.writerows(filas)
    open(os.path.join(RAIZ, CSV_ARCHIVO), 'wb').write(('﻿' + buf.getvalue()).encode('utf-8'))
    print('estado de cuenta: %s y %s (%d renglones)' % (ARCHIVO, CSV_ARCHIVO, len(filas)))
    return 0
