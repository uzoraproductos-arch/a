#!/usr/bin/env python3
"""La base al día: el registro de las fuentes de la base de datos.

Pedido del autor, 18-11-2026: «que nuestra base de datos quede bien
integrada… únicamente para alimentarla o actualizarla con las novedades», porque
lo que publican las dependencias no cambia cada día. Aquí vive, en un solo
lugar, cada fuente de la base:

- qué es y quién la publica;
- cada cuándo la publica y en qué fecha conviene empezar a buscar la siguiente
  (`revisar`: es una fecha nuestra para ir a ver, nunca una fecha de la ley
  salvo que `publica` cite el artículo);
- cómo entra: 🤖 «sola» (el flujo «Base al día» la baja, la cuadra y la publica
  cada semana), 🔔 «aviso» (un vigía detecta la novedad y una persona la coteja)
  o ✋ «a mano» (el archivo se baja con un botón o de un PDF, y se corre su script);
- qué script la integra y en qué archivo queda.

Este script no cambia ninguna cifra. Hace dos cosas:

    python3 herramientas/fuentes.py            # prueba el registro (corre en revision.py)
    python3 herramientas/fuentes.py --agenda   # escribe docs/base/agenda.json y el reporte

`generar(sello)` (lo llama apartados.py) escribe la página base-al-dia.html. La
página no depende del día en que se genera (el flujo «Expedientes al día» la
regenera cada mañana y no debe publicar ruido): el «ya toca» solo va en la
agenda, que escribe el flujo semanal.

Al integrar una fuente a mano: corre su script, cambia aquí su `corte` (si no se
lee solo del archivo) y su `revisar` por la fecha del periodo que sigue.
"""
import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVO = 'base-al-dia.html'
AGENDA = os.path.join(RAIZ, 'docs', 'base', 'agenda.json')

MODOS = {
    'sola': ('🤖', 'Se actualiza sola', 'El flujo «Base al día» la baja cada miércoles, rehace su cuadre y la publica si cambió. '
             'Si el archivo no cuadra o cambió de formato, se detiene y no publica nada.'),
    'aviso': ('🔔', 'Avisa y se coteja', 'Un vigía detecta la novedad cada semana; una persona la coteja contra su documento y la integra.'),
    'mano': ('✋', 'Se integra a mano', 'La dependencia la publica en un PDF, un Excel o detrás de un botón: se baja, se corre su script '
             '(que guarda la huella y se detiene si no cuadra) y se publica.'),
}
CADA = {'semanal': 7, 'mensual': 31, 'trimestral': 92, 'semestral': 183, 'anual': 366, 'bienal': 731}


def _lee(ruta, patron, tope=6000):
    """Un dato del encabezado de un archivo de la base (su corte o su fecha de descarga)."""
    try:
        with open(os.path.join(RAIZ, ruta), encoding='utf-8') as f:
            t = f.read(tope)
    except OSError:
        return ''
    m = re.search(patron, t)
    return m.group(1) if m else ''


def _fecha(iso):
    """2026-11-18 → 18-11-2026 (como se escriben las fechas en la plataforma)."""
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})$', iso or '')
    return '%s-%s-%s' % (m.group(3), m.group(2), m.group(1)) if m else (iso or '')


