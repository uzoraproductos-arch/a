# Contexto del proyecto — Auditavisión

> Documento de traspaso. Está escrito para que cualquier persona, o cualquier
> asistente de IA, pueda retomar el proyecto sin haber visto las conversaciones
> anteriores. Si trabajas en esto, léelo antes de tocar código.

## Regla de oro al cambiar de plataforma

**Este repositorio es la única fuente de verdad.** No existe una "copia buena"
en ninguna otra parte: ni en un chat, ni en una carpeta local, ni en el
historial de otra IA.

### La rama de trabajo no es `main`

**Todo el proyecto vive en `claude/funny-turing-imtm54`.** `main` se quedó
atrás y no tiene la calculadora cívica, ni el padrón municipal, ni las 32
entidades bajo el mapa, ni el Paquete Económico 2027 leído contra sus textos
legales. **Clonar `main` es empezar sin el trabajo hecho.**

```bash
git clone --branch claude/funny-turing-imtm54 \
  https://github.com/uzoraproductos-arch/a.git
cd a
```

El ciclo, sin excepciones:

```bash
git pull origin claude/funny-turing-imtm54   # ANTES de empezar a trabajar
# ...cambios...
git add -A && git commit -m "Describe el cambio"
git push origin claude/funny-turing-imtm54   # AL TERMINAR, aunque quede a medias
```

Si te quedas sin créditos, sin tokens o se cae la sesión, lo único que se
pierde es lo que no se haya empujado. Por eso conviene empujar seguido, incluso
trabajo incompleto: un commit imperfecto siempre vale más que un avance
perdido.

Para verificar que una copia está al día:

```bash
git fetch origin && git status
```

Si dice `up to date with 'origin/claude/funny-turing-imtm54'`, esa copia es la
buena. **No empujes a `main` sin permiso expreso del autor.**

### Dónde está cada cosa

| Qué | Dónde |
|---|---|
| Repositorio | `https://github.com/uzoraproductos-arch/a` |
| Rama de trabajo | `claude/funny-turing-imtm54` |
| Publicado y en vivo | `https://uzoraproductos-arch.github.io/a/` |
| Revisión abierta | Pull request #1 del repositorio |
| Copia comprimida | `.../a/archive/refs/heads/claude/funny-turing-imtm54.zip` |

La página publicada lleva su sello al pie: **Versión publicada: 20260922b**.
Si lo que ves en el navegador no coincide con el sello del `index.html` que
tienes delante, estás mirando una copia guardada por tu navegador, no la
publicación. Recarga forzando (`Ctrl+Shift+R`) o añade `?v=` a la dirección.

### Si trabajas con un agente de IA

`AGENTS.md`, en la raíz, es el archivo que Antigravity, Astra/Codex, Cursor y
los demás leen solos al abrir el proyecto: lleva las reglas duras —la rama, el
criterio editorial, las convenciones que rompen el archivo y los criterios de
terminado— en menos de 6,000 caracteres, por debajo del tope de 12,000 que
Antigravity impone a los archivos de reglas. Este documento, CONTEXT.md, es el
largo: el estado, lo hecho, lo pendiente y el porqué de cada decisión.

Si tu herramienta no toma `AGENTS.md` sola, cárgalo a mano: en Antigravity, como
regla de espacio de trabajo (`.agents/rules/`); en otras, pégalo al inicio de la
conversación. Dos frases bastan para arrancar: «lee AGENTS.md y CONTEXT.md antes
de tocar nada» y «trabajamos en la rama claude/funny-turing-imtm54».

## Qué es el proyecto

Auditavisión es una plataforma web de fiscalización ciudadana del gasto público
en México. Presenta el ejercicio del presupuesto federal y federalizado,
la estructura de los poderes del Estado y herramientas de verificación, dirigida
a un público no especializado pero sin renunciar al rigor técnico.

Versión declarada en el encabezado del HTML: **3.3 Golden Master**.

## Cómo está construido

Sitio estático, sin framework, sin proceso de compilación y sin dependencias que
instalar. Se abre y funciona.

```
index.html                       Estructura, 9 pestañas, contenido editorial
assets/css/auditavision.css      Diseño: temas claro y oscuro
assets/js/mexico-states-geo.js   Geometría de las 32 entidades (window.MEXICO_GEOJSON)
assets/js/audit-database.js      Datos fiscales, 16 colecciones (window.AUDIT_DB)
assets/js/audit-engine.js        Motor y controlador (window.AuditEngine)
herramientas/sello.py            Sube el sello de versión de las cinco hojas
AGENTS.md                        Reglas para agentes de IA (rama, criterio, límites)
```

El orden de carga importa: geometría y base de datos **antes** que el motor. El
motor lee `window.AUDIT_DB` y `window.MEXICO_GEOJSON` al ejecutarse y aborta si
no los encuentra.

Dependencias externas por CDN: Leaflet 1.9.4 para mapas y Google Fonts
(Playfair Display, Source Serif 4, JetBrains Mono, Inter).

### Convenciones que conviene respetar

- El archivo usa saltos de línea **CRLF**. Al editar con scripts, presérvalos o
  el diff se llena de ruido. Cuentas de CR sueltos que deben conservarse:
  `index.html` 56, `audit-engine.js` 2, `audit-database.js` 2,
  `auditavision.css` 1. El `.gitattributes` fija `* -text` para que Git no los
  convierta al clonar ni al commitear: sin esa línea, un clon en Windows con
  `core.autocrlf=true` normalizaría las más de 48,000 líneas del proyecto al
  primer commit y el diff dejaría de ser legible.
- El texto va **con acentos**. Es contenido de cara al público. Ojo:
  `audit-engine.js` mezcla acentos reales y secuencias `\u00e1`; al anclar un
  reemplazo, usa fragmentos cortos y sin acentos.
- `audit-engine.js` es un IIFE que expone su API en `window.AuditEngine` al
  final del archivo. Todo método invocado desde el HTML debe estar en ese
  objeto: si no, el botón no hace nada y la consola calla.
- La base de datos se llama **`window.AUDIT_DB`**, no `AuditDB`.
- **El sello de versión se sube a mano en todo cambio que toque `assets/`**,
  con `python3 herramientas/sello.py AAAAMMDD[letra]`. Sin eso el lector sigue
  viendo la copia que guardó su navegador. Si no tocaste `assets/`, no hace
  falta.
- La navegación usa `data-tab` en las pestañas y `data-sub` en las
  subpestañas; los paneles llevan `data-subpanel`.

## Cómo ejecutarlo

Requiere un servidor HTTP. Abrirlo con doble clic (`file://`) no funciona: el
navegador bloquea la carga de los scripts locales y verás la página en blanco.

```bash
python3 -m http.server 8000
# luego http://localhost:8000
```

## Las 9 pestañas

| # | Módulo | Contenido |
|---|---|---|
| 1 | Presupuesto | PEF y gasto federalizado por entidad |
| 2 | Acción financiera | Simuladores y comparativos |
| 3 | Legislativo | Iniciativas y Gaceta Parlamentaria |
| 4 | Judicial | Estructura del PJF y de la SCJN |
| 5 | Personajes políticos | Fichas de servidores públicos |
| 6 | Modo inspector | Verificación forense de noticias |
| 7 | Preguntas y glosario | FAQ y conceptos |
| 8 | Referencias | Fuentes oficiales |
| 9 | Comunidad | Participación ciudadana |

La pestaña 4 tiene cinco subpestañas (4.1 a 4.5), y la 4.1 a su vez tiene tres
subvistas: organigrama de la SCJN, estructura general del PJF y mapa territorial
de los 32 circuitos.

## Estado actual

### Hecho

- **Corrección de Espaciado Simétrico de la Casilla Principal (versión 20260924t):**
  - **Alineación Visual de la Casilla Showcase (`.civic-showcase-section`):** A partir de la anotación en `correcion pagina pral espacio casilla.png`, se corrigió el espacio superior de la casilla del carrusel (*"Descubre el rastro del gasto público"*).
  - **Simetría Vertical de 28px:** Previamente contaba con `margin: 0 auto 28px;`, lo que provocaba que la casilla quedara pegada (0px) a la barra del Radar Hacendario en Vivo (`.radar-hacendario-hub`), mientras que por debajo mantenía un margen de 28px respecto a la sección inferior de exploración cívica.
  - **Ajuste Aplicado:** Se estableció `margin: 28px auto;` en `assets/css/auditavision.css` (y en el espejo `auditavision/assets/css/auditavision.css`), logrando un espaciado idéntico y simétrico tanto arriba como abajo (`topGap = 28px`, `bottomGap = 28px`), verificado al 100% mediante inspección geométrica automatizada vía CDP en Edge Headless.
  - **Sello de Versión:** Elevado a `20260924t` con CRLF y lone CRs estrictamente preservados (1 en `auditavision.css`).

- **Desactivación Preventiva de Enlaces a la Enciclopedia y Plan de Integración Nativa (versión 20260924s):**
  - **Inspección de los 5 Mega-Menús:** Se auditaron exhaustivamente las opciones desplegables del encabezado fijo (`.site-top-nav`): *Búsqueda Forense*, *Acción Financiera*, *Descargar Datos*, *Consultar Recursos* y *Portal Digital*.
  - **11 Enlaces Desactivados con Badge 'Próximamente':**
    1. *Búsqueda Forense / Asignaciones:* `Padrón de Proveedores y Contratistas`
    2. *Búsqueda Forense / Detección ASF:* `Monitoreo de Empresas Facturadoras (EFOS)`
    3. *Acción Financiera / Presupuesto:* `Perfiles de Secretarías y Dependencias`
    4. *Acción Financiera / Entidades:* `Perfiles de las 32 Entidades (Atlas Extendido)`
    5. *Acción Financiera / Municipios:* `Padrón de los 2,479 Municipios (Censo Extendido)`
    6. *Descargar Datos / Abiertos:* `Descarga Personalizada en CSV/Excel`
    7. *Descargar Datos / Informes:* `Informes de Cuenta Pública ASF`
    8. *Descargar Datos / API:* `Diccionario de Datos y API Hacendaria`
    9. *Consultar Recursos / Atlas:* `Atlas Técnico Enciclopédico (9 Módulos)`
    10. *Consultar Recursos / Metodología:* `Compendio de Fuentes Oficiales`
    11. *Portal Digital / Formación:* `Canales Oficiales y Decálogo Auditor`
  - **Interacción y Feedback Cívico:** Cada enlace desactivado cuenta con la clase `.mega-link-disabled`, el badge visual `.badge-proximamente` y la función interactiva `window.AuditEngine.notificarEnDesarrollo(titulo)`, que despliega una notificación toast flotante (`#auditavisionRoadmapToast`) sin expulsar al usuario fuera de la plataforma.
  - **Módulos Nativos 100% Intactos y Operativos:** Se mantuvieron intactos los flujos de Búsqueda Avanzada de Contratos, Adjudicaciones Directas, Expedientes ASF ($51,024 mdp), Explorador PEF 2026 ($10.19 billones), Inversión en Megaobras, Calculadora Cívica de Sueldos y Ticket, Descarga masiva del Dataset EFIPEM (INEGI), Glosario Hacendario en vivo, Marco Legal (25 preceptos), Casillas FAQ, Pase Cívico y el Portal Público Digital (Ágora Cívica, hilos de discusión y réplicas con nick anónimo).
  - **Sello de Versión y Convenciones:** Elevado a `20260924s` con verificación al 100% en Edge Headless via CDP y preservación exacta de CRLF y lone CRs.

- **Módulo 3: Comparador Salarial de Choque (Tú vs Ellos) y Biblioteca Hacendaria (versión 20260924p):**
  - **Conservación del Menú Principal:** Se mantuvo 100% intacta la navegación principal que le agrada al autor, sin alterar los 5 menús ni la disposición de la cabecera.
  - **Módulo 3 Dividido en Dos Apartados:**
    - *Apartado A:* Calculadora Cívica del Contribuyente (ingreso bruto/neto, retenciones ISR/IMSS, a dónde va cada peso y Ticket Cívico viral).
    - *Apartado B:* Comparador Salarial de Choque (Tú vs los Servidores Públicos). Contrasta reactivamente el sueldo ingresado por el usuario contra Diputados Federales ($150,000/mes), Senadores ($171,450/mes), Ministros SCJN ($206,948/mes), Presidente ($186,093/mes) y Gobernadores ($135,000/mes). Calcula multiplicador de brecha (ej. 10.0x), días de vida laboral para igualar su salario, meses de trabajo que equivalen a su aguinaldo y cuántos trabajadores como el usuario se pagarían con 1 solo cargo. Incluye botón para copiar resumen a redes sociales y descarga de reporte.
  - **Biblioteca & Enciclopedia Hacendaria Integrada en Consultar Recursos:** Se unificó el marco legal hacendario (25 preceptos), el glosario de 77 términos y el repositorio de 32 fuentes oficiales (DOF, SHCP, ASF, Banxico, INEGI) dentro del menú "Consultar Recursos", conservando el rigor doctrinal sin recargar la suite operativa.
  - **Sello de Versión:** Actualizado a `20260924p` en `index.html` y `enciclopedia.html`.

- **Depuración Operativa de la Aplicación Auditavisión (versión 20260923e):**
  - **Identidad Oficial:** Se preserva el nombre **Auditavisión** de manera estricta e inmutable en el título, encabezados y créditos de la plataforma.
  - **Pestañas Seleccionadas:** La aplicación operativa (`index.html`) queda depurada a los 5 módulos esenciales solicitados:
    1. **1.1:** El Circuito del Dinero Público (`panoramica`: LIF, PEF, transferencias y etapas del gasto).
    2. **2.2:** Inversión por Sectores, Megaobras & Simulador de Pérdidas en tiempo real.
    3. **2.4:** Calculadora Cívica del Contribuyente & Ticket Cívico (`#ccTicketCivico`).
    4. **6:** Modo Inspector (6 Expedientes Forenses de alta repercusión con datos de ASF y SHCP).
    5. **7:** Preguntas, Glosario & Marco Legal Hacendario (con los 25 preceptos legales rectores de la LIF, LFPRH, CPEUM).
  - **Enciclopedia Cívica (`enciclopedia.html`):** Preserva el compendio documental completo de 9 pestañas (32 entidades, municipios, Poder Legislativo, Poder Judicial, personajes políticos y comunidad).
  - **Sello de Versión:** Actualizado a `20260923e` simultáneamente en ambos archivos mediante `herramientas/sello.py`.

- **Separación de la Arquitectura Cívica: Enciclopedia Intacta y Aplicación Auditor Cívico en Acción (versión 20260923d):**
  - **`enciclopedia.html`:** Preservada 100% intacta como el atlas enciclopédico de fiscalización y geopolítica (Presupuesto, Legislativo, Judicial, Políticos, Inspector, Glosario y Referencias). Enlaza a la aplicación con el botón *«Auditor Cívico en Acción (App) ➔»*.
  - **`index.html` (Auditor Cívico en Acción):** Enfocado en la interacción ciudadana directa (Calculadora Cívica, Ticket Cívico del Contribuyente, Expedientes Forenses, Auditoría de Inversiones, Pase Ciudadano "Las Dos Caguamas" y Comunidad). Glosario y Referencias ya no ocupan espacio en la barra superior de pestañas (reduciendo a 7 módulos limpios), sino que sus desgloses se ubican al pie de página sustituyendo las columnas de marco normativo y fuentes, con botones directos hacia `enciclopedia.html#faq` y `enciclopedia.html#referencias`.
  - **Navegación Fluida en `audit-engine.js`:** La función `switchTab` redirige automáticamente a la Enciclopedia cuando se invoca Glosario o Referencias en una página que no cuenta con dichos paneles locales.
  - **Herramienta `herramientas/sello.py`:** Sincroniza las 5 dependencias `?v=` y el pie visible simultáneamente en `index.html` y `enciclopedia.html`.

- **Expedientes Forenses de Auditoría, Ticket Cívico y Pase Ciudadano ("Las Dos Caguamas") (versión 20260923b):**
  - **Hero Action Bar (Dos Pilares & Membresía Cívica):** Botones de acceso directo en el encabezado a la Calculadora Cívica (`accion-financiera/calculadora`), la Auditoría de Inversiones (`presupuesto/panoramica`), y el botón del Pase de Auditor Ciudadano.
  - **Modelo de Negocios Cívico ("Las Dos Caguamas"):** Implementación del modal `#modalPaseCivico` bajo el eslogan *"En vez de comprarte dos caguamas, contrata esto y fiscaliza a tu gobierno"*. Ofrece plan mensual ($79 MXN/mes) y anual ($699 MXN/año) para descarga de dossiers ejecutivos en PDF (30 páginas con detalle municipal), Ticket Cívico en alta fidelidad y radar de alertas ASF. 100% independiente de partidos y gobiernos.
  - **Ticket Cívico del Contribuyente (Subpestaña 2.4):** Componente interactivo `#ccTicketCivico` tipo comprobante digital/térmico. Desglosa en tiempo real a dónde va cada peso del ISR del usuario (deuda pública, salud, educación, seguridad, programas sociales, infraestructura, etc.). Incluye botón para copiar resumen cívico listo para redes sociales y botón para descargar en alta calidad con el Pase Cívico.
  - **Pestaña 6 (Verificador / Modo Inspector) Rediseñada como Expedientes Forenses:** Se eliminó el formulario tosco de fact-checking y los checkboxes con hover artificial. Se incorporaron 6 expedientes oficiales de alta repercusión con datos de la ASF y la SHCP: Tren Maya, Segalmex, Refinería Dos Bocas, INSABI, Semáforo de Deuda de los 32 Estados y Sedena/Guardia Nacional. Cada uno con cifras de presupuesto, gasto devengado, monto observado por ASF, dictamen pericial oficial, enlace a `asf.gob.mx` y descarga de dossier. Conserva el explorador pericial de 3 niveles de gobierno (Pemex, CFE, IMSS, Estados y Municipios).
  - **Atmósfera Urbana Futurista (Día / Noche):** Fondos responsivos en `.site-header` (`city_night.jpg` y `city_day.jpg`) sincronizados con el botón de alternancia de tema claro/oscuro. Números tabulares en tipografía monospace para cifras y tablas financieras.
  - **Sello de Versión:** Actualizado a `20260923b` mediante `herramientas/sello.py`.

- Migración completa del proyecto al repositorio, verificada en navegador.
- **Organigrama de la SCJN (pestaña 4.1, subvista 1)** actualizado a la Corte
  posterior a la reforma judicial de 2024:
  - Nivel 1: nueve integrantes electos por voto popular, presidencia de Hugo
    Aguilar Ortiz, mayoría de seis votos, funcionamiento exclusivo en Pleno.
  - Nivel 2: presidencia rotativa cada dos años; se retiró la administración de
    recursos, hoy a cargo del Órgano de Administración Judicial.
  - Nivel 3: las dos Salas quedaron marcadas como estructura suprimida, con sus
    datos conservados y etiquetados como históricos.
  - Nivel 4: de once a nueve ponencias.
  - Nivel 5 (nuevo): Órgano de Administración Judicial, Tribunal de Disciplina
    Judicial y Escuela Federal de Formación Judicial.

- **Pestaña 4.5 dividida en dos partes.** La Parte 1 (cálculos globales, salas y
  focos rojos) quedó intacta. Se añadió una **Parte 2: «Costo y Resultado de la
  Reforma Judicial (2024–2028)»** con línea de tiempo de seis hitos, auditor de
  costo electoral, gráfica de tres vistas (presupuesto federal, participación y
  costo por voto, costo en las entidades), balance de resultados y hoja de ruta
  hacia la segunda elección, hoy diferida a junio de 2028.

- **Vinculación automática a glosario y referencias.** El motor recorre el texto
  visible de la pestaña activa y enlaza la primera aparición de cada concepto
  clave en cada subpanel: la palabra queda ligada al glosario y, a su derecha,
  se inserta la nota al pie con el número de la referencia que la respalda.
  - Catálogo de términos: `AUTOLINK_TERMINOS` en `audit-engine.js`. Añadir un
    concepto es añadir una línea con sus alias, el término exacto del glosario,
    la clave de referencia y su número.
  - Los acrónimos (PIB, IVA, ASF, DOF) se declaran con `cs: true` para exigir
    coincidencia de mayúsculas; sin eso, «IVA» se activaría dentro de «privada».
  - No toca enlaces ya existentes, encabezados, botones ni formularios, y omite
    por completo las pestañas de glosario y referencias.
  - El glosario pasó de 53 a 77 términos y el catálogo de referencias de 27 a 32.

- **Auditoría integral de formato, diseño y distribución** (pasada completa
  sobre las nueve pestañas). Se corrigieron defectos medidos, no supuestos:
  - *Desbordamiento horizontal en teléfono.* El bloque `.top-right` del
    encabezado llevaba `flex-shrink: 0` sin `min-width`, y los cajones
    laterales se ocultaban con `right: -750px`. Entre los dos empujaban el
    documento a 1026 px: las nueve pestañas se desplazaban de lado. Hoy el
    ancho del documento coincide con el de la pantalla en las nueve.
  - *Colisión del distintivo con la cinta de telemetría.* El texto en marcha
    pasaba por encima de «Auditoría en vivo».
  - *Encabezado compacto.* De 610 px a 467 px en teléfono y de 475 px a 360 px
    en tableta, sin retirar ningún elemento: los sellos de procedencia pasan
    a una fila deslizable.
  - *Medida de lectura.* Había párrafos de hasta 208 caracteres por renglón.
    Todas las pestañas quedaron en 80 o menos.
  - *Accesibilidad.* Enlace para saltar al contenido, foco visible (antes no
    existía ninguna regla), soporte de `prefers-reduced-motion`, aviso para
    quien navega sin JavaScript y ocultamiento de la mitad duplicada de la
    cinta a los lectores de pantalla.
  - *Descubrimiento.* Descripción, Open Graph, tarjeta de X, color de tema,
    datos estructurados JSON-LD e icono de sitio en SVG embebido. Antes, al
    pegar el enlace en cualquier red no aparecía ni título ni resumen.
  - *Impresión.* Hoja `@media print`: se imprime el contenido y no la
    interfaz, con pie de procedencia.
  - *Contraste en tema claro.* Neutralizados los fondos `rgba(0,0,0,0.3)`
    escritos en línea, que producían texto atenuado sobre gris.
  - *Pista de deslizamiento.* La barra de pestañas y la fila de sellos se
    deslizan en pantallas estrechas; un degradado avisa que hay más a la
    derecha y desaparece al llegar al final.

- **Reescritura de las nueve introducciones de pestaña** (`TAB_METADATA` en
  `audit-engine.js`). Eran inventarios de contenido en una sola oración de
  hasta 68 palabras. Ahora cada una abre con una idea y después enumera los
  instrumentos. No se retiró ninguna cifra.

- **Pestaña 1 reconstruida como panorámica del erario**, dividida en dos
  subpestañas. El alcance es deliberado: es vista de conjunto y marco legal,
  no auditoría. El detalle operativo corresponde a la pestaña 2.
  - **1.1 El Circuito del Dinero Público.** Las cuatro etapas del ciclo
    presupuestario —se recauda, se aprueba, se ejerce, se rinden cuentas— cada
    una con su instrumento, su plazo constitucional, su responsable y su
    fundamento legal. Luego, de dónde sale (nueve orígenes de la Ley de
    Ingresos 2026), en qué se va (gasto programable y no programable) y a
    dónde baja (el mapa y sus lentes, conservados sin un solo cambio).
    Cierra con cinco puntos ciegos y el bloque de fuentes.
  - **1.2 Del Peso Federal al Peso Local.** Los tres pisos de la hacienda
    pública con quién cobra, quién aprueba y quién fiscaliza en cada uno; la
    diferencia entre Ramo 28 y Ramo 33; un selector que arma el circuito de
    cualquiera de las 32 entidades; y las fichas municipales de esa entidad.
  - Los datos viven en `panoramaErario`, dentro de `audit-database.js`.
    Ingresos, egresos y gasto federalizado **cuadran al peso** con sus
    totales oficiales; hay una comprobación aritmética en el commit.
  - Cada cifra lleva un distintivo de trazabilidad: `oficial` cuando se lee
    directo del texto de la ley o del análisis del CEFP, y `derivado` cuando
    se obtiene por diferencia o a partir de porcentajes publicados. Esto es
    lo que permite que cualquiera rehaga la cuenta.

- **Afinaciones del vinculador automático.** Se añadió
  `AUTOLINK_OMITIR_CLASES`: las etiquetas compactas, los distintivos y las
  celdas de dato ya no reciben nota al pie, porque rompían su maquetación sin
  aportar nada. También se omiten `DT`, `TH`, `SUP` y `SUB`.

- **Unidad consistente dentro de cada gráfica** (`formatMdpFijo`). Mezclar
  «billones» y «mdp» en la misma columna obligaba a convertir de cabeza para
  comparar dos barras.

