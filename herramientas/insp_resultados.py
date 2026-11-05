# -*- coding: utf-8 -*-
"""Novena aplicación del Modo Inspector: «Revisa tu estado de resultados»
(pedido del autor, 05-11-2026: «que el usuario pueda subir un estado de
resultados… y nosotros evaluarlo, sin retener información privada», con el
molde de su plataforma Fortuvision: varias dimensiones y horizontes de 3 y 5
años). Es la entrega A de «Mi Auditavisión» (docs/PLAN-IMPLEMENTACION.md §4 bis).

La página la escribe este módulo (apartados.insp_nativa(), clave
'inspresultados') y la hace funcionar assets/auditor/js/insp-resultados.js,
que lee el archivo **en el navegador**: no se sube ni se guarda. Los patrones
con que se reconoce cada renglón salen de herramientas/lector_resultados.py, el
gemelo de Python, para que las dos versiones lean igual.
"""
import html
import json

import lector_resultados as lr
from presupuesto_modulos import chip

ESTILOS = ['insp-efos.css', 'insp-factura.css']
SCRIPTS = ['insp-resultados.js']
EJEMPLO = 'docs/ejemplos/estado-de-resultados-ficticio.csv'
LISR = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LISR.pdf'
PLANTILLA = ('Concepto,2021,2022,2023,2024,2025\r\nVentas netas,,,,,\r\nCosto de ventas,,,,,\r\nUtilidad bruta,,,,,\r\n'
             'Gastos de venta,,,,,\r\nGastos de administración,,,,,\r\nUtilidad de operación,,,,,\r\nGastos financieros,,,,,\r\n'
             'Productos financieros,,,,,\r\nUtilidad antes de impuestos,,,,,\r\nISR,,,,,\r\nUtilidad neta,,,,,\r\n')

DIMENSIONES = [
    ('🧮', 'Cuadre', 'Rehacemos las restas: ¿la utilidad bruta, la de operación, la de antes de impuestos y la neta dan lo que dice el estado?'),
    ('🧱', 'Estructura', 'Análisis vertical: de cada $100 vendidos, cuánto se va en costo, gastos, intereses e ISR.'),
    ('📈', 'Rentabilidad', 'Margen bruto, de operación y neto, año por año.'),
    ('⏳', 'Tendencia', 'Análisis horizontal: cuánto cambió cada renglón y cuánto crecieron las ventas al año en 3 y 5 años.'),
    ('🏛️', 'Impuestos', 'La tasa efectiva del ISR frente a la tasa de 30 % de las personas morales (LISR, art. 9).'),
    ('🏦', 'Deuda', 'Cuántas veces la utilidad de operación paga los gastos financieros.'),
]


def bot():
    return {'dimensiones': [d[1] for d in DIMENSIONES]}


def _ext(url, texto):
    return '<a href="%s" target="_blank" rel="noopener">%s ↗</a>' % (html.escape(url), texto)


