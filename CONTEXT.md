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