- **Subpestaña 4.6 — La Función Jurisdiccional** (`funcionJurisdiccional` en
  la base, módulo `fj-*` en el motor y en la hoja de estilos). Explica cómo
  decide el Poder Judicial, no cuánto cuesta. Seis bloques:
  1. Los cuatro instrumentos de control constitucional (amparo, controversia,
     acción de inconstitucionalidad y declaratoria general), en fichas que se
     despliegan con quién los promueve, plazo, alcance del fallo y órgano.
  2. La ruta procesal completa, conmutable entre **amparo indirecto** (9
     etapas) y **amparo directo** (5 etapas), con rail de nodos, barra de
     progreso y un botón «Recorrer el juicio» que avanza solo cada 3.4 s.
  3. Los cuatro recursos con su plazo y su fundamento.
  4. Las seis puertas de entrada a la Suprema Corte y el filtro de cada una.
  5. Las cuatro vías de creación de jurisprudencia y cómo se cambia una regla.
  6. Ocho puntos ciegos etiquetados `oficial`, `derivado` o `análisis`.

- **Nueva introducción de la pestaña 4.** El párrafo que abría con «A petición
  y requerimientos de la Auditoría Civil…» hablaba sólo de cifras. Se trasladó
  a 4.5, reescrito, dentro de un bloque «Balance presupuestal auditado». El
  hero de la pestaña 4 ahora presenta las dos dimensiones que se auditan
  —cuánto cuesta y cómo decide— y enumera lo que hace cada una de las seis
  subpestañas.

- **Capa visual de la subpestaña 4.1** (`pjo-*` y `pj-escalera` / `pj-peldano`).
  El contenido no cambió; cambió cómo se sirve. Antes de las fichas hay ahora
  tres capas de entrada:
  1. Cinco cifras de tamaño (9 ministras y ministros, 32 circuitos, órganos
     documentados calculados del propio árbol de datos, 54,500 plazas y
     $78,327 mdp del Ramo 03).
  2. Un contraste **antes / hoy** de la reforma, con la aclaración explícita
     de que la Primera y la Segunda Sala **ya no operan** y por qué se
     conservan sus fichas como anexo histórico.
  3. Las tres vistas convertidas de píldoras en tarjetas grandes con número,
     icono y una línea que dice qué se va a encontrar.
  Dentro de cada vista se añadió una **escalera jerárquica navegable**: un
  peldaño por nivel, con ancho decreciente y el número de fichas, que salta
  al nivel y lo destaca un instante.

- **Correcciones de forma en 4.1.** `.pj-node-badge` tenía `white-space:nowrap`
  y las insignias largas se cortaban a media palabra; ahora fluyen en varias
  líneas bajo el título. Los metadatos de cada ficha pasaron de un renglón
  corrido en monoespaciada a etiqueta y valor en bloque. Se actualizó el dato
  obsoleto «11 Ministros (9 en transición 2024)» en la vista del PJF.

- **Capa de citas (referencias 33 a 38 y 20 términos nuevos de glosario).**
  Se añadieron al catálogo la Ley de Amparo con sus dos reformas de 2025, los
  artículos 94, 100, 103, 105 y 107 constitucionales, la acción de
  inconstitucionalidad 164/2024, el Censo Nacional de Impartición de Justicia
  Federal del INEGI, el Acuerdo General 7/2025 de la Duodécima Época y el
  posicionamiento de la Barra Mexicana. El glosario creció de 77 a 97 términos
  con el vocabulario procesal del amparo. Se registraron 20 entradas nuevas en
  `AUTOLINK_TERMINOS`, de modo que esos términos quedan enlazados
  automáticamente en toda la plataforma, cada uno con su nota al pie al
  catálogo de fuentes.

- **Dos arreglos de navegación que benefician a todo el sitio.** El catálogo de
  referencias ahora se ordena por número de cita en lugar de por orden de
  inserción. Y la búsqueda del glosario prioriza la coincidencia exacta del
  término: antes, saltar desde una nota al pie abría la ficha vecina.

- **Subpestaña 4.2 reorganizada (Pleno y Ministros).** Se aplicó la misma
  receta de 4.1 sin reescribir el contenido: una capa de orientación arriba
  (`#plenoOrientacion`, función `renderPlenoOrientacion`) con cinco cifras de
  entrada, el contraste antes/hoy del régimen de la Corte y las dos
  composiciones convertidas en tarjetas grandes; debajo, una **ficha cerrada
  por cada integrante** (`renderPlenoFichas`, clases `.min-*`) con avatar de
  iniciales, insignia de origen, especialidad y tres cifras: sueldo neto,
  plazas de la ponencia y costo mensual del despacho. La tabla comparativa
  anterior se conserva íntegra como **vista alterna** mediante el conmutador
  `.pleno-modo-btn` (`setPlenoModoVista`). La gráfica comparativa y el bloque
  de cálculos siguen intactos, ahora dentro de bloques `.fj-bloque` con
  encabezado y entradilla. Las cuatro tarjetas métricas sueltas del encabezado
  se disolvieron en la capa de cifras, y la cinta de fuentes se convirtió en un
  bloque 4 con nota metodológica.

- **Dos cifras de 4.2 se calculan de la base, no se escriben a mano**: las
  plazas totales de las nueve ponencias (226) y el costo anual agregado
  ($217 mdp) se derivan sumando `asesores_plazas` y `costo_mensual_ponencia`.
  Si la base cambia, la cifra cambia sola. La nota metodológica advierte que
  ese costo es una suma a tabulador y no una partida etiquetada del PEF.

- **Corrección factual sobre la duración del encargo.** Tanto 4.1 como 4.2
  afirmaban que las ministras y ministros electos tienen encargos de doce
  años. Es incorrecto para esta primera Corte: el artículo tercero transitorio
  del decreto del 15 de septiembre de 2024 fijó periodos **escalonados de 8 y
  11 años** según los votos obtenidos, y las tres ministras que ya estaban en
  funciones agotan lo que resta de su periodo original de quince años. La
  regla general de doce años del artículo 94 corre a partir de 2033. Corregido
  en los tres lugares donde aparecía.

- **Barra de pestañas: se encimaban los rótulos al cambiar el tamaño.** Los
  botones tenían `flex: 1 1 auto` con `white-space: nowrap`. Entre 880 y
  1130 px de ancho se encogían por debajo del ancho de su propio texto y el
  rótulo se salía de la caja, montándose sobre el vecino: nueve de nueve
  botones desbordados a 880 px. Ahora es `flex: 1 0 auto` con `flex-wrap: wrap`
  y tope de crecimiento del 22%: la fila baja a un segundo renglón centrado en
  lugar de comprimir, y por debajo de 860 px se conserva la pista horizontal
  de teléfono (`flex-wrap: nowrap`). Verificado en barrido de 1600 a 360 px de
  veinte en veinte: cero desbordes y cero solapamientos.

- **Pestaña 9 reestructurada (Comunidad y Contraloría Social).** Las tres
  funciones que ya existían se conservan íntegras y ahora se distinguen: una
  capa de orientación (`#comOrientacion`, `renderComunidadOrientacion`) abre
  con tres tarjetas-ruta —aportar, denunciar, debatir— que saltan a su bloque,
  y debajo un cuadro de tres columnas dice **a dónde va a parar cada texto**.
  El contenido se reordenó en tres bloques `.fj-bloque` con ancla
  (`#bloqueAportar`, `#bloqueCanales`, `#bloquePortal`).

- **Corrección de honestidad en la pestaña 9.** El formulario respondía «tu
  observación ha sido registrada para revisión» y el foro «publicado con éxito
  en el Portal Público Digital», cuando ambos guardan en `localStorage`: nadie
  más los ve. Los mensajes ahora dicen que el texto queda en ese navegador y
  que los hilos serán públicos cuando haya servidor. Es la misma regla que
  rige los datos: prometer lo que no ocurre descalifica todo lo demás.

- **Inyección de HTML cerrada.** Todo lo que escribía una persona se pintaba
  con `innerHTML` sin escapar: un texto con `<img src=x onerror=…>` se
  ejecutaba. Se añadió `escHtml()` y se aplicó a los nueve puntos donde entra
  texto de la persona (observaciones, tesis, contenido, nick, réplicas, tipo
  de réplica, fuente, avatares). Verificado: el mismo intento de inyección que
  antes ejecutaba ahora se muestra como texto literal.

- **Canales oficiales: de 3 a 6, y uno estaba extinto.** La ficha de la
  Secretaría de la Función Pública describía un órgano que dejó de existir con
  ese nombre: la sustituyó la **Secretaría Anticorrupción y Buen Gobierno**
  (DOF 28/11/2024, en operación desde el 1 de enero de 2025) y la plataforma
  de alertadores cambió de dominio. Se corrigió y se añadieron la Fiscalía
  Especializada en Combate a la Corrupción, la Plataforma Nacional de
  Transparencia —que no es un canal de denuncia sino la herramienta para
  conseguir la prueba— y los órganos internos de control. Cada ficha responde
  ahora cuatro preguntas: para qué sirve, si admite anonimato, qué hay que
  tener a la mano y qué produce la denuncia.

- **El «decálogo» tenía cuatro puntos.** Ahora tiene diez, cada uno con su
  fundamento normativo concreto (arts. 134 y 6º CPEUM, arts. 33 y 37 de la Ley
  de Coordinación Fiscal, LGTAIP, LOPSRM, LGMDE, LGRA).

- **El foro dejó de envejecer mal.** Los hilos sembrados traían fecha fija y
  «hace 1 día» escrito a mano. Ahora guardan su antigüedad en días y la fecha
  se calcula al pintar (`fechaRelativa`). Además el selector de temas afirmaba
  que la deuda estaba en la pestaña 6, que es el Modo Inspector: se corrigió a
  la 2 y cada hilo lleva un botón que abre la pestaña con los datos que
  discute (`PORTAL_TEMA_PESTANA`).

- **Puente entre aportar y denunciar.** Cada observación guardada tiene un
  botón que la copia ya redactada —fecha, tipo, entidad, hechos— para pegarla
  en el formulario de un canal oficial, y otro para borrarla. El selector de
  entidades pasó de doce escritas a mano a las 32 de la base.

- **Referencias 39 a 42 y ocho términos nuevos de glosario.** Se añadieron el
  decreto de creación de la SABG, la Plataforma Nacional de Transparencia, la
  Ley de Obras Públicas y la Ley General en Materia de Delitos Electorales; y
  los términos Contraloría Social, Denuncia Ciudadana, Alertador, Falta
  Administrativa Grave, Solicitud de Acceso a la Información, Recurso de
  Revisión en Transparencia, Órgano Interno de Control y Empresa Fantasma
  (EFOS), todos registrados en `AUTOLINK_TERMINOS`. También se actualizó la
  referencia 13: la LAASSP del año 2000 quedó abrogada el 16 de abril de 2025.

- **La 5.4 dejó de arrancar en ceros.** Los cuatro simuladores (barras versus,
  tacómetro de salud, tarjetas y ranking) exigían pulsar «Evaluar» en tres
  lugares distintos antes de mostrar un solo dato: quien abría la pestaña veía
  gráficas planas, como si estuviera rota. Ahora cada bloque se anima solo
  cuando entra en pantalla, con `IntersectionObserver` y un candado
  (`vsxYaArrancado`) que se libera al pulsar «Reiniciar» o al volver a entrar.
- **Capa de orientación de la 5.4.** `renderVersusOrientacion()` pinta los tres
  pasos de juego y, debajo, tres cautelas metodológicas declaradas de frente:
  el PIB porfiriano es reconstrucción historiográfica y no cuentas nacionales;
  un Estado de 7.4% del PIB no hace lo mismo que uno de 25%; y 31 años de
  gobierno no se promedian igual que un sexenio.
- **Trazabilidad por métrica.** Cada una de las seis variables del catálogo
  lleva `fuente_dato` y `ref_fuente`, y el encabezado de la gráfica muestra la
  procedencia con enlace a la referencia. Antes la gráfica afirmaba cifras sin
  decir de dónde salían.
- **Línea guía «Nivel Díaz» sobre las barras y distancia por mandatario.** La
  referencia porfiriana sólo existía en la vista lineal; en barras había que
  comparar diez alturas a ojo. La línea se mide del DOM (`vsxColocarLineaDiaz`),
  no con una constante, porque la altura de los rótulos cambia. Cada barra
  lleva ahora su insignia ▲/▼ con la distancia frente a Díaz.
- **Bloque «La cifra detrás de la cifra».** Verificación aplicada a las tres
  estadísticas estelares de la propia pestaña: el célebre primer superávit de
  1894–1895 fue de $19,861.06 sobre ingresos de $43,074,052.93 (0.05% del
  presupuesto); el 70.6% de la vía férrea se tendió antes de 1900; y el «0% de
  ISR» no era una política sino una ausencia, porque el impuesto sobre la renta
  aparece en 1921 y se vuelve permanente entre 1924 y 1925.
- **Bloque «El otro balance».** Es el punto ciego que tenía la comparación: el
  tablero medía cómo se administró el dinero y nada sobre la gente. Cinco
  indicadores sociales con fuente censal —esperanza de vida (30 años en 1910
  contra 72.8 y 79.2 en 2026), analfabetismo (82.1% en 1895 y 73% en 1910
  contra 4.7% en 2020), salario mínimo real ($64.3 en 1877 a $60.1 en 1911, en
  pesos de 2018), campesinos con tierra propia (15% en 1910) y quién pagaba el
  Estado. Los dos indicadores cuyas cifras no viven en la misma escala llevan
  `sin_barras` y no se grafican: una barra llena bajo un rótulo que no es un
  porcentaje afirma visualmente lo que el dato no sostiene.
- **Defectos corregidos de paso en la 5.4.** El «Índice Global» de la consola
  de salud se quedaba en 0/100 mientras el tacómetro marcaba 94, de modo que
  el tablero se desmentía a sí mismo. El rótulo decía «Ningún Mandatario
  Seleccionado» cuando sí había uno elegido y lo que faltaba era evaluar. El
  título de la tabla anunciaba «7 Mandatarios Contemporáneos» cuando la base
  trae nueve, dos de ellos del siglo XIX, y el de la gráfica acotaba
  «1988–2026» incluyendo a Santa Anna y a Juárez. Y la métrica ferroviaria se
  pintaba como «19280» porque el código comparaba `metric.unidad === 'km'`
  mientras la unidad real es «km de vías»: el formato quedó centralizado en
  `versusFormatoCifra`, `versusCifraCero` y `versusEsKm`.
- **Referencias 43 a 46.** Estadísticas sociales del Porfiriato del INEGI,
  serie de esperanza de vida de CONAPO, Censo de Población y Vivienda 2020 y
  la reconstrucción del salario mínimo real en pesos de 2018 con datos de la
  CONASAMI.

- **Modo desglose en la 5.4.** Al elegir una variable en la barra de
  herramientas, la subpestaña se reduce a esa sola variable: la raíz
  `#versus54Raiz` recibe la clase `.vfoco-on` y los siete bloques marcados con
  `.vfoco-ocultar` —portada, capa de orientación, matriz comparativa, las tres
  cifras verificadas, el balance social, la trazabilidad y el muelle de
  navegación— se repliegan. Quedan en pantalla el aviso de desglose, los chips
  de variables, la gráfica y el nuevo bloque `#versusDesglose`. Nada se
  destruye: «Volver al tablero completo» lo devuelve todo, y `switchSubtab`
  apaga el modo para que nadie encuentre la 5.4 a medio replegar.
- **Bloque de desglose.** Cuatro tarjetas de cabecera —quién encabeza, quién
  cierra, dónde queda Don Porfirio Díaz y su distancia contra el promedio de
  los otros nueve—, el orden de los diez mandatarios con riel divergente
  anclado en el cero, la distancia de cada uno frente a Díaz y la procedencia
  del dato con su referencia. Cada renglón abre el marcador cara a cara.
- **El gasto público no lleva medallas.** Su `sentido_positivo` es nulo, así
  que la lista se ordena de mayor a menor y lo dice con todas sus letras: el
  tamaño del gasto depende de qué funciones asume el Estado, no del mérito de
  quien gobierna.
- **La métrica ferroviaria estaba mal nombrada.** Se llamaba «km acumulados»
  pero los datos son kilómetros atribuibles a cada periodo, y el −19,000 de
  1994–2000 es la extinción de Ferrocarriles Nacionales y el retiro del
  servicio de pasajeros, no vía levantada. Corregidos el nombre y la
  descripción; los 19,280 km de Díaz son de 31 años, no de un sexenio.
- **La gráfica de barras dibujaba los negativos como logros.** La altura se
  calcula con el valor absoluto, así que −19,000 km levantaba una barra casi
  tan alta como la de Díaz. Ahora esas barras van rayadas en diagonal y con
  filo rojo, y un pie de gráfica explica que la altura mide tamaño, no
  dirección. En el desglose esas mismas cifras sí quedan ordenadas.
- **La línea «Nivel Díaz» estaba entre 116 y 148 px fuera de lugar.** Las
  columnas llevan una transición CSS de 0.5 s, de modo que al cerrar la
  animación de JS todavía estaban creciendo y la línea se medía contra una
  altura intermedia. Se vuelve a medir 560 ms después, y la fórmula descuenta
  el filo inferior del escenario. El rótulo ya no se corta: se parte en dos
  líneas dentro de su canaleta.
- **Sin barra de desplazamiento visible.** El escenario de la gráfica, el
  contenedor lineal y la matriz siguen desplazándose con el dedo o la rueda,
  pero ya no dibujan la barra gris.

- **Barra de regreso asistido.** Al saltar al glosario, a las referencias o al
  marco legal desde cualquier hipervínculo, se anota de dónde venía la persona
  —pestaña, subpestaña y altura de la página— y aparece una barra fija con
  «Volver a donde estaba», «Inicio de la pestaña» y un cierre. Restituye el
  punto exacto de lectura. La barra se retira sola cuando alguien navega por
  su cuenta con la barra de pestañas o de subpestañas, y el cuerpo recibe un
  respiro al pie para que no tape la última ficha.
- **Las pestañas del glosario ya funcionan.** Sí filtraban, pero
  `filterGlossaryByCategory` leía el buscador, y quien llegaba por un
  hipervínculo lo tenía lleno con el término: cada categoría devolvía cero
  fichas y los botones parecían muertos. Ahora elegir una categoría vacía el
  buscador.
- **Los conteos del glosario se calculan de la base.** El rótulo decía «(53)»
  con 105 fichas cargadas. Cada pestaña muestra su propio número y el
  encabezado el total, todo derivado de `DB.glosario`.
- **La caja de búsqueda del glosario medía 208 px.** Su contenedor es un
  elemento flexible que se encogía al contenido; con `width: 100%` recupera
  los 520 px previstos.
- **22 definiciones nuevas** (105 → 127): Acción Financiera del Estado,
  Federalismo Fiscal, Hacienda Pública, Ingresos Presupuestarios, Deuda
  Subnacional, Sistema de Alertas (SHCP), Adecuación Presupuestaria, Anexo
  Transversal, Programa Presupuestario, Fideicomiso Público, Licitación
  Pública, Adjudicación Directa, Invitación a Cuando Menos Tres Personas,
  Testigo Social, Obra Pública, Convenio Modificatorio, Sistema Nacional
  Anticorrupción, Sujeto Obligado, Versión Pública, Auditoría de Desempeño,
  Artículo 134 Constitucional y Artículo 126 Constitucional.
- **22 entradas nuevas de autoenlace** más los alias «déficit fiscal»,
  «déficit presupuestal», «superávit fiscal» y «superávit presupuestal». El
  recorrido pasa de 180 a 232 hipervínculos de glosario con su nota al pie, sin
  anclas anidadas y sin términos enlazados que carezcan de ficha.

- **Hecho · Cimiento de derecho económico y cuentas ecológicas (Fase 0).** Se incorporó el andamio doctrinal que faltaba (capítulos 3–5 de Gómez Granillo / Gutiérrez Rosas).
  - `preceptos_legales` 25 → 28: se agregaron los artículos **25** (rectoría económica), **27** (propiedad originaria) y **28** (monopolios, áreas estratégicas y autonomía del banco central). Antes sólo existía el 26, de modo que la plataforma explicaba cómo se ejerce y fiscaliza el gasto, pero no con qué facultad el Estado interviene en la economía.
  - `referencias_legales` 46 → 51: CEEM (programa INEGI), boletín CEEM 2024, PIBE 2024, Ley de Planeación y LGEEPA.
  - Colección nueva `constitucion_economica`: los cuatro pilares (25, 26, 27, 28) con pregunta, facultad, órgano, ley secundaria, tres claves y un punto ciego cada uno.
  - Colección nueva `cuentas_ecologicas` con las CEEM 2024 del INEGI, publicadas el 1.º de diciembre de 2025. Cifras oficiales: PIB $33,506,847 mdp; CTADA $1,382,214 mdp (4.1%); PINE $25.7 billones (76.6%); agotamiento $144,020 mdp (0.4%); degradación $1,238,194 mdp (3.7%); gasto en protección ambiental $232,882 mdp (0.7%). Cada cifra lleva `estado: oficial | derivado`; sólo el consumo de capital fijo y el PIN se derivan por diferencia, y así se declaran. La cascada cierra al peso.
  - `glosario` 127 → 155 (28 términos nuevos) y 33 entradas de autolink, con los acrónimos sueltos (PND, PINE, CTADA, MIA) marcados `cs: true` para que no enlacen en minúsculas.
  - Los enlaces automáticos ahora llevan `data-termino` y `data-ref`, de modo que la auditoría del enlazado se hace contra el dato y no contra el texto del tooltip. La comprobación anterior de huérfanos era vacía porque el atributo no existía.
  - Se retiró el rótulo fijo «(25)» de la subpestaña 7.3, mismo defecto que el «(53)» del glosario.
  - Verificado: 236 enlaces de glosario con sus 236 notas al pie, 0 huérfanos, 0 anclas anidadas, 0 errores de JavaScript en las 9 pestañas. El incremento es de sólo 4 enlaces porque este vocabulario aún no está escrito en la interfaz; ese es el trabajo de la fase siguiente.

- **Hecho · Subpestañas 1.3 y 2.5 (Fases 1 y 2).** La doctrina del cimiento se volvió interfaz.
  - **1.3 «La Constitución Económica: con qué facultad»**: brújula de cuatro preguntas, una ficha por artículo (25, 26, 27, 28) con facultad, órgano que la ejerce, ley secundaria, tres claves y un punto ciego, y la cadena «del artículo al peso ejercido» en cinco eslabones. Botón nuevo `goToPrecepto()` que salta al texto del precepto en la 7.3 dejando marcada la barra de regreso.
  - **2.5 «El PIB no alcanza»**: cascada PIB → PIN → PINE con riel acumulativo (cada renglón arranca donde terminó el anterior y las restas van rayadas), desglose de agotamiento y degradación por componente, balanza de gasto en protección contra daño, cuatro puntos ciegos y cuatro implicaciones jurídicas.
  - **Simulador del PINE.** Tres controles (crecimiento nominal del PIB, costo ambiental y consumo de capital fijo como porcentaje del PIB) y tres escenarios preconfigurados. No resta un flujo contra un nivel: calcula el PINE del año siguiente y compara su crecimiento contra el del PIB, que es una identidad contable. Verificado contra el cálculo independiente en cuatro escenarios, incluido el decisivo (PIB +5.0% con costo ambiental al 8.0% → PINE −0.3%).
  - **Sello de verificación** `✓ Cifra oficial` / `ƒ Derivada por diferencia` en cada cifra de la 2.5: la regla editorial hecha interfaz.
  - Corregido: el `>` suelto que se imprimía como texto al cerrar la pestaña 1, y la nota al pie duplicada («[48] . [48]») que salía al sumar el enlace manual al automático.
  - Verificado: 445 enlaces de glosario con sus 445 notas al pie recorriendo **todas** las subpestañas, 0 huérfanos, 0 anclas anidadas, 0 desbordes de 1600 a 360 px, 0 errores de JavaScript.