# Cada fuente: id, que, quien, cada, publica, modo, script, datos, corte (texto o función),
# revisar (fecha AAAA-MM-DD para ir a buscar la siguiente), url (dónde la publica).
FUENTES = [
    # ── Se actualizan solas ────────────────────────────────────────────────
    {'id': 'sat-69b', 'que': 'Lista 69-B del SAT (operaciones presuntamente inexistentes)', 'quien': 'SAT',
     'cada': 'mensual', 'publica': 'El SAT la renueva en sus datos abiertos cuando publica oficios nuevos en el DOF (CFF, art. 69-B).',
     'modo': 'sola', 'script': 'actualizar_69b.py', 'datos': 'assets/auditor/data/sat-69b.js',
     'corte': lambda: 'al ' + _lee('assets/auditor/data/sat-69b.js', r'"corte": "([^"]+)"'),
     'url': 'https://www.gob.mx/sat/acciones-y-programas/notificacion-a-contribuyentes-con-operaciones-presuntamente-inexistentes-y-listados-definitivos-333336'},
    {'id': 'listas-sat', 'que': 'Listas del SAT de los arts. 69, 17-H Bis y 69-B Bis del CFF', 'quien': 'SAT',
     'cada': 'mensual', 'publica': 'El SAT las renueva en su portal de datos abiertos.',
     'modo': 'sola', 'script': 'anclar_listas.py', 'datos': 'assets/auditor/data/padron/',
     'corte': lambda: 'bajadas el ' + _fecha(_lee('docs/listas/listas.json', r'"descarga": "([^"]+)"')),
     'url': 'http://omawww.sat.gob.mx/cifras_sat/Paginas/DatosAbiertos/contribuyentes_publicados.html'},
    {'id': 'ofac-onu', 'que': 'Sanciones internacionales: lista SDN de la OFAC y lista consolidada de la ONU',
     'quien': 'Departamento del Tesoro de EE. UU. y Consejo de Seguridad de la ONU', 'cada': 'semanal',
     'publica': 'Las dos se actualizan varias veces al mes.',
     'modo': 'sola', 'script': 'anclar_listas.py', 'datos': 'assets/auditor/data/sanciones-int.js',
     'corte': lambda: 'bajadas el ' + _fecha(_lee('docs/listas/listas.json', r'"descarga": "([^"]+)"')),
     'url': 'https://sanctionslist.ofac.treas.gov/Home/SdnList'},
    {'id': 'sancionados', 'que': 'Directorio de Proveedores y Contratistas Sancionados',
     'quien': 'Secretaría Anticorrupción y Buen Gobierno', 'cada': 'semanal',
     'publica': 'Se actualiza con cada sanción que queda firme.',
     'modo': 'sola', 'script': 'anclar_sancionados.py', 'datos': 'assets/auditor/data/sancionados.js',
     'corte': lambda: 'consultado el ' + _fecha(_lee('assets/auditor/data/sancionados.js', r'"corte":"([^"]+)"')),
     'url': 'https://directoriosancionados.buengobierno.gob.mx/'},

    {'id': 'padron-sat', 'que': 'Padrón de contribuyentes del SAT (por tipo, situación, régimen, entidad y sector)', 'quien': 'SAT',
     'cada': 'mensual', 'publica': 'El SAT actualiza sus hojas de datos abiertos del padrón cada mes, con cifras preliminares.',
     'modo': 'sola', 'script': 'anclar_padron_sat.py', 'datos': 'docs/sat/padron-sat.json',
     'corte': lambda: _lee('docs/sat/padron-sat.json', r'"texto":"([^"]+)"'),
     'url': 'https://www.sat.gob.mx/minisitio/DatosAbiertos/padron.html'},
    {'id': 'udi', 'que': 'Valor de la UDI (para la exención de la casa habitación)', 'quien': 'Banco de México',
     'cada': 'semanal', 'publica': 'Banxico publica la UDI de cada día por adelantado (cuadro CP150); se consulta cada semana.',
     'modo': 'sola', 'script': 'anclar_udi.py', 'datos': 'docs/sat/udi.json',
     'corte': lambda: 'al ' + _fecha(_lee('docs/sat/udi.json', r'"fecha": "([^"]+)"')),
     'url': 'https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?sector=8&accion=consultarCuadro&idCuadro=CP150&locale=es'},

    # ── Avisan: un vigía las detecta y se cotejan ─────────────────────────
    {'id': 'leyes', 'que': 'Leyes y reglamentos que cita la plataforma', 'quien': 'DOF y Cámara de Diputados',
     'cada': 'semanal', 'publica': 'Cada reforma sale en el DOF y la Cámara actualiza su índice de leyes vigentes.',
     'modo': 'aviso', 'script': 'vigia_legislativo.py', 'datos': 'docs/legislativo/bandeja.json',
     'corte': 'se revisa cada día hábil',
     'url': 'https://www.diputados.gob.mx/LeyesBiblio/index.htm'},
    {'id': 'asf-semestral', 'que': 'Informe semestral de la ASF sobre observaciones y acciones', 'quien': 'ASF',
     'cada': 'semestral', 'publica': 'A más tardar el 1 de mayo y el 1 de noviembre (LFRCF, art. 38).',
     'modo': 'aviso', 'script': 'informe_semestral.py (vigía en semanal.py)', 'datos': 'herramientas/informe_semestral.py',
     'corte': 'al 30 de septiembre de 2026', 'revisar': '2027-05-01',
     'url': 'https://www.asf.gob.mx/Section/52_Informes_especiales'},
    {'id': 'fuentes-web', 'que': 'Documentos oficiales que respaldan las cifras (la bóveda de evidencias)',
     'quien': 'Cada dependencia', 'cada': 'semanal',
     'publica': 'Se revisa que cada documento siga abriendo y que su huella no haya cambiado.',
     'modo': 'aviso', 'script': 'boveda.py', 'datos': 'docs/boveda/evidencias.json',
     'corte': 'cada miércoles', 'url': 'https://www.dof.gob.mx/'},

    # ── A mano ────────────────────────────────────────────────────────────
    {'id': 'donatarias', 'que': 'Donatarias autorizadas (estadísticas del SAT con base en el Anexo 14 de la RMF)', 'quien': 'SAT',
     'cada': 'anual', 'publica': 'El SAT publica el Anexo 14 en el DOF en enero y sus «Estadísticos Donatarias Autorizadas» en su micrositio; el PDF se lee con pdftotext.',
     'modo': 'mano', 'script': 'anclar_donatarias.py', 'datos': 'docs/sat/donatarias.json',
     'corte': lambda: 'ejercicio ' + _lee('docs/sat/donatarias.json', r'"anio": (\d+)'), 'revisar': '2027-01-20',
     'url': 'https://www.sat.gob.mx/minisitio/DonatariasAutorizadas/index.html'},
    {'id': 'asociaciones-religiosas', 'que': 'Asociaciones religiosas con registro constitutivo', 'quien': 'Secretaría de Gobernación',
     'cada': 'mensual', 'publica': 'Gobernación publica su numeralia en el portal de Asuntos Religiosos. Al 19-11-2026 no respondió a la descarga: sigue pendiente de integrar.',
     'modo': 'mano', 'script': 'pendiente (padron_sat.py la anota en el Registro de pendientes)', 'datos': 'pendientes.html',
     'corte': 'sin integrar', 'revisar': '2026-12-01',
     'url': 'https://asociacionesreligiosas.segob.gob.mx/es/AsuntosReligiosos/Numeralia'},
    {'id': 'comprasmx', 'que': 'Contratos públicos de ComprasMX', 'quien': 'Secretaría Anticorrupción y Buen Gobierno',
     'cada': 'mensual', 'publica': 'Datos abiertos que se descargan con un botón (el servidor no los sirve a una descarga directa).',
     'modo': 'mano', 'script': 'actualizar_comprasmx.py', 'datos': 'assets/auditor/data/comprasmx/',
     'corte': 'contratos de 2025 y 2026', 'revisar': '2026-12-01',
     'url': 'https://comprasmx.buengobierno.gob.mx/datos-abiertos'},
    {'id': 'rpu', 'que': 'Registro Público Único de deuda de estados y municipios', 'quien': 'SHCP',
     'cada': 'trimestral', 'publica': 'Hacienda publica el registro cada día y los saldos se reportan cada trimestre. Su servidor manda incompleta la cadena de certificados, así que se baja a mano. El archivo del 18-11-2026 es idéntico (misma huella) al integrado: los saldos de septiembre aún no salen.',
     'modo': 'mano', 'script': 'anclar_rpu.py', 'datos': 'assets/auditor/data/deuda-rpu.js',
     'corte': lambda: 'al ' + _fecha(_lee('assets/auditor/data/deuda-rpu.js', r'"corte":"([^"]+)"')), 'revisar': '2026-12-01',
     'url': 'https://www.disciplinafinanciera.hacienda.gob.mx/'},
    {'id': 'shf-vivienda', 'que': 'Índice SHF de Precios de la Vivienda: precios de avalúo por entidad y variación anual por entidad y municipio', 'quien': 'Sociedad Hipotecaria Federal',
     'cada': 'trimestral', 'publica': 'La SHF publica cada trimestre su informe (PDF) y sus datos abiertos (Excel) en su página de documentos, unas seis semanas después del cierre.',
     'modo': 'mano', 'script': 'anclar_shf_vivienda.py', 'datos': 'docs/vivienda/shf-precios-vivienda.json',
     'corte': lambda: _lee('docs/vivienda/shf-precios-vivienda.json', r'"corte": "([^"]+)"', 3000), 'revisar': '2027-02-15',
     'url': 'https://www.gob.mx/shf/documentos/indice-shf-de-precios-de-la-vivienda-en-mexico-2025-a-2026'},
    {'id': 'sesnsp', 'que': 'Carpetas de investigación por fraude, por estado', 'quien': 'SESNSP',
     'cada': 'mensual', 'publica': 'El Secretariado publica sus datos abiertos de incidencia cada mes, alrededor del día 20.',
     'modo': 'mano', 'script': 'anclar_sesnsp_fraude.py', 'datos': 'docs/seguridad/sesnsp-fraude-estatal.json',
     'corte': lambda: 'corte ' + _lee('docs/seguridad/sesnsp-fraude-estatal.json', r'"corte": "([^"]+)"', 3000), 'revisar': '2026-11-20',
     'url': 'https://www.gob.mx/sesnsp/acciones-y-programas/datos-abiertos-de-incidencia-delictiva'},
    {'id': 'pef', 'que': 'Presupuesto de Egresos de la Federación', 'quien': 'Cámara de Diputados (DOF)',
     'cada': 'anual', 'publica': 'La Cámara lo aprueba a más tardar el 15 de noviembre (Constitución, art. 74, fr. IV) y sale en el DOF. Al 18-11-2026 el de 2027 aún no sale en el DOF ni en el índice de la Cámara.',
     'modo': 'mano', 'script': 'módulos de la Enciclopedia (audit-database.js)', 'datos': 'assets/auditor/js/audit-database.js',
     'corte': 'PEF 2026', 'revisar': '2026-11-25', 'url': 'https://www.dof.gob.mx/'},
    {'id': 'cuenta-publica', 'que': 'Cuenta Pública', 'quien': 'SHCP',
     'cada': 'anual', 'publica': 'Se entrega a la Cámara a más tardar el 30 de abril del año siguiente (Constitución, art. 74, fr. VI).',
     'modo': 'mano', 'script': 'integrar_cuenta_publica.py', 'datos': 'assets/auditor/js/audit-database.js',
     'corte': 'Cuenta Pública 2024', 'revisar': '2027-04-30', 'url': 'https://www.cuentapublica.hacienda.gob.mx/'},
    {'id': 'asf-entregas', 'que': 'Informe individual y general de la Cuenta Pública', 'quien': 'ASF',
     'cada': 'anual', 'publica': 'Tres entregas: último día hábil de junio, de octubre y el 20 de febrero (LFRCF, art. 35).',
     'modo': 'mano', 'script': 'integrar_asf_estados.py y módulos de auditoría', 'datos': 'assets/auditor/js/audit-database.js',
     'corte': 'Cuenta Pública 2024, segunda entrega', 'revisar': '2027-02-20', 'url': 'https://www.asf.gob.mx/'},
    {'id': 'leyes-ingresos-predial', 'que': 'Tablas del impuesto predial de las leyes de ingresos municipales (Zapopan, Guadalajara, Tlaquepaque, Tonalá y Tlajomulco)', 'quien': 'Congreso del Estado de Jalisco (Periódico Oficial «El Estado de Jalisco»)',
     'cada': 'anual', 'publica': 'Cada municipio aprueba su ley de ingresos con el Congreso del Estado; rige del 1 de enero. Se cambian los renglones de MUNICIPIOS con su huella nueva.',
     'modo': 'mano', 'script': 'cc_predial.py', 'datos': 'herramientas/cc_predial.py',
     'corte': 'leyes de ingresos 2026', 'revisar': '2027-01-31', 'url': 'https://congresoweb.congresojal.gob.mx/BibliotecaVirtual/busquedasleyes/Listado%272.cfm'},
    {'id': 'uma', 'que': 'Unidad de Medida y Actualización (UMA)', 'quien': 'INEGI (DOF)',
     'cada': 'anual', 'publica': 'Dentro de los primeros diez días de enero (Ley para Determinar el Valor de la UMA, art. 5).',
     'modo': 'mano', 'script': 'calculadora_civica de audit-database.js', 'datos': 'assets/auditor/js/audit-database.js',
     'corte': 'UMA 2026', 'revisar': '2027-01-10', 'url': 'https://www.inegi.org.mx/temas/uma/'},
    {'id': 'salario-minimo', 'que': 'Salario mínimo general', 'quien': 'CONASAMI (DOF)',
     'cada': 'anual', 'publica': 'La resolución sale en el DOF en diciembre y rige desde el 1 de enero.',
     'modo': 'mano', 'script': 'calculadora_civica de audit-database.js', 'datos': 'assets/auditor/js/audit-database.js',
     'corte': 'salario mínimo 2026', 'revisar': '2026-12-15', 'url': 'https://www.gob.mx/conasami'},
    {'id': 'tarifa-isr', 'que': 'Tarifa del ISR de sueldos (art. 96), subsidio para el empleo y tabla del RESICO', 'quien': 'SAT (Anexo 8 de la RMF)',
     'cada': 'anual', 'publica': ('Con la Resolución Miscelánea Fiscal del año. Desde el 1 de enero de 2027 el tope del RESICO sube de 3.5 a 5 millones de '
                                 'pesos (reforma a la Ley del ISR, DOF 13-11-2026, arts. 113-E y 113-F; las tasas no cambian): en enero se cambia '
                                 'tope_anual y el último renglón de resico.'),
     'modo': 'mano', 'script': 'calculadora_civica de audit-database.js', 'datos': 'assets/auditor/js/audit-database.js',
     'corte': 'Anexo 8 de la RMF 2026', 'revisar': '2027-01-01', 'url': 'https://www.sat.gob.mx/normatividad/58917/resolucion-miscelanea-fiscal-(rmf)'},
    {'id': 'cesantia', 'que': 'Cuota del patrón por cesantía y vejez (IMSS)', 'quien': 'Decreto de reforma a la LSS (DOF 16-12-2020)',
     'cada': 'anual', 'publica': 'Sube cada 1 de enero hasta 2030, según la tabla del Segundo transitorio.',
     'modo': 'mano', 'script': 'cesantia_2026 de audit-database.js', 'datos': 'assets/auditor/js/audit-database.js',
     'corte': 'tabla de 2026', 'revisar': '2027-01-01', 'url': 'https://www.diputados.gob.mx/LeyesBiblio/ref/lss.htm'},
    {'id': 'efipem', 'que': 'Finanzas públicas de estados y municipios (EFIPEM)', 'quien': 'INEGI',
     'cada': 'anual', 'publica': 'El INEGI publica las cifras definitivas de cada ejercicio el año siguiente.',
     'modo': 'mano', 'script': 'anclar_egresos_entidades.py, anclar_ingresos_entidades.py, anclar_*_municipios.py',
     'datos': 'assets/auditor/js/municipios-efipem.js', 'corte': 'ejercicio 2024, cifras definitivas', 'revisar': '2026-12-01',
     'url': 'https://www.inegi.org.mx/programas/finanzas/'},
    {'id': 'censos-gobierno', 'que': 'Censos de gobierno estatal, municipal, legislativo y judicial', 'quien': 'INEGI',
     'cada': 'anual', 'publica': 'Un censo por año para cada orden y poder de gobierno.',
     'modo': 'mano', 'script': 'administracion_publica.py, gestion_judicial.py, asistente_legislativo.py',
     'datos': 'herramientas/administracion_publica.py', 'corte': 'censos 2025', 'revisar': '2027-08-01',
     'url': 'https://www.inegi.org.mx/temas/gobierno/'},
    {'id': 'envipe', 'que': 'Encuesta de victimización (ENVIPE), por estado', 'quien': 'INEGI',
     'cada': 'anual', 'publica': 'Sale cada septiembre, con datos del año anterior.',
     'modo': 'mano', 'script': 'anclar_envipe_estados.py', 'datos': 'docs/seguridad/envipe-2026-entidades.json',
     'corte': 'ENVIPE 2026 (datos de 2025)', 'revisar': '2027-09-15', 'url': 'https://www.inegi.org.mx/programas/envipe/'},
    {'id': 'pobreza', 'que': 'Pobreza multidimensional por estado', 'quien': 'INEGI',
     'cada': 'bienal', 'publica': 'Cada dos años, con la ENIGH.',
     'modo': 'mano', 'script': 'anclar_pobreza_estados.py', 'datos': 'docs/social/pobreza-entidades-2024.json',
     'corte': 'pobreza 2024', 'revisar': '2027-08-01', 'url': 'https://www.inegi.org.mx/temas/pobreza/'},
    {'id': 'salud', 'que': 'IMSS e ISSSTE por estado y egresos del IMSS-Bienestar', 'quien': 'IMSS y Secretaría de Salud (DGIS)',
     'cada': 'anual', 'publica': 'La Memoria Estadística del IMSS y los cubos de la DGIS, una vez al año.',
     'modo': 'mano', 'script': 'anclar_salud_estados.py, anclar_egresos_bienestar.py',
     'datos': 'docs/salud/', 'corte': 'Memoria Estadística 2025 y egresos 2025', 'revisar': '2027-07-01',
     'url': 'https://www.imss.gob.mx/conoce-al-imss/memoria-estadistica-2025'},
    {'id': 'marco-geo', 'que': 'Límites de los municipios (Marco Geoestadístico)', 'quien': 'INEGI',
     'cada': 'anual', 'publica': 'Una edición por año.',
     'modo': 'mano', 'script': 'integrar_mg_municipios.py', 'datos': 'docs/geo/',
     'corte': 'Marco Geoestadístico 2024', 'revisar': '2026-12-15',
     'url': 'https://www.inegi.org.mx/temas/mg/'},
]


