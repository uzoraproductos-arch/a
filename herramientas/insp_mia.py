# -*- coding: utf-8 -*-
"""Décima aplicación del Modo Inspector: «Mi Auditavisión», el tablero
(entrega C de docs/PLAN-IMPLEMENTACION.md §4 bis, 05-11-2026; pedido del autor:
«algo como getquin»… «sin retener información privada»).

Junta en una sola vista lo que el lector revisa con las otras aplicaciones:
su lista de proveedores, cruzada con la lista 69-B, y los resúmenes que guardó
desde el Lector de facturas y desde «Revisa tu estado de resultados».

**Todo se guarda solo en el navegador del lector** (localStorage, clave
`av-mia`): no hay cuenta ni servidor. Lo hace funcionar
assets/auditor/js/insp-mia.js; los dos lectores escriben ahí con el mismo
formato (`miaGuardar()` en cada uno). Las alertas por correo cada semana son
la entrega D y necesitan cuentas, hospedaje y aviso de privacidad propio.
"""
import json

import insp_efos
from presupuesto_modulos import chip

ESTILOS = ['insp-efos.css', 'insp-factura.css']
SCRIPTS = ['insp-mia.js']


def construir(base, ref):
    m = insp_efos.meta()
    sit = {k: {'t': (nom if k != 'S' else 'Sentencia favorable'), 'c': cl, 'i': ico}
           for k, nom, cl, ico, _corto, _txt in insp_efos.SITUACIONES}
    datos = {'corte': m['corte'], 'sit': sit}
    return '''
<div class="ef cf" id="mia">
  <script type="application/json" id="miaDatos">%(datos)s</script>

  <section class="ef-hero" aria-labelledby="mia-tit">
    <h2 class="ef-hero-tit" id="mia-tit">Tu tablero de auditoría</h2>
    <p class="ef-hero-txt">Tus proveedores, cruzados con la lista 69-B del SAT %(chip_of)s, y los resúmenes que guardaste desde el Lector de facturas y desde «Revisa tu estado de resultados» %(chip_de)s.</p>
    <p class="cf-privado">🔒 <b>Esto se guarda solo en este navegador.</b> No hay cuenta ni servidor: no vemos tu lista ni tus resúmenes. Si borras los datos del navegador o usas otro equipo, no estarán. De tus facturas no se guarda el XML, solo el resumen.</p>
    <p class="ef-estado" id="miaEstado" role="status"></p>
  </section>

  <section class="ef-sec" aria-labelledby="mia-prov">
    <h2 id="mia-prov">🏢 Mis proveedores</h2>
    <p>Escribe o pega los RFC de las empresas a las que les compras o les pagas (uno por renglón, o separados por comas). Los cruzamos con la lista 69-B con corte al <b>%(corte)s</b>.</p>
    <label class="ef-lbl" for="miaRfc">RFC de tus proveedores</label>
    <textarea id="miaRfc" class="ef-area" rows="3" spellcheck="false" placeholder="AAA010101AAA, BBB010101BBB"></textarea>
    <p class="ef-busca-fila"><button type="button" class="ef-btn" id="miaAgregar">➕ Agregar a mi lista</button></p>
    <div id="miaProv" aria-live="polite"></div>
  </section>

  <section class="ef-sec" aria-labelledby="mia-rev">
    <h2 id="mia-rev">📋 Mis revisiones</h2>
    <p>Los resúmenes que guardaste con «📌 Guardar en Mi Auditavisión» desde el <a href="herramienta-inspector-factura.html">Lector de facturas</a> o desde <a href="herramienta-inspector-resultados.html">Revisa tu estado de resultados</a>.</p>
    <div id="miaRev" aria-live="polite"></div>
  </section>

  <section class="ef-sec" aria-labelledby="mia-sig">
    <h2 id="mia-sig">Lo que viene</h2>
    <ul>
      <li><b>Que te avisemos cada semana</b> si un proveedor tuyo entra a la lista 69-B o cambia de situación. El Vigía 69-B ya revisa la lista cada semana; para avisarte hace falta guardar tu lista con tu permiso, y eso llegará con cuentas y su aviso de privacidad.</li>
      <li>¿Necesitas revisar a muchos proveedores, con sus contratos públicos y lo que dijo la Auditoría Superior? <a href="servicios.html">Pide un servicio</a>.</li>
    </ul>
    <p class="ef-busca-fila"><button type="button" class="ef-btn ef-btn-sec" id="miaBorrar">🗑️ Borrar todo mi tablero</button></p>
  </section>
</div>''' % {
        'datos': json.dumps(datos, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'),
        'corte': m['corte'], 'chip_of': chip('oficial'), 'chip_de': chip('derivado'),
    }
