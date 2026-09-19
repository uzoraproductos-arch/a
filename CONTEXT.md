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

### Pendiente

- **Pestaña 4.2** (Pleno y Ministros, análisis comparativo): sigue con datos
  previos a la reforma. El usuario pidió expresamente no tocarla todavía.
- **Cifras presupuestales del Nivel 4 de 4.1**: las plazas y remuneraciones
  corresponden a la estructura de once ponencias y al tope salarial anterior.
  Hay una advertencia metodológica visible en la ficha. Deben contrastarse
  contra el Manual de Remuneraciones vigente antes de citarse.
- **Contenido de la pestaña 1 (Presupuesto)**: es la puerta de entrada y solo
  tiene 350 caracteres de texto —un párrafo de introducción— frente a los
  29,833 de la pestaña 3. El panel es mapa y botones, sin nada que explique
  qué está viendo el lector ni cómo leerlo. Es la brecha de contenido más
  grande de la plataforma.
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