def corte(f):
    c = f.get('corte', '')
    return c() if callable(c) else c


def probar():
    """Revisa el registro: campos completos, modos y cadencias conocidas, scripts y archivos que existen.
    Corre en revision.py: una fuente mal anotada detiene la revisión."""
    errores, vistos = [], set()
    for f in FUENTES:
        for k in ('id', 'que', 'quien', 'cada', 'publica', 'modo', 'script', 'datos', 'corte', 'url'):
            if not f.get(k):
                errores.append('%s: falta %s' % (f.get('id'), k))
        if f['id'] in vistos:
            errores.append('%s: id repetido' % f['id'])
        vistos.add(f['id'])
        if f['modo'] not in MODOS:
            errores.append('%s: modo desconocido %r' % (f['id'], f['modo']))
        if f['cada'] not in CADA:
            errores.append('%s: cadencia desconocida %r' % (f['id'], f['cada']))
        if f['modo'] == 'mano' and not re.match(r'\d{4}-\d{2}-\d{2}$', f.get('revisar', '')):
            errores.append('%s: una fuente a mano necesita la fecha `revisar` (AAAA-MM-DD)' % f['id'])
        if not os.path.exists(os.path.join(RAIZ, f['datos'])):
            errores.append('%s: no existe %s' % (f['id'], f['datos']))
        s = f['script'].split()[0].rstrip(',')
        if s.endswith('.py') and '*' not in s and not os.path.exists(os.path.join(RAIZ, 'herramientas', s)):
            errores.append('%s: no existe herramientas/%s' % (f['id'], s))
        if not corte(f).strip() or corte(f).strip() in ('al', 'bajadas el', 'consultado el', 'revisado el', 'corte'):
            errores.append('%s: no se pudo leer su corte' % f['id'])
    return errores


