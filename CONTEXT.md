# Contexto del proyecto — Auditavisión

> Documento de traspaso. Está escrito para que cualquier persona, o cualquier
> asistente de IA, pueda retomar el proyecto sin haber visto las conversaciones
> anteriores. Si trabajas en esto, léelo antes de tocar código.

## Regla de oro al cambiar de plataforma

**Este repositorio es la única fuente de verdad.** No existe una "copia buena"
en ninguna otra parte: ni en un chat, ni en una carpeta local, ni en el
historial de otra IA.

El ciclo, sin excepciones:

```bash
git pull origin main     # ANTES de empezar a trabajar
# ...cambios...
git add -A && git commit -m "Describe el cambio"
git push origin main     # AL TERMINAR, aunque quede a medias
```

Si te quedas sin créditos, sin tokens o se cae la sesión, lo único que se
pierde es lo que no se haya empujado. Por eso conviene empujar seguido, incluso
trabajo incompleto: un commit imperfecto siempre vale más que un avance
perdido.

Para verificar que una copia está al día:

```bash
git fetch origin && git status
```

Si dice `Your branch is up to date with 'origin/main'`, esa copia es la buena.

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
```

El orden de carga importa: geometría y base de datos **antes** que el motor. El
motor lee `window.AUDIT_DB` y `window.MEXICO_GEOJSON` al ejecutarse y aborta si
no los encuentra.

Dependencias externas por CDN: Leaflet 1.9.4 para mapas y Google Fonts
(Playfair Display, Source Serif 4, JetBrains Mono, Inter).

### Convenciones que conviene respetar

- El archivo usa saltos de línea **CRLF**. Al editar con scripts, presérvalos o
  el diff se llena de ruido.
- El texto va **con acentos**. Es contenido de cara al público.
- `audit-engine.js` es un IIFE que expone su API en `window.AuditEngine` al
  final del archivo. Todo método invocado desde el HTML debe estar en ese
  objeto.

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

### Pendiente

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
- **Título duplicado**: en varias pestañas el encabezado de `#tabintro` y el
  título del panel dicen casi lo mismo, uno debajo del otro.
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