def construir(base, ref):
    datos = {'conceptos': [[c, n, rx] for c, n, rx in lr.CONCEPTOS], 'tasa': lr.TASA_ISR, 'ejemplo': EJEMPLO,
             'plantilla': PLANTILLA, 'chipDe': chip('derivado')}
    dims = ''.join('<li class="cf-paso"><span class="cf-paso-ico" aria-hidden="true">%s</span><b>%s</b><p>%s</p></li>' % d for d in DIMENSIONES)
    return '''
<div class="ef cf" id="er">
  <script type="application/json" id="erDatos">%(datos)s</script>

  <section class="ef-hero" aria-labelledby="er-tit">
    <h2 class="ef-hero-tit" id="er-tit">¿Qué dice tu estado de resultados?</h2>
    <p class="ef-hero-txt">Sube el estado de resultados de tu empresa (o el de un cliente) con uno a seis años, y lo revisamos en seis dimensiones: cuadre, estructura, rentabilidad, tendencia a 3 y 5 años, impuestos y deuda. Todo lo que sale es %(chip_de)s: una cuenta con tus cifras, con su operación a la vista.</p>
    <p class="cf-privado">🔒 <b>Tu estado de resultados no sale de tu equipo.</b> Se lee aquí, en tu navegador: no lo subimos a ningún servidor ni lo guardamos. No tenemos certificación de seguridad: por eso no lo subimos. Al cerrar la página, se borra.</p>

    <div class="cf-entrada">
      <label class="ef-lbl" for="erArchivo">Tu estado de resultados en CSV</label>
      <div class="cf-suelta" id="erSuelta">
        <input type="file" id="erArchivo" class="cf-archivo" accept=".csv,.txt,.tsv,text/csv,text/plain">
        <p>o arrástralo aquí</p>
      </div>
      <details class="cf-pegar">
        <summary>¿Lo tienes en Excel? Copia las celdas y pégalas</summary>
        <label class="ef-lbl" for="erTexto">Las celdas, con los conceptos en la primera columna y un año por columna</label>
        <textarea id="erTexto" class="ef-area" rows="6" spellcheck="false" placeholder="Concepto	2024	2025&#10;Ventas netas	1,000,000	1,200,000"></textarea>
        <button type="button" class="ef-btn" id="erLeerTexto">Revisar lo que pegué</button>
      </details>
      <p class="ef-busca-fila">
        <button type="button" class="ef-btn ef-btn-sec" id="erEjemplo">🧪 Probar con una empresa ficticia</button>
        <button type="button" class="ef-btn ef-btn-sec" id="erPlantilla">⬇️ Descargar la plantilla (CSV)</button>
      </p>
    </div>

    <p class="ef-estado" id="erEstado" role="status">Elige tu archivo, pega tus celdas o prueba con el ejemplo.</p>
    <noscript><p class="ef-estado">Para revisarlo aquí hace falta JavaScript. Si sabes Python, la misma revisión está en herramientas/lector_resultados.py del repositorio.</p></noscript>
    <div class="cf-res" id="erRes" aria-live="polite"></div>
    <div class="ef-busca-fila" id="erAcciones" hidden>
      <button type="button" class="ef-btn ef-btn-sec" id="erLimpiar">🗑️ Borrar todo</button>
    </div>
  </section>

  <section class="ef-sec" aria-labelledby="er-dims">
    <h2 id="er-dims">Las seis dimensiones</h2>
    <ol class="cf-pasos">%(dims)s</ol>
  </section>

  <section class="ef-sec" aria-labelledby="er-como">
    <h2 id="er-como">Cómo debe venir tu archivo</h2>
    <ul>
      <li>La primera fila dice los años: <code>Concepto, 2023, 2024, 2025</code> (hasta seis).</li>
      <li>Cada renglón empieza con su concepto: ventas o ingresos, costo de ventas, utilidad bruta, gastos de venta y de administración (se suman), utilidad de operación, gastos y productos financieros, utilidad antes de impuestos, ISR y utilidad neta.</li>
      <li>Las cifras pueden traer <code>$</code> y comas; una pérdida, con signo menos o entre paréntesis.</li>
      <li>Si un subtotal no viene, lo calculamos y lo decimos. Un renglón que no reconocemos se enlista y no entra a las cuentas.</li>
    </ul>
  </section>

  <section class="ef-sec" aria-labelledby="er-no">
    <h2 id="er-no">Lo que esta revisión no dice</h2>
    <ul>
      <li><b>No es una auditoría ni un dictamen.</b> Revisamos las cifras que tú traes; no las cotejamos contra la contabilidad, los bancos ni el SAT.</li>
      <li><b>Una señal no es una irregularidad.</b> Una tasa de ISR baja puede deberse a pérdidas de años anteriores (LISR, art. 57) o a diferencias entre lo contable y lo fiscal; un margen que cae, a una mala racha. Es una pregunta que conviene hacer.</li>
      <li>La tasa de 30 %% es la de las personas morales (%(lisr)s, art. 9). Una persona física o un régimen especial tributa distinto.</li>
      <li>No compara contra otras empresas del sector: para eso hace falta información que nadie publica completa.</li>
      <li>¿Quieres que lo revisemos a fondo, con sus documentos? <a href="servicios.html">Pide un servicio</a>.</li>
    </ul>
  </section>
</div>''' % {
        'datos': json.dumps(datos, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'),
        'chip_de': chip('derivado'), 'dims': dims, 'lisr': _ext(LISR, 'Ley del ISR'),
    }