def agenda(hoy=None):
    """Qué toca revisar hoy. Una fuente a mano «ya toca» desde su fecha `revisar`; las que se actualizan solas
    o avisan se revisan cada semana en el flujo. Solo la escribe el flujo «Base al día» (depende del día)."""
    hoy = hoy or datetime.date.today()
    filas = []
    for f in FUENTES:
        r = f.get('revisar')
        toca = bool(r) and datetime.date.fromisoformat(r) <= hoy
        filas.append({'id': f['id'], 'que': f['que'], 'quien': f['quien'], 'modo': f['modo'], 'cada': f['cada'],
                      'corte': corte(f), 'revisar': r or '', 'toca': toca, 'script': f['script'], 'url': f['url']})
    return {'que_es': 'Lo que toca revisar de la base de datos. La escribe herramientas/fuentes.py --agenda en el flujo «Base al día».',
            'revisado': hoy.isoformat(), 'toca': [x['id'] for x in filas if x['toca']], 'fuentes': filas}


def reporte(a):
    t = ['## La base al día (%s)' % _fecha(a['revisado']), '']
    toca = [x for x in a['fuentes'] if x['toca']]
    if toca:
        t.append('**Ya toca revisar %d fuente%s a mano:**' % (len(toca), '' if len(toca) == 1 else 's'))
        t.append('')
        for x in toca:
            t.append('- %s (%s): tenemos %s. Se buscaba desde el %s. Script: `%s`. [Dónde se publica](%s)'
                     % (x['que'], x['quien'], x['corte'], _fecha(x['revisar']), x['script'], x['url']))
    else:
        t.append('Ninguna fuente a mano espera revisión.')
    t.append('')
    return '\n'.join(t)