- **Hecho · Simulador de megaobras (2.2), desarrollo mayor.**
  - **Los totales consolidados eran falsos.** Estaban escritos a mano y no cuadraban con la suma de las 12 obras: $4,066,853 mdp declarados contra $4,116,153 reales de inversión, y $78,685.1 contra $80,200.1 de pérdida anual. El «+185.3%» de sobrecosto no correspondía ni al promedio simple (218.6%) ni al ponderado (293.3%): no salía de ningún cálculo. Los datos **por obra** sí eran coherentes (anual → diaria → segundo cuadran en las 12); el defecto estaba sólo en los agregados. Ahora todo se deriva de `simFiltradas()` y nada se escribe a mano.
  - **La tira de indicadores no respondía a los filtros.** Se podía filtrar a un solo sector y los cuatro indicadores seguían mostrando el consolidado. Ahora los cuatro, incluido el ritmo del contador en vivo, se calculan sobre las obras que el filtro deja en pie.
  - **`.sim-kpis-strip` no tenía regla de CSS.** La clase existía en el HTML desde el principio pero nunca se estilizó, así que las cuatro tarjetas se apilaban a lo alto en cualquier pantalla. Ahora es una rejilla de 4 → 2 → 1 columnas.
  - **Nuevo: ordenamiento** por pérdida anual, sobrecosto, costo real, pesos de más y cronología.
  - **Nuevo: comparativa** de las obras filtradas en barras, ordenada por la misma variable, con salto a la ficha.
  - **Nuevo: bloque de escala** que pone el costo junto a cinco anclas conocidas (Ramo 33, gasto federalizado, deuda subnacional, costo ambiental anual y PEF), cada una con su ejercicio y su referencia. Lleva la advertencia de que la suma de las obras son pesos nominales de 1988 a 2024 sin deflactar y las anclas son de un solo ejercicio: sirve para el orden de magnitud, no para una equivalencia exacta.
  - **Nuevo: bloque de procedencia** que explica cómo se calcula cada cifra, incluido que el contador en vivo proyecta el ritmo anual y no mide un gasto instantáneo, y que declara el pendiente: cada obra aún no lleva la referencia puntual del informe que la sustenta.
  - Sobre el contador en vivo: se sospechó una fuga de temporizadores al refiltrar y se descartó instrumentando `setInterval`. Hay exactamente un reloj activo tras 4 cambios de sector, 2 de sexenio, 3 de orden y 6 idas y vueltas a la subpestaña. La aparente duplicación era un artefacto de medición.
  - Verificado: 447 enlaces de glosario con sus 447 notas, 0 huérfanos, 0 anclas anidadas, 0 desbordes de 1600 a 360 px en la 2.2, 0 errores de JavaScript. Los agregados mostrados coinciden con el cálculo independiente sobre la base.

### Hecho - Reorganizacion visual de la subpestana 2.2

- Los tres filtros dejan de ser tiras de pastillas. Temporalidad: cinco losetas con la cifra de cada
  cadencia a la vista, para comparar antes de pulsar. Sector: mosaico de seis losetas con icono grande,
  numero de obras, costo real y cuota del total. Administracion: linea del tiempo 1988-2024 con torre
  proporcional al numero de obras del periodo.
- El desglose (orden, comparativa, mesas y fichas) nace replegado en `#simDesglose` y se abre al elegir
  sector o sexenio, o con el boton "Ver todas". La escala y la procedencia quedan siempre visibles.
- Tres mesas de calculo nuevas, cada una de cero al resultado: (1) de lo aprobado a lo erogado, con
  columna acumulada; (2) como se arma la perdida operativa anual, mas la cadena de conversion del ano
  al segundo; (3) de la cifra agregada al bolsillo, con boton que carga el importe en la calculadora 2.3.
- Punto ciego declarado: FARAC aparece en Salinas y en Zedillo, asi que los seis periodos suman trece
  obras y no doce. Se dice en la propia linea del tiempo.
- Notas al pie y glosario aplicados al panel con `autolinkAmbito`; las etiquetas compactas nuevas
  (`sim-dial-*`, `sim-los-*`, `sim-seg-*`, `sim-t-*`, `sim-cad-*`, `sim-pr-*`) van en la lista de omision.

### Hecho - La tira de indicadores vuelve a estar siempre a la vista (2.2)

- Defecto de raiz encontrado al perseguirlo: `body` tenia `overflow-x: hidden`, que convierte al cuerpo
  en contenedor de desplazamiento y deja inerte a `position: sticky` en toda la plataforma. Ni la barra
  de pestanas se anclaba, pese a tener la regla desde el principio. Se cambia a `overflow-x: clip`,
  que recorta igual pero no crea contenedor de desplazamiento, dejando `hidden` como respaldo.
- `.sim-kpis-strip` se ancla arriba: los cuatro bloques y el contador en vivo acompanan al usuario
  mientras explora selectores, mesas y fichas. En pantallas de 1080 px o menos vuelve al flujo normal.
- Se retira el salto automatico al desglose que introdujo la reorganizacion: era lo que empujaba la
  tira fuera de pantalla al elegir un sector.
- Selectores comprimidos de 1,127 px a 811 px: loseta de sector a dos renglones, torres de la linea
  del tiempo mas bajas, cabeceras y rellenos mas ajustados.

### Hecho - 2.2: unidades legibles, tira global e inventario por sector

- DEFECTO DE UNIDADES corregido. La etiqueta "mil mdp" se leia como "mil millones de pesos" cuando
  significaba mil millones multiplicados por mil: `$461.4 mil mdp` son 461,392 millones de pesos, mil
  veces mas de lo que sugeria. `simMdp` pasa a una escala explicita: millones / mil millones / billones.
  Se elimina "mil mdp" del dial, la cadena de la mesa 2 y las fichas de obra.
- La tira de cuatro indicadores mide SIEMPRE las 12 obras evaluadas. Solo la cadencia temporal la altera;
  sector y sexenio ya no la tocan. Las cifras del filtro pasan a la cabecera del desglose, en tres
  tarjetas propias que ademas dicen que cuota del universo representa el recorte.
- Bloque nuevo `#simPorSector`: las 12 obras completas agrupadas por sector, con aprobado, erogado,
  diferencia, sobrecosto y cuota del total; cabecera de sector con nota al pie y salto a la ficha desde
  cada renglon. Incluye leyenda de unidades y el pendiente declarado del informe puntual por obra.

**Hecho — 2.2 en tres bloques y telemetria contra reloj.**
- La subpestana 2.2 se reorganiza en tres secciones numeradas: (1) *El pulso del gasto* con la tira de cuatro indicadores y la temporalidad; (2) *¿Por donde quiere entrar?* con sector estrategico, administracion presidencial y el desglose que abren; (3) *Obra por obra, peso por peso* con el inventario por sector, la escala y la procedencia.
- Las fichas vivas de obra suben al primer lugar dentro del desglose: al pulsar un sector o un sexenio aparecen antes que el ordenamiento, la comparativa y las mesas.
- **Defecto corregido:** el contador de telemetria viva se reiniciaba a cero en cada re-dibujo (elegir sector, sexenio o cadencia) porque el `innerHTML` de la tira lo reescribia en `+$0.00` y los segundos se contaban por pulsos de `setInterval`. Ahora se calcula contra el reloj desde `state.simuladorInicioVista` y se repinta en el mismo render, asi que ningun filtro lo toca.
- Pastilla flotante `#simTelFlota`: cuando la tira del bloque 1 sale de vista, el acumulado se reduce a una pastilla anclada a la esquina inferior; un `IntersectionObserver` la muestra y la oculta, y desaparece al salir de la 2.2.
- Se retiran tres notas al pie manuales que duplicaban al autolink (`[14] [14]` en procedencia y en los cierres de las mesas 1 y 2).

**Hecho — bloque 2 en dos partes y simulador comparativo de obras.**
- El bloque 2 se divide en parte A (sector estrategico: la loseta abre el desglose con las cifras del filtro y las fichas vivas de cada obra) y parte B (administracion presidencial: la linea del tiempo mas el simulador comparativo).
- `renderSimuladorComparativo()` sustituye a `renderSimuladorRanking()`. Replica el mecanismo del simulador comparativo de la 5.1: barra de control con distintivo, texto de estado, boton «Evaluar», «Reiniciar a ceros» y casilla de evaluacion al pasar el cursor; las barras nacen en cero y escalan con `requestAnimationFrame` y suavizado cubico.
- A diferencia del ranking anterior, **no se recorta con los filtros**: compara siempre las 12 obras. El sector y el sexenio elegidos resaltan los renglones que les tocan y atenuan el resto (`.sim-comp-fuera`), de modo que la comparacion nunca pierde el universo.
- Los cinco criterios (perdida anual, sobrecosto, costo real, pesos de mas, cronologia) suben al simulador comparativo; cambiar de criterio reordena y vuelve a animar si ya estaba evaluado. Se retira `renderSimuladorOrden()` y el contenedor `#simOrdenChips`.
- Las tres mesas de calculo bajan al bloque 3, que queda como: mesas, inventario por sector, escala y procedencia.

**Hecho — simulador sexenal en la linea presidencial (2.2, bloque 2, parte B).**
- La linea del tiempo 1988–2024 se vuelve simulador al modo de la 5.4: las seis torres nacen en cero y se levantan a su altura real con `requestAnimationFrame` y suavizado cubico, mientras el numero de obras y el costo del periodo cuentan en paralelo.
- Barra de control con solo dos mandos, como se pidio: «Evaluar los seis sexenios» y «Reiniciar a ceros». Sin casilla de evaluacion al pasar el cursor.
- Carril `.sim-seg-riel` de altura fija (92 px): la torre crece desde la base sin mover el resto de la loseta. Se retiran de `.sim-seg-torre` el `min-height: 12px` (impedia llegar a cero) y la `transition: height`, que competia con la animacion por fotograma.
- Las torres pasan de 12–46 px a 0–90 px, para que el crecimiento se lea.

**Hecho — la 2.2 pasa a subpestanas A / B / C y se recupera el filtrado fusionado.**
- Los bloques 2 y 3 dejan de apilarse: ahora son subpestanas dentro de la 2.2, con `#simTabs` y `state.simParte`. El bloque 1 (el pulso) se queda arriba, siempre visible.
- **Parte A, «Sector e industria»**: se recupera la forma de filtrar que se prefirio. El mosaico de industria y una tira nueva de pastillas de mandato (`renderSimuladorMandatoPills`) filtran **a la vez** sobre la misma lista, y las fichas de obra estan **siempre a la vista**, sin replegarse. Cada pastilla de mandato lleva el numero de obras que tiene dentro de la industria elegida, y se deshabilita si no tiene ninguna.
- **Parte B**: linea presidencial con su simulador sexenal y el simulador comparativo de las 12 obras.
- **Parte C**: las tres mesas de calculo, el inventario por sector, la escala y la procedencia.
- Se retira `state.simuladorDesglose` y toda la mecanica de replegar: «Quitar los filtros» devuelve las doce obras en lugar de esconderlas. `simVerSector` lleva ahora a la parte A con el sector puesto y salta a la ficha.
- Cambiar de subpestana no reinicia nada: el filtro es compartido, de modo que lo elegido en A sigue senalado en B y sigue rigiendo las mesas de C.

**Corregido — los filtros de la parte A se mataban entre si; cadena del filtro restituida.**
- **Defecto (reproducido):** con una industria elegida, cuatro de las siete pastillas de mandato llevaban `disabled` y no respondian al clic; simetricamente, al elegir un mandato quedaban desactivadas las industrias sin obras en ese periodo. El filtro parecia roto en ambas direcciones. Ahora ningun control se desactiva: el que no tiene obras se atenua y recupera opacidad al pasar el cursor.
- Cuando la combinacion queda vacia, la cuadricula muestra un aviso que lo dice con todas sus letras y ofrece dos salidas de un clic (ver ese mandato en todas las industrias, o esa industria en todos los mandatos). La escala deja de dibujar una tabla de ceros y explica que no hay monto que comparar.
- **Cadena restituida:** vuelve `renderSimuladorRankingFiltro()` a la parte A, entre las cifras del filtro y las fichas: «Las N obras del filtro, comparadas por …», con los cinco criterios de orden. El criterio es compartido con el simulador comparativo de la parte B, de modo que ordenar en un sitio reordena en el otro.
- El bloque de escala «Contra que se compara este dinero» baja de la parte C a la parte A, que es donde cierra la cadena: mandato e industria → comparativa → fichas vivas → escala.

**Hecho — motor de conteo en la parte A y reacomodo de A / B.**
- Motor de conteo compartido (`simAnimarZona`): cualquier elemento que declare `data-anim-v` (con `data-anim-f`: mdp, pct, pctS, pesos, entero) o `data-anim-w` arranca en cero y sube a su valor con `requestAnimationFrame` y suavizado cubico. Es el mismo mecanismo del simulador comparativo, generalizado.
- Las tres tarjetas del filtro (costo real, aprobado frente a erogado, perdida operativa anual) cuentan desde cero cada vez que cambia la industria o el mandato, incluidos sus subtextos: cuota, brecha, sobrecosto y pesos por segundo. Boton «↺ Contar de nuevo» en la cabecera para repetirlo a peticion.
- La comparativa del filtro hace lo mismo: al cambiar de criterio las barras nacen en cero y crecen, y los valores cuentan. Se ve la barra llegar a su porcentaje en lugar de aparecer puesta.
- `prefers-reduced-motion: reduce` entrega el dato de golpe, sin animacion. Verificado con `emulateMedia`.
- Las cifras animadas llevan `font-variant-numeric: tabular-nums` para que el renglon no baile mientras suben los digitos.
- **Reacomodo:** el simulador comparativo de las 12 obras baja de la parte B a la parte A, entre la comparativa del filtro y las fichas. La parte B queda terminando en el simulador sexenal. Queda una sola fila de criterios en A, rotulada «Ordenar y medir por», que gobierna las dos listas.

### Hecho (pestaña 6: Modo Inspector potenciado)
- **Objetivo declarado arriba de todo**, en tres pasos: elija a quién
  mirar, lea su círculo de salud financiera, contraste lo que se dijo.
  Con la lista de fuentes y la regla de que nada se estima.
- **Explorador de los tres niveles**: 8 entes federales, 32 estados y 83
  municipios —123 expedientes— con buscador por nombre, estado,
  municipio, partido o gobernante.
- **Círculo de salud financiera** en SVG generado por código, animado
  con la curva de siempre. Índice 0–100 de tres ejes con pesos
  declarados: autonomía 40 %, limpieza en la cuenta 35 %, holgura ante
  la deuda (o esfuerzo recaudatorio en municipios) 25 %. Las
  normalizaciones se imprimen en pantalla; el índice se declara como
  construcción propia, no como calificación crediticia ni dictamen ASF.
- **El nivel federal no lleva círculo, a propósito**: sus insumos son
  cifras redactadas y no series comparables entre una empresa del
  Estado, un ramo y un poder autónomo. Se dice en pantalla y se
  conserva su matriz de cuatro pilares.
- Abrir un ente federal **sincroniza** el selector del módulo de
  contraste, para auditar la afirmación contra el mismo ente.
- Ficha copiable en texto plano; el módulo de afirmaciones se conserva
  íntegro bajo un separador que lo anuncia como tercer paso.

### Hecho (nuevo orden de las subpestañas de la pestaña 2)
- 2.1 Maquinaria Financiera · 2.2 Inversión por Sectores · **2.3 El PIB
  No Alcanza** · **2.4 Calculadora Cívica** · **2.5 Bitácora y Alertas**.
- Se reordenaron también los paneles en el DOM, no sólo los botones, y se
  renumeraron sus comentarios y títulos internos.
- La mesa 3 de la 2.2 apunta ahora a «la calculadora cívica de la 2.4».

### Hecho (pastillas de mandato y arranque en ceros)
- **Defecto:** con un mandato de una sola obra (Salinas, Fox) la lista
  comparativa se escondía tras un aviso y parecía que el botón no
  respondía. Ahora se dibuja el renglón único, medido contra la obra
  mayor del universo, que es la única escala con sentido cuando no hay
  con quién comparar dentro del filtro.
- **Segunda causa, y es dato real:** Enciclomedia y la Refinería
  Bicentenario tienen `perdida_anual_mdp: 0`. Bajo el criterio por
  omisión su barra mide cero. Se añade un aviso que lo dice —cero de
  registro, no hueco— y ofrece el criterio de costo real.
- **Arranque en ceros.** Las tarjetas del filtro y la lista ya no cuentan
  solas: nacen en cero y sólo se llenan al pulsar «↺ Contar de nuevo» o
  «Evaluar». El arranque por cursor queda apagado por omisión.
- Con `prefers-reduced-motion` las cifras se entregan puestas, porque
  para esa persona la animación no es el medio de lectura.

### Hecho (bloque 2 de la 2.2: por qué 12 y no 13)
- Nuevo bloque de texto entre el pulso del gasto y las subpestañas A/B/C,
  numerado **2**, que explica el caso **FARAC**: concesionado por Salinas
  y rescatado por Zedillo, su registro dice «Carlos Salinas / Ernesto
  Zedillo», así que al repartir por mandato aparece en dos columnas y las
  seis torres de la parte B suman 13 sobre un universo de 12.
- Declara las tres opciones que había y por qué se eligió contarlo doble
  en lo político y una sola vez en lo monetario.
- La cabecera que abre las subpestañas queda numerada **3**.

### Hecho (fusión de las dos listas comparativas de 2.2 A)
- La parte A tenía dos listas que decían casi lo mismo. Ahora es **una
  sola**, que reúne las funciones de ambas:
  - de la lista del filtro: que la industria y el mandato la recorten, y
    que de ella cuelguen las fichas vivas y la escala;
  - del simulador comparativo: **Evaluar**, **Reiniciar a ceros**,
    **Activar al pasar cursor**, el arranque en cero con conteo, y
    **«Ver las 12 en contexto»**, que devuelve el universo completo con
    lo que queda fuera del filtro atenuado.
- El interruptor «en contexto» es lo que evita volver a tener dos listas:
  una misma lista, dos alcances. En esa vista, pulsar una obra atenuada
  pone su industria en el filtro.
- `simAnimarZona` acepta un aviso de término, para que la lista sepa
  cuándo pasar a «evaluación completada».
- Nuevas funciones: `simRankEvaluar`, `simRankReiniciar`,
  `simRankToggleHover`, `simRankHoverEntra`, `simRankUniverso`.

### Hecho (paso previo: retiro del simulador comparativo en 2.2 A)
- Se eliminó de la parte A el **simulador comparativo** completo (barra de
  «Evaluar / Reiniciar a ceros / Activar al pasar cursor», rótulo
  «Las 12 obras medidas por pérdida anual» y su lista del universo entero).
  Duplicaba la lectura de la comparativa que ya vive arriba.
- Queda una sola lista en A: **«Las obras del filtro comparadas por…»**,
  gobernada por los chips «Ordenar y medir por» y por los filtros de
  industria y mandato, con su conteo desde cero.
- Retirados: `renderSimuladorComparativo`, `simCompFormato`, `simCompObras`,
  `simCompEnFiltro`, `simCompHayFiltro`, `simCompEvaluar`, `simCompReiniciar`,
  `simCompToggleHover`, `simCompHoverEntra`, el estado `simCompEvaluado` /
  `simCompHover`, el div `#simComparativo` y las reglas `.sim-comp`,
  `.sim-comp-fuera`. Se conserva `simCompValor` porque lo usa la lista que
  se queda, y `.sim-comp-pres` por el pie de cada renglón.

### Hecho (1.1: las cifras de la panorámica arrancan en ceros)

- Los tres bloques de cifras de la subpestaña 1.1 —**«Cuánto dinero es»**,
  **«1 · De dónde sale»** y **«2 · En qué se va»**— dejan de aparecer
  puestas al abrir la pestaña. Nacen en cero y sólo se contabilizan a
  petición, con la misma mecánica que ya rige la 2.2 y la 5.4.
- **Dos mandos por bloque y nada más**, como se pidió: «Contabilizar» y
  «↺ Reiniciar a ceros». Sin arranque por cursor y sin criterios que
  elegir, porque aquí la cuenta es una sola y se lee de arriba abajo.
  Contenedores nuevos `#erarioTotalMandos`, `#ingresosMandos` y
  `#egresosMandos` en el HTML; barra generada por `erarioBarraMandos()`,
  que reutiliza `.evaluacion-controls-bar` sin estilos nuevos.
- Se anima **todo lo que es dato**: las cinco tarjetas de la cifra total y
  el porcentaje de deuda sobre el ingreso; y en las dos gráficas, el
  subtotal y el porcentaje de cada cabecera de grupo, el ancho de cada
  barra, el monto y el porcentaje de cada renglón.
- **Motor compartido, no uno nuevo.** Se usan `simAnimarZona` y
  `simPonerEnCeros` tal cual: misma curva, mismo suavizado cúbico, mismo
  respeto por `prefers-reduced-motion` y mismo valor exacto al cerrar,
  sin arrastre de redondeo. Funciones nuevas: `erarioSincronizarZona`,
  `erarioBarraMandos`, `renderErarioTotalMandos`, `renderFlujoMandos`,
  `erarioContar`, `erarioReiniciar`, `flujoContar`, `flujoReiniciar`.
- **Defecto corregido de paso: la unidad cambiaba a media cuenta.** La
  cifra de portada usaba `formatMoneyMdp`, que escribe en mdp por debajo
  del billón y en billones por encima. Al contar desde cero la tarjeta
  pasaba de «$0 mdp» a «$10.19 billones», y ese salto de unidad se lee
  como un salto del dato. Se añade el formato `billones`, de unidad fija
  de principio a fin. Es la misma regla que ya obligó a `formatMdpFijo`:
  dentro de una misma gráfica la unidad no cambia.
- **Segundo defecto corregido: la transición de CSS competía con la
  animación por fotograma.** `.fc-relleno` llevaba
  `transition: width 0.5s`, de modo que al cerrar el conteo la barra
  seguía creciendo por su cuenta. Mismo defecto que tuvieron las torres
  sexenales de la 2.2. Se retira mientras la barra la gobierne el motor
  (`.fc-relleno[data-anim-w]`).
- El `aria-label` de cada renglón conserva la cifra real: quien navega
  con lector de pantalla recibe el dato, no la animación.
- `eval-status-text` y `fc-grupo-monto` se suman a
  `AUTOLINK_OMITIR_CLASES`, por la regla ya establecida de que las
  etiquetas compactas y las celdas de dato no reciben nota al pie.
- Verificado en navegador: las tres zonas arrancan en ceros y con las
  barras a 0 %; los dos botones responden en los tres bloques; los
  porcentajes de ingreso suman 100.0 % y los de egreso 69.6 % + 30.4 %;
  el reinicio devuelve todo a cero; abrir el detalle de un renglón **no**
  borra la cuenta ya hecha; con `prefers-reduced-motion` el dato se
  entrega de golpe a los 60 ms; 0 desbordes en 32 anchos de 1600 a
  360 px; 0 errores de JavaScript; y el autoenlace de la 1.1 queda
  idéntico al de antes del cambio (11 enlaces de glosario, 11 notas al
  pie, 0 anidadas, 0 huérfanos).

### Hecho (1.1: el grupo de impuestos, completo y con fundamento)

- **Se acabó «Otros impuestos».** El renglón que agrupaba cuatro conceptos
  distintos se abre en los que la ley enumera, con la cifra oficial de cada
  uno: **Accesorios de impuestos** ($135,769.4), **ISAN** ($20,161.8),
  **Exploración y extracción de hidrocarburos** ($7,070.4) e **Impuestos de
  ejercicios anteriores** ($62.7). La gráfica pasa de 9 a 12 renglones.
- **Defecto de dato corregido, y era real.** La base daba $162,523.2 mdp a
  «Otros impuestos». El residual oficial es **$163,064.3**: faltaban 541.1
  mdp, que estaban inflando la línea de derechos, productos y
  aprovechamientos. Con la corrección el grupo Impuestos cierra en
  **$5,838,541.1 mdp**, exactamente el total del Artículo 1º de la LIF 2026,
  y el arreglo de ingresos sigue cuadrando al peso con `totalLIF`. Los 541.1
  los absorbe la línea marcada `derivado`, que es justo la que se obtiene por
  diferencia.
- **Fuente.** Ley de Ingresos de la Federación para el Ejercicio Fiscal de
  2026, Artículo 1º, publicada en el DOF el 7 de noviembre de 2025. Se
  descargó el texto de la Cámara de Diputados y se extrajeron las cifras del
  cuadro; la suma de los nueve rubros de impuestos reproduce el total
  publicado sin ajuste.
- **Cada impuesto responde ahora tres preguntas**, no una: qué grava (ya
  estaba), **qué efecto jurídico produce** (campo `efecto`, nuevo) y de dónde
  sale la cifra. La ficha lleva la clave del concepto en la LIF, el
  fundamento legal y dos botones: uno al **glosario** y otro a la
  **referencia** del catálogo de fuentes.
- **Desglose dentro del desglose.** Los rubros que la propia ley abre traen
  su tabla: el IEPS con sus **once** componentes —de combustibles
  automotrices ($473,279.1) a bebidas energetizantes ($100.2)— y comercio
  exterior con importación y exportación. Las once cifras del IEPS suman
  $761,501.9 al peso. Nacen en cero y cuentan al abrirse la ficha, con el
  motor `simAnimarZona`.
- **Bloque nuevo: «Y los que la ley enumera, pero deja en cero».** El
  Artículo 1º contempla impuestos **sobre el patrimonio** (1.12), **sobre
  nóminas** (1.15) y **ecológicos** (1.16), los tres presupuestados en $0.0.
  No se grafican —una barra de cero se lee como defecto de maquetación— pero
  se declaran con su explicación: no hay impuesto federal al patrimonio, el
  de nóminas es estatal, y los gravámenes ambientales que sí recauda la
  Federación viven dentro del IEPS.
