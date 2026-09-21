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