def construir():
    from apartados import pagina  # noqa: F401  (se importa aquí para que --agenda corra sin generar páginas)
    grupos = []
    for modo, (ico, nombre, expl) in MODOS.items():
        fs = [f for f in FUENTES if f['modo'] == modo]
        tarjetas = []
        for f in fs:
            tarjetas.append(
                '<article class="pe-item" id="fuente-%s">\n'
                '            <h3 class="pe-que">%s %s</h3>\n'
                '            <p class="pe-porque"><b>Tenemos:</b> %s · <b>Cada cuándo:</b> %s</p>\n'
                '            <p class="pe-quien"><b>🏛️ La publica:</b> %s. %s</p>\n'
                '            <p class="pe-donde"><a href="%s" target="_blank" rel="noopener">🔗 Dónde se publica ↗</a></p>\n'
                '          </article>' % (f['id'], ico, f['que'], corte(f), f['cada'], f['quien'], f['publica'], f['url']))
        grupos.append({'id': 'modo-' + modo, 'titulo': '%s %s' % (ico, nombre), 'texto': expl, 'tarjetas': [],
                       'bloque': '<div class="pe-lista">\n          ' + '\n          '.join(tarjetas) + '\n        </div>'})
    n = {m: sum(1 for f in FUENTES if f['modo'] == m) for m in MODOS}
    cab = ('<div class="pe-resumen">\n'
           '          <div><b>%d</b><span>fuentes de la base</span></div>\n'
           '          <div class="pe-r-d"><b>%d</b><span>🤖 se actualizan solas cada semana</span></div>\n'
           '          <div class="pe-r-p"><b>%d</b><span>🔔 avisan y se cotejan</span></div>\n'
           '          <div class="pe-r-h"><b>%d</b><span>✋ se integran a mano</span></div>\n'
           '        </div>\n'
           '        <p class="pe-regla">Las dependencias no publican cada día: cada fuente tiene su calendario. La base no se rehace a diario; '
           'se alimenta con cada novedad, y cada novedad pasa por el mismo camino: su huella, su cuadre y su chip. Lo que una dependencia '
           'no publica queda en el <a href="pendientes.html">Registro de pendientes</a>.</p>') % (
        len(FUENTES), n['sola'], n['aviso'], n['mano'])
    secciones = [{'id': 'resumen', 'titulo': 'La base en números', 'texto': '', 'sin_cab': True, 'bloque': cab, 'tarjetas': []}] + grupos
    return {
        'archivo': ARCHIVO, 'menu': 'La base al día', 'menu_archivo': 'indice.html',
        'padre': ('pilares.html#base', 'Nuestros pilares'), 'icono': '🔄', 'titulo': 'La base al día',
        'lema': 'Cada fuente, su calendario y cómo se actualiza',
        'entrada': ('De dónde sale cada dato de la base de datos, quién lo publica, cada cuándo y cómo entra a la plataforma: '
                    'lo que se actualiza solo cada semana, lo que un vigía detecta y se coteja, y lo que se integra a mano. '
                    'Así sabes de qué fecha es cada cifra y cuándo esperar la siguiente.'),
        'secciones': secciones,
    }