- **Referencias 52 a 57**: Ley del ISR, Ley del IVA, Ley del IEPS, LIGIE
  2022 (con la Ley Aduanera y el art. 131 CPEUM), Ley Federal del ISAN y Ley
  de Ingresos sobre Hidrocarburos. Las seis URL se verificaron contra el
  portal de la Cámara de Diputados antes de citarse.
- **Glosario 155 → 163.** ISR, IVA e IEPS dejan de compartir una sola ficha
  agrupada y tienen la suya; se suman ISAN, Impuestos al Comercio Exterior
  (Aranceles), Accesorios de las Contribuciones, Impuesto por la Actividad de
  Exploración y Extracción de Hidrocarburos y Rezago Fiscal. El autoenlace se
  repartió en consecuencia: cada acrónimo apunta a su ficha y a su ley, no al
  Código Fiscal genérico.
- Los enlaces van en la **ficha de detalle**, no en el renglón de la gráfica:
  el renglón ya es un botón y anidar un enlace dentro rompe la navegación por
  teclado. Verificado: 0 enlaces dentro de botón.
- Verificado: los 8 renglones de impuestos abren ficha con efecto jurídico,
  enlace a glosario y enlace a referencia; el de glosario abre la ficha
  correcta en la pestaña 7 y el de referencia lleva a la 8; los porcentajes
  de la gráfica suman 100.0 % y los subtotales de grupo 57.3 % + 28.3 % +
  14.4 %; 14 enlaces de glosario con sus 14 notas al pie en la 1.1, 0
  anidadas; 0 desbordes de 1600 a 360 px; 0 errores de JavaScript.

### Hecho (1.1: los ingresos no tributarios, al mismo nivel)

- **Los cuatro renglones restantes reciben el trato de los impuestos**:
  efecto jurídico, clave del concepto en la LIF, fundamento legal, enlace a
  glosario y enlace a referencia. La 1.1 queda con **16 de 16 fichas**
  completas.
- **Corrección de clasificación, y era de fondo.** La base ponía las cuotas de
  seguridad social y los derechos bajo «No tributarios». El artículo 2º del
  Código Fiscal dice que las contribuciones son cuatro especies: impuestos,
  **aportaciones de seguridad social**, **contribuciones de mejoras** y
  **derechos**. Productos y aprovechamientos sí son no tributarios (art. 3º).
  Las familias pasan de tres a cuatro: Impuestos · Otras contribuciones ·
  No tributarios · Financiamiento.
- **Se acabaron las cifras derivadas en la gráfica de ingresos.** El renglón
  agregado «Derechos, productos y aprovechamientos» ($939,655.6, `derivado`)
  y «Organismos y empresas del Estado» se abren en los rubros que la ley
  enumera: contribuciones de mejoras $39.6, derechos $157,081.7, productos
  $16,488.3, aprovechamientos $203,520.5, venta de bienes y servicios
  $1,630,973.6 y transferencias del FMP $232,630.4. **Los 16 renglones son
  ahora `oficial`**: no queda una sola cifra obtenida por diferencia.
- **Corrección de vigencia.** La ficha decía «empresas productivas del
  Estado», figura creada en 2013. La reforma de 2024-2025 las convirtió en
  **empresas públicas del Estado**, con leyes propias publicadas el 18 de
  marzo de 2025.
- **Partidas que restan.** La ficha de deuda muestra los cinco componentes,
  dos de ellos negativos: los déficits de organismos (−$101,616.2) y de
  empresas públicas (−$284,154.8). Se dibujan **rayadas y con filo rojo**,
  escaladas por valor absoluto, con pie que aclara que la barra mide tamaño y
  no dirección. Es la misma solución que se aplicó a los negativos de la 5.4.
  La ficha deja ver que el bruto ($1,858,397.4 de endeudamiento interno) es
  mayor que el neto que aparece en la gráfica.
- **Defecto de forma corregido:** `formatMdpFijo` escribía «$-101,616». El
  signo va delante del peso, no entre el peso y la cifra.
- **El rótulo dejó de mentir.** Decía «Nueve orígenes componen el ingreso
  federal» con la gráfica mostrando dieciséis. Ahora lo pinta
  `renderFlujoConteo()` a partir de la base, así que no puede volver a
  desmentirse.
- **Referencias 58 a 62**: Ley del Seguro Social (con la del ISSSTE), Ley de
  Contribución de Mejoras por Obras Públicas Federales de Infraestructura
  Hidráulica, Ley Federal de Derechos, Leyes de la Empresa Pública del Estado
  (Pemex y CFE) y Ley del Fondo Mexicano del Petróleo. Las cinco URL
  verificadas contra el portal de la Cámara de Diputados.
- **Glosario 163 → 170**: Aportaciones de Seguridad Social, Contribuciones de
  Mejoras, Derechos (Contribución), Productos (Ingresos del Estado),
  Aprovechamientos, Empresas Públicas del Estado y Fondo Mexicano del
  Petróleo (FMP).
- Verificado: 16/16 fichas con efecto, glosario y referencia; los porcentajes
  de renglón suman 100.0 % y las cuatro familias 57.3 + 7.8 + 20.4 + 14.4;
  todos los desgloses cuadran con su renglón al peso; 0 desbordes de 1600 a
  360 px; 0 errores de JavaScript. Comparación estructural contra el commit
  anterior: 20 colecciones intactas, 57 referencias y 163 términos previos
  idénticos, `panoramaErario` sin cambios fuera de `ingresos`.

### Hecho (1.1: la ficha del renglón pasa a ventana lateral)

- **El desglose se abre como los argumentos particulares de la 5.2**:
  cubierta oscura, panel lateral que entra desde la derecha y cierre por
  Escape, por la cruz, por la cubierta o volviendo a pulsar el mismo
  renglón. Motivo: al nombrar los dieciséis orígenes con su clave de ley,
  su efecto jurídico y su desglose interno, la caja de debajo de la
  gráfica llegó a medir más que la gráfica que la invoca. Abrirla empujaba
  media página hacia abajo y obligaba a buscar otra vez el renglón que se
  venía leyendo. Verificado: la gráfica no se mueve un píxel al abrir.
- **Más ancha que las demás ventanas: 980 px** frente a los 740 del lateral
  estándar y los 780 del argumento de García Luna. La ficha trae tabla de
  componentes; a 740 px los nombres largos se partían en dos líneas.
- **Desplazamiento vertical propio**, con barra dorada
  (`scrollbar-color` sobre `var(--bg-void)`; se conservan las reglas
  `::-webkit-scrollbar` para los navegadores que aún no leen la propiedad
  estándar) y `scrollbar-gutter: stable` para que el texto no salte cuando
  aparece.
- **Dos franjas de aviso en los bordes**, encendidas por
  `flujoFichaSombras()` según el recorrido que quede: arriba si hay texto
  por encima, abajo si lo hay por debajo, ninguna si la ficha cabe entera.
  La barra del navegador no basta como aviso —en macOS y en el móvil se
  esconde hasta que alguien la mueve—. Primer intento: sombras por fondo
  con `background-attachment: local`. **No sirvió**: el fondo del
  contenedor queda detrás de las tarjetas opacas de la ficha y no se veía.
  De ahí el marco `.flujo-ficha-marco`, que es a quien cuelgan.
- **Defecto de tema corregido.** La cabecera de toda ventana lateral lleva
  un degradado oscuro fijo, igual en claro que en oscuro. Al llevar la
  cifra del renglón a esa franja, en tema claro `--text-main` es casi negro
  y **el monto desaparecía**. Los tonos de esa franja —y sólo de esa
  franja— quedan fijados en `.audit-drawer-ancha .drawer-header`.
- **Debajo de la gráfica queda la invitación**, una línea de 45 px que ya
  no empuja nada, en vez de la ficha entera.
- **Una ventana, un renglón encendido.** Saltar de un renglón de ingresos a
  uno de egresos apaga el primero: dos barras marcadas como activas con una
  sola ficha a la vista mentirían sobre el estado de la pantalla.
- **La cuenta sigue arrancando en ceros** y empieza 300 ms después de
  pulsar, cuando el panel ya entró: contar detrás del borde sería mover el
  dato donde nadie lo ve. Quien pidió menos movimiento recibe el dato de
  golpe, sin espera.
- **Accesibilidad**: `role="dialog"`, `aria-modal`, `aria-labelledby`,
  `aria-hidden` sincronizado, `aria-expanded` en cada renglón, el foco va a
  la cruz al abrir y vuelve al renglón al cerrar, y el fondo se bloquea
  mientras la ventana está arriba.
- **Los enlaces de la ficha cierran la ventana antes de saltar** (captura
  en `.glos-link, .ref-link, .fd-enlace`): si la ventana siguiera encima,
  el glosario o la referencia quedarían detrás de la cubierta y parecería
  que el enlace no hizo nada.
- **El texto de la ficha se autoenlaza aquí**, con `autolinkAmbito(p.body)`,
  porque la ventana cuelga del `<body>` y la pasada general sólo recorre el
  panel activo.
- **Otro rótulo que mentía**: los mandos de ingresos decían «frente al mayor
  de los nueve» con dieciséis renglones en pantalla. Ahora sale de la base.
- Verificado: la ventana abre, cierra por las cuatro vías y no se abre sola
  al volver a la pestaña; el cuerpo se desplaza hasta el tope; las franjas
  encienden y apagan donde deben y ninguna aparece si la ficha cabe;
  16/16 fichas con efecto, glosario y referencia; la cuenta arranca en
  $0 mdp y 0 % y llega al dato de la ley; 0 desbordes de 1600 a 360 px con
  la ventana abierta; las cuatro ventanas de argumento particular de la 5.2
  y las nueve pestañas siguen abriendo; 0 errores de JavaScript.

### Hecho (la pestaña 1 pasa de tres a cuatro subpestañas)

- **Nueva numeración.** 1.1 sigue igual · **1.2** se queda sólo con los
  estados · **1.3 es nueva**, dedicada al municipio · **1.4** es la que era
  1.3, la Constitución Económica. El eslabón municipal, que era el último
  bloque de la 1.2, se mudó a la 1.3 con subpestaña propia.
- **El tratamiento de la 1.1 se replicó en las dos.** Barras que nacen en
  ceros, dos mandos —«Contabilizar» y «Reiniciar a ceros»—, ficha lateral
  por renglón con fundamento, efecto jurídico, desglose y enlaces a
  glosario y referencias. **31 fichas** en la pestaña 1; 25 completas, las
  6 pendientes son las de egresos de la 1.1, que ya venían así.
- **Una sola maquinaria para las cuatro gráficas.** En vez de triplicar
  ciento veinte líneas, se extrajo un registro (`FICHA_CTX`) que dice, para
  cada vista, de dónde salen sus renglones, qué rótulo lleva su ficha y de
  qué color van sus barras. `renderFlujo` quedó como alias de
  `renderBarras`; `renderFlujoDetalle` se volvió `renderFicha`;
  `itemIngresoSel`/`itemEgresoSel` se volvieron el mapa `fichaSel`. La 1.1
  se verificó renglón por renglón después del refactor: 16/16 intactas.

#### Los datos: todo lo nuevo sale del PEF 2026 y de la LCF

- Se extrajo el **Presupuesto de Egresos de la Federación 2026** (PDF de
  8.6 MB, DOF 21/11/2025) con el extractor propio en Python puro —no hay
  `pdftotext` ni `pypdf` en el entorno—, y de ahí salieron el **Anexo 1**
  (gasto neto por ramo) y el **Anexo 22** (Ramo 33 fondo por fondo).
- **DEFECTO DE FONDO CORREGIDO.** La base traía «Ramo 33 — Aportaciones» en
  $1,127,075.3 mdp. El PEF cifra el Ramo 33 en **$1,041,892.9** y el
  **Ramo 25** en **$85,182.4**: la base sumaba dos ramos distintos bajo el
  nombre de uno. Ahora son cuatro renglones —28, 33, 25 y convenios— y los
  tres primeros son `oficial`. El total del gasto federalizado no se movió:
  $2,810,800.0 mdp.
- **Ramo 33 con sus ocho fondos, al peso**: FONE $546,396.8 · FORTAMUN
  $136,817.4 · FAIS $135,060.7 · FASSA $84,635.9 · FAFEF $74,754.9 · FAM
  $43,464.6 · FAETA $10,811.4 · FASP $9,951.1. Suman exactamente
  $1,041,892.906925. Se guardan con los seis decimales del PEF porque a una
  sola cifra decimal la suma cerraba en .8 y no en .9.
- **Ramo 28 sin cifras inventadas.** El PEF publica su total, no su reparto
  por fondo. En vez de estimarlo, la ficha muestra **cómo lo reparte la ley**
  —20 % de la RFP al Fondo General, 1.25 % al de Fiscalización, 1 % al de
  Fomento Municipal, 9/11 del IEPS de gasolinas, 100 % del ISR del personal
  local, 0.136 % a municipios de frontera— y una nota que dice qué falta y
  dónde se publica. Campo nuevo `reglas` y bloque `.fd-pendiente`.
- **Tercer distintivo de trazabilidad: `pendiente`.** Ni oficial ni derivado:
  dato que la fuente sencillamente no publica. Lo llevan las tres fichas de
  facultad municipal.
- **La 1.3 en cifras**: FORTAMUN $136,817.4 y FISMDF $118,689.4 (Anexo 22)
  son lo único que el PEF cifra como municipal. Aparte va la lista de lo que
  **la ley garantiza sin cifrar**: el ≥20 % del Fondo General (LCF art. 6º),
  el Fondo de Fomento Municipal (art. 2-A III), el IEPS de gasolinas
  (art. 4-A) y el 0.136 % de frontera y litoral (art. 2-A I). Y tres fichas
  de facultad del artículo 115 fracc. IV: predial, derechos por servicios y
  participaciones.
- **El punto ciego del tercer piso**, citado literal del artículo 115: «Las
  legislaturas de los Estados aprobarán las leyes de ingresos de los
  municipios […] Los presupuestos de egresos serán aprobados por los
  ayuntamientos». Es el único piso donde quien aprueba el ingreso no es
  quien responde por el gasto. Verificado contra el PDF de la CPEUM.
- **Glosario 170 → 180**: Gasto Federalizado, Recursos de Libre Disposición,
  Recursos Etiquetados, Sistema Nacional de Coordinación Fiscal, Hacienda
  Municipal, Ramo 25, FAFEF, FAM, FAETA y FASP.

#### Enlaces muertos en el catálogo de fuentes

Un barrido de las 62 referencias encontró **seis URL de diputados.gob.mx
rotas** (404). Una cita que no abre vale menos que ninguna, así que se
corrigieron todas y se recomprobaron: `ref-lcf` (Ley de Coordinación
Fiscal, la más citada por este cambio), `ref-lgcg`, `ref-laassp`,
`ref-lgmde`, `ref-lgdp` y `ref-lpcgpf`, esta última apuntada ahora a la
versión histórica entre las leyes abrogadas. **Las 62 URL de
diputados.gob.mx devuelven 200.** Las demás (DOF, CIEP, IMCO, INAI,
CourtListener) no son alcanzables desde este entorno y no pudieron
comprobarse.

**Pendiente de cotejo:** la Cámara publica hoy la Ley General de Deuda
Pública bajo el título **«Ley Federal de Deuda Pública»**, con el nombre
original como subtítulo, pero su PDF sigue diciendo «última reforma DOF
30-01-2018». No se renombró en la base porque el decreto que la renombra no
pudo citarse: el DOF no es alcanzable desde este entorno. Hay 8 menciones
en la base y 2 en `index.html` esperando esa comprobación.

#### Verificado

Las cuatro subpestañas abren; los mandos de las cuatro gráficas y de las
dos zonas por entidad arrancan en ceros y cuentan; el federalizado suma
100.0 % y $2,810,800 mdp; los ocho fondos del Ramo 33 cierran en
$1,041,893; la ficha del Ramo 28 muestra seis reglas y cero barras; los
selectores de entidad de la 1.2 y la 1.3 quedan sincronizados; la 1.4 sigue
pintando brújula, cuatro pilares y cadena; las cuatro ventanas de argumento
particular de la 5.2 y las nueve pestañas siguen abriendo; 0 desbordes de
1600 a 360 px; 0 errores de JavaScript. Comparación estructural contra el
commit anterior: 20 colecciones intactas, `estados` idéntica, los 170
términos previos del glosario sin cambios, `panoramaErario` sin cambios
fuera de `federalizado` y del nuevo `municipal`.

### Hecho (1.3: el padrón municipal completo, con cifras del INEGI)

El bloque «4 · Municipio por municipio» mostraba **83 municipios** de los
2,479 del país: cuatro de Jalisco, tres de Aguascalientes. Era una muestra
presentada como si fuera el padrón. Ahora están los **2,479**, entidad por
entidad, y cada uno con lo que de verdad ingresó.

**La fuente.** INEGI, *Estadística de Finanzas Públicas Estatales y
Municipales* (EFIPEM), conjunto de datos municipal, ejercicio 2024, cifras
definitivas. Es la única fuente nacional que desciende al municipio: ni el
Presupuesto de Egresos ni la Ley de Ingresos lo hacen. Se descargó el paquete
de datos abiertos (96 MB) y se extrajeron, para cada municipio, el total de
ingresos, participaciones, aportaciones, FORTAMUN, FISMDF, predial, ingresos
propios y el total de egresos. El padrón de nombres y claves viene del
*Catálogo de Entidades, Municipios y Localidades* del mismo instituto.

Vive en `assets/js/municipios-efipem.js` (258 KB), aparte de
`audit-database.js`, y expone `window.AUDIT_MUNICIPIOS`. Los valores están en
**pesos enteros**, copia fiel de la fuente; la conversión a millones y la
dependencia se derivan en el motor, para que el archivo de datos no contenga
ni una operación propia. Los 11,900 valores publicados se cotejaron uno a uno
contra el CSV original: cero diferencias.

**Lo que se corrigió de paso.** Las cifras que la base traía de esos 83
municipios eran aproximaciones. En los totales fallaban poco, pero en predial
fallaban mucho: Aguascalientes capital figuraba con $890 mdp y recaudó
$522.3; Campeche con $210 y recaudó $48.2; Los Cabos con $1,450 y recaudó
$648.0. Se sustituyeron por las oficiales en la colección `estados`, de modo
que el cajón estatal, el buscador y el círculo del inspector digan lo mismo
que la tabla nueva. Se reescribieron 389 campos y ninguno fuera del arreglo
`estados`.

Cinco municipios quedaron **sin cifra** en vez de con cifra inventada: las
cuatro alcaldías de la Ciudad de México que la base traía y Juchitán de
Zaragoza, que no rindió cuenta en 2024. Los tres consumidores de esos campos
llevan ahora guarda de nulo.

**Tres fichas que estaban en blanco, ya cifradas.** Las fichas de facultad del
artículo 115 prometían: «se incorporará cuando pueda citarse contra esa
fuente». La fuente llegó, y con ella:

| Ficha | 2024 | de dónde sale |
|---|---|---|
| Predial y contribuciones sobre la propiedad | $52,543.2 mdp | suma EFIPEM |
| Derechos por servicios públicos | $48,348.2 mdp | suma EFIPEM |
| Participaciones federales municipales | $268,861.2 mdp | suma EFIPEM |

Van marcadas **derivado**, no oficial: por la definición de la propia
plataforma, una suma de cifras publicadas no se lee directamente de un
documento. Cada ficha lleva un bloque nuevo, «Cómo se obtuvo esta cifra», que
dice que son 2,380 municipios de 2,479 y qué falta en la suma. Se añadió la
referencia **63**, `ref-inegi-efipem`.

**La Ciudad de México, dicha como es.** Sus dieciséis demarcaciones aparecen
en el catálogo pero nunca en la estadística municipal, en ningún año. No es
omisión del INEGI: el artículo 122, apartado A, fracción VI constitucional
manda que «sujeto a las previsiones de ingresos de la hacienda pública de la
Ciudad de México, la Legislatura aprobará el presupuesto de las Alcaldías». No
tienen la hacienda del 115. Ponerles un cero se leería como que no recibieron
nada; se les pone la explicación (`MUN_SIN_HACIENDA` en el motor).

**Forma.** Tabla y no reja de tarjetas: Oaxaca tiene 570 municipios y en
tarjetas serían veinte pantallas sin comparación posible. Trae buscador por
nombre (sin acentos), seis criterios de orden, resumen animado de la entidad
y ficha lateral por municipio —misma ventana que la de la 1.1, con su propio
`munFichaDrawer`—. La ficha conserva el dossier de la redacción para los 83
municipios que ya lo tenían, en bloque aparte y con filo rojo, para que no se
confunda con la cifra del INEGI.

**Tres defectos de rendimiento, medidos y corregidos.** Con 570 municipios,
tocar una cifra obligaba a recalcular la disposición de la tabla entera: 82.7
ms por cuadro, cinco veces el presupuesto de uno. Se corrigió con tres cosas:
`table-layout: fixed` con `<colgroup>` (que además quita el temblor de las
columnas mientras sube el contador), `content-visibility: auto` en las filas
—las que no asoman no se disponen— y un corte, `MUN_TOPE_ANIM = 130`: arriba
de ahí se cuenta el resumen, que sí está a la vista, y la tabla recibe su
cifra ya hecha. Animar 545 renglones que nadie ve costaba y no comunicaba
nada. De paso, `simAnimarZona` lee ahora los valores una sola vez en lugar de
releer `dataset` en cada cuadro, lo que beneficia a todas las zonas del
sitio. Medido: p90 de 83.3 ms a 16.8 ms.

**Nota sobre el entorno de prueba.** El navegador sin GPU de este contenedor
corre la página en reposo a ~47 ms por cuadro. Cualquier medición de
rendimiento hecha aquí debe compararse contra ese piso, no contra 16 ms.

### Hecho (1.1: las seis fichas de egresos, completas — y dos cifras corregidas)

Los seis renglones de «2 · En qué se va» tenían monto y una línea de
descripción, pero ninguno tenía efecto jurídico, fundamento, glosario ni
referencia. Ahora los seis los tienen, y la pestaña 1 cierra en **31 de 31
fichas completas**.

Todo se fundamentó contra texto primario, descargado y leído en esta sesión:
la Ley Federal de Presupuesto y Responsabilidad Hacendaria (última reforma
DOF 09-04-2026), la Constitución, la Ley de Coordinación Fiscal y el decreto
del Presupuesto de Egresos 2026.

| Ficha | Fundamento | Lo que se dice |
|---|---|---|
| Desarrollo Social | LFPRH 2º-XXVII y 28-II | La ley misma excluye pensiones y programas sociales universales del gasto ajustable (2º-XXIV Bis) |
| Gobierno | LFPRH 2º-XXVII y 28-II · CPEUM 126 | Los ramos autónomos reciben techo, no distribución: la Cámara no los reasigna |
| Desarrollo Económico | LFPRH 2º-XXVII y 28-II · CPEUM 25 y 28 | Pemex y CFE son dos tercios de la finalidad |
| Costo financiero | CPEUM 73-VIII · LFPRH 2º-XXV y XXVIII | El gasto neto total «no incluye las amortizaciones»: esto paga intereses, no capital |
| Participaciones | LCF 1º, 2º y 9º | Inembargables, salvo el 25 % afectable en garantía: la puerta de la deuda estatal |
| ADEFAS | LFPRH 54 · CPEUM 126 | Lo no devengado al 31 de diciembre no puede ejercerse; ADEFAS es la excepción |

**Dos cifras que no resistieron la comprobación.**

*Primera.* «Costo financiero» decía $1,571,652.6 mdp y ADEFAS $71,276.4. El
**Anexo 8 del decreto** —«Costo financiero de la deuda y otras
erogaciones»— cierra en $1,572,073,260,826, y el Ramo General 30 del Anexo 1
en $70,855,700,000. Ambas estaban desviadas **exactamente $420.7 mdp**, en
sentidos opuestos, de modo que el subtotal no programable salía bien y el
error se escondía. Quedan en la cifra del decreto, marcadas `oficial` en vez
de `derivado`, y el costo financiero estrena desglose exacto del Anexo 8:
Ramo 24 ($1,297,681.1), costo financiero de Pemex y CFE ($238,838.8), Ramo 34
de apoyo a ahorradores ($35,553.4) y Ramo 29 en ceros.

*Segunda.* «Gobierno» figuraba con $1,697,583.6 mdp y «Desarrollo Económico»
con $481,012.4. Estaban **intercambiadas**, y se demuestra con el propio
Anexo 1: Pemex ($517,362.1) y CFE ($554,567.5) suman $1,071,929.6 mdp, más
del doble de lo que la base asignaba a la finalidad que contiene energía. La
reconstrucción ramo por ramo confirma el orden correcto —Gobierno ≈ $493,068
frente a $481,012.4; Desarrollo Económico ≈ $1,644,048 frente a
$1,697,583.6—, dentro del 3 % en ambos casos, mientras que con la asignación
anterior el desfase de Desarrollo Económico era del 242 %.

La suma de los seis renglones sigue siendo exacta: $7,094,708.8 mdp de gasto
programable, $3,098,974.9 de no programable, **$10,193,683.7 de gasto neto
total**, los tres al peso del Presupuesto.

**Lo que queda dicho como pendiente.** La clasificación funcional no viene en
el decreto sino en los tomos analíticos de Hacienda, y los portales de la
Secretaría y del CEFP no se alcanzan desde este entorno. Las tres fichas
programables lo declaran en su bloque «Lo que aquí falta, y por qué»,
explican que la cifra se contrastó contra el Anexo 1 reconstruyendo la
finalidad ramo por ramo, y anuncian que se sustituirá por la del tomo
analítico en cuanto pueda citarse.

### Hecho (1.4: el Paquete Económico 2027, leído contra sus documentos)

La 1.4 tenía la parte dogmática —los artículos 25, 26, 27 y 28— y se quedaba
ahí. Ahora sigue con lo que el Estado hizo con esa facultad: el paquete que el
Ejecutivo entregó a la Cámara de Diputados el **8 de septiembre de 2026**.

**De dónde salen las cifras.** El portal `ppef.hacienda.gob.mx` responde 503
desde este entorno, igual que `transparenciapresupuestaria` y `cefp.gob.mx`.
La ruta que sí funciona es la **Gaceta Parlamentaria de la Cámara de
Diputados**, que publica el paquete íntegro el día que lo recibe:

```
https://gaceta.diputados.gob.mx/PDF/66/2026/sep/20260908-A.pdf   Ley de Ingresos
https://gaceta.diputados.gob.mx/PDF/66/2026/sep/20260908-B.pdf   Proyecto de PEF
https://gaceta.diputados.gob.mx/PDF/66/2026/sep/20260908-C.pdf   Criterios Generales
```

Esos PDF guardan sus objetos dentro de flujos comprimidos (`/Type/ObjStm`) y
separan líneas con `\r`, de modo que el extractor `pdftxt.py` de la sesión
anterior encontraba **cero** páginas. El módulo `pdfobjstm.py` del cuaderno de
trabajo resuelve ambas cosas: reindexa sin anclar a `\n` y descomprime los 228
flujos de objetos. Con eso salen 77 páginas de Criterios, 310 de Ley de
Ingresos y 254 del decreto, todas legibles.

**Qué se añadió.** Ocho bloques nuevos, numerados del 5 al 12 dentro de la
misma subpestaña, más el bloque de fuentes:

| Bloque | Contenido |
|---|---|
| 5 | El itinerario que manda la ley: seis fechas, del 1 de abril al Diario Oficial, cada una con su precepto textual |
| 6 | Marco macroeconómico y estimación de finanzas públicas, 2026 contra 2027 |
| 7 | En qué se irá: clasificación funcional, 20 programas sociales y 20 prioridades de inversión |
| 8 | **Simulador de sensibilidades** con los seis coeficientes oficiales de Hacienda |
| 9 | Las once medidas fiscales, ordenadas por lo que recaudan |
| 10 | Amortiguadores y pasivos contingentes |
| 11 | La senda 2026-2032 |
| 12 | Diez puntos ciegos |

**El simulador no inventa un solo coeficiente.** Los Criterios publican en su
página 48 un cuadro de sensibilidades: medio punto de crecimiento vale 30.2
mmp de recaudación, un dólar de petróleo 9.6 mmp, cincuenta mil barriles 21.8
mmp, veinte centavos de tipo de cambio 8.1 mmp de ingresos petroleros y 2.1 de
costo financiero, cien puntos base de tasa 37.9 mmp y cien puntos base de
inflación 1.3 mmp. Las seis palancas usan esos números y cada una lleva su cita
textual debajo. El simulador **hereda a propósito** la limitación que la propia
fuente declara: mide el efecto aislado de cada variable, sin interacciones, y
mantiene fijo el PIB nominal. Añadir interacciones exigiría inventar
coeficientes que nadie publicó.

El veredicto se mide contra el **artículo 17 de la Ley Federal de Presupuesto**:
sólo una desviación mayor al 2% del gasto neto total —$212,729.8 mdp— obliga a
la Secretaría a justificarse en el informe trimestral. La ley dice
«desviación», sin signo: recaudar de más también obliga a explicarse.

**Identidades que cuadran al peso** (comprobadas con el decreto en mano):

```
gasto neto total (art. 2 del PPEF)      10,636,488.1
  - diferimiento de pagos                 -121,400.4
  = gasto neto pagado                  10,515,087.7  ✔ cuadro II.6

total de la Ley de Ingresos (art. 1)    10,636,488.1
  - ingresos presupuestarios            -9,156,528.9
  = financiamiento                       1,479,959.2
  = déficit 1,358,558.8 + diferimiento 121,400.4     ✔

programable devengado 7,432,529.7 + no programable 3,203,958.4
  = 10,636,488.1                                      ✔
```

**Hallazgo que confirma el trabajo anterior.** El cuadro II.6 de los Criterios
trae la columna «2026 aprobado», y coincide al décimo con lo que la sesión
pasada se corrigió en la 1.1 a partir del Anexo 8 del PEF: costo financiero
**1,572,073.3**, ADEFAS **70,855.7**, participaciones 1,456,045.9, programable
devengado 7,094,708.8 y no programable 3,098,974.9. La corrección de aquella
sesión queda confirmada por una fuente independiente.

**Novedades de código.**

- `simFmt` gana dos formatos: `mmp` (miles de millones, la unidad de los
  Criterios) y `mdd` (millones de dólares). Convertir a la unidad de la casa
  escondería de qué documento viene el dato.
- Tres zonas de conteo nuevas en `ZONAS_SIMPLES`: `pefin`, `pegasto` y
  `pecolchon`, con su estado inicial en `state.zonaContado`.
- `renderPaquete2027()` se llama desde dentro de `renderConstitucionEconomica`,
  **antes** de `autolinkAmbito`, para que los términos hacendarios nuevos
  entren en el mismo barrido de autoenlace.
- Cuatro referencias nuevas: **64** Criterios 2027, **65** PPEF 2027, **66**
  Iniciativa de Ley de Ingresos 2027 y **67** comunicado 71 de Hacienda.
- Las barras nuevas llevan `[data-anim-w] { transition: none; }`, por el
  defecto ya conocido: una transición de CSS compitiendo con la animación por
  cuadro hace que la cuenta se vea a saltos.

**Lo que el paquete todavía no es.** Ley. La Cámara puede modificarlo hasta el
15 de noviembre. El bloque de fuentes lo dice con todas sus letras y anuncia
que la sección se contrastará contra el decreto publicado en el Diario Oficial.

### Hecho (1.1: la clasificación funcional, por fin citable, y una cifra que no era)

La investigación de la 1.4 trajo de rebote la fuente que a la 1.1 le faltaba.
Los Criterios Generales de Política Económica 2027 publican, en el cuadro de su
página 39, la **clasificación funcional del gasto programable** con una columna
«PEF 2026 aprobado». Es justo lo que las tres fichas programables declaraban
como pendiente: «no viene en el decreto, sino en los tomos analíticos».

**Lo que decía la base contra lo que publica la fuente** (miles de millones):

| Renglón | Antes | Criterios 2027, p. 39 |
|---|---:|---:|
| Desarrollo social | 4,916.1 | **4,929.4** |
| Desarrollo económico | 1,697.6 | **1,695.7** |
| Gobierno | 481.0 | **320.7** |
| Poderes, autónomos, INEGI y TFJA | — | **142.3** |
| Fondos de estabilización | — | **6.6** |
| Total | 7,094.7 | 7,094.7 |

El «Gobierno» de 481.0 no existía: la finalidad de la Administración Pública
Federal vale 320.7 y los poderes y órganos autónomos van en renglón aparte con
142.3. Juntos son 463.0, que es el 1.2% del PIB que la serie funcional
2020-2026 del mismo documento reporta para gobierno. La sesión anterior acertó
al invertir Gobierno y Desarrollo Económico —la dirección era esa— pero las
magnitudes venían de una reconstrucción, y ya no hace falta reconstruir.

**El bloque de egresos de la 1.1 pasa de seis fichas a ocho.** Las dos nuevas:

- **Poderes y órganos autónomos**, con el artículo 5º fracción I de la Ley
  Federal de Presupuesto, que enumera qué comprende la autonomía presupuestaria:
  aprobar su propio proyecto, ejercerlo sin sujetarse a las disposiciones de
  Hacienda, autorizar sus adecuaciones, pagar por su tesorería y determinar sus
  propios ajustes si caen los ingresos.
- **Fondos de estabilización**, con el artículo 19: los excedentes se destinan
  *primero* a cubrir el aumento del gasto no programable y sólo lo que sobre se
  reparte 25/65/10 entre FEIEF, FEIP e infraestructura de las entidades.

**Precisión.** La fuente publica en miles de millones, así que los cinco
renglones suman $7,094,700.0 mdp y no los $7,094,708.8 del cuadro de finanzas
públicas: 8.8 millones de redondeo de la fuente. La 1.1 lo dice en el subtítulo
del bloque y cada ficha lo repite en su «cómo se obtuvo». La cifra de portada
sigue siendo la del decreto, al peso.

**Hallazgo añadido a la 1.4.** El artículo 19 fracción IV define la «reserva
adecuada» de los fondos: 0.08 por la suma de impuestos totales y transferencias
del Fondo Mexicano del Petróleo estimados en la Ley de Ingresos para el FEIP, y
0.04 para el FEIEF. Con las cifras del artículo 1º de la Iniciativa de Ley de
Ingresos 2027 —$6,263,886.8 mdp de impuestos y $210,774.0 de transferencias—:

```
FEIP   meta legal  517,972.9 mdp   saldo 136,600.0   =  26.4%
FEIEF  meta legal  258,986.4 mdp   saldo  13,300.0   =   5.1%
```

Las dos tarjetas de amortiguadores y el punto ciego 8 lo llevan.

**De paso.** La ficha lateral repetía la misma cifra dos veces en todo renglón
por debajo del billón, porque `formatMoneyMdp` y `formatMdpFijo` devuelven lo
mismo en ese rango. La equivalencia ahora sólo se escribe cuando cambia de
unidad. Afecta a las cuatro vistas de fichas, no sólo a la 1.1.

### Hecho (1.4: el paquete, leído ahora contra sus textos legales)

Hasta aquí la 1.4 se apoyaba en tres anexos de la Gaceta Parlamentaria 7121:
la Ley de Ingresos, el decreto de Egresos y los Criterios. Resultó que el
paquete tiene **catorce**. El índice del día los enumera, y de ahí salieron
las dos iniciativas de reforma —ISR y Ley Federal de Derechos— que antes sólo
conocíamos por la descripción que los Criterios hacen de ellas.

**Lo verificado.** Las once medidas fiscales publicadas resisten el texto
legal: el tope del 96.67% con su variante del 99%, el umbral de cincuenta
millones y cinco ejercicios, el límite del 50% a las pérdidas con el plazo de
diez a quince años, la baja de intereses netos del 30% al 20%, la derogación
del Capítulo VI donde vivía el Régimen Opcional para Grupos de Sociedades, los
umbrales del RESICO con su opción de IVA al 7% sin acreditamiento, la
retención de intereses que pasa de 0.90% a 0.68% y la repatriación al 7.5%.
Ninguna hubo que corregir.

**Lo que el texto legal añade.** La exposición de motivos de la reforma al ISR
explica el mecanismo que faltaba: de las 318 mil empresas que no pagaron el
impuesto, 223 mil —el 70.3%— no lo hicieron porque sus deducciones igualaron o
superaron sus ingresos. Y mide el sesgo: las que más ISR pagan registran
operaciones con contribuyentes de perfil facturero en el 3.5% de sus
deducciones; las que menos pagan, en el 10%. De ahí sale el 96.67%, que no era
una cifra arbitraria. Los dos datos entran al punto ciego 4 y a la ficha de la
medida.

**El punto ciego nuevo, el once.** Cuatro de los catorce anexos se publican
como imagen escaneada, sin capa de texto: la reforma a la Ley Aduanera, las
dos leyes enteramente nuevas —la de Economía Digital y la catastral y
registral— y el informe sobre la facultad arancelaria. Los archivos del portal
de Hacienda sí traen texto, pero salen con los permisos bloqueados, incluida
la casilla de extracción para accesibilidad: la que consultan los lectores de
pantalla. Tres de los cuatro escaneados son leyes, y una toca la base del
predial.

**Un defecto que salió de paso.** El pie de cada punto ciego resolvía su
fuente con una cadena de ternarios que reconocía tres claves; cualquier otra
se acreditaba a los Criterios aunque el dato viniera de otro documento. Ahora
es una tabla, y los once pies citan lo que de verdad los respalda. Tres
referencias nuevas: 68 (reforma al ISR), 69 (reforma a la Ley Federal de
Derechos) y 70 (el índice de la Gaceta 7121).

### Hecho (1.4: los cuatro pilares se despliegan al pulsarlos)

Los articulos 25, 26, 27 y 28 venian los cuatro abiertos, asi que la
subpestana arrancaba con cuatro fichas completas -respuesta, facultad,
organo, ley secundaria, tres claves y punto ciego- antes de la primera cifra
del paquete economico. El lector llegaba cansado a lo que venia a ver.

Ahora la cabecera declara que articulo es, como se titula y que pregunta
contesta; lo demas espera al clic. Se usa el mismo acordeon que ya emplean
los puntos ciegos y el itinerario en esta misma subpestana, y la estructura
que la guia de accesibilidad recomienda: el encabezado envuelve al boton, con
`aria-expanded` y `aria-controls`. Al repintar se devuelve el foco al boton
pulsado, o el teclado quedaria a la deriva; y el cuerpo recien revelado pasa
por el barrido de terminos, porque no existia cuando corrio el anterior.

Los cuatro botones de la brujula siguen llevando a su pilar, y ahora ademas
lo abren.

### Hecho (1.1: de dónde sale, en qué se va y a dónde baja se pliegan)

La subpestaña abría con los tres capítulos desplegados a la vez: dos gráficas
con su simulador y un mapa con su columna de rankings, uno detrás de otro.
Entre el encabezado y el último punto ciego mediaban cinco o seis pantallas, y
quien llegaba buscando el mapa tenía que recorrerlas todas. Ahora cada capítulo
anuncia su nombre y espera el clic.

**Se pliegan por separado, no en acordeón.** Es la diferencia con los pilares de
la 1.4: allí abrir uno cierra el anterior, porque los cuatro artículos se leen
de uno en uno. Aquí el origen y el destino del dinero se leen comparándolos, y
cerrar uno para ver el otro le quitaría al lector justo la operación que la
subpestaña propone. Los tres pueden estar abiertos a la vez.

**El cuerpo se oculta, no se repinta.** También distinto de la 1.4. Dentro viven
un mapa de Leaflet y dos simuladores que nacen en ceros y suben cuando alguien
pulsa «Contabilizar»: volver a pintarlos al plegar el capítulo le borraría al
lector la cuenta que acaba de mandar hacer. Comprobado: se contabiliza, se
cierra, se reabre y las barras siguen donde estaban.

**Una corrección de estructura, de paso.** La barra de lentes y el área del mapa
vivían *fuera* de su bloque, como hermanos sueltos del subpanel: el encabezado
«3 · A dónde baja» no gobernaba nada más que su propio párrafo. Ahora quedan
dentro del cuerpo que ese encabezado despliega.

**El detalle que el cambio exigía.** Leaflet mide su contenedor cuando se
construye, y el mapa nace dentro de un cuerpo oculto: cree tener cero píxeles de
alto. Al abrir el capítulo se le pide volver a medir —`invalidateSize()`, el
mismo remedio que la plataforma ya usaba al cambiar de pestaña—. Medido en el
navegador: el lienzo pasa de 0×0 a 1140×646 y los 32 estados aparecen.

**El cuerpo no lleva relleno lateral**, a propósito: la gráfica y el mapa miden
abiertos exactamente lo mismo que cuando colgaban sueltos del subpanel. Un marco
alrededor del mapa habría supuesto una tarjeta dentro de otra —la barra de
lentes ya trae la suya— y le habría quitado cuarenta píxeles al territorio.

### Hecho (el sello de versión de las hojas y los guiones)

GitHub Pages sirve cada archivo con `cache-control: max-age=600`: el navegador
puede seguir enseñando la versión anterior hasta diez minutos después de
publicar, y más si el lector recarga de forma normal —una recarga revalida el
documento, pero no siempre sus dependencias—. El efecto práctico era que un
cambio publicado y correcto parecía no haber ocurrido.

Ahora las cinco dependencias de `index.html` llevan sello: `?v=20260921a`. Cada
publicación que toque `assets/` cambia la dirección del archivo y el navegador
no tiene nada cacheado que reutilizar.

**Hay que subir el sello a mano en cada cambio que toque `assets/`.** Es el
precio de no tener un paso de compilación. El formato es `AAAAMMDD` más una
letra cuando hay varias publicaciones el mismo día: `20260921a`, `20260921b`.
El guion `herramientas/sello.py` lo cambia en los cinco de golpe, sube también
el renglón del pie y comprueba que los saltos CRLF queden intactos. Sin
argumento dice cuál es el sello vigente y sugiere el siguiente.

**Y el sello, a la vista.** Al pie de la página, bajo el aviso de
transparencia, aparece «Versión publicada: 20260921b». Sin ese renglón no hay
modo de saber si quien reporta un problema está viendo lo que acabamos de
publicar o una copia guardada por su navegador: la respuesta deja de ser una
conjetura y pasa a ser un dato que el lector puede leer en voz alta.


### Hecho (1.1: las 32 entidades, una por una, bajo el mapa)

El mapa coloreaba y la columna lateral resumía los cinco extremos de cada
lado. Entre el quinto y el vigesimoctavo quedaban veintidós entidades que
nadie podía leer: se veían en el mapa como un tono, pero su cifra no aparecía
en ninguna parte. Ahora están las treinta y dos, ordenadas de mayor a menor
por la lente vigente, con su barra en proporción real y su cifra al canto.
Pulsar cualquiera abre su expediente, igual que en el mapa.

**Con los mandos de la casa.** Nacen en ceros y suben cuando alguien pulsa
«Contabilizar», como las gráficas de los bloques 1 y 2. La zona de conteo es
el cuerpo entero del bloque, de modo que la columna de extremos y el cuadro de
las 32 suben a la vez: es un solo bloque y se comporta como uno. Los dos mapas
—geográfico y cartograma— quedan intactos; no llevan cifra animable y el
barrido no los toca.

**Un registro de lentes en lugar de siete ternarios.** Cada renglón repetía
una cadena de condicionales para saber qué campo mirar, y **la lente de deuda
no figuraba en ninguna**: elegirla enseñaba, en silencio, el ranking de gasto
federalizado. Ahora hay una tabla —rótulo, campo, formato, si la métrica se
puede sumar— y añadir una lente no obliga a tocar el código que la pinta. La
deuda, además, trae su semáforo en cada renglón.

**Sumar sólo lo que se puede sumar.** En gasto, Ramo 28, Ramo 33, ASF y deuda
el primer recuadro es la suma de los 32 renglones; en gasto por habitante y en
dependencia federal sumar daría una cifra sin significado, así que el recuadro
es el promedio y el segundo la mediana. Las cuatro cifras del resumen van
marcadas como **derivadas**: se calculan aquí, no se leen de la fuente.

**El suelo de la barra, distinto en cada sitio.** La columna lateral conserva
su mínimo del 15 %: con cinco renglones y un solo extremo a la vista, una
barra fiel de dos píxeles no se vería. El cuadro de las 32, donde el lector sí
compara, usa la proporción real con un mínimo del 0.8 %, y un valor de cero
—Tlaxcala, sin deuda registrada— se dibuja sin barra.

### Hecho (2.4: la calculadora cívica, con el aparato legal de 2026)

La subpestaña repartía el dinero del lector entre **nueve rubros con
porcentajes escritos a mano y sin una sola fuente declarada** —27.6 % a
transferencias, 13.2 % a deuda, 12.8 % a pensiones…—. No venían de ningún
documento. Se retiraron por completo.

**Lo que hay ahora, en cuatro bloques.**

1. **Su ingreso.** Monto, periodicidad (al mes o al año), naturaleza (bruto o
   neto) y régimen fiscal, entre seis: sueldos y salarios, RESICO, actividad
   empresarial y profesional, arrendamiento, plataformas tecnológicas y *no sé
   en cuál estoy*, que sigue adelante con el supuesto de sueldos y lo declara
   en cada renglón. El campo admite «15,000», «15000» y «15 000».
2. **Lo que le retienen.** Cuatro cajas —bruto, ISR, cuotas del Seguro Social,
   neto— y la cascada renglón por renglón, cada uno con el artículo que lo
   funda. Debajo, el renglón de la tarifa en que cayó el lector con sus dos
   vecinos, para que se vea el escalón.
3. **A dónde iría cada peso.** Su ISR anual repartido con las proporciones de
   los ocho renglones del Presupuesto de Egresos 2026 que ya publica la 1.1.
4. **El reloj de la deuda y de lo perdido.** Cuatro cuentas anuales divididas
   entre habitantes o entre contribuyentes, en cinco cadencias, con un contador
   en vivo del acumulado nacional.

**De dónde sale cada número.** Las dos tarifas del ISR se transcribieron del
**Anexo 8 de la Resolución Miscelánea Fiscal 2026, DOF del 28 de diciembre de
2025** (apartado B fracción V la mensual, C fracción II la anual), descargado
del sitio del SAT. La tabla del RESICO está en el texto del **artículo 113-E**.
Las cuotas obreras vienen de cinco artículos de la **Ley del Seguro Social**
(25, 106 II, 107 II, 147 y 168 II b), que suman **2.375 %** del salario base
más **0.40 %** del excedente de tres UMA. La **UMA** ($117.31 diarios,
$3,566.22 al mes) del INEGI, DOF 9 de enero de 2026. El **salario mínimo**
($315.04 y $440.87) de la CONASAMI, DOF 9 de diciembre de 2025. El **subsidio
para el empleo** —el valor mensual de la UMA por 15.02 %, hasta $11,492.66 de
ingreso— del decreto publicado el 31 de diciembre de 2025.

**Dos reglas que dejan el descuento en cero, y que la primera versión no
tenía.** Al salario mínimo no se le retiene nada, y por dos leyes distintas: el
último párrafo del **artículo 96 de la Ley del ISR** prohíbe la retención a
quien en el mes únicamente percibe un salario mínimo, y el **artículo 36 de la
Ley del Seguro Social** ordena que en ese caso el patrón cubra íntegramente
también la cuota obrera. Sin ellas la calculadora le cobraba a un salario
mínimo $133.66 de impuesto y $224.46 de cuotas que la ley no le cobra.

**Tres decisiones de método.**

- **Las cuotas de seguridad social no entran en el reparto del gasto.** El
  artículo 2º del Código Fiscal las define como contribución con destino
  específico: no van a la bolsa común, no forman parte de la Recaudación
  Federal Participable y no se reparten a estados ni municipios. Repartirlas
  como gasto general habría repetido el error que este bloque vino a corregir.
- **El IVA se presenta como escenario, no como dato.** Cuánto IVA paga cada
  quien depende de en qué gasta, y parte del consumo está a tasa cero o exenta.
  El bloque lleva sello propio —«escenario, no dato»— y una barra que el lector
  mueve. Es el único renglón de la subpestaña que la plataforma no afirma.
- **La deducción no es dinero que salga del bolsillo.** La cascada la mostraba
  restada junto al impuesto, de modo que el arrendador parecía perder el 35 %
  que en realidad se queda. Ahora hay tres clases de renglón con su signo:
  movimientos (− y +), subtotales (=) y renglones que sólo explican cómo se
  llega a la base gravable (·).

**El cálculo desde el neto.** Quien conoce su depósito y no su sueldo escribe
el neto y la página busca el bruto por aproximaciones sucesivas. Se hace así, y
no despejando, porque la tarifa tiene once tramos, el subsidio un tope y la
cuota obrera dos bases distintas: una fórmula cerrada sería falsa.

**El puente desde la 2.2, corregido.** El botón llevaba una cifra de sobrecosto
por contribuyente al campo de un formulario que pide un ingreso —dos cosas
distintas leídas como una— y anunciaba la subpestaña 2.3. Ahora lleva al reloj
del bloque 4, que es donde esa cifra significa algo, y dice 2.4.