def generar(sello):
    from apartados import pagina
    errores = probar()
    if errores:
        print('fuentes: el registro tiene errores:\n  ' + '\n  '.join(errores))
        return 1
    texto = pagina(construir(), sello).replace('\r\n', '\n').replace('\n', '\r\n')
    open(os.path.join(RAIZ, ARCHIVO), 'wb').write(texto.encode('utf-8'))
    print('la base al día: %s con %d fuentes' % (ARCHIVO, len(FUENTES)))
    return 0


def main():
    if '--agenda' in sys.argv:
        a = agenda()
        os.makedirs(os.path.dirname(AGENDA), exist_ok=True)
        previo = None
        if os.path.exists(AGENDA):
            with open(AGENDA, encoding='utf-8') as f:
                previo = json.load(f)
        # Solo se reescribe si cambió algo más que la fecha: sin ruido en las semanas quietas.
        if not previo or {k: v for k, v in previo.items() if k != 'revisado'} != {k: v for k, v in a.items() if k != 'revisado'}:
            with open(AGENDA, 'w', encoding='utf-8', newline='\n') as f:
                json.dump(a, f, ensure_ascii=False, indent=1)
                f.write('\n')
        print(reporte(a))
        return 0
    errores = probar()
    if errores:
        print('fuentes: el registro tiene errores:\n  ' + '\n  '.join(errores))
        return 1
    print('fuentes: %d fuentes en el registro, todas con su calendario, su script y su archivo' % len(FUENTES))
    return 0


if __name__ == '__main__':
    sys.exit(main())