**Comprobado.** La prueba de la tarifa no compara contra cifras escritas a
mano: verifica que la cuota fija de cada renglón sea el impuesto acumulado de
todos los anteriores, que es la propiedad que el cuadro del Diario Oficial debe
cumplir. Los veintidós renglones de las dos tarifas la cumplen; la única
desviación son **dos centavos en el décimo renglón del cuadro anual**, que
vienen de la fuente y se comprobaron contra el PDF del SAT. Las tres cascadas
cuadran, los seis regímenes rinden cifra, el reloj avanza, el móvil de 390 px
no desborda y la consola no arroja errores.

### Hecho (el respaldo, listo para cambiar de plataforma)

El proyecto va a seguir desarrollándose en otras herramientas —Antigravity de
Google y Astra de OpenAI—, y el traspaso tenía una trampa puesta por este mismo
documento: la regla de oro mandaba `git pull origin main` y `git push origin
main`. **Es la rama equivocada.** Todo el trabajo vive en
`claude/funny-turing-imtm54`, que va treinta y siete commits por delante:
quien hubiera seguido la instrucción al pie de la letra habría clonado una
copia sin la calculadora cívica, sin el padrón municipal, sin las 32 entidades
bajo el mapa y sin el Paquete Económico leído contra sus textos legales. Habría
trabajado sobre un fantasma y creído que el trabajo anterior se perdió.
Corregido: la regla de oro nombra ahora la rama real, advierte de `main` y
prohíbe empujar ahí sin permiso.

**`AGENTS.md`, en la raíz.** Es el archivo que Antigravity, Astra/Codex,
Cursor y prácticamente cualquier agente salido de 2025 en adelante leen solos
al abrir el proyecto: el estándar abierto que sustituyó a los `.cursorrules` de
cada casa. Lleva seis apartados —la rama, el criterio editorial, cómo está
construido, las convenciones que rompen el archivo, los criterios de terminado
y el tono— en 5,769 caracteres. El tamaño no es capricho: Antigravity corta los
archivos de reglas a 12,000 caracteres, y el equipo de Codex documentó que
Astra rinde peor con archivos largos, porque todo lo que se carga siempre
compite con la instrucción del momento. Lo largo se queda aquí, en CONTEXT.md,
que el agente lee cuando lo necesita.

**`herramientas/sello.py`, dentro del repositorio.** El guion que sube el sello
de versión vivía en el cuaderno de trabajo de la sesión, que no viaja con el
código: la convención más fácil de romper era justo la que no tenía
herramienta que la sostuviera fuera de aquí. Ahora está versionado, encuentra
la raíz por sí mismo, preserva los CRLF, verifica que sigan siendo cinco
dependencias y un renglón al pie, y sin argumento dice cuál es el sello vigente
y sugiere el siguiente.

**`.gitattributes` con `* -text`.** Salió al revisar el traspaso y es el riesgo
más silencioso de todos. Los CRLF no están sólo en el disco: están dentro de
los objetos de Git. No había `.gitattributes`, y en Windows `core.autocrlf=true`
viene activado por omisión: el primer commit hecho desde ahí habría normalizado
las más de 48,000 líneas del proyecto. Donde debía verse un cambio de tres
renglones se habría visto un diff del tamaño del repositorio entero, y con él
se habría perdido la trazabilidad de qué se tocó y por qué —que en una
plataforma de fiscalización es justamente lo que hay que poder demostrar—.
`-text` apaga toda conversión y conserva los bytes tal cual, en cualquier
sistema y con cualquier configuración local.

Y una tabla de enlaces en la regla de oro: repositorio, rama, dirección
publicada, revisión abierta y copia comprimida, con el sello vigente al lado,
para que cualquiera pueda comprobar en diez segundos si lo que tiene delante es
la versión buena.

### Hecho (el primer lote de arreglos baratos)

Cuatro asuntos del inventario, escogidos por ser los de menor costo.

**La ley de deuda llevaba el nombre equivocado, y ahora está citada.** La
plataforma decía «Ley General de Deuda Pública» diez veces —ocho en la base y
dos en el HTML— contra una sola «Ley Federal». El pendiente llevaba tiempo
esperando una cita del Diario Oficial y por fin se consiguió: el texto vigente
que publica la Cámara de Diputados lleva al margen la nota **«Denominación de
la Ley reformada DOF 27-04-2016»**. El nombre vigente es **Ley Federal de Deuda
Pública**; el original, de la publicación del 31 de diciembre de 1976, era el
General. Corregidas las diez menciones, el acrónimo (LGDP → LFDP) y el
identificador interno de la referencia. La ficha de la referencia 04 no borra
el nombre viejo: cuenta el linaje completo, que es lo que manda el criterio
editorial sobre estructuras derogadas.

**Retirada la colección `impuestos`.** Nadie la leía desde que se reescribió la
2.4 y cargaba cifras hasta 33.3 % por debajo de la Ley de Ingresos 2026. Son
1,621 bytes menos de base y una trampa menos para quien la consulte.

**El icono de la misión de la pestaña 6 se encogía por debajo de su propio
contenido.** Era un elemento flexible sin `flex-shrink: 0`: la caja medía 28 px
y el glifo, 37. Con `flex: 0 0 auto` mide los 37 que necesita.

**Cuatro títulos que se repetían a sí mismos.** En las pestañas 3, 4, 6 y 7 el
encabezado del panel repetía el de la pestaña, en dos casos palabra por palabra
y con el número de módulo incluido. Ahora siguen el patrón que ya tenían las
otras cinco: la pestaña se nombra, el panel se titula.

| | Antes | Ahora |
|---|---|---|
| 3 | Poder Legislativo: Periodos de Sesiones, Elecciones… | Quién Aprueba el Dinero, y Cada Cuándo |
| 4 | Suprema Corte de Justicia de la Nación: Presupuesto… | El Poder que También se Fiscaliza |
| 6 | 6. Modo Inspector (Auditoría Forense Hacendaria en Vivo) | Contraste una Afirmación Contra su Fuente |
| 7 | 7. Preguntas, Glosario & Marco Legal Hacendario | El Diccionario del Dinero Público |

**Y uno que no era defecto.** El barrido señalaba la cabecera de los pilares de
la 1.3 como desbordada en 20 px. Al corregirla, la cabecera se encogió de 1,230
a 437 px: esos 20 px eran el sangrado completo con que la cabecera entra en el
relleno de su tarjeta, escrito a propósito con `width: calc(100% + 40px)` y
márgenes negativos. Revertido. Queda anotado para que nadie vuelva a
«arreglarlo»: una medición de desbordamiento no distingue un error de un
sangrado deliberado, y quien lo toque tiene que mirar la pantalla antes.

### Hecho (la copia local de Windows, integrada a la rama)

Del 23 al 25 de septiembre se trabajó en una copia local sin `.git` y nada se
empujó: la rama se quedó en `20260922c` mientras la copia llegaba a
`20260925a` (enciclopedia.html, Inspector ciudadano, carrusel de hallazgos,
`investigaciones/`). El ZIP `Auditavision_Plataforma_20260925.zip` se cotejó
contra la rama antes de integrarlo: parte del último commit remoto y conserva
sus arreglos. Dos títulos emergentes de `index.html` habían vuelto a decir «Ley
General de Deuda Pública»; se corrigieron a **Ley Federal de Deuda Pública**
(denominación reformada, DOF 27-04-2016), como el resto de la plataforma.

Se dejaron fuera, a propósito:

- `assets/img/caso-lista.jpeg` y `caso-tlaxcala.jpeg`: ninguna página los usa,
  e INSPECTOR-ENTREGA.md advierte que son capturas aportadas **sin licencia de
  redistribución**. Publicarlos en GitHub Pages sería publicarlos.
- Copias sueltas de la raíz (`audit-engine.js`, `auditavision.css`,
  `auditavision.html`, `* (1).html`, `crecimiento_gasto_sexenal.html`,
  `infografia_fiscal_mx.html`, `create_database.py`, `imagen obrador.jpeg`):
  ninguna página las enlaza y las dos primeras son versiones viejas de los
  archivos de `assets/`.
- Los cinco PDF del Paquete Económico (13 MB): son documentos públicos que se
  descargan de su fuente; el repositorio cita, no aloja.

### Hecho (2.6: lo que cuestan el Congreso y la Judicatura, con sus documentos)

Se integraron los dos libros de trabajo del autor, que ahora viven en
`investigaciones/`: `Auditavision_Poder_Judicial_2026.xlsx` y
`Auditavision_Desglose_2024.xlsx`. Se sumaron las cifras del Decreto PEF 2026
(DOF 21-11-2025), descargado y cotejado por su huella SHA-256 (`6db4a86b…`,
la misma que registra el libro judicial). Todo entra por
`herramientas/integrar_poderes.py`, que es idempotente y conserva los CRLF;
vuelve a correrse si cambian los libros.

- **Nueva colección `AUDIT_DB.poderes`.** Ramo 01 ($17,529.1 mdp) y Ramo 03
  ($70,005.6 mdp) por unidad, con proyecto contra aprobado (Anexo 32, DOF
  p. 108: la Cámara recortó $15,954.6 mdp al Judicial); capítulos por unidad
  responsable; la SCJN al 31 de agosto; el OAJ de abril a junio; los 32
  circuitos (pagos parciales, derivado); el ejercicio 2024 de Diputados y
  Senado auditado por la ASF; los 32 congresos locales (INEGI, CNPLE 2025), y
  dos congresos auditados. Cada registro lleva estado, documento y página.
- **Por qué 2024 en el Legislativo:** para 2026 solo existe el aprobado; 2024
  es el último año con gasto ejercido **y** auditado (Cuenta Pública 2024).
- **Subpestaña 2.6** en Acción Financiera (enciclopedia) y en el menú de la
  portada. Fondo sólido, 40 chips, 33 enlaces a documento con página.
- **Comparador «Tú vs Ellos» (2.4 B), corregido.** Decía que un ministro ganaba
  $206,948 al mes, más que la Presidencia, contra el art. 127. Ahora lee la
  remuneración total anual **neta** del Anexo 23 del PEF 2026 (Presidenta
  $2,073,878; Senado $2,037,848; Auditor Superior $2,037,546; Diputados
  $1,307,224) y, para la Corte, el Manual del PJF 2026 ($134,310 netos al mes,
  cifra parcial y así rotulada). Compara neto contra neto con el neto que el
  lector calculó en el Apartado A. Se retiró la tarjeta de «Gobernador
  promedio», que no tenía documento.
- **Ticket cívico:** dos renglones nuevos con lo que llega de su ISR a cada
  Poder (derivado; ya incluido en el reparto, no se suma).
- **Referencias:** 13 identificadores rotos corregidos (cuatro fallaban en
  silencio y dos abrían la ficha equivocada) y 10 notas que citaban una ley
  distinta de la que decían («Art. 134 CPEUM [02]» abría la LFPRH). Las fichas
  21 y 22 ahora apuntan a su documento exacto, y se sumaron las 71 a 75. Cero
  identificadores rotos en las dos páginas.
- **Glosario:** 8 términos nuevos con enlace automático (remuneración total
  anual neta, dieta, Ramo 01, unidad responsable, capítulo de gasto, muestra
  auditada, monto por aclarar, TEPJF).
- **Regreso del glosario:** vuelve a la palabra exacta que se pulsó, en el
  mismo lugar de la pantalla, y la marca un instante (antes quedaba unos 300 px
  desplazado).

### Hecho (estado de cuenta cívico, verificador 69-B y menú sin promesas vacías)

- **El ticket pasa a «Estado de Cuenta Cívico»** (2.4): cabecera con ciudad
  genérica en SVG (de noche o de día según el tema), folio, periodo, resumen
  de cuatro cifras (bruto, ISR, cuotas IMSS, neto), movimientos con barras, lo
  que llega a los Poderes y una línea «Ellos» (diputación federal, neto contra
  neto, Anexo 23). Dice en el propio documento que no es un comprobante
  fiscal. Las cuotas IMSS ya no se suman como «impuestos».
- **Imagen para compartir gratuita** (`descargarEstadoCuenta`): PNG de
  1080 × 1350 dibujado en canvas, sin librerías, en los dos temas.
- **Verificador de proveedores, lista 69-B del SAT** (pestaña Inspector):
  14,234 registros con corte al 31-12-2025, búsqueda por RFC o nombre, las
  cuatro situaciones explicadas (definitivo, presunto, desvirtuado, sentencia
  favorable) y el oficio y la fecha de publicación de cada una. Los datos
  viven en `assets/data/sat-69b.js` (1.5 MB, se descargan solo al usarlo) y
  se regeneran con `python3 herramientas/actualizar_69b.py`.
- **Menú superior:** de 11 «Próximamente» quedan 2 (descarga CSV y
  diccionario de datos). Los demás llevan a lo que ya existía: ComprasMX, el
  verificador 69-B, el treemap de ramos, las 32 entidades y los municipios de
  la Enciclopedia, las referencias y los canales de denuncia.
- **Enlaces a subpestañas:** `enciclopedia.html#pestaña/subpestaña` abre la
  subpestaña indicada.

### Hecho (lectura por capítulos: piloto en la 2.6)

- **Componente de capítulos** (`capMontar`, `capIr`, `capTodo`): toma los
  bloques de una sección y monta arriba un índice de tarjetas (número,
  título, cifra clave con su chip y una línea de resumen). Se lee un
  capítulo a la vez, con barra de avance y «anterior / siguiente»; un botón
  permite leer todo de corrido. Para usarlo en otra sección basta pasarle la
  raíz, una clave y la lista de tarjetas.
- **Piloto en la 2.6:** de 4,887 px de desplazamiento a un índice de 644 px.
  Las cifras de las tarjetas salen de la colección `poderes` (la de nómina,
  88.9 %, del renglón total del Ramo 03).
- **El estado de cuenta usa las fotos de la ciudad del autor** en la cabecera
  (noche o día, con un paneo lento), en la vista y en la imagen PNG.
- **Regreso del glosario más preciso:** la palabra se busca solo dentro de la
  subpestaña de origen y la posición se corrige tres veces mientras la página
  termina de acomodarse.

### Pendiente

- **Extender la lectura por capítulos** al resto de las secciones largas,
  empezando por la 2.2 (megaobras: 7,666 px y 3,451 palabras), la 1.1, la
  2.4 y el Inspector. Espera el visto bueno del autor sobre el piloto.
- **Fondos de ciudad:** el autor eligió a propósito una ciudad extranjera
  generada con IA para evitar problemas de derechos. Se conservan.
- **En teléfono, la barra superior fija ocupa cerca de un tercio de la
  pantalla** (marca, cinco menús, botones y buscador). Hay que compactarla.
- **Descarga CSV y diccionario de datos** siguen en «Próximamente».
- **«Búsqueda avanzada de contratos»** promete filtrar contrataciones por
  año, ramo y monto, y el Inspector no hace eso: reescribir o conectar con
  datos de ComprasMX.
- **La lista 69-B se actualiza a mano**: correr el script cada vez que el SAT
  publique un corte nuevo y subir el sello.
- **Las cifras viejas de las pestañas 3 y 4 contradicen a la 2.6.**
  `judicial_reservado` dice $78,327 mdp para el Poder Judicial (oficial:
  $70,005.6), $5,900 para la Corte ($5,208.7) y $68,627 para un CJF que ya no
  existe; la 4.2 y la 4.4 calculan «costo por ponencia», que el libro judicial
  marca como pendiente. `legislativo.federal` dice $9,282 mdp para Diputados
  (2026 aprobado: $9,602.7). Falta decidir con el autor si esas pestañas se
  reescriben con la colección `poderes` o se funden con la 2.6.
- **Las 1,056 auditorías municipales de la ASF** (hoja «ASF municipios» del
  libro 2024) pueden anclar los 83 montos municipales sin referencia de abajo.
- **Referencias no oficiales por sustituir:** 46 (columna de opinión de El
  Universal) y 38 (Barra Mexicana de Abogados). 14 fichas apuntan todavía a la
  página de inicio de su institución y no al documento.
**Auditoría del 26 de septiembre (versión 20260925a).** Lo agregado del 23 al
25 de septiembre no cumple todavía la regla editorial. Bloquean la versión
final, en este orden:

- **Imágenes de IA sin aviso.** 7 de 10 JPG de `assets/img/` traen C2PA de
  Google (`trainedAlgorithmicMedia`); el `alt` las presenta como lugares
  reales. Rotular «Ilustración generada con IA» o sustituir por fotos con
  licencia. La de «Palacio Nacional» no es el Palacio Nacional.
- **Cifras que no coinciden entre secciones.** `showcaseData` (motor) contra
  `simulador_megaobras`: Tren Maya $156,000 vs $120,000 mdp, AIFA +53.3 % vs
  +460.1 %, Dos Bocas $378,000 vs $350,000 mdp; costo de la deuda $1,388,400
  (carrusel) vs $1,572,073 mdp (radar) vs «más de $1.2 billones» (ficha
  Sheinbaum). El carrusel debe leer de la base, no llevar sus cifras.
- **«Erosión patrimonial» ($54,010.89/s).** Suma costo financiero (gasto legal,
  flujo) con observaciones ASF por aclarar (saldo) y probablemente cuenta dos
  veces al IPAB (FOBAPROA en megaobras y Ramo 34 en costo financiero).
  INSPECTOR-ENTREGA.md ya lo había retirado. Retirar.
- **Simulador de megaobras en pesos nominales 1988–2024**, sin INPC, con dos
  rescates financieros (FOBAPROA, FARAC) que hacen el 69 % de la «pérdida».
  Ninguna de las 12 obras tiene campo de fuente.
- **Noticias sin URL ni estado.** `not-02` fecha la aprobación del PEF 2026 el
  10 de enero de 2026; el art. 74-IV CPEUM fija el 15 de noviembre anterior.
- **Fichas presidenciales sin una sola fuente**, con acusaciones graves,
  `asf_monto_num` inventado para Salinas (5,000) y trato desigual a la
  presidenta en funciones. Riesgo legal.
- **Pase de $79/mes** que promete funciones inexistentes y habla de
  «lanzamiento electoral». Ocultar.
- **Vocabulario**: «Dictamen de auditoría forense», «Costo real auditado»,
  «Fuente oficial verificada», «Versión 3.3 Aprobada».

Diseño: texto sobre fotografía ilegible (axe: 10 y 18 fallas de contraste),
etiqueta de la cinta encimada, botón flotante sobre «Reiniciar a ceros», falta
`scroll-margin-top`, primera pantalla móvil ocupada por menú, 30 elementos
clicables sin teclado, dos cabeceras y tres marcas. Informe completo con
capturas: https://claude.ai/artifact/QmXudJvRc5Hs7kp3ZDrEzF

- **Los 83 montos observados por la ASF en municipios no llevan referencia.**
  El campo `observacionesASF` de `estados[].municipios[]` guarda un número
  —42, 15, 8…— y **ni un solo campo de fuente o de informe que lo sustente**:
  la búsqueda de `fuenteObservaciones` o `refObservaciones` en la base da cero.
  Alimentan el eje «limpieza en la cuenta» del círculo de salud financiera de
  la pestaña 6, así que un número sin respaldo se convierte en calificación.
  Hay que anclarlos al informe individual de la ASF que los reporta o marcarlos
  como pendientes en la ficha.

- **El poblacional de la 2.4 no lleva referencia puntual.** Los relojes dividen
  entre **134.4 millones de habitantes**, la proyección de CONAPO a mitad de
  2026. La base de datos abierta del Consejo no resultó accesible desde este
  entorno al integrar la cifra (la conexión se corta), de modo que la
  referencia al cuadro exacto de las *Proyecciones de la Población de México y
  las entidades federativas 2020-2070* queda declarada como pendiente en la
  propia ficha. El segundo denominador —63.2 millones de contribuyentes— ya
  venía marcado como pendiente en el catálogo macro y lo sigue estando.
- **La 2.4 no considera las exenciones del artículo 93 ni las deducciones
  personales.** No entran aguinaldo, prima vacacional, horas extra, gastos
  médicos, colegiaturas, intereses hipotecarios ni aportaciones voluntarias al
  retiro, y se supone un ingreso parejo los doce meses. Está dicho al pie de la
  subpestaña. Incorporarlas exigiría un formulario bastante mayor; la decisión
  de hasta dónde llegar es del autor.
- **El predial del régimen de arrendamiento no se conoce.** El artículo 115
  permite deducirlo además del 35 % a ciegas, pero haría falta el recibo del
  municipio. El impuesto que la calculadora muestra es, por eso, un techo.

- **Los 32 renglones no cuadran con el total nacional, y ahora se ve.** Salió
  al sumar el cuadro de entidades. El Presupuesto de Egresos cifra el gasto
  federalizado en **$2,810,800 mdp**; los 32 renglones de la base suman
  **$2,506,179 mdp**. Faltan **$304,621 mdp**, el 10.8 %. En el Ramo 28 la
  distancia es mayor: **$1,456,046 mdp** oficiales contra **$1,187,900 mdp**
  repartidos, un 18.4 %. La razón está en la propia base: el decreto publica el
  total de cada ramo, no su distribución estatal, y ésa la da a conocer
  Hacienda en acuerdos posteriores —la ficha del Ramo 28 ya lo advertía como
  pendiente—. Mientras tanto, **las cifras por entidad no tienen fuente
  citable**: no llevan chip de estado y no deberían llevar el de «oficial».
  El cuadro publica la diferencia al pie del resumen en lugar de callarla.
  Dos caminos: incorporar el acuerdo de distribución del Diario Oficial cuando
  esté, o marcar las 32 cifras como estimación y decirlo en la ficha. Lo
  primero es lo correcto; lo segundo es lo mínimo.

- **El Ramo 33 por entidad no se coteja todavía.** Los 32 renglones suman
  $1,114,100 mdp. El Presupuesto cifra el Ramo 33 en $1,041,892.9 mdp y el
  Ramo 25 en $85,182.4 mdp: juntos, $1,127,075.3 mdp. No consta si la cifra
  por entidad incluye el Ramo 25, así que esta lente no lleva la línea de
  cuadre que sí llevan gasto y Ramo 28. Resolverlo exige la misma fuente.

- **La leyenda del mapa de la 1.1 no dice la verdad.** Salió al probar los
  capítulos plegables, y es anterior a ellos: `legendCaption`, `legendMin`,
  `legendMid`, `legendMax` y `legendGradient` están escritos a mano en el HTML y
  **ningún renglón del motor los toca**. El rótulo dice «Gasto Federalizado
  Total» aunque el lector haya elegido Ramo 28, alertas ASF o dependencia
  federal, y las marcas de la escala son las palabras «Mínimo», «Medio» y
  «Máximo», sin cifra. El mapa sí cambia de color al cambiar de lente; lo que
  miente es el pie. Pendiente de decisión: rotular la escala con los valores
  reales de la métrica activa o retirarla.

- **La pestaña 9 necesita servidor.** Las tres funciones están completas en
  interfaz, pero el formulario y el foro guardan en `localStorage`: sólo en el
  navegador de quien escribe. Para que el portal sea de verdad un espacio
  público hace falta persistencia compartida, moderación y una política de
  datos. La interfaz ya lo advierte en vez de fingir lo contrario.

- **Fotografía e ilustración**: la plataforma sigue sin una sola etiqueta
  `<img>`. Las «figuritas» de 4.1 y 4.2 son iconos tipográficos y bloques de
  color. Antes de incorporar imágenes hay que decidir su procedencia (banco
  libre o ilustración propia): una imagen de origen dudoso desacredita tanto
  como un dato inventado.
- **Cifras presupuestales del Nivel 4 de 4.1**: las plazas y remuneraciones
  corresponden a la estructura de once ponencias y al tope salarial anterior.
  Hay una advertencia metodológica visible en la ficha. Deben contrastarse
  contra el Manual de Remuneraciones vigente antes de citarse.
- **Ramo 28 y Ramo 33 por entidad**: los totales federales de 2026 que hoy se
  muestran en la subpestaña 1.1 son los oficiales ($1,456,045.9 mdp y
  $1,127,075.3 mdp). Los montos **por entidad** de la colección `estados`
  corresponden a un corte anterior y suman totales distintos ($1,385,200 y
  $1,114,800 mdp). La base es internamente consistente, así que el mapa y los
  comparativos funcionan bien, pero la distribución entidad por entidad debe
  actualizarse contra el acuerdo de distribución publicado en el Diario
  Oficial el 12 de diciembre de 2025. Hasta entonces, la subpestaña 1.2 lo
  advierte en su bloque de fuentes.
- **Colección `impuestos`**: sus montos de ISR, IVA e IEPS son anteriores a la
  Ley de Ingresos 2026 y difieren de los que muestra `panoramaErario`. Alimenta
  la calculadora de la pestaña 2; conviene alinearla al tocar ese módulo.
- **Estilos en línea**: hay 1,326 atributos `style=` en el HTML. Ganan a
  cualquier regla de la hoja de estilos, que es justo el origen del problema
  de contraste en tema claro y de los párrafos demasiado anchos. Conviene
  migrarlos a clases por módulo conforme se vaya tocando cada pestaña.
- **Material gráfico**: la plataforma no tiene una sola etiqueta `<img>`.
  Falta la capa de fotografía, ilustración y animación prevista.
- **Cifra federal ejercida del proceso electoral judicial**: se publica como
  aproximada (≈$7,200 mdp) a la espera de la cuenta pública y de la
  fiscalización de la ASF.
- **Umbral de votos de la declaratoria general de inconstitucionalidad**: la
  ficha 4.6 la describe como «mayoría calificada» sin fijar el número, porque
  el art. 105 pasó de ocho a seis votos con la reforma de 2024 pero no se pudo
  verificar el texto vigente del art. 107 fracc. II (los portales del DOF, la
  SCJN y la Cámara de Diputados están bloqueados por el proxy). Precisar al
  tener acceso al articulado.
- **Riesgo disciplinario del precedente** (tarjeta `det-disciplina` de 4.6):
  se publica marcada como `análisis`, no como dato. Procede de crítica
  académica, no de un artículo que sancione expresamente el apartarse de un
  precedente. Si aparece la norma concreta, reetiquetar como `oficial`.
- **Decisión editorial abierta**: si las Salas suprimidas deben permanecer
  documentadas como estructura histórica o desaparecer del organigrama.

## Criterio editorial

Es una plataforma de fiscalización: **un dato inventado la desacredita entera**.

- Toda cifra debe poder rastrearse a una fuente oficial: ASF, SHCP,
  Transparencia Presupuestaria, Banxico, DOF, INE, Gaceta Parlamentaria.
- Si un dato no se puede verificar, se etiqueta como pendiente de verificación
  en vez de estimarse.
- Las estructuras derogadas se marcan con su vigencia en lugar de borrarse: la
  trazabilidad de qué cambió y cuándo tiene valor propio para el lector.

## Cómo verificar un cambio

No basta con que el archivo compile. Antes de dar por buena una modificación:

```bash
node --check assets/js/audit-engine.js     # sintaxis
python3 -m http.server 8000                # y abrir en el navegador
```

En el navegador, revisa que la consola no arroje errores, que la pestaña
afectada renderice y que los enlaces a glosario y referencias sigan resolviendo.


## Hito: Versión 20260924a — Telemetría en Vivo de Adeudos y Arquitectura Cívica

Actualización aprobada para dotar a la plataforma de operatividad forense en tiempo real y arquitectura dual, integrando los patrones de diseño cívico de **Civio (¿Dónde van mis impuestos?)**, **Operação Serenata de Amor** y **USAspending.gov**:

1. **Arquitectura Dual Operativa / Enciclopédica:**
   - `index.html` se consolida como la aplicación operativa focalizada en los módulos de acción directa: **1.1** (El Circuito del Dinero Público), **2.2** (Inversión & Megaobras Presidenciales), **2.4** (Calculadora Cívica & Ticket del Contribuyente), **6** (Modo Inspector Forense) y **7** (Glosario & 25 Preceptos Legales).
   - `enciclopedia.html` preserva íntegramente la obra completa de 9 módulos para consulta enciclopédica profunda.
   - Ambas interfaces están interconectadas mediante accesos en la botonera hero y en el pie de página.

2. **Radar Forense en Vivo · Conteo por Segundo de Adeudos y Deuda desde el Inicio de Sesión:**
   - La telemetría inicia su cronómetro en el instante en que el usuario abre la plataforma (`sessionStorage`), calculando la acumulación ininterrumpida de pasivos:
     - **Pérdida operativa de megaobras:** +$2,543.13 MXN / seg ($80,200.1 mdp anuales).
     - **Costo financiero de deuda soberana:** +$49,849.80 MXN / seg ($1,572,073.3 mdp anuales).
     - **Erosión patrimonial total:** +$54,010.89 MXN / seg.
   - Barra fija de telemetría de alta visibilidad con pulso animado, tiempo de navegación y acceso directo a los módulos.
   - Sincronización transparente con las tarjetas vivas del simulador 2.2 (`.sim-live-card-loss`) y el reloj de deuda de la calculadora 2.4.

3. **Esquema Proporcional del Erario (Inspiración Civio & USAspending):**
   - Incorporación del pipeline presupuestal visual: LIF ($10.19 B) → PEF ($10.19 B: 69.6% Programable / 30.4% No Programable) → Transferencias Federalizadas ($2.81 B a 32 estados y 2,479 municipios).
   - Barra apilada interactiva con porcentajes y montos oficiales del PEF 2026.
   - Bloques de equivalencias cívicas tangibles (costo de oportunidad: hospitales, becas universitarias y sobrecostos).

4. **Expedientes Forenses con Métrica de Sospecha (Inspiración Serenata de Amor):**
   - 6 casos documentados con dictámenes periciales de la ASF, hipervínculos oficiales y distintivos sancionatorios (FGR, pliegos pendientes, daño patrimonial).

5. **Pie de Página Reestructurado:**
   - Sustitución de listas estáticas por tres bloques de consulta: Principios Cívicos, Compendio Documental de Fuentes Oficiales (acceso directo a `enciclopedia.html#referencias`) y Glosario / Marco Normativo (25 preceptos legales).


## Hito: Versión 20260924g — Rediseño Institucional USAspending Explorer, Mega-Menús, Showcase Cívico y Desglose Bajo Demanda

Actualización integral del diseño web y la experiencia de usuario de Auditavisión, adoptando el estándar visual y funcional de **USAspending.gov** (Spending Explorer) según los esquemas y requerimientos de producción:

1. **Cabecera con Mega-Menús Desplegables Tipo USAspending:**
   - La barra de navegación superior cuenta con 4 pilares multinivel con paneles flotantes en 2 columnas:
     - **Búsqueda Forense:** Búsqueda avanzada de contratos federales, padrón de proveedores/contratistas (RFC), auditoría de adjudicaciones directas, dossiers de $51,024 mdp en irregularidades ASF y monitoreo de EFOS.
     - **Explorar los Datos:** Explorador del PEF 2026 ($10.19 B), perfiles de dependencias (SHCP, PEMEX, CFE, SEDENA, Bienestar), perfiles de las 32 entidades ($2.81 B federalizados), padrón de los 2,479 municipios y calculadora salarial.
     - **Descargar Datos:** Exportación personalizada en CSV/Excel, dataset municipal completo EFIPEM (INEGI), informes oficiales de la ASF y diccionario de datos.
     - **Recursos & Atlas:** Glosario hacendario, marco constitucional (Arts. 73, 74, 115, 134 CPEUM, LDF), fuentes oficiales verificadas y acceso al atlas de 9 módulos en la Enciclopedia.
   - Botón directo de compartir (`navigator.share` / portapapeles), insignia de autoría de Inspector Meteoro y selector de tema.

2. **Paleta Cromática Oficial (Azul Federal, Gris Pizarra y Crepúsculo Urbano):**
   - Transición de la paleta previa a los colores institucionales de fiscalización: Azul Marino Federal (`#002b5b`, `#07192f`), Gris Pizarra y Acero (`#334155`, `#475569`, `#64748b`), Blanco Hielo (`#f8fafc`) y acentos en Rojo de Auditoría (`#dc2626`).
   - Fondo urbano crepuscular translúcido con efecto de vidrio esmerilado (*frosted glass* con `backdrop-filter: blur(16px)`), permitiendo apreciar la profundidad del horizonte urbano de fondo tanto de día como de tarde-noche.

3. **Showcase Cívico: Carrusel Interactivo de Descubrimiento ("¿Descubre qué es?"):**
   - Incorporación de 5 fotografías documentales de alta resolución de la infraestructura pública mexicana:
     - **Tren Maya:** 1,554 km de vías y sobrecosto auditado de +230.1% ($156,000 mdp original vs >$515,000 mdp ejercido).
     - **Refinería Dos Bocas:** Complejo petroquímico y sobrecosto auditado de +136.2% ($8,000 MDD original vs >$18,900 MDD ejercido).
     - **Deuda Soberana & Palacio Nacional:** $1.38 billones de pesos anuales sólo en pago de intereses (+$49,849.80/seg).
     - **Aeropuerto Felipe Ángeles (AIFA):** Terminal aérea y sobrecosto final del +53.3% con subsidios operativos continuos.
     - **Salud y Educación (Ramo 33):** Distribución a municipios y $51,024 mdp pendientes de solventar ante la ASF.
   - Rotación automática cada 6 segundos, navegación con flechas y puntos, y ventana modal interactiva (`#descubrimientoModal`) con la radiografía forense oficial y botón directo para auditar el proyecto.

4. **Desglose Operativo Bajo Demanda ("Comienza a explorar"):**
   - La página inicial presenta una vista limpia y concisa: Cabecera → Radar Hacendario en Vivo → Auditoría en Imágenes → Cuadro de Fiscalización con 5 Tarjetas Maestras.
   - El espacio operativo profundo (pestañas, mapas de las 32 entidades, simuladores y tablas ASF) permanece plegado por defecto (`display: none`).
   - Al hacer clic en cualquier botón **"Comienza a explorar ➔"**, se desglosa suavemente en la parte inferior el módulo correspondiente con animación fluida, actualización cartográfica y scroll automático.
   - Incluye botón de control para volver a plegar: `[▲ Plegar desglose operativo y volver a la cabecera]`.

5. **Pie de Página Institucional Permanente:**
   - La sección de cierre con **Principio y Compromiso Ciudadano**, **Marco Legal y Constitucional**, **Fuentes Oficiales y Catálogo** y sello de versión se mantiene permanentemente visible al pie de la página.

6. **Invariantes Técnicas Conservadas:**
   - CRLF y lone CRs preservados rigurosamente: `index.html` (56), `auditavision.css` (1), `audit-engine.js` (2), `audit-database.js` (2).
   - Sello de versión: `20260924g`.


## Hito: Versión 20260924h — Controles de Visualización y Desglose Analítico del Radar Hacendario en Vivo

Actualización de diseño y experiencia de usuario para optimizar el confort visual del lector y permitir la fiscalización profunda bajo demanda:

1. **Controles de Visualización junto al Radar Hacendario en Vivo:**
   - Incorporación de un clúster de controles interactivos situado inmediatamente al lado de la insignia del radar y del cronómetro de sesión:
     - **Botón [👁️ Ocultar estadísticas] / [👁️ Mostrar estadísticas]:** Permite al usuario replegar o desplegar al instante las 3 tarjetas de telemetría activa (.radar-live-items). Al ocultarlas, la barra superior se compacta en una sola línea delgada y limpia, reduciendo el ruido visual para quienes prefieren una lectura enfocada en el contenido editorial o navegan en dispositivos móviles con pantalla reducida.
     - **Persistencia de sesión:** La preferencia de visibilidad del usuario se conserva en sessionStorage (auditavision_radar_stats_hidden), manteniéndose si el usuario recarga la página.
     - **Botón [📊 Desglosar cifras ▾] / [▲ Plegar desglose]:** Abre un panel desplegable de auditoría en profundidad (#radarDesgloseDrawer) que transparenta las operaciones matemáticas, ritmos temporales y fuentes documentales de cada concepto.

2. **Cajón de Desglose Forense en Profundidad (#radarDesgloseDrawer):**
   - **Tira de Ritmos Temporales:** Equivalencias del ritmo de erosión patrimonial (+,010.89/seg) proyectadas a escala de minuto (+.24 mdp/min), hora (+.4 mdp/h), día (+,666.5 mdp/día) y año (,703,297 mdp/año).
   - **Rejilla de 3 Columnas por Concepto:**
     - *Déficit Operativo de 12 Megaobras:* +,543.13/seg (,200.1 mdp/año) con desglose de Tren Maya, Refinería Olmeca (Dos Bocas), AIFA, Mexicana y Corredor Interoceánico, sustentado en informes financieros SHCP y Cuenta Pública ASF. Botón de acceso directo para auditar las 12 megaobras.
     - *Intereses y Costo Financiero de Deuda Soberana:* +,849.80/seg (,572,073.3 mdp/año) correspondiente al Anexo 8 del PEF 2026 y criterios de política económica SHCP/Banxico (15.4% del presupuesto total). Botón de acceso a calculadora cívica y costo de deuda.
     - *Irregularidades ASF Pendientes de Solventar:* +,617.96/seg (,024 mdp) dictaminadas en fiscalizaciones superiores de la ASF (68% en estados/municipios y 32% en dependencias federales). Botón de acceso a dossiers forenses.
   - **Barra de Acumulado Dinámico de la Visita:** Muestra en tiempo real cuánto se ha acumulado en déficit de megaobras, intereses de deuda y observaciones ASF exclusivamente durante el tiempo de navegación del usuario en la sesión abierta (#desgloseLiveTimer).
   - **Cierre y Accesibilidad:** Botón [▲ Plegar desglose], compatibilidad con tecla Escape y estados de accesibilidad ARIA completos.

3. **Invariantes Técnicas Conservadas:**
   - Saltos de línea CRLF preservados en todos los archivos.
   - Cuentas de lone CR intactas: index.html (56), enciclopedia.html (56), auditavision.css (1), audit-engine.js (2), audit-database.js (2).
   - Sello de versión actualizado: 20260924h.
   - Sincronización idéntica entre la raíz del repositorio y la carpeta auditavision/.


## Hito: Versión 20260924i — Reorganización del Cuadro a 4 Módulos e Integración de Diccionario y Atlas en la Cabecera Superior

Afinación de arquitectura cívica y ergonomía visual para focalizar el espacio de exploración operativa y jerarquizar los recursos de consulta dogmática:

1. **Cuadro de Fiscalización Ciudadana Focalizado en 4 Módulos Operativos:**
   - La cuadrícula central de exploración (.explorer-cards-grid) se consolida con exactamente **4 módulos de acción y auditoría directa**:
     - **Módulo 1:** Circuito del Dinero (LIF, PEF .19 B, Gasto Federalizado a 32 estados .81 B y municipios).
     - **Módulo 2:** Inversión & Megaobras (Sobrecostos reales de Tren Maya, Dos Bocas, AIFA y 12 proyectos estratégicos).
     - **Módulo 3:** Calculadora Cívica (Rastro de impuestos según sueldo e índice de los 2,479 municipios).
     - **Módulo 4:** Inspector Forense (Alertas de la ASF, expedientes de daño patrimonial y empresas facturadoras EFOS).
   - Se retira del cuadro la quinta tarjeta, logrando un balance visual simétrico de 4 columnas en escritorios (grid-template-columns: repeat(4, 1fr)).

2. **Integración de «Diccionario y Atlas» en el Menú Superior:**
   - La cuarta pestaña de la barra de navegación superior pasa a denominarse formalmente **«Diccionario y Atlas»** (#navItemRecursos).
   - Se fusiona e integra el Módulo 5 con el debido desglose de sus **3 subpestañas temáticas**, distribuyendo su contenido en un mega-menú de dos columnas:
     - **Columna 1 · Diccionario & Marco Legal (3 Subpestañas del Módulo):**
       1. **Glosario de Términos Hacendarios & Conceptos Clave:** Compendio enciclopédico de conceptos técnicos, deuda y PEF con buscador y filtros por categoría (abrirDiccionarioSubtab('faq-glosario')).
       2. **Marco Legal Hacendario & 25 Preceptos:** Artículos 73, 74, 115 y 134 de la CPEUM, LIF, LFPRH, Ley de Disciplina Financiera y Reforma Judicial (abrirDiccionarioSubtab('faq-marco-legal')).
       3. **Preguntas Frecuentes en Casillas Didácticas:** Consultas ciudadanas esenciales sobre el funcionamiento y fiscalización del gasto público (abrirDiccionarioSubtab('faq-preguntas')).
     - **Columna 2 · Atlas Normativo & Formación Ciudadana:**
       1. **Atlas Técnico en la Enciclopedia:** Acceso a los 9 módulos profundos del erario (enciclopedia.html).
       2. **Compendio de Fuentes Oficiales:** Trazabilidad documental de DOF, SHCP, ASF, Banxico, INEGI y Transparencia Presupuestaria.
       3. **Pase y Guías del Auditor Cívico:** Mecanismos de vigilancia comunitaria.
   - Nueva función del motor window.AuditEngine.abrirDiccionarioSubtab(subtabId): despliega el panel en el área operativa, activa la subpestaña seleccionada y desplaza la vista suavemente hasta su contenido.

3. **Conservación Íntegra de Contenidos e Invariantes Técnicas:**
   - Cero contenido eliminado: todos los textos, buscadores, preceptos legales y casillas se preservan intactos en su subpanel respectivo (#tab-panel-faq).
   - Saltos de línea CRLF preservados en todos los archivos.
   - Cuentas de lone CR intactas: index.html (56), enciclopedia.html (56), auditavision.css (1), audit-engine.js (2), audit-database.js (2).
   - Sello de versión actualizado: 20260924i.
   - Sincronización idéntica entre la raíz del repositorio y la carpeta auditavision/.


## Hito: Versión 20260924j — Actualización Formal de Denominaciones en las 4 Pestañas Superiores

Alineación terminológica y jerárquica de la navegación institucional en la barra superior (site-top-nav) de Auditavisión:

1. **Denominación Definitiva de los 4 Pilares Superiores:**
   - **Pestaña 1:** **«Búsqueda Forense»** (conserva su denominación: búsqueda avanzada de contratos, padrón de proveedores, adjudicaciones directas y dossiers ASF).
   - **Pestaña 2:** **«Acción Financiera»** (renombrada desde «Explorar los Datos»: homologa la denominación técnica del erario, concentrando el explorador del PEF .19 B, megaobras, perfiles de las 32 entidades y calculadora cívica).
   - **Pestaña 3:** **«Descargar Datos»** (conserva su denominación: descargas de datasets en CSV/Excel, base municipal EFIPEM INEGI e informes de Cuenta Pública).
   - **Pestaña 4:** **«Consultar Recursos»** (renombrada desde «Diccionario y atlas»: concentra el compendio dogmático con el desglose de las 3 subpestañas operativas —Glosario, 25 Preceptos Legales y Preguntas Frecuentes en Casillas— junto al Atlas Técnico en la Enciclopedia y fuentes oficiales).

2. **Consistencia de la Barra de Pestañas Operativa:**
   - La barra de navegación de módulos (#mainTabbar) y los metadatos dinámicos del motor (TAB_METADATA['faq']) reflejan la denominación unificada **«Consultar Recursos»**, garantizando que el usuario identifique el mismo concepto tanto en el mega-menú de cabecera como en la mesa de trabajo de fiscalización.

3. **Invariantes Técnicas Conservadas:**
   - Saltos de línea CRLF preservados en todos los archivos.
   - Cuentas de lone CR intactas: index.html (56), enciclopedia.html (56), auditavision.css (1), audit-engine.js (2), audit-database.js (2).
   - Sello de versión actualizado: **20260924j**.
   - Sincronización idéntica entre la raíz del repositorio y la carpeta auditavision/.

## Hito: Versión 20260924k — Traslado de la Función 1 («Ayúdanos a fiscalizar») a la Plataforma Principal como Drawer Lateral

Integración de la herramienta de contraloría social y buzón cívico de la **Pestaña 9 (Función 1)** de la enciclopedia en la plataforma principal (index.html), estructurada como la función oficial de retroalimentación ciudadana con despliegue en drawer lateral deslizante:

1. **Mecanismo de Despliegue en Drawer Lateral:**
   - Panel lateral deslizante (#ayudanosFiscalizarDrawer) con clase .audit-drawer que hereda el mecanismo de los argumentos particulares de la Pestaña 5.2 (#garciaLunaArgumentoDrawer, etc.).
   - Telón de fondo oscuro con desenfoque (#ayudanosFiscalizarOverlay, .audit-drawer-overlay).
   - Cierre unificado mediante botón ✕ (.drawer-close-btn), clic en el telón de fondo y pulsación de la tecla Escape.
   - Control de scroll del cuerpo de página (document.body.style.overflow = 'hidden' / '').

2. **Doble Punto de Acceso (Disparadores de Retroalimentación):**
   - **Botón en Barra Superior (site-top-nav):** Se añade el botón .nav-action-btn.nav-feedback-btn con etiqueta 📢 Ayúdanos a fiscalizar en el bloque de acciones de cabecera junto a «Compartir».
   - **Botón Flotante (.floating-feedback-container):** Se actualiza el botón flotante inferior para denominarse 📢 Ayúdanos a fiscalizar, disparando la apertura del drawer lateral.

3. **Herramienta Cívica Íntegra (Función 1 de Pestaña 9):**
   - Orientación sobre privacidad y anonimato: resguardo 100% local en el navegador del usuario sin transmisión de datos sensibles.
   - Caja metodológica *«Qué vuelve útil un reporte»* (Qué, Dónde, Cuándo, Con qué dinero, Con qué prueba).
   - Formulario cívico #comunidadForm con selector de tipo de participación, selector de entidad federativa auto-poblado con las 32 entidades oficiales (poblarSelectorEntidades()), campo de texto con contador dinámico de caracteres hasta 1,000 (#comCharCount) y mensajes de estado (#comStatusMsg).
   - Módulo de historial local #comentariosListContainer para consultar observaciones guardadas en localStorage, copiarlas al portapapeles con redacción formal para canales oficiales (copiarObservacion) o eliminarlas (orrarObservacion).

4. **Invariantes Técnicas Conservadas:**
   - Saltos de línea CRLF preservados en todos los archivos.
   - Cuentas de lone CR intactas: index.html (56), enciclopedia.html (56), ssets/css/auditavision.css (1), ssets/js/audit-engine.js (2), ssets/js/audit-database.js (2).
   - Sello de versión actualizado: **20260924k**.
   - Sincronización idéntica entre la raíz del repositorio y la carpeta uditavision/.

## Hito: Versión 20260924l — Integración del «Portal Digital» al lado de «Consultar Recursos»

Integración de la herramienta cívica de la **Pestaña 9 (Función 3: Portal Público Digital · ¿Quieres Dialogar o Replicar?)** de la enciclopedia en la plataforma principal (`index.html`), configurada como el quinto pilar en la navegación superior al lado de «Consultar Recursos» y como pestaña operativa con ágora cívica, debates y réplicas:

1. **Quinto Pilar en la Barra Superior (`site-top-nav`):**
   - Incorporación de **«Portal Digital»** (`#navItemPortal`) inmediatamente a la derecha de «Consultar Recursos».
   - Mega-Menú temático (`#menuDropdownPortal`) con dos columnas:
     - **Ágora Cívica & Diálogos:** Acceso directo al Portal Digital (`seleccionarModuloExplorer('portal')`), salto rápido a publicación de postura (`#portalNuevoDebateForm`) y a la lista de discusiones con réplicas (`#portalFilterBar`).
     - **Garantías Cívicas & Formación:** Garantía de privacidad sin datos personales (100% anónimo con nick libre) y enlace documental a las 6 puertas oficiales de denuncia y decálogo auditor en la Enciclopedia.

2. **Acceso en la Barra de Pestañas Operativa (`#mainTabbar`):**
   - Se añadió el botón `<button role="tab" data-tab="portal"><span class="num">🌐</span>Portal Digital</button>`.
   - Al activarse, la cabecera dinámica `#tabintro` se actualiza con los metadatos correspondientes (`TAB_METADATA['portal']`) y se muestra el panel operativo.

3. **Panel Operativo Íntegro (`#tab-panel-portal`):**
   - **Banner Hero & Garantías de Privacidad:** Badges de protección cívica (100% sin datos personales, acceso con seudónimo, debate de ideas y fuentes).
   - **Formulario Creador de Nuevo Debate (`#portalNuevoDebateForm`):** Nick o pseudónimo con generador aleatorio `🎲` (`generarRandomNick()`), selector de tema, selector de postura con botones interactivos (`#portalStanceGroup`: Matiz, A Favor, En Contra, Aporte), título / tesis, desarrollo con contador de 1,200 caracteres (`#portalCharCount`), fuente oficial y publicación con `submitNuevoDebate(event)`.
   - **Barra de Filtros Temáticos (`#portalFilterBar`):** Chips de filtrado interactivo por eje temático (Presupuesto, Megaobras, SCJN, Personajes, Deuda & Banxico, Todos).
   - **Contenedor Dinámico de Debates & Réplicas (`#portalDebatesListContainer`):** Tarjetas de debate sembradas y locales con apoyo cívico (`likeDebate`), despliegue de hilos (`toggleReplyBox`), respuestas directas anidadas (`submitReplica`), enlace directo para compartir (`copyDebateLink`) y enlace contextual para auditar los datos de la plataforma vinculados al debate (`irAPestanaDesdeDebate`).

4. **Invariantes Técnicas Conservadas:**
   - Saltos de línea CRLF preservados en todos los archivos.
   - Cuentas de lone CR intactas: `index.html` (56), `enciclopedia.html` (56), `assets/css/auditavision.css` (1), `assets/js/audit-engine.js` (2), `assets/js/audit-database.js` (2).
   - Sello de versión actualizado: **20260924l**.
   - Sincronización idéntica entre la raíz del repositorio y la carpeta `auditavision/`.

## Hito: Versión 20260924m — Correcciones del Módulo 1 (Jerarquía Limpia y Unificación Editorial)

Optimización de la experiencia de usuario y arquitectura visual del Módulo 1 con base en las observaciones y correcciones señaladas en `correcciones modulo 1 .png`:

1. **Reubicación de Control de Repliegue al Fondo (Recuadro Rojo):**
   - Se retiró la barra superior `.barra-plegar-container` del inicio de `#seccionDesgloseModulos`.
   - Se reubicó al pie del espacio operativo como `.barra-plegar-inferior`, permitiendo que el usuario mantenga el control tras culminar la lectura del contenido de fiscalización para colapsar el desglose y volver suavemente a la cabecera.

2. **Eliminación de la Franja Intermedia `#moduloActivoArea` (Recuadro Morado):**
   - Se suprimió el bloque `#moduloActivoArea`, eliminando la duplicidad de pestañas intermedias (`#mainTabbar`) y pastillas de metadatos (`.prov`), las cuales ya están debidamente reflejadas en las 4 tarjetas del hero, en el radar hacendario, en el pie de página y en las referencias oficiales (APA 7).
   - Se retiró el buscador `#globalSearchInput` de este punto, quedando reservado para su reubicación en la plataforma sin interferir en el flujo operativo.
   - En el motor (`audit-engine.js`), `seleccionarModuloExplorer(tabKey)` ahora desplaza la vista suavemente directo al inicio del panel del módulo seleccionado (`#tab-panel-${tabKey}`).

3. **Unificación Editorial del Módulo 1 «El Circuito del Dinero Público» (Recuadro Verde):**
   - Se eliminó el bloque externo `#tabintro` y la subpestaña solitaria `1.1 El Circuito del Dinero Público: De Dónde Sale y En Qué se Va`.
   - Se unificó la apertura de la sección en un único encabezado editorial limpio (`.section-hero`):
     - Kicker de capítulo: *«Panorámica del Erario · Ejercicio Fiscal 2026»*.
     - Título único: *«1. El Circuito del Dinero Público»*.
     - Párrafo integrado que articula de manera fluida las cuatro etapas del gasto: LIF ($10.19 billones), PEF ($10.19 billones), transferencias a las 32 entidades y 2,479 municipios ($2.81 billones entre Ramo 28 y Ramo 33) y revisión ante la ASF en Cuenta Pública.
     - Conexión inmediata y sin repeticiones con el esquema arquitectónico de las 3 etapas (`civic-flow-schematic`).

4. **Invariantes Técnicas Conservadas:**
   - Saltos de línea CRLF preservados en todos los archivos.
   - Cuentas de lone CR intactas: `index.html` (56), `enciclopedia.html` (56), `assets/css/auditavision.css` (1), `assets/js/audit-engine.js` (2), `assets/js/audit-database.js` (2).
   - Sello de versión actualizado: **20260924m**.
   - Sincronización idéntica entre la raíz del repositorio y la carpeta `auditavision/`.

## Hito: Versión 20260924n — Correcciones del Módulo 1-B (Simulador Contable, Termostato de Salud Financiera y Citas Oficiales)

Implementación exhaustiva de las correcciones anotadas en `correciones modulo 1 - b.png` para el Módulo 1 (El Circuito del Dinero Público):

1. **Simulador Contable del Flujo Presupuestal en 3 Etapas (Recuadro Morado):**
   - Las tres etapas (Ingresos Totales LIF, Destino Federal PEF y Transferencias Federalizadas) y sus desgloses ahora inician por defecto en ceros (`$0.00 Billones`, `$0.00 B`, `0.0%`).
   - Incorporación de la barra de mandos `.evaluacion-controls-bar` (`#flujoContableMandos`) con sello «SIMULADOR CONTABLE DEL FLUJO», estado dinámico y botones «Contabilizar» y «Reiniciar a ceros».
   - Animación armónica suave (curva cúbica de ~1200ms vía `requestAnimationFrame`) que cuenta desde $0 hasta los valores objetivo ($10.19 B en LIF, $10.19 B en PEF y $2.81 B en transferencias).
   - Incorporación de las citas y fundamentos legales oficiales entre corchetes: LIF `[10]`, ISR `[52]`, IVA `[53]`, IEPS `[54]`, Endeudamiento neto `[04]`, PEF `[11]`, Gasto Programable `[02]`, Ramos 28 y 33 `[05]`.

2. **Simulador de Salud Financiera y Desglose Proporcional del PEF 2026 (Recuadro Naranja / Rojo):**
   - Se implementó la sección interactiva `.salud-erario-seccion` con su barra de mandos dedicada (`#saludErarioMandos`), sello «TERMOSTATO HACENDARIO & PROPORCIONES» y controles «Contabilizar» / «Reiniciar a ceros».
   - **Barra Proporcional Apilada Dinámica:** Inicia en ceros (`$0.0 MDP / 0.0%`) y crece animada al contabilizar: Gasto Programable (69.6% / $7.09 B), Costo Financiero de la Deuda (15.4% / $1.57 B), Participaciones Ramo 28 (14.3% / $1.46 B) y Adefas/Otros (0.7% / $70.9 mdp), con total dinámico acumulado a $10,193,683.7 MDP (100%).
   - **Termostato de Salud Financiera Circular (SVG):** Dial circular con aro reactivo animado mediante `stroke-dashoffset` (`0` a `54 de 100`), chip de rigidez (`🟡 Margen Frágil / 54/100`), diagnóstico fiscal en vivo sobre la rigidez del 30.4% ineludible y tres micro-indicadores paramétricos (Deuda 15.4%, Programable 69.6%, Federalismo 14.3%).
   - Al pulsar «Reiniciar a ceros», el dial, los porcentajes y las barras retornan suavemente a ceros.

3. **Citas Oficiales, Enlaces a Glosario y Nota Metodológica de Equivalencias (Recuadro Tres):**
   - **Hospitales:** Enlace a glosario «Costo Financiero de la Deuda» y cita de ley `[04]` (Ley Federal de Deuda Pública) para los 2,850 hospitales generales de zona.
   - **Becas:** Enlace a glosario «Gasto Federalizado» y cita `[05]` (Ley de Coordinación Fiscal) para las 12.5 millones de becas universitarias anuales.
   - **Sobrecosto:** Cita `[07]` (Auditoría Superior de la Federación) para el sobrecosto y subsidio por segundo del Tren Maya.
   - **Nota Metodológica al Pie (`.civio-equiv-nota`):** Justificación de costos paramétricos oficiales (IMSS HGZ-144 camas a $550 mdp, becas Benito Juárez superior a $33,600 anuales y auditorías de la ASF), con accesos directos al Glosario Hacendario y al Catálogo de Referencias Oficiales.

4. **Ficha Flotante Modal de Referencias Legales (APA 7):**
   - Se implementó `#modalFichaReferencia` en `index.html`. Al pulsar cualquier cita `[04]`, `[05]`, `[10]`, `[52]`, etc., se despliega una ficha modal con la cita APA 7 oficial, fundamento legal, enlace directo a los documentos en el DOF / Cámara de Diputados y botón para explorar la enciclopedia, con cierre vía botón o tecla Escape.

5. **Invariantes Técnicas Conservadas:**
   - Saltos de línea CRLF preservados en todos los archivos.
   - Cuentas de lone CR intactas: `index.html` (56), `enciclopedia.html` (56), `assets/css/auditavision.css` (1), `assets/js/audit-engine.js` (2), `assets/js/audit-database.js` (2).
   - Sello de versión actualizado: **20260924n**.
   - Pruebas completas en navegador Edge headless vía CDP (Runtime evaluate, animaciones de contabilización y reseteo validadas al 100%).
   - Sincronización idéntica entre la raíz del repositorio y la carpeta `auditavision/`.

## Hito: Versión 20260924o — Encabezado Fijo y Buscador del Navegador en Barra Superior

Implementación de las correcciones solicitadas a partir del archivo anotado `correcciones encabezado fijo y navegador buscar.png`:

1. **Encabezado Fijo y Adhesivo (.site-top-nav · Recuadro Verde):**
   - Se configuró `.site-top-nav` con `position: sticky; top: 0; z-index: 1010;` tanto en modo oscuro como en modo claro.
   - Refuerzo de fondo con efecto cristal (`backdrop-filter: blur(16px)`), sombreado y transición suave para garantizar perfecta legibilidad al desplazarse hacia abajo o hacia arriba a lo largo de toda la plataforma cívica.
   - Los mega-menús contextuales (`Búsqueda Forense`, `Acción Financiera`, `Descargar Datos`, `Consultar Recursos`, `Portal Digital`) se mantienen completamente anclados y accesibles durante el desplazamiento.

2. **Buscador Inteligente del Portal Navegador (#globalSearchInput · Recuadro Morado):**
   - Se reestructuró el extremo derecho de la barra de navegación en un contenedor vertical de dos niveles (`.nav-right-container`):
     - Nivel superior (`.nav-right-actions`): Botones de acción existentes intactos (`Ayúdanos a fiscalizar`, `Compartir`, `Inspector Meteoro`, `Tema`).
     - Nivel inferior (`.nav-search-wrap`): Casilla del buscador universal `.search-command-bar.nav-search-bar` con ícono `🔍`, input estilizado `#globalSearchInput` con placeholder `"Buscar estado, municipio, ramo, presidente o ley..."` y dropdown flotante `#searchResultsDropdown` (`z-index: 1060;`).
   - Se optimizó `initSearch()` en `assets/js/audit-engine.js`:
     - Búsqueda en 32 estados y 2,479 municipios: al seleccionar, se despliega automáticamente la sección `#seccionDesgloseModulos` (`display: block` y clase `desglose-abierto`), se abre el drawer estatal/municipal y se enfoca el contenido.
     - Búsqueda en Glosario Hacendario: redirige a `goToGlossary(termino)`.
     - Búsqueda en Ramos PEF: salta al desglose presupuestal del PEF.
     - Búsqueda en Mandatarios / Presidentes: salta al módulo de personajes políticos.
     - Búsqueda en Debates del Portal Digital: salta a las tesis cívicas ciudadanas.
     - Soporte para tecla `Escape` para cerrar resultados.

3. **Invariantes Técnicas Conservadas:**
   - Saltos de línea CRLF preservados en todos los archivos.
   - Cuentas de lone CR intactas: `index.html` (56), `assets/css/auditavision.css` (1), `assets/js/audit-engine.js` (2), `assets/js/audit-database.js` (2).
   - Sello de versión actualizado a **20260924o** en todas las referencias de `index.html` y `enciclopedia.html`.
   - Banco de pruebas automatizado en navegador real (Edge headless vía CDP) validando al 100% las 8 pruebas: anclaje adhesivo (`position: sticky`, `top: 0px`, `z-index: 1010`), persistencia en scroll (1000px), interactividad del input, apertura de resultados, despliegue de módulos y 0 errores en consola.
   - Sincronización idéntica entre la raíz del repositorio y la carpeta `auditavision/`.
   - Paquete de entrega ZIP: `Auditavision_EncabezadoFijoYBuscador_20260924o.zip`.


## Hito: Versión 20260924q — Treemap Proporcional del PEF 2026 (USAspending) & Banderas Rojas Forenses ASF (Serenata de Amor)

Implementación integral de las herramientas visuales y analíticas inspiradas en los portales líderes de fiscalización del gasto público:

1. **Treemap Proporcional del PEF 2026 (Estilo USAspending Spending Explorer):**
   - Árbol presupuestario jerárquico oficial de 3 niveles en `assets/js/audit-database.js` (`treemapPEF`):
     - **Nivel 1 (7 Funciones Macro - $10.19 Billones):** Desarrollo Social ($4.93B · 48.4%), Desarrollo Económico ($1.67B · 16.4%), Costo Financiero de la Deuda ($1.39B · 13.6%), Participaciones a Estados y Municipios Ramo 28 ($1.39B · 13.6%), Gobierno y Seguridad ($495k mdp · 4.9%), ADEFAS y Pasivos ($173k mdp · 1.7%), Poderes y Órganos Autónomos ($152k mdp · 1.5%).
     - **Nivel 2 (Ramos y Dependencias):** Secretaría de Bienestar ($579.8k mdp), IMSS ($1.47B), SEP ($450.2k mdp), CFE ($545k mdp), PEMEX ($510k mdp), SEDENA ($259.4k mdp), SICT ($140.5k mdp), etc.
     - **Nivel 3 (Programas Insignia Clave):** Pensión para el Bienestar de Adultos Mayores ($482.9k mdp), Becas Benito Juárez ($131.9k mdp), Pensiones IMSS ($980.5k mdp), Generación Eléctrica CFE, etc.
   - Navegación *drill-down* interactiva mediante clic con barra de migajas (*breadcrumbs*) y botón de retorno al nivel superior.
   - Selector de vista integrado en `#eb-egresos`: alterna al instante entre `[🟦 Treemap Proporcional (USAspending)]` y `[📑 Lista de Barras]`.
   - Bloques proporcionales con tema cromático por sector, porcentajes respecto al PEF total y del bloque, descripción oficial y chips normativos.

2. **Detector de Banderas Rojas ASF en Estados y Municipios (Estilo Operación Serenata de Amor / Rosie):**
   - Algoritmo analítico forense `obtenerBanderasRojasEstado` y `obtenerBanderasRojasMuni` evaluando:
     - 🔴 **Monto Crítico ASF:** Observaciones por solventar > $500 mdp a nivel estatal o > $15 mdp a nivel municipal.
     - 🚩 **Adjudicaciones Directas:** Porcentaje oficial de compras otorgadas sin licitación pública en adquisiciones estatales.
     - 🚩 **Dependencia Extrema:** Entidades con más del 88% de ingresos federalizados y débil recaudación local.
     - 🚨 **Semáforo de Deuda SHCP:** Estados en semáforo Amarillo (en observación) o Rojo (elevado).
   - **Expediente Estatal (Drawer Lateral `#auditDrawer`):** Integrado en `index.html` y `enciclopedia.html` con el panel `#dRedFlagsPanel` mostrando el desglose de alertas categorizadas y conteo de riesgos.
   - **Tarjetas Municipales (`.muni-card`):** Insignias forenses visibles (`.muni-flag-pill`) indicando el estatus de auditoría y montos observados.
   - **Radar Nacional de Banderas Rojas en Módulo 4 (`#tab-panel-verificador`):** Rejilla panorámica interactiva con el Top 6 de estados con mayores irregularidades acumuladas y acceso directo a su expediente.

3. **Invariantes Técnicas y Aseguramiento:**
   - Saltos de línea CRLF preservados en todos los archivos del repositorio.
   - Cuentas de lone CR intactas: `index.html` (56), `enciclopedia.html` (56), `assets/css/auditavision.css` (1), `assets/js/audit-engine.js` (2), `assets/js/audit-database.js` (2), `CONTEXT.md` (0).
   - Sello de versión incrementado a **20260924q** en todas las referencias de `index.html` y `enciclopedia.html`.
   - Paquete de respaldo generado: `auditavision_actualizado_20260924q.zip`.

## Hito: Versión 20260924r — Supresión de Subpestañas Redundantes en Módulo 2 y Módulo 3

Implementación de las correcciones solicitadas en las capturas anotadas `correciones modulo 2.png` y `correciones modulo 3.png`:

1. **Supresión del Bloque de Pestañas (.subtabs-bar · Recuadro Morado):**
   - Se eliminó el contenedor `.subtabs-bar[data-parent="accion-financiera"]` que albergaba los dos botones:
     - `Inversión Estratégica, Megaobras & Simulador de Pérdidas`
     - `Calculadora Cívica del Contribuyente`
   - Al estar Módulo 2 ("Inversión & Megaobras") y Módulo 3 ("Calculadora Cívica") claramente definidos e individualizados desde las tarjetas maestras del explorador y desde la navegación superior, esta barra de pestañas resultaba redundante y generaba confusión visual.
   - Ahora, tanto el Módulo 2 como el Módulo 3 inician de inmediato con sus respectivas cabeceras hero (`section-hero`), manteniendo una estética limpia, coherente y unificada con los Módulos 1, 4 y 5.

2. **Optimización del Desplazamiento en Navegación:**
   - En `assets/js/audit-engine.js`, se actualizó la función `seleccionarModuloExplorer(tabKey)` para enfocar directamente el subpanel activo (`simulador-megaobras` o `calculadora`), garantizando un desplazamiento suave y preciso a la cabecera del módulo seleccionado.

3. **Invariantes Técnicas Conservadas:**
   - Saltos de línea CRLF preservados en todos los archivos.
   - Cuentas de lone CR intactas: `index.html` (56), `assets/css/auditavision.css` (1), `assets/js/audit-engine.js` (2), `assets/js/audit-database.js` (2).
   - Sello de versión actualizado a **20260924r** en todas las dependencias de `index.html` y `enciclopedia.html`.
   - Pruebas automatizadas en Edge headless vía CDP ejecutadas al 100% (verificación de inexistencia de `.subtabs-bar` en DOM, activación de paneles y 0 errores en consola).
   - Paquete de entrega ZIP: `Auditavision_SupresionPestanasMod2y3_20260924r.zip`.


## Investigación preparatoria: calculadora cívica y fiscalización ASF — 20260924

- Entregable: [Base de investigación](investigaciones/base-calculadora-civica-finanzas-asf.md), con alcance confirmado: Poder Legislativo, gobiernos estatales, ayuntamientos y cabildos para integrar gradualmente la calculadora cívica.
- Incluye cuatro expedientes comprobados de ASF (Diputados y Senado CP 2024; distribución de participaciones de Jalisco CP 2024; FORTAMUN de Puebla CP 2023), fórmulas propuestas, estructura de información y fuentes complementarias.
- Hallazgos pendientes de corregir: adjudicación directa predeterminada en 60%, ausencia de observaciones convertida a cero, etiquetas favorables presentadas como solventadas y umbrales internos sin metodología oficial verificada.
- Pendientes: cobertura nacional y desgloses de cabildo; actualización por acción y corte; importes y remuneraciones locales; población de referencia; validación de legislación procesal vigente; programación y pruebas de integración. No se modificaron archivos de la aplicación ni assets.
- Entrega guardada localmente. La carpeta no tiene repositorio Git reconocido; no fue posible efectuar pull, commit ni push sin recuperar una copia Git de trabajo. Se preservó la carpeta existente.


## Desglose numérico para la calculadora — 20260925

- Informe: investigaciones/desglose-numerico-finanzas2024.md; datos: investigaciones/desglose-numerico2024.json; Excel filtrable: outputs/01a0d5f6/Auditavision_Desglose_2024.xlsx (9 hojas).
- Cobertura: Diputados y Senado CP 2024, 32 congresos locales INEGI, 32 auditorías de participaciones estatales y 1,056 auditorías integrales municipales/alcaldías, dos congresos auditados y clasificación administrativa de Cuernavaca.
- Validación: registros únicos por auditoría y coincidencia de duplicados; sumas conciliadas con el marco ASF; partidas de personal y capítulos cuadrados; fórmulas del Excel sin errores; nueve hojas renderizadas y revisadas.
- Pendientes: extracción EFIPEM definitiva 2024 para ingresos y egresos completos (los ZIP históricos descargados llegan a 2023), costo específico de todos los cabildos, remuneraciones individuales y seguimiento posterior por acción. No se extrapola la muestra ASF a todo el presupuesto.
- Investigación guardada localmente, sin modificar la aplicación ni assets. Sigue pendiente recuperar una copia Git para commit/push; esta carpeta no tiene repositorio reconocido.

## Investigación numérica del Poder Judicial federal — 20260925

- Informe: investigaciones/presupuesto-judicial-federal2026.md. Base: investigaciones/presupuesto-judicial-federal2026.json. Excel: outputs/judicial2026/Auditavision_Poder_Judicial_2026.xlsx (10 hojas, filtros y comparativas editables).
- Alcance: aprobado 2026 del Ramo 03 (70,005,628,646 pesos), SCJN (5,208,743,404), OAJ (59,190,814,696), TEPJF (3,749,492,877; Sala Superior y Salas Regionales) y TDJ (1,856,577,669). No se incorporan presupuestos estatales ni proyectos 2027.
- Detalle: 183 filas jerárquicas PEF; 127 partidas SCJN con ocho columnas al 31-08-2026; cierre SCJN 2025 y semestre 2026; 140 UEG y 1,768 registros UEG/partida OAJ exclusivamente abril–junio 2026; 32 agregados parciales de pagos por circuito. Nómina centralizada no atribuida arbitrariamente a circuitos.
- Comparativas: participaciones presupuestarias, equivalencias con ingreso y tabulador neto. Manual DOF 27-02-2026, pp. 8–9: ministro 134,310 netos mensuales y 290,273 netos anuales conjuntos de aguinaldo/prima vacacional. Son referencias tabulares, no nómina efectivamente pagada. Se identifica el 206,948 histórico del comparador existente para revisión futura.
- Verificación: sumas exactas de unidades y conceptos PEF, partidas y ocho columnas SCJN, UEG y detalle por partida OAJ. Fórmulas del Excel sin errores, entradas cero/negativas/vacías controladas y vistas de las diez hojas revisadas. Copias oficiales y hashes SHA-256 conservados en investigaciones/fuentes-judicial y en el catálogo JSON.
- Discrepancias documentadas: SHCP y OAJ difieren en 10,637,899 pesos entre capítulos 3000/4000 con total anual idéntico; estados OAJ marzo muestran pagados distintos por clasificación. Se mantienen separados, sin etiquetarlos como irregularidad ni combinarlos en acumulados.
- Pendientes: costo completo por circuito/tribunal/juzgado, presupuesto y nómina por ponencia y área interna SCJN, conciliación OAJ, pago individual efectivo, salas regionales individuales y ejercicio TDJ. Faltan matrices de adscripción y distribución, aclaraciones documentales y nóminas específicas. No se estima con promedios.
- Entrega de investigación local. No se modificaron assets, HTML, sello ni calculadora; su integración queda pendiente. La carpeta continúa sin repositorio Git reconocido: pull/commit/push no disponibles. No se enviaron solicitudes externas.

## Hito: Versión 20260925a — Integración de Investigación LEGO ( MDD), Cadena Petroquímica y Ampliación de Auditoría en Imágenes (8 Slides)

1. **Investigación Cívica de IED y Cadena Petroquímica:**
   - Expediente documentado: investigaciones/expediente-ebrard-lego-ied-petroquimica.md.
   - Foco: Anuncio de Marcelo Ebrard (Secretaría de Economía) sobre la inversión privada de LEGO en Ciénega de Flores, NL ( MDD, 1,300 empleos directos).
   - Cruce con gasto público: Respaldo hídrico federal con el Acueducto El Cuchillo II (Conagua/Sedena, >,000 mdp), exenciones de ISN estatales (3%) y el cuello de botella petroquímico nacional (Pemex con >65% de capacidad ociosa en Cangrejera/Morelos, provocando que >70% de resinas de ingeniería ABS y polietileno deban importarse).
   - Noticia de inteligencia fiscal: 
ot-07 integrada en AUDIT_DB.noticias (Modo Inspector).

2. **Expansión de la Sección de Portada 'Auditoría en Imágenes' (De 5 a 8 Slides):**
   - **Slide 6 (Nuevo):** Expansión LEGO & Cadena Petroquímica (Secretaría de Economía · Marcelo Ebrard).
   - **Slide 7 (Nuevo):** Tren Interurbano México-Toluca 'El Insurgente' (SICT / CDMX, presupuesto base ,608 mdp vs real auditado >,000 mdp, +172% sobrecosto y 10 años de retraso).
   - **Slide 8 (Nuevo):** Megafarmacia del Bienestar en Huehuetoca (Birmex, adquisición/adecuación ,500 mdp +  mdp/año gasto corriente de operación, <1% recetas surtidas).
   - Incorporación de imágenes 16:9 (showcase_lego_expansion.jpg, showcase_tren_toluca.jpg, showcase_megafarmacia.jpg) y 8 dots de navegación en index.html y uditavision/index.html.

3. **Verificación y Pruebas Automatizadas:**
   - Ejecutadas pruebas automatizadas en Microsoft Edge Headless vía CDP (scratch/verify_showcase_cdp.py), verificando 8 slides, 8 dots, modales de hallazgos activos con datos oficiales y 0 errores de consola.
   - Sello de versión incrementado a **20260925a** mediante herramientas/sello.py.
   - Invariantes de formato CRLF y lone CRs preservadas al 100% en todos los archivos.
   - Paquetes de entrega ZIP generados: Auditavision_AuditoriaImagenes_LegoObras_20260925a.zip.
