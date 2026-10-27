# Contexto del proyecto — Auditavisión

> Documento de traspaso. Está escrito para que cualquier persona, o cualquier
> asistente de IA, pueda retomar el proyecto sin haber visto las conversaciones
> anteriores. Si trabajas en esto, léelo antes de tocar código.

## Regla de oro al cambiar de plataforma

**Este repositorio es la única fuente de verdad.** No existe una "copia buena"
en ninguna otra parte: ni en un chat, ni en una carpeta local, ni en el
historial de otra IA.

### Se trabaja en la rama, `main` es la versión entregada

**Todo el trabajo se hace en `claude/funny-turing-imtm54`.** `main` guarda la
versión que el autor aprueba. El 29-09-2026, con permiso expreso del autor, se
llevaron a `main` los 133 commits de la rama y las dos quedaron idénticas
(`196084e`). Desde entonces `main` solo avanza cuando el autor lo pide, así que
la rama puede volver a ir adelante: parte siempre de la rama.

```bash
git rev-list --count origin/main..origin/claude/funny-turing-imtm54   # 0 = iguales
```

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
| Revisión | El pull request #1 se fusionó en `main` el 29-09-2026; lo nuevo irá en un pull request nuevo |
| Copia comprimida | `.../a/archive/refs/heads/claude/funny-turing-imtm54.zip` |

La página publicada lleva su sello al pie (al 29-09-2026: **Versión publicada: 20260928o**).
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

## Una sola plataforma: la Enciclopedia antigua se retiró (decisión del autor, 24-10-2026)

Primero el autor dijo que la plataforma Enciclopedia antigua (`enciclopedia.html`,
de 9 pestañas, con `assets/css`, `assets/js` y `assets/data`) quedaba «en el
olvido»; el mismo día decidió **fusionarla**: que quede una sola plataforma y
se depure lo que ya no sirve «por cuestiones de fuente o contenido, porque ya
obra en Auditavisión». Se hizo así:

- **Se retiraron** `enciclopedia.html` (351 KB) y sus tres carpetas (5.9 MB:
  motor, base de datos, geometría, padrones, lista 69-B y estilos). Nada de
  Auditavisión los cargaba: el auditor usa sus copias de `assets/auditor/`.
- `enciclopedia.html` **redirige** a `enciclopedia-auditavision.html`
  (`REDIRECCIONES` de `apartados.py`), para que ningún enlace viejo muera.
- **El código queda en el historial**: `git show 490233d:enciclopedia.html`
  (y `490233d:assets/js/...`) lo recupera, por si un día se retoma.

Inventario de lo que traía, contra lo que ya tiene Auditavisión:

| Pestaña antigua | Dónde vive ya | Qué se depuró |
|---|---|---|
| 1 Presupuesto (circuito, 32 entidades, municipios, Paquete 2027) | Números: `numeros-camino-del-dinero`, `-las-32-entidades`, `-los-municipios`, `-paquete-2027*` | Nada nuevo: ya decía «se mudó a la plataforma» |
| 2 Acción financiera (deuda y Banxico, megaobras, PIB, calculadora, bitácora, costo de los Poderes) | `numeros-cuentas-*`, Inversión y Megaobras, `datos-ambiente-pib`, Calculadora Cívica, `numeros-lo-que-cuestan-los-poderes` | La bitácora (notas sin fuente) |
| 3 Legislativo (cámaras, periodos, elecciones, congresos estatales, remuneraciones) | `datos-poder-legislativo` y sus 4 subpáginas, cotejadas con la Constitución, la LGIPE y el INE | Simuladores de «austeridad» de San Lázaro y el Senado, costo por legislador (IMCO), los «14 niveles» de sueldos: cifras sin documento oficial |
| 4 Judicial (Pleno, sueldos, elección, amparo, jurisprudencia) | `datos-poder-judicial` y sus 6 subpáginas | Cálculos de ponencias y asesores sin documento |
| 5 Políticos (mandatarios, Porfirio Díaz) | Ya retirados el 27-09-2026; la balanza de Porfirio vive como trivia en Aprende | Todo |
| 6 Verificador, 7 Diccionario, 8 Referencias | Modo Inspector, `diccionario.html`, `fuentes-oficiales.html` | Nada nuevo |
| 9 Comunidad | `participa.html` y el cajón «Cuéntanos lo que viste» | El Pase del Auditor (ya retirado) |

**Lo que se rescató** (pedido del autor, 24-10-2026, sello 20261024p). Solo el
tema: cada línea se cotejó contra el texto vigente, con su huella SHA-256.
- En `datos-judicial-como-decide.html` (y en el chat, `D.jud`): «Los cuatro
  caminos para defender la Constitución» (`medios`, arts. 103, 105 y 107),
  «Los recursos del amparo» (`recursos`, Ley de Amparo arts. 80 a 105, 201 y
  202, última reforma DOF 16-10-2025) y «¿Cuándo llega un caso a la Suprema
  Corte?» (`llegar_corte`, arts. 105 y 107; Ley de Amparo 83 y 84).
- En `datos-legislativo-elecciones.html` (y en el chat, `D.leg`): «El proceso
  electoral, etapa por etapa» (`ruta`, LGIPE 208, 225, 251, 310 y 312) y
  «Cómo evaluar a una candidata o candidato» (`candidatos`, Constitución 38,
  41 y 55; LGIPE 243; LGPP 79; LGRA 29 y 32; votaciones de la Gaceta
  Parlamentaria).
- No entró lo que no se pudo sostener: la cuenta de «seis puertas» a la
  Corte (la Constitución da las vías, no un número) y el sistema
  «Conóceles» del INE para 2027 (el portal del INE no se pudo consultar desde
  aquí; queda por cotejar cuando lo publique).

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
assets/auditor/css/auditavision.css     Diseño: temas claro y oscuro
assets/auditor/js/mexico-states-geo.js  Geometría de las 32 entidades (window.MEXICO_GEOJSON)
assets/auditor/js/audit-database.js     Datos fiscales (window.AUDIT_DB)
assets/auditor/js/audit-engine.js       Motor y controlador (window.AuditEngine)
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

## Plan de lanzamiento (`docs/LANZAMIENTO.md`)

Pedido del autor, 24-10-2026: todos los pendientes para salir en línea (dominio, hospedaje, base de datos, correo, aviso de privacidad, canales, datos que se actualizan solos y difusión), por tipo y en siete fases. Nada de la fase 1 en adelante empieza sin las decisiones de la fase 0. El 24-10-2026 se retiró el Pase del Auditor Cívico: §4.4 evalúa las dos vertientes para sostener la plataforma (donaciones y Servicios del Auditor Virtual, por suscripción o créditos) y recomienda las dos por etapas.

## Siguiente tarea: legibilidad en celular (`docs/ux/PLAN.md`)

Condición del dueño: **la plataforma debe ser fácil de leer y de entender,
empezando por el celular.** Una auditoría medida (29-09-2026, 390 px, 11
vistas) encontró que entre el 78 y el 86 % del texto visible mide menos de
14 px, que hay entre 50 y 198 emojis por vista, y que cada módulo empieza unas
cinco pantallas abajo. El plan completo, con decisiones, fases y metas, está en
**`docs/ux/PLAN.md`**. Pasó por un CEO review y por dos revisiones externas.

Orden acordado: lectura en todo el sitio → módulos en capas → dominio propio
→ URLs por módulo (SEO/GEO) → datos por página.

**Fase 0 en curso.** No tiene cambio visible:

- `herramientas/guardia_legibilidad.py` mide la legibilidad.
- `docs/ux/fase-0-propuestas.md` reúne lo que el autor debe aprobar: los cambios
  a AGENTS.md y a DESIGN.md, y los nombres de secciones y rutas.

Nada de la fase 1 empieza sin ese visto bueno.

**Estado al 12-10-2026:** el autor aprobó la propuesta 3: se retiran las «tres puertas» (Lee / Explora / Consulta) y sus rutas, y manda el menú de cinco pestañas del 09-10. También aprobó la 1, ya aplicada en AGENTS.md: ramas cortas `ux/fase-…` (§1), reglas de lectura (§4, sin la de emojis: el autor decidió conservarlos y la guardia ya no los exige), §5 línea 1 corregida a `assets/auditor/js` y línea 6 con la guardia de legibilidad. Siguen sin aprobar la 2 (escala de letra y fondo sin fotografía) y la 4 (dominio: el autor lo comprará). La línea base de la guardia es del 29-09 y hay que volver a medirla antes de la fase 1.

## Sistema de marca (`DESIGN.md`), hecho el 29-09-2026

**`DESIGN.md` en la raíz es la referencia única de la marca**: logo, color,
tipografía, forma y voz. Se generó con el skill
`.claude/skills/brand-book-generator/` y las respuestas del autor:

- **Alcance:** solo Auditavisión. Inspector Meteoro queda como firma del autor
  y Fortuvisión fuera.
- **Lema:** *El gasto público, a la vista.*
- **Público:** ciudadanía general. **Qué no es:** un sitio oficial.
- **Tono:** riguroso, cívico, sobrio, didáctico.
- **Logo:** la moneda de oro inspectora con alas **se queda** como logo
  principal (`assets/auditor/img/logo-auditavision.svg`), para 56 px o más. Se
  le sumó un **símbolo plano** aprobado por el autor, «moneda con rostro»
  (bombín, ojo tras la lupa, bigote y alas), para favicon, sellos y una tinta.
  Hay 19 SVG en `assets/brand/logos/{combined,symbol,wordmark}/`, todos solo
  con `fill` y con el nombre en contornos (Playfair Display Black).
- **Paleta:** se conservan los siete acentos (decisión del autor) y cada uno
  queda con un solo papel: oro marca, carmesí alerta, esmeralda oficial, ámbar
  derivado, naranja advertencia, cian referencia y azul información.

El brief `docs/marca/BRIEF.md` se escribió sobre `main` y describía un
encabezado con emoji ⚖️ y superficies sólidas. El auditor de esta rama ya
tenía la moneda ilustrada y superficies translúcidas sobre la fotografía de la
ciudad: `DESIGN.md` documenta lo que hay en esta rama.

El brand book interactivo que produce el skill está en **`brand/`** y se abre
en `/brand/`: `brand-book.jsx` es el componente React del skill y
`brand/index.html` lo carga con React, Babel y Tailwind por CDN, sin paso de
compilación. Muestra los 19 SVG con descarga y los dos temas. Si cambia
`DESIGN.md`, se actualiza `brand-book.jsx` a mano.

Aplicar `DESIGN.md` al sitio es trabajo aparte y queda pendiente (lista en su
§9 y abajo, en Pendiente).

**Bigote estilo Zapata, retirado (07-10-2026, sello 20261007a).** El 01-10
se cambió el bigote del logo a estilo Zapata; el autor lo rechazó («ese no
es el logo») y se revirtió completo: ilustración, los 13 SVG de
`assets/brand/logos/`, `brand/brand-book.jsx` y `DESIGN.md` (vuelve a v1.0).
El logo es el de antes. No se vuelve a tocar el bigote sin que el autor lo pida.

**Piel cívica (08-10-2026, sello 20261008a).** El autor pidió volver a la
portada anterior (las cinco herramientas con icono, «Explora el panorama»,
el radar y el carrusel, que `ux/fase-1` había quitado) y quedarse solo con la
redacción de `ux/fase-1`. Además pidió quitar la foto de fondo y acercar el
aspecto a Civio y USAspending (fondo blanco, barra azul, gris) y a Operação
Serenata de Amor (un color por rubro). Hecho:
- `assets/auditor/css/civico.css`, cargada después de la hoja maestra: sin
  foto de fondo en los dos temas; tema claro de entrada (llave nueva
  `auditavision_tema_civico`), barra superior azul, franjas grises, acento
  azul en lugar de dorado; cada tarjeta de rubro con su franja, su icono y su
  botón del color del rubro (dinero azul, obras naranja, calculadora verde,
  inspector rojo, ambiente verde azulado).
- Portada: lema «El gasto público, a la vista», la cifra de la ASF con su
  fuente y la guía «Cómo se usa» (de `ux/fase-1`), arriba de los rubros. El
  carrusel bajó después de los módulos, para que el módulo abra pegado a los
  rubros.
- Redacción: menús con nombres sencillos (Busca y verifica, Sigue el dinero,
  Descarga los datos, Aprende, Participa), «Cuéntanos lo que viste», «Cerrar y
  volver al inicio» y los textos del motor que `ux/fase-1` pasó de usted a tú.
  Los emojis se quedan: el autor quiere los iconos.
- No se trajeron de `ux/fase-1` la navegación de cuatro secciones, la capa
  `legibilidad.css/js` ni la carga diferida del padrón municipal.

**Los seis rectángulos de la portada (08-10-2026, sello 20261008b).** El
autor ordenó la portada en seis franjas de ancho completo, cada una con su
fondo y una raya de color arriba, como los bloques de Serenata de Amor:
1. Cabecera (logo, menús, Cuéntanos, Compartir, Inspector Meteoro, buscador).
2. Radar (datos de referencia y cifras en perspectiva).
3. Panorama: un solo título, «Explora el panorama de las finanzas públicas en
   México», con «El gasto público, a la vista» como etiqueta encima y una
   frase para cualquier persona («de dónde sale el dinero de todos, en qué se
   gasta y quién revisa que se use bien»). «Cómo se usa» va arriba de los
   cinco rubros y **sin cifras**: la cifra de la ASF salió de la portada,
   porque las cifras se descubren dentro de los módulos.
4. Auditoría en imágenes (intacta por decisión del autor).
5. Pie: principios, cómo leer cada cifra, fuentes y glosario. Las fuentes
   ahora citan, con liga a su ficha del catálogo: PEF 2026, LFPRH, Ley de
   Presupuesto, Contabilidad y Gasto Público Federal (1976, **abrogada**, como
   antecedente), Ley General de Contabilidad Gubernamental y Ley Federal de
   Deuda Pública (que hasta 2016 se llamó Ley General de Deuda Pública).
   Todas ya estaban en `AUDIT_DB` con su vigencia.
6. Renglón final con la leyenda de transparencia y el sello.

**Menú de tres rayas (08-10-2026, sello 20261008c).** En pantallas de 1100 px
o menos el índice del rectángulo 1 ya no se amontona: queda plegado tras un
botón ☰ «Menú» (`toggleMenuMovil` en el motor, aspecto en `civico.css`). Al
desplegarse muestra los cinco menús uno debajo del otro (cada uno se abre en
su lugar), el buscador, Compartir, Inspector Meteoro y el tema, y al final un
recuadro rojo «¿Viste algo raro con el dinero público?» con el botón
«Cuéntanos lo que viste». Se cierra al elegir un destino, al tocar fuera o con
Escape. En computadora la cabecera no cambia.

**Paleta azul y nuevo orden (08-10-2026, sello 20261008d).** El autor pidió
basar los colores en el dragón blanco de ojos azules (concepto «corporativo»):
la cabecera en azul corporativo fuerte (degradado #071d47 → #0b2a63 → #123d8a)
y una escala de azules que baja hasta el blanco en las franjas (blanco, blanco
hielo #f1f7fe, azul claro #e3f0fd, azul hielo #d6e9fc), con rayas que alternan
celeste #4f9be8 y azul #1a56b8. El acento del tema claro es azul. Los colores
de contenido no cambian: rubros, rojo de alertas y chips de estado. Es solo
el marco; no se usa ningún nombre, logo ni imagen de la franquicia.
Nuevo orden de los rectángulos: 1 cabecera, 2 los cinco módulos, 3 auditoría
en imágenes, 4 datos de referencia y radar (antes iba arriba; ahora va justo
antes de «Principio y Compromiso Ciudadano»), 5 pie, 6 renglón final.

**Herramientas y Datos en el índice (08-10-2026, sello 20261008e).** El autor
pidió que la portada la protagonicen las imágenes. Cambios:
- El bloque del panorama (título, «Cómo se usa» y los cinco módulos) pasó al
  índice como **primer apartado, «Herramientas»**: un panel ancho que se abre
  desde la cabecera. Al pulsar «Comenzar», el panel se cierra (también si el
  cursor sigue encima: clase `mega-suprimido`) y el módulo abre debajo de las
  imágenes.
- El radar (datos de referencia y cifras en perspectiva) pasó al índice como
  **último apartado, «Datos de referencia»**.
- La portada queda en cuatro franjas: 1 cabecera, 2 auditoría en imágenes,
  más grande (alto de hasta 70 % de la pantalla, título y pregunta mayores),
  3 pie, más discreto (letra y márgenes menores), y 4 renglón final.
- `seleccionarModuloExplorer` ahora calcula el salto descontando la cabecera
  fija (antes el salto de respaldo dejaba el módulo cientos de píxeles abajo),
  y `plegarDesgloseModulos` vuelve al inicio de la página.

**Un solo tema: el claro (08-10-2026, sello 20261008g).** El autor pidió
eliminar el tema oscuro. Se quitó el botón «◐ Tema» de la cabecera;
`initTheme` fija siempre `data-theme="light"` y borra la preferencia guardada
(`auditavision_tema_civico`), así que quien la tenía en oscuro ve el claro.
`toggleTheme` sigue exportada, pero ya no alterna. Las reglas oscuras de
`auditavision.css` se dejaron en su sitio: son la base sobre la que se monta
el claro (`:root` es oscuro y `[data-theme="light"]` lo corrige), y
arrancarlas sería reescribir la hoja entera sin ganancia visible.

**Acciones y buscador a la derecha (08-10-2026, sello 20261008h).** En
escritorio (más de 1100 px), «Cuéntanos lo que viste», «Compartir»,
«Inspector Meteoro» y el buscador quedan pegados al borde derecho de la
cabecera. El buscador ocupa justo el ancho de la fila de botones: sus bordes
izquierdo y derecho coinciden con los de «Cuéntanos» e «Inspector Meteoro».
Se quitó el recuadro blanco que rodeaba la caja de búsqueda. En celular no
cambia nada (todo vive en el menú ☰).

**Legibilidad y sobriedad de color (08-10-2026, sello 20261008i).** Fusión de
la revisión de color de Antigravity (puntos 1 a 6 aprobados por el autor; el 7,
oro en la cabecera, quedó fuera). Se descartó su modo oscuro, el oro como
identidad, el fondo pergamino y, sobre todo, su ámbar para «pendiente»: en la
plataforma el ámbar es `derivado` y `pendiente` es gris punteado; ese
significado no cambia. Contraste medido con WCAG (mínimo 4.5:1), en
`civico.css`:
1. Chip `derivado` `#B7791F` → `#8A5A12` (3.32 → 5.38:1 sobre su fondo).
2. Chip `oficial` `#1E824C` → `#18703F` (3.89 → 5.42:1).
3. Rubro obras `#C8641B` → `#A9541A` en textos y botones (3.97 → 5.29:1);
   la franja de la tarjeta conserva el tono vivo (`--rubro-obras-raya`).
4. Alertas y anomalías: tarjeta blanca, borde de 1 px y borde izquierdo rojo
   de 3 px, sin fondo teñido. Los textos pensados para fondo oscuro pasan a
   tinta o rojo. Se corrigió de paso un texto de la alerta ASF de la ficha
   estatal que ya se leía mal (1.83:1, color en línea).
5. Botones secundarios (CSV, copiar, controles del radar, cambio de vista):
   blanco con borde neutro; el color pleno queda para la acción principal.
6. Tarjetas y paneles sin sombra difusa; al pasar el cursor cambia el borde.
   Menús, modales y cajón conservan su sombra porque flotan.
(Resuelto en 20261008l: la caja del treemap ya va en tema claro.)

**Imágenes de fondo en cabecera y pie (08-10-2026, sello 20261008j).** El
autor eligió imágenes propias de su carpeta («Gasto público → imágenes»):
- Cabecera: `assets/auditor/img/portada/cabecera-pasillo.webp` (el pasillo
  con dos personas, el azul al lado y el edificio). Va a la derecha, a su
  tamaño natural, con el borde izquierdo desvanecido en la propia imagen
  (canal alfa) para que no se note el corte. Un paneo de 48 s la recorre del
  pasillo hacia el edificio; con «reducir movimiento» queda quieta. El índice
  y la marca llevan una sombra leve para leerse sobre la foto.
- Pie («Principio y Compromiso»): `pie-noche.jpg` (ciudad de noche) como
  marca de agua; `pie-planos.jpg` (ciudad en planos con grúas) se guardó como
  alternativa: se cambia en la variable `--pie-imagen` de `civico.css`.
- **Pendiente de derechos:** las tres vienen de Pinterest y su autoría no
  está acreditada; la de noche lleva la firma «AFERA XV». Antes de pasar a
  `main`, sustituirlas por imágenes propias o generadas con IA (con su
  etiqueta), o conseguir permiso y acreditar al autor.

**«Auditoría en imágenes» centrada en pantallas anchas (08-10-2026, sello
20261008k).** En monitores de más de 1560 px el recuadro quedaba pegado a la
izquierda con un hueco blanco a la derecha (lo reportó el autor con captura):
la regla de ancho uniforme del 27-09 fijaba `max-width: 1560px` y la piel
cívica le había quitado el `margin: auto`. Ahora la franja gris ocupa todo el
ancho y el recuadro queda centrado, alineado con el espacio donde se abren
los módulos (comprobado a 1600, 1920 y 2560 px).

**Treemap del presupuesto y barra de mandos en tema claro (08-10-2026, sello
20261008l).** La caja del treemap (módulo Presupuesto → 2.2 «En qué se va»)
seguía con el fondo casi negro del tema oscuro y cifras ilegibles. Ahora es
blanca; cada bloque lleva el color de su categoría en el borde izquierdo, la
cifra y un tinte suave (social verde azulado, económico ámbar, gobierno rojo,
deuda carmín, participaciones verde, autónomos morado, ADEFAS gris). Migas,
insignia de nivel, botón «Volver» y banda de resumen pasan a azul cívico.
De paso, la barra «Contabilizar / Reiniciar» (`.evaluacion-controls-bar`,
usada por ocho gráficas) también era oscura: ahora es gris claro con sello
azul y botón principal azul. Contraste medido: todo el texto de la caja
pasa de 4.5:1 en nivel 1, en el subnivel y en la vista de lista.

**El índice abre páginas; «Datos de referencia» se despliega a todo lo ancho
(08-10-2026, sello 20261008m).** Por decisión del autor, seis apartados del
índice ya no se desglosan en un menú: cada uno abre su propia página, con la
información ordenada por secciones, tarjetas y un «En esta página»:
`herramientas.html` (los cuatro módulos y la guía «Cómo se usa»),
`busca-y-verifica.html` (desde el 09-10-2026, redirección al Modo Inspector),
`sigue-el-dinero.html`, `descarga-los-datos.html`,
`aprende.html` y `participa.html`. **No se editan a mano:** se generan con
`python3 herramientas/apartados.py`, que toma el sello de `index.html`
(`sello.py` ya lo llama solo). Llevan la misma cabecera y cargan
`auditavision.css`, `civico.css`, `apartados.css` y el pequeño
`apartados.js` (menú de tres rayas y «Compartir»); no cargan el motor.
Sus tarjetas vuelven al auditor con `index.html?ir=destino&ancla=id`: el
motor (`irDesdeApartado`) solo acepta los destinos de su lista
(`IR_MODULOS` e `IR_DESTINOS`), limpia la dirección al llegar y repite el
salto si la página, recién cargada, lo dejó corto. «Datos de referencia»
sigue siendo desplegable, pero ya no mide 1240 px fijos pegados a la
izquierda: ocupa todo el ancho (contenido centrado hasta 1560 px). En
celular, la cifra del radar y su ritmo por segundo ya no se enciman. Las
cifras de las tarjetas son las mismas que tenía el menú, con su misma fuente
en el `title`.

**Cabecera más alta para que se vea la imagen (08-10-2026, sello
20261008n).** A petición del autor, arriba de la página la cabecera mide al
menos 190 px en escritorio y 150 px en celular, para que se aprecie la imagen
del pasillo. Al desplazarte más de 120 px se encoge a su alto de siempre
(clase `body.cabecera-compacta`, con holgura hasta 10 px para que no
parpadee) y vuelve a crecer al regresar arriba; lo hacen el motor y
`apartados.js`. Al saltar a un módulo, la cabecera se encoge *antes* del
salto (`altoCabeceraCompacta`): si cambiaba de alto a medio camino, el
desplazamiento suave se interrumpía.

**«Sigue el dinero» en seis capítulos y la deuda en el tiempo (08-10-2026,
sello 20261008o).** La página sigue ahora el orden de *Introducción al
Derecho Económico* (Gómez Granillo y Gutiérrez Rosas, Esfinge, 1995),
capítulos 5 y 7, puesto al día: 1 De dónde sale, 2 Quién lo decide, 3 Quién
lo gasta y en qué, 4 A dónde baja, 5 Cuánto debemos, 6 Y a ti. Cada capítulo
trae una franja «Ayer y hoy» (lo que explicaba el libro, con su página, y lo
vigente, con su documento). No se copian cifras ni pasajes del libro.
`apartados.py` acepta ahora en cada sección `num`, `ayer`, `bloque` (HTML
propio) y, en el apartado, `libro` y `scripts`.

El capítulo 5 es un módulo nuevo, `assets/auditor/js/deuda-tiempo.js`
(autónomo, no usa el motor): línea de tiempo del SHRFSP como % del PIB o en
billones de pesos corrientes, de 1994 a la proyección de 2027, con franjas
por sexenio (convención de seis años calendario de la evaluación sexenal),
«Contabilizar / Reiniciar a ceros», barra de años, ficha por sexenio
(recibió, entregó, cambio `derivado`, máximo, hitos) y la tabla completa.
Regla de la serie: cada año viene de la publicación oficial más reciente
encontrada, y la cifra anterior queda visible cuando una revisión del PIB la
cambió. Fuentes, todas descargadas y leídas el 08-10-2026:
- 2000-2011: ASF, Informe del Resultado CP 2012, Tomo Ejecutivo, p. 67.
- 2012-2015: ASF, IGE CP 2018, p. 258 del PDF (2012 era 36.8 en la CP 2012).
- 2016-2019 (% y pesos hasta 2022): ASF, IGE CP 2022, pp. 149-150.
- 2020-2025 en %: Criterios 2027, cuadro con el PIB revisado (p. 53 del
  PDF): 50.2, 49.1, 47.6, 46.6, 51.9, 52.6. Antes se publicaron 51.6, 50.8,
  49.4 (ASF), 46.8 (SHCP Com. 5/2024) y 51.4 (SHCP Com. 4/2025).
- 2026 estimado 54.0 % y 2027 proyectado 55.0 %, con sus saldos en pesos:
  Criterios 2027, pp. 18 y 68 del PDF.
- 1994: 36.9 % de deuda neta económica amplia (Banxico), otro indicador,
  dibujado aparte. 1995-1999 queda `pendiente`: no hay serie comparable.

**Lo de 52.3 contra 54.0 en 2026 no era contradicción:** 52.3 % es lo que se
aprobó y 54.0 % es el cierre estimado. Los propios Criterios (p. 18 del PDF)
explican que, con el PIB revisado por el INEGI, el 52.3 aprobado equivale a
54.5 %.

Gráfica 1 del libro (deuda externa del sector público 1988-1994, en dólares):
Banxico, Informe Anual 1994, Anexo 6, p. 165, confirma 78,747 millones en
1993 y da 85,436 millones en 1994 (el libro anota 85.1). De 1988 a 1992 son
cifras del libro y van como `pendiente`. Las cifras del Porfiriato tampoco
tienen fuente primaria en el auditor: se mencionan sin números y se enlaza a
la Enciclopedia (`enciclopedia.html#tab-panel-politicos`, que no se tocó).

Pendiente de este bloque: la evaluación sexenal sigue usando las cifras de
su momento (36.8 en 2012, 51.4 en 2024), mientras la línea de tiempo usa las
revisadas (37.2 y 51.9). Hay que decidir un solo criterio. También faltan el
saldo en pesos de 2025, la serie 1995-1999 y verificar en Banxico la deuda
externa de 1988 a 1992.

**Las tarjetas se despliegan en su propia página (08-10-2026, sello
20261008p).** El autor pidió que, al pulsar una tarjeta de un apartado, la
información se desplegara ahí mismo y no lo regresara a la página inicial.
Ahora `apartados.js` intercepta las tarjetas que van a `index.html?ir=...`
y abre, debajo de la fila de la tarjeta, un **visor**: un marco con
`index.html?ir=...&visor=1`, de alto de pantalla, con «Pantalla completa» y
«Cerrar». La dirección no cambia. Con Ctrl, Cmd o la rueda del ratón la
tarjeta se abre en otra pestaña, como cualquier enlace.

En el auditor, `&visor=1` dentro de un marco marca `html.modo-visor` desde el
`<head>`, antes de pintar, y `civico.css` esconde cabecera, portada, pie,
barras de regreso y botones flotantes. En modo visor, los enlaces a otras
páginas se abren en la ventana completa (`target=_top`). Los destinos que son
ventanas (descargas, CSV, fuentes, reporte, Pase) dejan detrás un aviso con
«Abrirla de nuevo» y «Cerrar este panel»; este último usa `postMessage` con
el mismo origen. La lista de destinos que son panel y no ventana está en
`VISOR_PANELES`. Si el ancla de una tarjeta es un bloque plegable del erario
(`eb-*`), ahora llega abierto (antes llegaba cerrado).

Verificado a 1440 y a 390 px en 15 tarjetas de los seis apartados (módulos,
anclas y ventanas): la dirección no cambia, el módulo y su bloque quedan
arriba del visor, «Cerrar» funciona, 0 errores y sin desborde. La entrada
directa `index.html?ir=...` sigue funcionando igual.

**El Circuito del Dinero se reparte en Sigue el dinero (09-10-2026, sello
20261008q).** El autor pidió quitar de Herramientas el módulo «Circuito del
Dinero», que repetía lo de Sigue el dinero, y organizar su contenido ahí sin
duplicar. Herramientas queda con cuatro módulos y una línea que manda a Sigue
el dinero. Los bloques del Circuito pasaron a tarjetas de los capítulos:
1 (arquitectura, cuánto dinero es, de dónde sale, a qué equivale, lo que la
cifra no dice), 3 (en qué se va, margen del presupuesto, estado de resultados
CP 2024) y 4 (el mapa). La tarjeta «Ramos y dependencias» abría lo mismo que
«En qué se va» y se fusionaron. Nuevo **foco del visor**: si el ancla es un
bloque `eb-*`, `visorFoco()` (motor) abre sus ancestros y esconde todo lo
demás (`.visor-oculto`): portada del módulo, índice, bloques hermanos y
subbloques internos, que tienen su propia tarjeta. «Pantalla completa» sigue
abriendo el módulo entero. Verificado bloque por bloque: cada tarjeta muestra
solo su bloque, arriba, 0 errores.

**El examen de los presidentes, en Aprende (09-10-2026, sello 20261008q).**
La trivia del bloque 3 de Megaobras («Administración presidencial», 3.2) se
mudó a `aprende.html#trivia`, en un guion propio sin motor:
`assets/auditor/js/trivia-presidentes.js`. Son 12 preguntas en cuatro rondas
(Porfiriato, economía, deuda, fiscalización), cada una con su gráfica que
arranca en ceros, su lección y sus fuentes; modo «contra reloj» de 20 s por
pregunta; y al final la calificación y **el estado de cuenta de cada
presidente**: crecimiento, empleo, deuda que recibió y que entregó, su saldo
en puntos del PIB, la deuda nueva en pesos y su **reloj por segundo**, que
corre en vivo, más auditorías y recuperaciones. El bloque 3 de Megaobras se
llama ahora «Las obras de cada sexenio» y conserva la línea de obras, con un
aviso de la mudanza. El código `renderPresEval` del motor quedó inerte (no
hay `#presEval`); la colección `DB.evaluacion_sexenal` sigue siendo la fuente
de las cifras copiadas al guion: si cambia una, se cambia en ambos.

Criterio de deuda decidido para la trivia: la publicación oficial más
reciente de cada año, igual que la línea de tiempo (Calderón 37.2 y López
Obrador 51.9, con la cifra original en la nota).

**El Porfiriato, verificado contra el INEGI.** Se cotejaron contra las
*Estadísticas históricas de México 2014* (cuadros 14.18, 16.3, 16.6 y 3.7) las
cifras que circulan y que trae la Enciclopedia (congelada, no se tocó):
- El «primer superávit de 1894-1895, por $19,861» no se sostiene: el INEGI da
  déficit de $1.2 millones ese año; la racha de superávits empieza en
  1895-1896 (+5.4). Los $19,861 quedan pendientes de la Memoria de Hacienda.
- Vías: 617 km en 1876 y 19,748 en 1910 (no 640 y 19,280).
- Aduanas: 45.2% del ingreso efectivo en 1894-1895, no 52% (derivado).
- Analfabetismo: 82.1% (1895, mayores de 6), 77.7% (1900) y 72.3% (1910).
- Ingresos 8.2%, gasto 7.4%, deuda 30.5% y superávit 0.8% del PIB: sin fuente
  oficial; no se usan. Tampoco el desglose del timbre (28%).
La trivia lleva un recuadro «Lo que corregimos al verificar el Porfiriato».

**Aprende en pestañas y «La Columna del Erario» (09-10-2026, sellos
20261009i y 20261009j).** Decisiones del autor:
- Las secciones de `aprende.html` son pestañas (`'pestanas': True` en
  `apartados.py`; la lógica genérica vive en `apartados.js`): el contenido
  solo se despliega al pulsar la pestaña, y pulsarla otra vez la cierra.
  Sin JavaScript se ven todas. `#trivia`, `#biblioteca`, `#kit` y
  `#noticias` abren su pestaña.
- Cuarta pestaña, **Noticias relevantes**: columnas editoriales con formato
  de periódico (`assets/auditor/js/columnas.js` + `columnas.css`). Rescatan,
  verificado contra documentos oficiales, lo que fueron la 5.2 («Personajes
  relevantes») y la 5.3 («Datos curiosos de personajes secundarios») de la
  Enciclopedia, retiradas el 27-09-2026 por no citar fuentes (commit
  d36e030). **No se copió nada de aquellas fichas**: cuatro revisiones
  independientes buscaron cada afirmación en su documento oficial (DOJ,
  UIF, Presidencia, CJF, Senado, SIL, ASF, FGR, SFP, DOF, PEF 2026, IPAB,
  INEHRM, SEP, Sedena, AGN, Banxico). Quedaron 14 columnas: 6 de personajes
  (García Luna, Segalmex, Lozoya, Robles, Gordillo, Gómez Urrutia), 4 de
  hechos (partida secreta, Fobaproa-IPAB, origen del Ramo 33, expediente de
  la «Casa Blanca») y 4 de historia (Santa Anna, Juárez 1861, Limantour,
  Banco de México 1925). Cada una lleva cifras con chip y sus documentos.
- Lo que no se pudo sostener (31 afirmaciones) se publica al pie del diario
  en «Lo que dejamos fuera y por qué». Entre ello: la columna completa de
  Raúl Salinas de Gortari y la de Carlos Romero Deschamps (Pemexgate), las
  multas del IFE de 2003 y los retratos de dominio público, porque el
  entorno no pudo abrir repositoriodocumental.ine.mx, justice.gov, Wikimedia
  ni otros sitios: **falta de la plataforma, pendiente**.
- Ojo: la sentencia de García Luna (460 meses) se tomó del comunicado del
  DOJ leído a través del buscador, porque justice.gov estaba bloqueado; la
  Presidencia confirma los 38 años. Conviene abrir el comunicado del DOJ.
- Las imágenes son ilustraciones de grabado (emoji sobre trama), no fotos:
  no se publican fotografías de personas sin licencia verificada.
- **Pedido del autor (09-10-2026, sello 20261009l):** la pestaña «Kit del
  auditor» se llama ahora **«Fuentes del auditor»** (su id sigue siendo
  `#kit`). Además pidió columnas sobre tres temas, y se verificaron con la
  misma regla:
  - **Acapulco (Abelina López Rodríguez): 2 columnas.** La primera trata de
    lo que observaron la ASF (2022: 27.1 mdp; 2023: 3.7 mdp; 2024: 206.2 mdp;
    suma derivada de 237.1 mdp) y la ASE de Guerrero. La segunda, de la
    controversia constitucional 174/2025, resuelta el 6-07-2026: la Corte
    invalidó por falta de competencia el pliego de la ASE por 898.6 mdp
    (FAISMUN 2023), sin juzgar el manejo del dinero. **La premisa de «más de
    600 millones de la ASF» no se sostuvo:** el monto era de la ASE y la
    Corte no exoneró a nadie. Queda explicado en «Lo que dejamos fuera». Las
    observaciones se dirigen al municipio, no a la persona. Pendiente:
    integrar el engrose de la CC 174/2025 cuando la SCJN lo publique.
  - **Hijos de Salinas de Gortari y NXIVM: sin columna.** No se pudo abrir
    ningún documento oficial (EDNY 1:18-cr-00204, DOJ, sentencia
    SRE-PSC-75/2021 del TEPJF), y ninguno localizado los acusa. Es falta de
    la plataforma.
  - **López Beltrán y Amílcar Olán: sin columna.** Ningún documento oficial
    abierto los vincula con contratos o investigaciones. Romedic, el balasto
    del Tren Maya, Portacelis y «El Clan» solo aparecen en prensa. Para
    reabrirla faltan el registro del CEN de Morena ante el INE, CompraNet
    histórico y SIGER, la lista de Cofepris de diciembre de 2022 y algún
    expediente de FGR, SAT o UIF. Es falta de la plataforma: esos sitios no
    abren desde el entorno.
  - Hay 16 columnas y 58 afirmaciones descartadas.

**Participa en pestañas, el logotipo abre «Quiénes somos» y la ventana
lateral más ancha (09-10-2026, sello 20261009m).** Decisiones del autor:
- `participa.html` funciona como Aprende (`'pestanas': True`): dos
  pestañas, «Ágora cívica» (`#agora`) y «Garantías cívicas»
  (`#garantias`), que se despliegan al pulsarlas.
- En las páginas generadas, el logotipo ya no lleva a la portada. Ahora es
  un botón (`#apartadoPresentacion`) que abre la presentación «Quiénes
  somos» en la ventana lateral, sin salir de la página. Como esas páginas
  no cargan el motor, `apartados.js` lleva una copia del texto de
  `abrirPresentacion()`: **si cambia uno, cambia el otro**. Para volver a
  la portada está el botón «Ir a la página principal» al pie de la
  ventana. En `index.html` el logotipo ya hacía eso.
- La ventana lateral (`.glos-drawer`) pasa de 420 a 580 px (`civico.css`).
  Lo heredan la presentación, el glosario y las notas.

**Registro de pendientes (10-10-2026, sello 20261010g).** Decisión del
autor: cada pendiente lleva su etiqueta, su porqué y el enlace oficial donde
debería estar el dato.
- **`pendientes.html`.** Lo genera `herramientas/pendientes.py` y hoy trae
  37 fichas:

  | Quién debe resolverlo | Fichas |
  |---|---|
  | Una dependencia que debe publicarlo | 19 |
  | La plataforma, que aún no integra el documento | 12 |
  | Nadie: es un dato histórico | 6 |

  Las fichas salen de dos lados: los registros `pendiente` de la base,
  leídos con un adaptador por bloque, y la lista `PROPIOS`, para lo que el
  motor escribe en su código (matriz ASF 2018, municipios sin cuenta,
  INAFED, huachicol, costo por usuario, pesos de 2024 y la ficha del Tren
  Maya). La generación se detiene si una ficha no trae porqué, responsable
  o enlace.
- **Toda etiqueta «pendiente» abre el registro.** Un escucha en la fase de
  captura, en `audit-engine.js` y en `apartados.js`, lleva al registro al
  hacer clic. Con `data-pend` lleva a la ficha exacta: el Estado de Cuenta
  ya lo usa. Desde el visor abre en la ventana principal.
- **Base de datos.** Se completaron:
  - `url_resultados` en los cuatro programas sociales;
  - el `url` de IMSS-Bienestar;
  - el `motivo` y el `url` del reloj de pérdidas de las megaobras.

  El motivo de los resultados dice ahora que el CONEVAL se extinguió y que
  sus funciones de evaluación pasaron al INEGI en 2025.
- **Comprobaciones.** `inventario.py` reporta como roto un `data-pend` sin
  ficha. AGENTS.md §2 lleva la regla nueva.

**Propuesta de Astra, entrega 6: Servicios de investigación (10-10-2026, sello 20261010k).**
Decisión del autor: **el Pase del Auditor convive con los Servicios.** El Pase
sostiene la consulta gratuita; los Servicios son trabajo a la medida que se
cotiza. Aún no hay dominio, así que todo queda listo para el lanzamiento. El
autor hace la revisión legal y dio por buena la redacción.
- **`servicios.html`** (Participa › Servicios), generada por `servicios()` en
  `apartados.py`. Tiene cinco secciones:
  1. los cuatro servicios de Astra, con su entregable y para quién son;
  2. el proceso en siete pasos;
  3. el precio, sin tarifa: las primeras saldrán de pilotos pagados y no se
     inventan;
  4. la política de independencia, versión 1, con diez compromisos (lista
     `INDEPENDENCIA`);
  5. el formulario «Solicita una investigación».
- **El formulario** (`assets/auditor/js/servicios.js`) arma la solicitud en el
  navegador y no envía ni guarda nada. Pide los campos obligatorios, si quien
  solicita es parte del caso y que acepte la política y el alcance. Deja
  revisar, copiar y descargar (.txt). El botón «Enviar» queda desactivado
  mientras `CANAL_SOLICITUD` (en `apartados.py`) esté vacío. **Para abrirlo
  en el lanzamiento:** se pone la dirección, por ejemplo
  `'mailto:investigaciones@dominio.mx'`, y se corre `sello.py`. El botón
  entonces abre el correo con asunto y cuerpo ya escritos.
- **Servicio pertinente** (punto 8): cada `auditoria-*.html` cierra con
  «¿Necesitas ir más a fondo en este caso?», que lleva a
  `servicios.html?tema=<título>#solicitud` con el tema escrito.
- Participa tiene una tercera pestaña, «Servicios», con tarjetas a Servicios
  y al Pase. El Pase enlaza a Servicios, y el índice y las novedades los
  incluyen.

Pendientes de la entrega 6:
- **El canal de envío** (`CANAL_SOLICITUD`): espera el dominio.
- **Las tarifas**: salen de los pilotos pagados.
- **El tablero comercial del punto 10** (visitas, solicitudes, cotizaciones,
  horas). Necesita analítica y registro de encargos que el sitio estático no
  tiene.
- **Entrega 7** (comunidad): hecha el mismo día; ver arriba.

**Revisión de seguridad (12-10-2026, sello 20261012a).** A pedido del autor se revisó el código del auditor con la skill `security-audit` de Cloudflare (solo lectura). No hubo vulnerabilidades: los parámetros `?ir=`, `?ancla=` y `?abrir=` ya se validaban, el `?q=` del asistente se escapa, los `postMessage` comprueban el origen, Leaflet lleva SRI, los 57 `target="_blank"` llevan `noopener` y no hay claves en el código. Se corrigieron dos detalles, probados en Chromium antes y después:
- **El `#ancla` de la dirección** ya no rompe la página: `apartados.js` lo lee con `hashId()` (atrapa el `URIError` de un `%` mal formado y solo admite letras, números, `-` y `_`), y el motor aplica la misma regla a la subpestaña de `#pestaña/subpestaña`. Antes, `herramientas.html#%E0%A4%A` y `sigue-el-dinero.html#"]x` lanzaban un error.
- **Los debates guardados en `localStorage`** pasan por `debateValido()` antes de pintarse: `id`, `postura`, colores, `apoyos` y réplicas deben tener la forma que la plataforma les da; un `fuente_url` mal formado se quita. Antes, un debate manipulado ejecutaba código, y `uzoraproductos-arch.github.io` es un origen compartido por todos los sitios de la cuenta.
- **Los otros cinco lectores del `#ancla`** (`biblioteca.js`, `columnas.js`, `expedientes.js`, `glosario.js`, `agora.js`; sello 20261012b) atrapan el `URIError`: `fuentes-oficiales.html`, `marco-legal.html`, `expedientes.html`, `glosario.html` y `agora.html` con `#%E0%A4%A` lanzaban «URI malformed». Solo usan `getElementById` o comparan, así que no hacía falta filtrar el id.
- Sin cambiar: Google Fonts sin SRI (su CSS varía por navegador) y sin CSP (GitHub Pages no permite cabeceras; se podría poner por `<meta>`).

**Datos abiertos e Informes oficiales, en sus páginas (11-10-2026, sello 20261011t).** A pedido del autor, las dos pestañas de Datos ya no despliegan fichas: cada una abre su portada (`datos-abiertos.html` e `informes-oficiales.html`), con dos tarjetas, y cada tarjeta abre su página:
- `datos-descargas.html`: las siete bases en CSV.
- `datos-municipios.html`: la base EFIPEM del INEGI, con la consulta por estado.
- `informes-cuenta-publica.html`: los 8 capítulos de la Auditoría Superior.
- `informes-diccionario.html`: el diccionario de datos.

Están en `DATOS_PARTES` y las genera `datos_paginas()` en `apartados.py`. `datos.js` ya no despliega nada: llena el `<div data-ficha-fija="<id>">` de cada página con las mismas funciones `FICHAS`, sin cambiar contenido ni cifras. Se quitó `fichas()` de `apartados.py`; el CSS `.dt-ficha` se queda sin uso. Las anclas viejas `descarga-los-datos.html#abiertos`, `#informes` y `#ficha-<id>` redirigen (`DATOS_ANCLAS`). El enlace del radar a la ASF va directo a `informes-cuenta-publica.html`. El índice general lista las cuatro páginas.

**Donaciones (11-10-2026, sello 20261011s).** A pedido del autor, Participa suma la pestaña **Donaciones**, que abre `donaciones.html` (`donaciones()` en `apartados.py`; `donaciones.css` y `donaciones.js` en `assets/auditor/`). El Pase del Auditor Cívico se queda: el autor aún no decide si sostener la plataforma con el Pase, con donativos o con ambos. La página trae tres partes. **La alcancía de la transparencia** es un cochinito SVG con monedas que caen; su nivel se llena con lo recaudado entre la meta, y el botón «Echa una moneda de prueba» la anima sin sumar nada. **Cuentas claras** muestra lo que entró y en qué se gastó, con comprobante y sin nombres de donantes. **Las reglas de tu donativo** citan tres compromisos de `INDEPENDENCIA` y la nota de que el donativo no es deducible, porque Auditavisión no es donataria autorizada (LISR art. 151, fr. III). **Regla: la alcancía solo muestra dinero que de verdad entró.** Todo sale de `CANAL_DONACION`, `DONACIONES_META`, `DONACIONES_ENTRADAS` y `DONACIONES_SALIDAS`; para anotar un movimiento se agrega ahí y se regenera. Hoy el canal está vacío, el botón «Donar» está desactivado con la etiqueta «Próximamente», la alcancía marca $0 y la meta dice «Por definir». **Pendiente del autor:** abrir la pasarela de pago (`CANAL_DONACION`) y fijar la meta con lo que cuesta sostener la plataforma (`DONACIONES_META`).

**Garantías cívicas en cuatro páginas (11-10-2026, sello 20261011r).** A pedido del autor, igual que Comunidad: `garantias.html` queda como portada con el aviso «Auditavisión no recibe denuncias» y cuatro tarjetas, y cada una abre la suya: `garantias-brujula.html` (la brújula), `garantias-puertas.html` (las seis puertas), `garantias-derechos.html` (las diez garantías) y `garantias-reto.html` (¿Mito o realidad?). Están en `GARANTIAS_PARTES` en `apartados.py`, y `garantias()` devuelve la lista de páginas; los textos siguen saliendo de `window.AUDIT_DB`, sin cambios ni cifras nuevas. Al pie de cada una va `partes_nav()`, la barra genérica que ahora usa también `comunidad_nav()`. Las anclas viejas (`garantias.html#brujula`, `#puertas`, `#derechos`, `#reto` y `#puerta-<canal>`) redirigen. En `garantias.js` cada bloque arranca solo si está en la página; «Ver su ficha ➔» de la brújula lleva a `garantias-puertas.html#puerta-<canal>`, que abre el detalle de esa puerta y la resalta, y «Repasar las diez garantías» del reto lleva a su página. El índice general muestra las cuatro partes bajo Garantías cívicas.

**Comunidad en cinco páginas (11-10-2026, sello 20261011q).** A pedido del autor, la pestaña Comunidad de Participa ya no se despliega: es `'pagina': 'comunidad.html'`. Esa página queda como portada con cinco tarjetas, y cada una abre la suya: `comunidad-reporta.html`, `comunidad-error.html`, `comunidad-tema.html`, `comunidad-compartir.html` y `comunidad-erratas.html`. Están en `COMUNIDAD_PARTES` en `apartados.py`, y `comunidad()` devuelve la lista de páginas. Al pie de cada una va `comunidad_nav()`. Las anclas viejas `comunidad.html#reporta` (y las demás) y `participa.html#comunidad` redirigen. La redirección por ancla conserva ahora `location.search` cuando el destino no trae `?` ni `#`, así que `comunidad.html?pagina=X#error` llega con la página ya escrita. Los formularios los sigue armando `comunidad.js`, que se carga en todas las páginas. Los enlaces del cajón de la cabecera, Garantías, Pendientes y el bot apuntan ya a las páginas nuevas.

**Índice general al día (11-10-2026, sin sello: no toca `assets/`).** A pedido del autor, `indice()` en `apartados.py` suma lo que faltaba. En el **Modo Inspector**, «Grandes investigaciones» (`INVESTIGACIONES`) encabeza sus ocho aplicaciones, y «Pregúntale al Auditor» (`ASISTENTE`) va al final. En **Datos**, bajo «Hoy y los estados de cuenta», van sus dos páginas: `radar-presupuesto-en-curso.html` y `radar-estado-de-cuenta.html`. Los cuatro apartados de la Biblioteca se muestran como hijos de ella. La metodología cita las «Referencias» de la Biblioteca en vez del «Compendio de Fuentes Oficiales». Hay cinco **Novedades** nuevas: el bot, «Lo que aún no sé», las dos tarjetas del Inspector, la página de Noticias y la portada simplificada. Ya no queda ninguna página de la plataforma fuera del índice; la única que no aparece es `enciclopedia.html`, que es un proyecto aparte.

**Portada sin buscador (11-10-2026, sin sello: solo `index.html`).** A pedido del autor («ya tenemos al bot»), se quitó de la cabecera de la portada el buscador `#globalSearchInput` (bloque `.nav-search-wrap`). Las búsquedas las atiende ahora «Pregúntale al Auditor». `initSearch()` del motor no cambia: si no encuentra la casilla, no hace nada. El CSS de `.nav-search-*` se queda en `assets/auditor/css` sin uso, para no subir el sello por un cambio cosmético.

**Portada: textos de Auditoría en imágenes más sencillos (11-10-2026, sin sello: solo `index.html`).** A pedido del autor, se quitó la etiqueta «🇲🇽 AUDITORÍA EN IMÁGENES» encima del título del carrusel, y la etiqueta y la pregunta de las nueve imágenes se reescribieron en palabras llanas y sin siglas: «Ramo 33» pasa a «el dinero que baja a tu municipio», «la ASF» a «los auditores», y salen PEF, IEPS, SAT, SICT, FONATUR y Birmex. No hay cifras nuevas: las preguntas no dan números. Las páginas `auditoria-*.html` no cambian; su título y la línea «Esta investigación:» bajo el carrusel (`data-nombre`, que escribe `auditorias.py`) siguen como estaban.

**Noticias relevantes, página propia (11-10-2026, sello 20261011p).** A pedido del autor, la pestaña «Noticias relevantes» de Aprende ya no despliega las columnas: abre `noticias-relevantes.html` (`NOTICIAS` en `apartados.py`), con «La Columna del Erario» en su formato de periódico sin cambios (`columnas.js` y `columnas.css` se cargan ahí y ya no en `aprende.html`). `aprende.html#noticias` y cualquier `aprende.html#col-<id>` redirigen a la página nueva y conservan el ancla de la columna. Para eso `hash_a_pagina` acepta ahora claves con prefijo (`'col-*'`).

**Biblioteca del Erario Público (11-10-2026, sello 20261011o).** A pedido del autor, el «Diccionario del Erario Público» se llama ahora **Biblioteca del Erario Público** y se reorganizó sin quitar contenido. La pestaña de Aprende abre directo `diccionario.html` (el archivo no cambia, para no romper enlaces). Ahí hay **cuatro tarjetas** y cada una abre su página: **Diccionario** (`glosario.html`, el glosario de términos hacendarios), **Referencias** (`fuentes-oficiales.html`, el catálogo numerado de fuentes al que llevan las notas [n]), **Marco Legal Hacendario** (`marco-legal.html`) y **Preguntas Frecuentes** (`preguntas-frecuentes.html`). Desaparecen los estantes intermedios: `biblioteca-hacendaria.html` y `fuentes-del-auditor.html` redirigen a la Biblioteca (`REDIRECCIONES`). El **Pase del Auditor Cívico** se mudó a **Participa**, como pestaña que abre su página (`PASE` en `apartados.py`). Ya no hay `ESTANTES`: `BIBLIOTECA` es una lista plana y `BIB_NOMBRE` guarda el nombre. Los textos del motor que decían «Diccionario del Erario Público» dicen ahora «Biblioteca».

**Modo Inspector: dos tarjetas autónomas (11-10-2026, sello 20261011n).** A pedido del autor («darles autonomía a las tarjetas y que su información únicamente se abra en una nueva página»), `herramienta-inspector.html` ya no despliega las ocho aplicaciones ni el bot: presenta dos tarjetas, «Dos maneras de entrarle». **Grandes investigaciones** abre la página nueva `herramienta-inspector-investigaciones.html` (constante `INVESTIGACIONES`, función `herramienta_divisiones()` en `apartados.py`), con las ocho aplicaciones. **Pregúntale al Auditor** abre el bot. Las migas de las aplicaciones y de `servicios.html` pasan por «Grandes investigaciones» (`padre3`), y su botón «volver al índice» lleva ahí. Las anclas viejas `#modulos` y `#pregunta` redirigen a la página que les toca.

**«Pregúntale al Auditor»: «Lo que aún no sé» (11-10-2026, sello 20261011m).** A pedido del autor, el bot anota las preguntas que no supo contestar y las que el lector marca con el botón **«🤔 No era lo que buscaba»** de cada nota. La lista vive en el recuadro «Lo que aún no sé» de la página (`localStorage`, clave `auditavision.bot.sinRespuesta`, máximo 50, cuenta las repeticiones) y sirve para decidir qué fichas agregar primero. **El sitio es estático: nada se envía solo.** El lector la copia y la pega en `comunidad.html#tema`; cuando se llene `CANAL_COMUNIDAD` en `apartados.py`, aparece el botón «Enviarlas a Auditavisión» (mailto con la lista armada). Un registro central de todas las preguntas, sin intervención del lector, necesita servidor: decisión pendiente del autor, junto con la capa generativa.

**«Pregúntale al Auditor», segunda vuelta: clasificación, enlaces y más cobertura (11-10-2026, sello 20261011l).** A pedido del autor («contesta rápido, en bandeja de plata»): (1) aviso de **mejora continua** en la página y en la tarjeta; (2) cada nota trae **«Cómo leer estas cifras»**, que justifica cada chip presente: oficial (de qué documento sale), derivado (la operación va junto a la cifra; si solo hay aproximación, rango con mínimo, máximo y punto medio, cada cota con su fuente) y pendiente (por qué falta, a quién le toca y el enlace donde debería estar, en un recuadro); (3) **enlaces directos a la fuente oficial**: Sistema de Alertas de Hacienda y Matriz de Datos Básicos de la ASF en las entidades, portal de informes de la ASF en los expedientes, el documento de cada remuneración; (4) fichas nuevas: **15 remuneraciones de cargos públicos** (`comparador_salarial`, con su estado y operación) y **94 secciones** de las páginas, que se buscan por todo su texto y llevan al ancla exacta. Total: 674 fichas. Sin cifras nuevas: todo sale de lo ya publicado.

**Modo Inspector: «Grandes investigaciones» y el bot interno «Pregúntale al Auditor» (11-10-2026, sello 20261011k).** A pedido del autor: los ocho módulos del Modo Inspector se llaman ahora **aplicaciones** y forman la división «Grandes investigaciones» (cada una con su página, como antes). Aparte, una segunda división con una herramienta nueva: **«Pregúntale al Auditor»** (`herramienta-inspector-pregunta.html`), un **bot interno** con el logo de Auditavisión. El lector escribe una pregunta y recibe una **nota técnica sellada** (folio `NT-AAAAMMDD-XXXXXXXX` y huella SHA-256 de la ficha, con el mismo sello del Estado de Cuenta). **No es una IA generativa, a propósito:** solo busca entre 565 fichas que ya están publicadas y verificadas (246 términos del glosario, 10 expedientes, 32 entidades, 125 fuentes oficiales, 48 pendientes y las páginas) y, si ninguna responde, lo dice; así no puede inventar una cifra (§2). Nada sale del navegador. Archivos: `herramientas/asistente.py` (escribe la base `assets/auditor/js/asistente-base.js` y el chat; lo llama `apartados.generar()` al final), `assets/auditor/js/asistente.js` (búsqueda con peso por rareza de cada palabra, siglas, sinónimos de uso común e intención de la pregunta; `?q=` precarga una pregunta; `window.AuditorBot.buscar()` para revisar puntajes) y `assets/auditor/css/asistente.css`. Sin cifras nuevas. **Pendiente de decisión del autor:** una capa generativa (un modelo de lenguaje que redacte con las fichas) necesitaría un servidor con llave de API, que GitHub Pages no tiene, y una regla para que no escriba cifras fuera de las fichas.

**Las cuatro herramientas, con su icono en el encabezado y su propio tono (11-10-2026, sello 20261011j).** A pedido del autor, el trato de Costo Ambiental pasa a las otras tres: el icono de la herramienta (y el de cada módulo) va grande en el título de su página, y el encabezado toma su color: naranja para Inversión y Megaobras, dorado para la Calculadora Cívica y gris para el Modo Inspector (`.herr-cab.rubro-*` en `assets/auditor/css/apartados.css`). Las cuatro tarjetas con foto de la pestaña Herramientas y la fila «Las otras herramientas» ya no llevan icono: solo el nombre. Se controla con `HERR_ICONO_CAB` en `herramientas/apartados.py`. Sin cifras nuevas.

**Costo Ambiental: encabezado verde gris, cinco aplicaciones y «Crisis ambientales» (11-10-2026, sello 20261011i).** A pedido del autor:

- **Encabezado.** En las páginas de Costo Ambiental el encabezado toma el verde gris de su imagen (#4c5f45, `.herr-cab.rubro-ambiente` en `apartados.css`) y el icono de la tarjeta sube junto al título, grande (`icono_cab` en `pagina()`; `HERR_ICONO_CAB`). Las otras tres herramientas siguen en azul: si el autor lo quiere igual, basta sumar su rubro a `HERR_ICONO_CAB` y darle su tono.
- **Aplicaciones.** Sus módulos se llaman «aplicaciones» (`HERR_PALABRA`): «Las 5 aplicaciones», «aplicación 1 de 5», «Todas las aplicaciones de…». Las tarjetas conservan su tamaño horizontal.
- **Quinta aplicación, «Crisis ambientales»** (`herramienta-ambiente-crisis.html`). La escribe `herramientas/crisis_ambientales.py` (llamada desde `generar()` vía `herramienta_modulo(..., bloque=...)`), con `crisis.css` y `crisis.js` (la calculadora). Secciones: el hueco (pérdidas esperadas de los Criterios 2027, p. 51, contra fondo del Ramo 23 2026 + seguro 10.4 mmp + bonos 595 mdd × 18.0, derivado), el fondo año por año (PEF 2018-2020, 2026 y proyecto 2027), lo que costaron según CENAPRED, la calculadora «Lo que cuesta esperar» (arranca en $0; tasa promedio de la deuda, derivada, o Cetes 2027, oficial), tres fichas (Otis, Simón, agua de Guadalajara) y el daño de fondo del agua (INEGI CEEM 2024).
- **Fuentes.** Seis fichas nuevas en el compendio, [120] a [125] (`herramientas/anclar_crisis.py`): CENAPRED 2023 y 2024, ASF 2023-0362 y 2024-0353, DOF de la declaratoria de Otis y el comunicado del plan de Otis. Los comunicados de Jalisco, de Presidencia y del DOF secundarios se citan con enlace directo. Todo se cotejó el 11-10-2026 en el documento oficial.
- **Lo que no entró por ser solo de prensa:** los $42,101 mdp del Plan Hídrico de Jalisco, los $8,500 mdp de El Zapotillo, los $609 mdp federales para plantas en el Santiago, las «342 / más de 400 colonias» y las «488 mil piezas» de enseres de Otis (la ASF dice «más de 400 mil»). Nueve pendientes nuevos en el registro: `otis-diferencia`, `otis-financiamiento`, `simon-danos`, `gdl-plan-costos`, `gdl-zapotillo`, `gdl-colonias`, `gdl-calidad`, `cenapred-serie`, `fonden-2021-2025`.
- **Notas.** CENAPRED se contradice con Otis: su cuadro 1.2 dice $84,207 mdp y su texto $88,910 (el total de 2023); se usa el cuadro. Los «~21 mmp» de cobertura que cita `paquete_2027.contingentes` (seguro + bonos) no aparecen así en los Criterios: son seguro 10.4 mmp + bonos 595 mdd. Hay que revisar Simón cuando el DOF publique su declaratoria. Siguiente etapa propuesta: línea del tiempo filtrable por año, estado y tipo de fenómeno.

**Baja al territorio en tres páginas, y el Diccionario del Erario Público (11-10-2026, sello 20261011h).** A pedido del autor, la portada de «Baja al territorio» (`numeros-baja-al-territorio.html`) queda como la de Presupuesto: solo tres tarjetas en mosaico, sin franja «Ayer y hoy», sin nota del libro y sin saltos al pie. Cada tarjeta abre su página, escrita por `herramientas/territorio_modulos.py` desde `window.AUDIT_DB` (entran en `NUMEROS_MODULOS` con parte `baja`):
- `numeros-mapa-del-gasto-federalizado.html` (ancla vieja `eb-mapa`): el mapa de las 32 entidades dibujado en SVG desde `mexico-states-geo.js` (sin Leaflet), con cinco lentes (Ramos 28 y 33, por habitante, dependencia federal, deuda, por aclarar ante la ASF), colores por quintiles, ficha de cada estado, resumen y el cuadro de las 32 de mayor a menor (en la primera lente, cada barra partida en Ramo 28 y Ramo 33). Se depuraron las lentes separadas de Ramo 28 y Ramo 33 y el cartograma. El cuadre contra el Presupuesto y lo que el acuerdo de distribución no asigna se conservan.
- `numeros-las-32-entidades.html`: tres pisos de la hacienda, los cuatro ramos del gasto federalizado con su grado de libertad (fondos del Ramo 33 y del 25 en barras, reglas del 28) y el circuito de cada estado con selector (`?e=CLAVE#circuito`).
- `numeros-los-municipios.html`: FORTAMUN y FISMDF, lo que la ley garantiza sin cifra, lo que cobran por su cuenta (con la razón participaciones ÷ predial, derivada), el punto ciego del art. 115 y el padrón del INEGI con selector, buscador y orden (`?e=CLAVE#padron`; lee `municipios-efipem.js`).
Lo interactivo vive en `assets/auditor/js/territorio.js`; los estilos `tt-*`, al final de `numeros.css`. Las cifras de la Ciudad de México sin fuente (convenios, recaudación propia, dependencia 2024) ya no se muestran: van como `pendiente` con su ficha `entidades-cdmx`, que ahora apunta a las páginas nuevas, igual que `municipios-sin-cuenta`. Las fichas laterales de cada ramo y de cada municipio del motor no se trasladaron; el motor sigue intacto en la portada.
La franja «Ayer y hoy» de esta parte pasó a la pregunta frecuente «¿Cuál es la diferencia entre el Ramo 28 y el Ramo 33?» (con la ficha [119] en sus referencias), y la descripción de esa ficha dice dónde vive cada franja. Además, el Diccionario del Gasto Público se llama **Diccionario del Erario Público** (apartados.py, `index.html`, `apartados.js` y el motor del auditor; las novedades viejas conservan el nombre de su fecha).

**Modo Inspector: su presentación menciona Servicios (11-10-2026, sello 20261011g).** A pedido del autor, la presentación del Modo Inspector suma una frase: «Y si un caso necesita ir más a fondo, en el módulo de Servicios puedes pedir una investigación a la medida: cada cifra con su documento y bajo una política de independencia.». Va en `HERRAMIENTAS` (apartados.py) y en `PROEMIOS` de `assets/auditor/js/audit-engine.js`, que deben decir lo mismo. La copia congelada de `assets/js` no se tocó.

**«Servicios» pasa de Participa al Modo Inspector (11-10-2026, sin sello: no toca `assets/`).** A pedido del autor, la pestaña «Servicios» de Participa se quitó y su contenido es el módulo 8 del Modo Inspector (`HERRAMIENTAS`, tema `servicios.html`). La página `servicios.html` conserva su nombre para no romper enlaces y cuelga de Herramientas › Modo Inspector. Trae todo lo que tenía: los cinco servicios, cómo trabajamos, precio, política de independencia y formulario. También suma la otra tarjeta de la pestaña, el Pase del Auditor Cívico, y al pie lleva «Las otras herramientas». `participa.html#servicios` redirige a `servicios.html`. Participa queda con Ágora, Garantías y Comunidad, y el índice general ya no lista Servicios bajo Participa: aparece entre los módulos del Modo Inspector.

**«Presupuesto», solo tarjetas, sin saltos al pie (11-10-2026, sin sello: no toca `assets/`).** A pedido del autor, la portada `numeros-presupuesto.html` ya no lleva «← Volver a Números» ni «Siguiente parte → Gasto público»: quedan sus cinco tarjetas y el pie general. Las páginas de cada tarjeta y de los 16 renglones conservan su anterior y siguiente.

**«Presupuesto», sin «Ayer y hoy» y con un solo pie (11-10-2026, sello 20261011f).** A pedido del autor, `numeros-presupuesto.html` ya no lleva la franja «Ayer y hoy» ni la nota del libro al pie («Notas y referencias»): su contenido vive en el Diccionario. El «ayer» (cap. 7, p. 96, la acción financiera del Estado) y el «hoy» (Ley de Ingresos, DOF 7-11-2025, art. 31 fr. IV) se sumaron a la pregunta frecuente «¿Qué persigue la acción financiera del Estado…?», con las fuentes [10] y [119], y la ficha [119] del compendio dice dónde quedó. Las otras tres partes de Números conservan su franja y su nota. El pie de las páginas de Presupuesto (portada, sus cinco tarjetas y los 16 renglones del ingreso) es ahora `presupuesto_pie()`: anterior y siguiente, compactos y lado a lado también en móvil, y un enlace «↑» para subir solo cuando el anterior no es ya la página de arriba. Se quitaron los chips «Más de…», la lista de 16 renglones y la barra «Números: todas sus partes», que repetían destinos (las migas de arriba ya llevan a Números). La última tarjeta (Paquete 2027) sigue a la parte siguiente, Gasto público; el último renglón (Deuda), a «¿A qué equivale?». En «Cuánto dinero es», el enlace final solo lleva a los ocho renglones del gasto: los 16 orígenes son el botón «Siguiente». Pendiente de decisión: aplicar el mismo pie a Gasto público, Baja al territorio y Cuentas claras.

**«Presupuesto»: cinco tarjetas en mosaico, sin datos repetidos (11-10-2026, sello 20261011e).** A pedido del autor, las tarjetas de `numeros-presupuesto.html` tienen el tamaño de las pestañas de Datos, Aprende y Participa (`apartado-pestanas np-mosaico`, tres por fila; la sección lleva `mosaico` y cada tarjeta, su descripción breve en `t[6]`). Se revisaron las páginas, salvo Paquete 2027, en busca de cifras reiteradas: «El peso de 2026» y «Cuánto dinero es» repetían el total, el cuadre y el reparto de lo que entra y lo que sale. Se fundieron en «Cuánto dinero es»: la cifra, las dos barras interactivas y lo que baja al territorio. Se quitaron las columnas y las listas por familia y por renglón, que repetían los 16 orígenes y el simulador de Gasto público; en su lugar quedan enlaces. `numeros-el-peso-de-2026.html` redirige ahí. «El camino del dinero» ya no repite montos de renglón (ISR, IVA, IEPS, programable y federalizado por ramo) ni la gráfica «Cuánto mueve cada etapa»: deja una cifra por etapa con quién responde, plazo y fundamento, y remite a las páginas con el detalle. Pendiente de decisión: «El camino» comparte plazos y artículos con «¿Quién lo aprueba?» de Gasto público.

**«Presupuesto», solo tarjetas (11-10-2026, sin sello: no toca `assets/`).** A pedido del autor, la página `numeros-presupuesto.html` queda en seis tarjetas y nada más; cada una abre su página. «El peso de 2026» (las dos barras, `numeros_peso`) y «Los 16 orígenes del ingreso» (el contador, `numeros_renglones`, con los tres renglones en cero) dejaron de estar en la página y viven en `numeros-el-peso-de-2026.html` y `numeros-los-16-origenes.html`, como módulos de `NUMEROS_MODULOS` (`np-peso`, `nr-origenes`) con `numeros.js`. Las anclas viejas `#numPeso` y `#nrRenglones` redirigen a su página; «Volver» de los renglones del ingreso, `?abrir=eb-ingresos`, el índice general y «sigue» del camino del dinero llevan a la página nueva.

**«Presupuesto»: sus cuatro módulos en página propia (11-10-2026, sello 20261011d).**
Pedido del autor: los módulos de la tarjeta «Presupuesto» (Cuánto dinero es, ¿A qué equivale?, El camino del dinero, Paquete Económico 2027) se abrían en un marco que cargaba el auditor completo y se contaban ahí: tardaban.

- `herramientas/presupuesto_modulos.py` (nuevo) escribe las cuatro páginas desde `AUDIT_DB`, con las cifras ya puestas: `panoramaErario`, `calculadora_civica.parametros.poblacion`, `cuenta_publica_asf.cp2024.total.porAclarar`, `constitucion_economica` y `paquete_2027`. `numeros_modulo()` acepta `bloque`: con él la página es propia, carga `numeros.css` y `presupuesto.js` y ya no lleva iframe. Los módulos de Gasto público y Cuentas claras siguen con el marco.
- Las cifras que en el motor estaban fijas (ISR 3.07, IVA 1.59, 69.6 %, etc.) ahora se calculan de la base; sumas y porcentajes llevan chip `derivado`.
- `assets/auditor/js/presupuesto.js` (nuevo, CRLF): solo el simulador de sensibilidades del Paquete 2027 (mismos coeficientes, escenarios y veredicto del art. 17 LFPRH que el motor). Las barras crecen con CSS (`.pm-*` en `numeros.css`), respetando movimiento reducido.
- ¿A qué equivale? marca el huachicol como `pendiente` con `data-pend="huachicol-evasion"`; la página se agregó a esa ficha en `pendientes.py`. La «Ficha pericial: retirada» del Tren Maya no se trasladó.

**«Gasto público», dinámico (11-10-2026, sello 20261011c).**
Pedido del autor: reestructurar la página para que sea dinámica, con gráficas y simulador
contable, centrada en dos preguntas: quién tiene la facultad de aprobar el gasto y cómo se
reparte. `numeros-gasto-publico.html` lleva ahora, en este orden:
- **«¿Quién lo aprueba? El ciclo del presupuesto»** (`gasto_ciclo()`, `GP_CICLO`, `GP_QUIEN`).
  Son seis paradas en pestañas: propone, aprueba los ingresos, aprueba el gasto, lo ejerce,
  cierra el año y lo revisa. Cada parada trae:
  - su autoridad y su fecha límite;
  - «En los hechos», con las fechas de 2026 que sí están en la base: LIF 2026 en el DOF el
    07-11-2025, PEF 2026 el 28-11-2025 y los Criterios 2027 en la Gaceta del 08-09-2026;
  - el texto oficial **cotejado** de `preceptos_legales`: CPEUM 73, 74-IV, 79, 126 y 134;
    LFPRH 17-18, 42 y 54; LIF 2026 art. 2o.

  Debajo va la tabla «Quién puede qué»: Ejecutivo, Diputados, Senado y ASF, frente a Ley de
  Ingresos, Presupuesto de Egresos, deuda y revisión, cada celda con su artículo. La fecha
  en que Diputados aprobó el PEF 2026 no está en la base, así que no se da.
- **«¿Cómo se reparte? El simulador contable»** (`gasto_reparte()`):
  - un contabilizador que lleva los $10,193,683.7 mdp de cero a su cifra;
  - una gráfica en tres niveles (total, programable / no programable, ocho renglones), con
    ficha al tocar cada tramo;
  - «Si el presupuesto fuera de…», que reparte cualquier cantidad en la misma proporción
    (derivado, con su operación).

  Las cifras salen de `panoramaErario.egresos`, **no** de `treemapPEF`, que trae otros montos
  (Desarrollo Económico 1,670,300 y costo financiero 1,388,400 contra 1,695,700 y
  1,572,073.3): esa discrepancia de la base queda por revisar.
- **«¿Hacia dónde va? Los tres presupuestos»** (`numeros_tres()`, sin cambios).
- **Los desgloses**, cada uno en su página: el simulador «Reparte tú» y las cuatro páginas de
  módulo. Megaobras y costo ambiental **se quitaron** de aquí porque ya están en
  Herramientas; una línea al pie lleva allá.
- **Una página por renglón del gasto** (`egreso_pagina()`, `numeros-egreso-*.html`, 8). Cada
  una trae su cifra, «de cada $100», qué cubre, su ley, por qué importa y cómo se obtuvo. El
  costo financiero trae además el desglose del Anexo 8.
- El JS es `assets/auditor/js/gasto-publico.js` (nuevo) y los estilos son `.gp-*` en
  `numeros.css`. Además, en «El peso de 2026» de la página Presupuesto, los renglones del gasto
  enlazan a sus páginas.
- Con este sello se corrigió también el comentario de `numeros.js` que seguía diciendo
  `numeros-se-recauda.html`.

**«Cuentas claras»: «Se paga lo que se debe» y «Se revisa», fundidas (11-10-2026, sin sello nuevo).**
Pedido del autor. Números queda en **cuatro** tarjetas: Presupuesto, Gasto público, Baja al
territorio y Cuentas claras.
- `numeros-cuentas-claras.html` contiene, en este orden: un texto de entrada; el «Ayer y hoy» de la deuda; la
  línea de tiempo de la deuda (`deuda-tiempo.js`); y cinco tarjetas:
  - el estado de resultados, con página de módulo nueva, `numeros-estado-de-resultados.html`;
  - el Estado de Cuenta Cívico;
  - los Expedientes;
  - dos herramientas que llevan a Herramientas: «Qué encontró la ASF» y «El reloj de la deuda»,
    que ahora abre `herramienta-calculadora-reloj.html` (ya no se duplica).
  Al final de la página va el cierre «¿Y a ti, cuánto te toca?».
- `numeros-la-deuda.html` y `numeros-se-revisa.html` redirigen ahí (`NUMEROS_ANTES`). Los
  enlaces del Registro de pendientes al estado de resultados van a su página de módulo.

**«Gasto público»: «Se aprueba» y «Se gasta», fundidas; «Se recauda» se llama «Presupuesto» (11-10-2026, sin sello nuevo: no se tocó `assets/`).**
Pedido del autor. Números queda en **cinco** tarjetas y cada una lleva ya su descripción
breve (quinto campo de `NUMEROS_PARTES`, en `<small>`, como en Participa):
Presupuesto, Gasto público, Baja al territorio, Se paga lo que se debe y Se revisa.
- `numeros-presupuesto.html` vuelve a ser la página real (la de «Se recauda», con el
  título «Presupuesto: cuánto dinero es y de dónde sale»); `numeros-se-recauda.html`
  redirige a ella.
- `numeros-gasto-publico.html` junta a los dos: un solo texto, un «Ayer y hoy» con los
  capítulos 5 y 7 del libro, el bloque de los tres presupuestos (`numeros_tres()`) y siete
  tarjetas: el simulador «Reparte tú el presupuesto», cuatro páginas de módulo nuevas
  (`numeros-lo-que-cuestan-los-poderes.html`, `numeros-ramos-y-dependencias.html`,
  `numeros-margen-del-presupuesto.html`, `numeros-lo-que-la-cifra-no-dice.html`) y, por
  ser herramientas, megaobras y costo ambiental, que ahora llevan a
  `herramienta-megaobras.html` y `herramienta-ambiente.html` en vez de duplicarlas.
  `numeros-se-aprueba.html` y `numeros-se-gasta.html` redirigen ahí (`NUMEROS_ANTES`).
- `NUMEROS_MODULOS` lleva un sexto campo, la parte a la que pertenece cada módulo, y
  `numeros_modulo()` arma su navegación «Más de …» con sus hermanos.
- Las redirecciones (`redireccion()`) conservan ya la consulta (`?…`) y el `#ancla` cuando el
  destino no trae los suyos, y las páginas de cada parte mandan un `?abrir=eb-*` viejo a
  la página de su módulo (sin bucle: se omite el que apunta a sí misma).
- (Resuelto con el sello 20261011c.) Quedaba en los comentarios de `numeros.js` el nombre viejo `numeros-se-recauda.html`; no
  se cambió para no tocar `assets/` (y subir el sello) solo por un comentario.

**«Presupuesto» y «Se recauda», fundidas (11-10-2026, sello 20261011b).**
Pedido del autor: fusionar las dos tarjetas, conservar lo mejor de ambas y derivar
páginas nuevas. Números queda en **seis** tarjetas. `numeros-se-recauda.html` lleva:
arriba «El peso de 2026» (las dos barras, `numeros.js`); después «Los 16 orígenes del
ingreso» (`numeros_renglones()`), nativo y con contador («▶ Contabilizar» / «↺ Reiniciar
en ceros», que arranca en ceros) en el mismo `numeros.js`, más los tres rubros que la LIF deja en $0.0.
- **Cada renglón tiene su página** (`ingreso_pagina()`, `numeros-ingreso-*.html`, 16):
  cifra oficial, «de cada $100» (derivado, con su operación), qué grava, efecto jurídico,
  ley con su referencia, glosario y su desglose (`componentes` de `panoramaErario`,
  negativos rayados en rojo). El ISR y los demás sin componentes dicen que la LIF los
  autoriza en un solo renglón: no se inventa desglose. Era la ficha que el motor abría en
  una ventana lateral **dentro** del visor, donde quedaba fuera de la vista (el error del
  desglose que señaló el autor).
- **Las otras tarjetas tienen su página de módulo** (`NUMEROS_MODULOS`, `numeros_modulo()`,
  con el bloque del motor en un marco, como los módulos de herramientas):
  `numeros-cuanto-dinero-es.html`, `numeros-a-que-equivale.html`,
  `numeros-camino-del-dinero.html` y `numeros-paquete-2027.html`.
- `numeros-presupuesto.html` fue una redirección a «Se recauda» hasta que esa página tomó el nombre «Presupuesto» (ver arriba).
  `?abrir=eb-*` y las anclas viejas llevan a la dirección nueva (`NUMEROS_ABRIR` guarda
  ya la URL completa).
- Herramientas: nada de estas dos tarjetas era herramienta ni estaba duplicado en ellas.
  Para la siguiente tarjeta queda una duplicada: «El reloj de la deuda» (Se paga lo que se debe) abre el módulo
  de la Calculadora Cívica, que ya tiene página propia en `herramienta-calculadora-reloj.html`.

**Números en siete páginas (11-10-2026, sello 20261011a).**
Pedido del autor: replicar la estructura del Radar hacendario. `sigue-el-dinero.html`
es ahora una portada de **siete tarjetas** sin número y sin descripción, y cada una abre
su página (`NUMEROS_PARTES` y `numeros_preparar()` en `apartados.py`):
`numeros-presupuesto.html` (El peso de 2026, `numeros.js`), `numeros-se-recauda.html`,
`numeros-se-aprueba.html`, `numeros-se-gasta.html` (los tres presupuestos),
`numeros-baja-al-territorio.html`, `numeros-la-deuda.html` (línea de tiempo) y
`numeros-se-revisa.html` (con el cierre «¿Cuánto te toca?»). Cada paso conserva su
franja «Ayer y hoy» y la nota [119] al pie; todas llevan la barra `numeros_nav()`.
Las anclas viejas (`#origen`, `#gasta`, `#numPeso`, `#ati`...) y `?abrir=eb-*` se
redirigen solas a la página que corresponde (`hash_a_pagina` y `abrir_a_pagina`).
En `numeros.js`, «Ver el paso N» pasó a «Ver «nombre de la página»».

**Números reorganizado (10-10-2026, sello 20261010zf).**
Pedido del autor: la pestaña estaba «fuera de orden» (un camino de cinco pasos arriba y
seis capítulos con otra numeración abajo) y la «Nota de referencia» era un apartado.
Ahora `sigue-el-dinero.html` es un solo recorrido de **seis pasos**, que son las pestañas:
1 Se recauda (`#origen`), 2 Se aprueba (`#decide`), 3 Se gasta: los tres presupuestos
(`#gasta`), 4 Baja al territorio (`#baja`), 5 Se paga lo que se debe (`#deuda`) y 6 Se
revisa (`#revisa`, nuevo: ASF, Cuenta Pública, Estado de Cuenta Cívico, Expedientes).
«¿Cuánto te toca?» dejó de ser pestaña: es el cierre del recorrido y `#ati` redirige a
`herramienta-calculadora.html`. El simulador «Reparte el presupuesto» entró al paso 2.
- **El peso de 2026** (arriba de los pasos): dos barras con todo lo que entra (Ley de
  Ingresos, 4 grupos) y todo lo que sale (presupuesto social, nacional, del Estado, fondos
  de estabilización y lo ya comprometido). Al tocar un tramo se abre su detalle: cifra,
  «de cada $100», chip, de qué está hecho, fuente, glosario y el paso donde se explica.
  Lo arma `numeros_datos()` en `apartados.py` con `panoramaErario` y lo pinta
  `assets/auditor/js/numeros.js` (+ `numeros.css`). Ninguna cifra se escribe en el JS.
- **Los tres presupuestos** (paso 3, `numeros_tres()`): la lectura doctrinal en tres
  renglones, armada con la clasificación funcional oficial (CGPE 2027, p. 39):
  del Estado = Gobierno $320,700.0 + poderes y autónomos $142,300.0 = $463,000.0 mdp
  (derivado); nacional = Desarrollo económico $1,695,700.0 (oficial); social = Desarrollo
  social $4,929,400.0 (oficial). Aparte, ya comprometido (no programable) $3,098,974.9
  (derivado: costo financiero + Ramo 28 + ADEFAS) y fondos de estabilización $6,600.0.
  Suman $10,193,674.9; los $8.8 mdp restantes son redondeo de la fuente (lo dice la página).
  Advertencia escrita: agua potable y urbanización van en desarrollo social en la
  clasificación oficial, no en el presupuesto nacional de la doctrina.
- **La nota del libro** ya no es enlace ni ventana: es la nota [119] al pie («Notas y
  referencias», `libro_pie()`), con la ficha del compendio, los conceptos en el glosario
  y el Diccionario. La franja «Ayer y hoy» de cada paso va plegada y llama a esa nota.
- Pendiente de verificación editorial: la página del libro donde aparece la lectura en
  tres presupuestos. La plataforma la atribuye a «la doctrina del derecho económico» con
  la nota [119] general, sin número de página.

**Tarjetas del Radar con descripción narrativa (12-10-2026, sin cambio de sello).** A pedido del autor, las seis tarjetas de `radar-hacendario.html` vuelven a llevar texto: una frase corta (unas dos líneas), sin cifras; el autor pidió acortar la primera versión, que era de párrafo. Viven en `RADAR_NARRATIVA` (`herramientas/apartados.py`). Esto revierte, solo en esas seis tarjetas, la decisión siguiente; la barra `radar_nav` y las tarjetas de `radar-hoy.html` siguen sin texto.

**Tarjetas del Radar sin descripción (10-10-2026, sin cambio de sello).**
Decisión del autor: las tarjetas del Radar hacendario llevan solo icono y título. Se
quitó el texto descriptivo de las pestañas de `radar-hacendario.html`, de la barra
«Radar hacendario: todas sus partes» (`radar_nav`) y de las dos tarjetas de
`radar-hoy.html`. Lo descriptivo queda en la entrada de cada página. `RADAR_PARTES`
conserva su descripción porque el índice general la usa. No se tocó `assets/`.

**«El peso en el tiempo», en tres páginas y con simulador (12-10-2026, sello 20261012f).** Pedido del autor: `radar-peso.html` queda como índice de tres tarjetas, cada una con su página (`RADAR_PESO_PARTES` en `apartados.py`, con `padre3` hacia el índice):
- `radar-peso-monedas.html`, **El peso frente al dólar, el euro y la inflación**: las tarjetas de hoy y las tres gráficas, ahora con un simulador. «▶ Recorrer los sexenios» avanza año por año de 1988 a la proyección de 2032; la gráfica se descubre hasta ese año, la franja del presidente se resalta y un marcador dice el año, quién gobernaba (nombre completo y periodo) y cuenta hasta las cifras de ese año. Arranca en ceros y «↺ Reiniciar en ceros» lo regresa ahí. También hay una barra para elegir el año, botones con cada presidente y la gráfica se puede tocar. En celular el lienzo es más angosto (430 en vez de 720 unidades) para que sus letras se lean.
- `radar-peso-sexenios.html`, **El peso en cada sexenio** (la tabla de antes).
- `radar-peso-maquina.html`, **La máquina del tiempo del peso** (la de antes).
Las cifras del marcador son las mismas de las gráficas (Banxico, y la proyección de los Criterios Generales de Política Económica de Hacienda); donde no hay dato lo dice: el euro antes de 2000, el euro proyectado, los años sin administración del radar. `radar.js` arranca cada bloque solo si su página lo trae. No se agregó ni cambió ninguna cifra.

**El reloj corre con los años que sí tienen dato (12-10-2026, sello 20261012e).** Pedido del autor: que en `radar-reloj.html` ninguna combinación se quede sin contador, con los datos que ya tenemos y con su porqué a la vista. Antes, 28 de las 120 combinaciones (administración × qué contar × moneda) mostraban solo «pendiente». Ahora corren 112:
- **Salinas** (ingresos, gasto, inversión e intereses): el ritmo es la suma de 1990 a 1994, los cinco años con dato, entre los segundos de esos cinco años. La suma del sexenio sigue `pendiente` en el tablero y en el duelo (no se compara con sumas de seis años); el reloj solo usa el ritmo, con chip `derivado` y el `pendiente` de `radar-1989` al lado.
- **Zedillo en euros:** el ritmo es el de 2000, el único año del sexenio con cotización del euro en Banxico.
- **Salinas en euros** no existe (no había euro): esa opción se desactiva, el reloj pasa a «pesos de hoy» y se dice por qué.
`apartados.py` agrega un campo `parcial` (valor, años, operación y justificación) a los valores que no se pueden sumar completos; `radar.js` lo usa solo en el reloj. **Queda pendiente** la «Deuda nueva» de Salinas y de Zedillo (8 combinaciones): no hay en la base un saldo en pesos de la misma serie al recibir y al entregar (el SHRFSP empieza en 2000; para 1994 solo hay la deuda neta de Banxico como % del PIB). Para completarla haría falta integrar el saldo en pesos de la deuda neta de los Informes Anuales de Banxico (1988, 1994 y 2000), con su fuente. No se agregó ni cambió ninguna cifra.

**El duelo arranca en ceros (12-10-2026, sello 20261012c).** Pedido del autor: en `radar-duelo.html` (Datos → Radar hacendario → Duelo de administraciones) las cifras y las barras nacen en cero y el botón «▶ Empezar duelo» las lleva a su valor (1.8 s; instantáneo con `prefers-reduced-motion`). El mismo botón pasa a «↺ Reiniciar en ceros», y cambiar cualquiera de las dos administraciones también regresa todo a cero. El HTML lo arma `duelo_html` en `apartados.py` (`#rdDueloCuenta`, `#rdDueloBtn`, `#rdDueloTxt`) y la animación vive en `radar.js` con el mismo método de tramos `.rd-num` que «Contar». No se agregó ni cambió cifra. Ajuste del mismo día (sello 20261012d), a pedido del autor: el botón se encimaba con el segundo selector, así que ahora va centrado y en columna: primero el aviso, debajo el botón y luego los nombres de los presidentes (`.rd-duelo-cuenta` en `radar.css`).

**El contador de «Hoy: el presupuesto en curso» (10-10-2026, sello 20261010ze).**
Pedido del autor: en `radar-presupuesto-en-curso.html` las cifras arrancan en cero y el
botón «▶ Contar» las anima hasta su valor (2.4 s, curva de salida; instantáneo con
`prefers-reduced-motion`). El mismo botón pasa a «↺ Reiniciar en ceros». El recuadro
«Durante tu visita» queda borroso y con candado, y su reloj no corre, hasta que se
presiona «Contar»; al reiniciar vuelve a bloquearse y a cero. El HTML lo arma
`RADAR_HOY` en `apartados.py` (`#rdCuenta`, `#rdContar`, `#rdHoyVivo`, `#rdCandado`) y la
animación vive en `assets/auditor/js/radar.js`: las cifras siguen escritas completas en el
HTML (sin JavaScript se ven tal cual y el botón no aparece); el script parte cada número
en tramos `.rd-num` con sus mismos decimales y separadores. No se agregó ni cambió cifra.

**La institución como órgano en los estados de cuenta de cargos (10-10-2026, sello 20261010zd).**
A pedido del autor, los 35 documentos de cargos (diputación federal, Senado,
32 congresos locales y Suprema Corte) suman, al frente y después del
termostato, un panel «Como órgano: cuánto nos cuesta y qué revisó la Auditoría
Superior». Lo arma `radar_cargos()` con dos secciones marcadas `panel`. El
sello las firma como cualquier otra sección.
- **Lo que nos cuesta** (`panel: costo`):
  - Federales: el aprobado 2026 (PEF, Anexo 1). Cada día = aprobado ÷ 365.
    Por habitante = aprobado ÷ 134,407,258 (CONAPO, mitad de 2026, derivado).
  - La parte del gasto 2025 que se fue en servicios personales: capítulo 1000
    ÷ total ejercido. Diputados 57.1% y Senado 59.1% (CP 2025). Corte 84.7%,
    con su estado analítico y el renglón «Total».
  - Congresos locales: lo ejercido en 2024 (INEGI, CNPLE). Cada día = ÷ 366,
    porque 2024 fue bisiesto.
  - **Sin costo por habitante en los congresos locales**: falta integrar la
    población de 2024 del CONAPO (el proxy de esta sesión no dejó bajar el
    CSV), y dividir entre la de 2026 mezclaría años.
- **Del dinero que ejerció a lo que falta aclarar** (`panel: embudo`):
  - Lo ejercido en 2024. Diputados: pagado según ASF_DIP p. 4. Senado:
    devengado según ASF_SEN p. 5. Corte: CP 2024 por UR, en mdp, derivado.
  - El universo y la muestra de la ASF; la parte revisada = muestra ÷
    ejercido; lo que quedó fuera de la muestra.
  - Acciones, monto por aclarar y recuperaciones de la Matriz de Datos Básicos
    (ASF_MDB, p. 31), con el resultado.
  - Corte: la Matriz no da la muestra en pesos, solo su representatividad
    (92.81% del universo). Recuperaciones: $8,133,300.
  - Congresos locales: solo NL (auditoría 1402: $4.5 millones por aclarar) y
    Tlaxcala (1940: $5.0 millones recuperados). En los demás, el frente dice
    que la auditoría no está integrada en la plataforma, sin culpar a nadie.
- Se quitaron las secciones viejas «Ante la Auditoría Superior» y «El congreso
  del estado: lo que gastó», que quedaron dentro del panel, y el «Aprobado
  2026» repetido en el presupuesto. Los capítulos 2026 de la Corte pasan a su
  propia caja.
- **Cambian los folios de los 35 documentos de cargos**: su contenido cambió.
  Los de las administraciones siguen iguales.
- Hojas: 39 de 42 caben en dos. Los de Diputados, Senado y la Corte ocupan tres
  porque el frente se extiende.

**El sello se titula «Dictamen técnico de Auditavisión» (10-10-2026, sello 20261010zc).**
A pedido del autor, el pie del estado de cuenta ya no dice «Sello de
verificación de Auditavisión»: el título, el anillo del sello y su texto
alternativo dicen «Dictamen técnico de Auditavisión». La leyenda, la huella
y los folios no cambian.

**«Verifica un estado de cuenta», al Modo Inspector (10-10-2026, sello 20261010za).**
A pedido del autor, la sección de verificación salió de la página que expide
el estado de cuenta y es el **módulo 7 del Modo Inspector**, con página propia:
`herramienta-inspector-verifica.html` (parte «Busca y verifica»).
- La arma `radar()` en `apartados.py` a partir de `herramienta_modulo()` (misma
  cabecera, migas y navegación de módulos), pero en vez del marco carga
  `#rdDatos`, `#exCargos` y `estado-administracion.js`. La clave
  `inspverifica` está en `MODULOS_PROPIOS` para que el ciclo de herramientas no
  le genere un marco.
- `estado-administracion.js` arranca solo la verificación cuando la página no
  trae `#exDoc`. «Ver el documento» es un enlace a
  `radar-estado-de-cuenta.html?adm=` o `?doc=`, que lo genera al abrir.
- El sello de los documentos nuevos apunta a
  `herramienta-inspector-verifica.html?verifica=FOLIO`. Los PDF impresos antes
  llevan `radar-estado-de-cuenta.html?verifica=`: esa página los redirige.
- Folios y huellas no cambian. La página que expide termina con el documento
  generado: no lleva ningún aviso de verificación (pedido del autor, sello
  20261010zb).

**El estado de cuenta, en una hoja por los dos lados (10-10-2026, sello 20261010z).**
A pedido del autor (referencia: hoja oficio, 216 × 340 mm; «la medida es lo de
menos»: lo que importa es separar lo gráfico al frente y lo informativo atrás):
- **Imagen del encabezado:** la que mandó el autor (ilustración de una mesa de
  sesiones), recortada a una franja que deja ver la mesa y su gráfica circular
  y fuera la marca de agua de la esquina:
  `assets/auditor/img/encabezado-estado-de-cuenta.jpg` (736 × 240). Va en los
  42 documentos.
- **Anverso, lo gráfico:** encabezado, el **termostato** (una rueda con un gajo
  por indicador o señal y su color, sin sumar en nota global, y un medidor por
  indicador de peor a mejor en tres tercios con la marca donde cae la cifra; en
  los cargos, el tope del art. 127 en escala de 0 a 120% y las palomitas de
  bruta y neta) y las cuentas en cajas: concepto, cifra, chip de estado y un
  número de nota. **Los negativos van en rojo** (`.ex-neg`).
- **Reverso, lo informativo:** la justificación por secciones, en dos
  columnas: cada nota numerada dice qué mide la cifra, su operación, su regla
  y su fuente (F1, F2… con página); luego el fundamento legal, las fuentes
  oficiales y al final el sello con la leyenda de que no es documento oficial.
- **La huella no cambió:** firma las mismas cifras, así que los folios ya
  expedidos siguen valiendo.
- **Al descargar:** `@page` de 216 × 340 mm; el reverso empieza en hoja nueva.
  Antes de imprimir, `emparejar()` mide cada caja con el ancho de la hoja
  (`.ex-medir`) y las reparte en dos columnas parejas en orden de lectura. Las
  tablas de más de 8 renglones van a lo ancho, partidas en dos. Caben en una
  hoja por los dos lados 40 de los 42 documentos; la diputación federal y la
  senaduría ocupan un poco más en el anverso (hoja 3).

**«Hoy y los estados de cuenta» se vuelve índice de dos páginas (10-10-2026, sello 20261010y).**
A pedido del autor, `radar-hoy.html` ya no muestra el presupuesto en curso: es un
índice con dos tarjetas, «📌 Hoy: el presupuesto en curso»
(`radar-presupuesto-en-curso.html`, nueva) y «🧾 Expide un estado de cuenta»
(`radar-estado-de-cuenta.html`). Las anclas viejas `#hoy` y `#expide` de
`radar-hoy.html`, el `#hoy` de `radar-estado-de-cuenta.html` y las `rc-*` de
Números llevan a la página de cada una.

**«Expide» abre su propia página y el documento se genera con un botón (10-10-2026, sello 20261010x).**
A pedido del autor:
- **Página propia.** La tarjeta «🧾 Hoy y los estados de cuenta» del Radar lleva
  ahora a `radar-hoy.html` (que dejó de ser redirección): el presupuesto en
  curso y una tarjeta que abre la herramienta en `radar-estado-de-cuenta.html`.
  La herramienta se queda en esa dirección porque va impresa en el sello de los
  PDF (`?verifica=`, `?doc=`, `?adm=`). El ancla vieja `#hoy` de esa página
  lleva a `radar-hoy.html#hoy`.
- **Botón «🧾 Generar estado de cuenta»**, junto a «Descargar en PDF». Elegir
  de quién ya no arma el documento: queda en espera hasta que se presiona el
  botón, y «Descargar en PDF» se habilita solo después. Un enlace compartido
  (`?doc=` o `?adm=`) y el «Ver el documento» de la verificación lo generan
  directamente, porque son documentos ya expedidos.
- **Encabezado más amplio**, con el logo a 104 px (antes 54) y espacio para una
  imagen que se repite en todos los estados de cuenta. La imagen se guarda como
  `assets/auditor/img/encabezado-estado-de-cuenta.(svg|png|jpg|jpeg|webp)`:
  `apartados.py` la detecta y la pone en `data-cabecera` de `#exApp`; si no
  existe, no se pide nada al servidor. **Pendiente: el autor enviará la imagen.**

**Se suma la senaduría al estado de cuenta (10-10-2026, sello 20261010w).**
El autor notó que faltaban los senadores. Quinto tipo en «¿De quién?»: la
senaduría (`?doc=senado`, folio `AV-SEN-…`). Lo que cobra (dieta neta del
Manual del Senado; bruta, ISR, neta, aguinaldo y prima del seguro de vida del
Anexo 23.2.2), sus asesores (niveles 34, 30 y 29 del tabulador), 128
integrantes (CPEUM art. 56, cotejado), presupuesto 2026, avance a junio,
cierre 2025 por capítulo y la auditoría 32 de la ASF (CP 2024) con sus
capítulos. Las dos señales quedan en verde. El aguinaldo que equivale a 60 días
y no a 40 enlaza a su pendiente (`prest-aguinaldo-sen`). Son 35 documentos.

**El estado de cuenta de diputaciones y de la Suprema Corte (10-10-2026, sello 20261010v).**
A pedido del autor, la herramienta «Expide» de `radar-estado-de-cuenta.html#expide`
ya no es solo de las administraciones. El paso 1 pregunta «¿De quién?»:
administración presidencial, diputación federal, diputación local (selector de
los 32 congresos) o Suprema Corte (ministra o ministro, su ponencia y sus
asesores). La tarjeta del Radar se llama ahora «🧾 Hoy y los estados de cuenta».
- **Datos.** `radar_cargos()` en `apartados.py` arma el JSON `#exCargos` (34
  documentos) solo con `comparador_salarial` y `poderes` de la base: lo que
  cobra cada cargo (Manual de la Cámara, Anexo 23 del PEF, Manual del PJF y los
  documentos de 12 congresos), el presupuesto, el ejercicio y la auditoría de
  su institución (PEF 2026, Cuenta Pública 2025, avance al 2.º trimestre de
  2026, SCJN al 31 de agosto, CNPLE 2025 y ASF CP 2024). El JS no escribe
  cifras: solo pinta y firma. Integrantes con su artículo: 500 (CPEUM art. 52)
  y 9 (art. 94).
- **Es el estado de cuenta del cargo, no de una persona:** cada cargo cobra
  con un solo tabulador; no se nombra a nadie.
- **No se reparte el presupuesto entre el número de personas** (ni entre las
  500 curules ni entre diputados locales): ese reparto no es un dato.
- **Dos señales con regla de ley, en vez del semáforo de tercios:** el tope del
  art. 127, fr. II (neto contra neto con la Presidenta: verde si la cifra
  completa queda abajo, rojo si lo rebasa, sin color si es parcial y queda
  abajo) y la obligación de publicar la remuneración bruta y la neta (LGTAIP
  DOF 20-03-2025, art. 65, fr. VII: verde con las dos, ámbar solo bruta, sin
  color si no localizamos el documento de 2026). Ambos artículos se cotejaron
  con el texto vigente de diputados.gob.mx. Resultado: diputación federal 2
  verdes; Corte 1 verde y 1 sin color (cifra parcial); 7 congresos verdes en
  transparencia, 5 ámbar (Sinaloa, Tlaxcala, Nayarit, Campeche, Yucatán) y 20
  sin color.
- **Ponencia de la Corte:** secretario de estudio y cuenta y asesor (rangos
  del Manual del PJF). Cuántas plazas tiene cada ponencia sigue pendiente
  (`poderes-judicial-1`); las cifras de «35 colaboradores» y «$34.2 millones»
  siguen fuera por no tener documento.
- **Pendientes:** nuevo `asesores-congresos-locales` (falta de la plataforma).
  Los `neto-diputado_local-*`, `poderes-legislativo-0` y `poderes-judicial-1`
  ahora también dicen que aparecen en el estado de cuenta.
- **Folio y sello:** `AV-DIPFED-…`, `AV-DL<estado>-…` (`AV-DLGTO-…`) y
  `AV-SCJN-…`; el enlace es `?doc=<id>` (`dip-fed`, `dip-loc-gto`, `scjn`). La
  verificación recorre las 7 administraciones y los 34 documentos. Los folios
  de las administraciones no cambiaron.

**«Hoy» y «Expide el estado de cuenta», una sola tarjeta (10-10-2026, sello 20261010u).**
Por decisión del autor, las dos partes del Radar se fusionaron en la tarjeta
«🧾 Hoy y el estado de cuenta de cada administración». Es una sola página con
dos secciones: `#hoy` (el presupuesto en curso) y `#expide` (la herramienta).
La página conserva `radar-estado-de-cuenta.html`, porque esa dirección va
impresa en el sello de los PDF (`?verifica=`). `radar-hoy.html` es ahora una
redirección (`REDIRECCIONES`) a `radar-estado-de-cuenta.html#hoy`, y las
anclas viejas (`radar-hacendario.html#hoy`, `#expide` y los `#rc-*` de Datos)
llevan a su sección. La página carga `radar.js` (contador de «Hoy») y
`estado-administracion.js`. El Radar queda en seis partes.

**Expide el estado de cuenta de cada administración (10-10-2026, sello 20261010t).**
El autor pidió una herramienta que «expida» el estado de cuenta de cada
administración, de la última presidenta hasta la fecha, con su salud
financiera evaluada y descarga con sello de Auditavisión. Vive en
`radar-estado-de-cuenta.html`, la primera parte del Radar (`RADAR_PARTES`),
y la anima `assets/auditor/js/estado-administracion.js` (+ su `.css`) con el
mismo JSON `#rdDatos` del Radar. Decisiones del autor:
- **Semáforo por indicador, sin calificación global.** Seis indicadores en %
  del PIB (`RADAR_SEMAFORO`): balance presupuestario (ingresos − gasto), cambio
  de la deuda por año, deuda al cierre, peso de los intereses, inversión física
  e ingresos. Regla escrita en el documento: el rango entre la mejor y la peor
  de las administraciones cerradas con dato se parte en tres tercios iguales
  (verde, ámbar, rojo). La deuda de Salinas queda fuera (Banxico, no SHRFSP).
  Lo de la ASF va sin color (la definición del monto por aclarar es de 2019).
  Sheinbaum se evalúa con los mismos cortes, marcada «preliminar» (un año).
  Cita la LFPRH art. 17 (equilibrio presupuestario) como contexto, no como corte.
- **Sello de verificación.** Huella SHA-256 de las cifras del documento (el
  mismo modelo que se pinta), folio `AV-<iniciales>-<8 hex>` que sale de la
  huella, versión de la plataforma y liga `?verifica=<folio>`. La sección
  «Verifica» recalcula las huellas con los datos vigentes. La leyenda dice
  que no es un documento oficial. Si cambian los datos, los folios cambian y
  los documentos viejos ya no verifican: así se dice en el resultado.
- **PDF imprimible.** «Descargar en PDF» copia el documento a `#exPrint` y
  abre la impresión; en `@media print` solo se imprime eso (≈5 hojas carta).
El tablero lleva «🧾 Expide su estado de cuenta» en cada ficha, y el Estado
de Cuenta Cívico enlaza a la herramienta.

**El Radar hacendario, en seis páginas (10-10-2026, sello 20261010s).**
El autor pidió que cada parte del radar tuviera su propia página en lugar
de desplegarse en una sola. `radar-hacendario.html` queda como portada con
seis tarjetas (`RADAR_PARTES` en `apartados.py`), y cada parte vive en la
suya: `radar-tablero.html`, `radar-peso.html`, `radar-reloj.html`,
`radar-duelo.html`, `radar-hoy.html` y `radar-como-leer.html`. Mismo
contenido, mismas cifras y misma interactividad. `radar()` devuelve ahora
la lista de las siete páginas. Cada subpágina lleva al pie la barra
`radar_nav()` con las seis partes y las migas Datos › Radar hacendario.
Las anclas viejas (`radar-hacendario.html#peso`, `#duelo`, etc., y los
`#rc-*` de Datos) redirigen a su página. `radar.js` arranca cada bloque solo
si su página lo trae; el contador de «Hoy» ya no depende de `#rdDatos`. El
pendiente `radar-1989` apunta ahora al tablero, al reloj y al duelo. El
índice general lista las seis partes bajo Datos.

**El peso en el tiempo y una sola fuente para el Radar (10-10-2026, sello 20261010r).**
El autor pidió cerrar los pendientes del radar y tomar en cuenta, en las
comparativas, gráficas y simuladores, la inflación del peso a través del
tiempo, su proyección, su valor actual y su comparativa con el dólar y el
euro.
- **Una sola fuente para las series anuales.** Las cuatro series (ingresos,
  gasto neto, inversión física y costo financiero) salen ahora, de 1990 a
  2025, de las **Estadísticas Oportunas de Finanzas Públicas de Hacienda**
  (`presto.hacienda.gob.mx`, cuadro «Pesos corrientes multianual», anual):
  pesos y % del PIB, ambos **oficiales**. Sustituyen al Anexo del 5.º
  Informe (1995-2016) y a los Criterios (2017-2025), y quitan el salto de
  definición entre gasto neto total y pagado. La inversión física
  presupuestaria es unas décimas menor que la del Anexo en algunos años.
  - El portal pide sesión: se consulta con un navegador automatizado que
    abre el menú y reescribe la consulta (formatos 3, 5, 11 y 12;
    presentación 1 = millones de pesos y 6 = % del PIB).
  - **Resuelto:** `radar-salinas-pib` y `radar-pesos-2017` salen del
    Registro. **Queda** `radar-1989`: Hacienda empieza en 1990, así que
    Salinas se mide con cinco de sus seis años (promedio en % del PIB, con
    aviso) y sus sumas en pesos siguen pendientes.
- **`finanzas_sexenales.peso`**, de Banxico (SIE): INPC mensual (SP1,
  1988-sep. 2026), pesos por dólar promedio mensual (SF329, 1988-2026),
  pesos por euro (SF57923, desde 2000: antes no hay serie), el FIX y el euro
  del 9 de octubre de 2026 (SF43718 y SF46410) y la **proyección oficial**
  de los Criterios 2027, Anexo III.1 (p. 69 del PDF): inflación dic/dic y
  dólar promedio 2026-2032. El euro no tiene proyección oficial y se dice.
- **En la página:**
  - selector de moneda en las sumas del tablero, el reloj y dos renglones
    del duelo: pesos de cada año, **pesos de hoy** (× INPC sep. 2026 ÷ INPC
    promedio del año), dólares y euros (÷ tipo de cambio promedio del año);
  - **💱 El peso en el tiempo:** tarjetas de hoy (dólar, euro, inflación de
    12 meses y proyección), tres gráficas SVG con las bandas de cada
    sexenio y la proyección punteada (lo que cuesta lo mismo, inflación año
    por año, dólar y euro), el peso en cada sexenio (inflación acumulada y
    tipo de cambio al recibir y al entregar) y la máquina del tiempo del
    peso.
- **Para actualizar:** cada mes cambian el INPC y el tipo de cambio; cada
  septiembre, la proyección (Criterios). Se reemplaza el bloque en la base
  y se sube el sello.
- Posible siguiente paso: con la misma fuente se pueden llenar los pesos
  de 2024 del Estado de Cuenta (`estado-cuenta-pesos-2024`); el
  subejercicio sigue necesitando el Tomo II de la Cuenta Pública.

**Radar hacendario: cada administración, con sus números (10-10-2026, sello 20261010q).**
El autor pidió que el radar dejara de ser cifras sueltas de 2026 y mostrara,
administración por administración, los ingresos, la inversión, el costo, la
deuda y lo pendiente ante la ASF, con simuladores. Ahora es su propia página,
`radar-hacendario.html` (pestaña de Datos con ➔; `#radar` y las anclas
viejas `#rc-*` redirigen).
- **Cómo se genera.** `radar()` en `apartados.py`, con `radar.css` y
  `radar.js`. Python promedia y suma; cada cifra llega al JSON `#rdDatos`
  con su chip, su operación y su fuente. Se borraron
  `herramientas/plantillas/radar.html` y `assets/auditor/js/radar-datos.js`.
- **Qué hay:**
  - **El tablero:** siete administraciones (Salinas a Sheinbaum, esta
    marcada «en curso: solo 2025»), cinco tarjetas (💰 ingresos, 🏗️
    inversión, 🏛️ costo del gobierno e intereses, 📉 deuda, ⚖️ ASF) y, al
    tocar una, la comparativa en barras que crecen desde cero, con el
    detalle «¿De dónde sale?» de cada cifra y las megaobras del sexenio.
  - **⏱️ El reloj de cada administración:** deuda nueva, intereses,
    inversión, ingresos o gasto al ritmo promedio de su sexenio (suma ÷
    segundos de sus seis años).
  - **⚔️ Duelo:** dos administraciones cara a cara, sin ganador.
  - **📌 Hoy:** las cifras 2026 del radar anterior, con su chip, y las
    equivalencias durante la visita.
- **Los datos nuevos** viven en `AUDIT_DB.finanzas_sexenales`:
  - 1995-2016: montos de la Cuenta Pública según el Anexo Estadístico del
    5.º Informe de Gobierno (pp. 447, 453 y 463); su % del PIB es
    **derivado** con el PIB nominal del INEGI base 2018 (PIBT_3).
  - 2017-2025: el % del PIB **oficial** de los Criterios Generales 2024
    (2017-2018), 2026 (2019) y 2027 (2020-2025), todos ya en base 2018.
    Los Criterios anteriores usaban base 2013 y no se mezclan.
  - Deuda al recibir y al entregar: la misma serie de la trivia y de la
    línea de tiempo de Números. **Si cambia allá, cambia aquí.**
  - ASF: `evaluacion_sexenal` y, para 2025, la primera entrega de la CP 2025.
- **Pendientes nuevos en el Registro (resueltos con el sello 20261010r):** `radar-salinas-pib` (el PIB base
  2018 empieza en 1993: Salinas sin % del PIB) y `radar-pesos-2017` (los
  montos en pesos de 2017 a 2025 están en la Cuenta Pública, que no se
  pudo abrir). Por eso el reloj y las sumas en pesos solo corren para
  Zedillo, Fox y Calderón (y la deuda, para todos los sexenios cerrados).
- **Ojo al leer:** con el PIB base 2018 los porcentajes de los noventa
  salen más bajos que los que Hacienda publicó entonces; está dicho en
  «Cómo leer».

**Garantías cívicas tiene su propia página (10-10-2026, sello 20261010p).**
El autor leyó la pestaña «Garantías cívicas» de Participa y perdió su
objetivo: juntaba cinco bloques largos y tres repetían lo que ya vive en
otro lado. Se depuró y se mudó a `garantias.html`.
- **Qué se quitó y a dónde fue:**
  - la orientación de «las tres funciones» y «a dónde va lo que escribes»:
    lo dicen ya Comunidad, el cajón «Cuéntanos lo que viste» y el aviso del
    Ágora; en la página nueva queda en una sola línea («Importante»);
  - la «Función 1», copia de «Cuéntanos lo que viste»: vive en la cabecera
    y en `comunidad.html`;
  - `herramientas/participa_html.py` y `assets/auditor/js/participa.js`
    quedaron sin uso y se borraron (la portada conserva su propia copia en
    el motor). `participa.html` ya no carga scripts.
- **Qué se quedó, con un objetivo claro:** a qué puerta oficial tocar, qué
  te protege y qué llevar. La página sale de `garantias()` en
  `apartados.py`, con `garantias.css` y `garantias.js`:
  - **🧭 La brújula:** tres preguntas (qué viste, si tienes prueba, si
    necesitas no dar tu nombre) y la ruta en pasos. Sin prueba, el paso 1
    es la PNT; si es delito y no quieres dar tu nombre, agrega la
    plataforma de alertadores de la SABG. La lista `BRUJULA_QUE` resume el
    «para qué» de cada canal.
  - **🚪 Las seis puertas:** fichas cortas con «¿Sin dar tu nombre?» y un
    `<details>` con qué llevar, qué produce y el fundamento.
  - **🛡️ Las diez garantías:** el decálogo en cartas que se voltean (sin
    JavaScript se leen las dos caras).
  - **🎯 ¿Mito o realidad?:** siete afirmaciones (`GARANTIAS_RETO`); la
    explicación y el fundamento de cada una se leen del decálogo o del
    canal en la base.
  - Todo el texto legal sale de `window.AUDIT_DB` (`comunidad.*` y
    `referencias_legales`); no se teclea en el generador.
- **En la base:** los textos de los canales y del decálogo pasaron al tú
  («adjúntalos», «Pregunta por escrito», «documenta»…).
- **Enlaces:** la pestaña lleva ➔ y `participa.html#garantias` redirige a
  la página; el cajón y su nota de denuncia enlazan a `garantias.html`; el
  índice general toma la página de la pestaña.

**El Ágora cívica tiene su propia página (10-10-2026, sello 20261010o).**
La pestaña «Ágora cívica» de Participa ya no despliega su contenido: abre
`agora.html`, la red de réplica y diálogo. Es decisión del autor: «que
funcione como red social».
- **Cómo se genera.** La página sale de `agora()` en `apartados.py`, con
  `agora.css` y `agora.js`.
  - Las listas `AGORA_TEMAS`, `AGORA_POSTURAS`, `AGORA_PREGUNTAS` y
    `AGORA_REGLAS` viven ahí.
  - Temas, posturas y colores le llegan a la página en `#agDatos`.
- **Qué hay en la página:**
  - **Perfil cívico:** seudónimo con 🎲, lugar, una línea y color de
    avatar, más contadores de hilos, réplicas, apoyos dados y hilos con
    fuente.
  - **Cinco insignias** locales: 🗣️ Primera voz, 📄 Cita su fuente,
    🏛️ Fuente oficial, 🔁 Replicador y 🤝 Escucha activa.
  - **El muro:**
    - compositor con postura (incluye ❓ Pregunta), tema y enlace a la
      fuente;
    - orden por recientes, más apoyados, más replicados, con fuente o mis
      hilos;
    - filtros por #tema y búsqueda.
  - **Cada hilo:**
    - Apoyar, Replicar (el hilo se despliega con su formulario), Compartir
      (`agora.html#<id>`), Ver los datos (la página de su tema) y Borrar si
      es tuyo;
    - 🔍 Pedir fuente, cuando el hilo no la trae;
    - la fuente lleva una etiqueta: «dominio oficial» (gob.mx, ASF,
      INEGI, Banxico…), «otra fuente» o «sin enlace».
  - **Columna derecha:** temas en conversación, preguntas para empezar
    (las propone la plataforma, sin cifras), cómo se replica bien y lo que
    llega con el servidor.
  - **Descargar mis hilos** en JSON.
- **Honestidad.** El aviso «Versión de prueba» dice que todo vive solo en
  el navegador. No hay hilos sembrados con usuarios inventados. Los hilos
  usan la llave del foro anterior (`auditavision_foro_debates`), así que no
  se pierde nada.
- **En Participa:**
  - la pestaña lleva ➔, y una sección con `'pagina'` se pinta como enlace,
    sin panel;
  - `apartados.js` deja pasar el clic de una pestaña sin `aria-controls`;
  - `participa.html#agora` redirige a la página nueva (`hash_a_pagina`);
  - la ruta 3 de la orientación lleva a `agora.html`.
- **Pendiente:** el muro público, seguir temas o personas, los avisos de
  réplica, la moderación y la verificación entre pares necesitan
  servidor.

**Una sola puerta: «Cuéntanos lo que viste» (10-10-2026, sello 20261010n).**
El autor notó que «📢 Cuéntanos lo que viste» (cabecera) y «✏️ ¿Viste un
error?» (pie) hacían casi lo mismo. Le gustaba el cajón que se despliega del
primero y la página Comunidad del segundo. Se fusionaron:
- **Hay un solo botón: «📢 Cuéntanos lo que viste».** Está en la cabecera
  de todas las páginas, en el menú de celular y en el botón flotante de la
  portada. Abre el mismo cajón lateral en todas, incluida `index.html`.
  Antes, en las páginas generadas, mandaba a la portada.
- **El cajón tiene tres rutas que se despliegan** (`<details>`; abrir una
  cierra las otras):
  1. **Algo raro con el dinero público.** Pide qué fue, dónde, cuándo, qué
     viste, con qué dinero y con qué prueba. Aclara que no es denuncia y
     enlaza las seis puertas oficiales (`participa.html#garantias`).
  2. **Un dato mal en esta plataforma.** La página ya va escrita.
  3. **Un tema que deberíamos investigar.**
- **Fuente única.** `formas(pre)` en `apartados.py` arma los tres
  formularios. Los usan el cajón (`puerta()`, con id `pt…`) y
  `comunidad.html` (id `cm…`), que es la versión en página: `#reporta`,
  `#error`, `#tema`, `#compartir` y `#erratas`.
  - `cabecera()` incluye el cajón en cada página generada.
  - `poner_puerta()` lo copia en `index.html` entre
    `<!-- puerta:inicio -->` y `<!-- puerta:fin -->`.
- **JavaScript.** `comunidad.js` abre y cierra el cajón (`window.Puerta`) y
  ahora se carga en todas las páginas. Todo `[data-puerta]` lo abre, y su
  valor (`reporta`, `error`, `tema`) despliega esa ruta. Sin JavaScript, el
  enlace lleva a `comunidad.html`. En la portada,
  `openAyudanosFiscalizar()` del motor llama a `window.Puerta`.
- **CSS.** Los estilos están en `assets/auditor/css/puerta.css`, cargada en
  todas las páginas. Los formularios cívicos (`.sv-form`, `.sv-campo`…)
  pasaron ahí desde `servicios.css`. `sello.py` ya sube el `?v=` de
  `puerta.css` y `comunidad.js` en `index.html`.
- **Lo que se retiró:**
  - el «¿Viste un error?» del pie (`error_pie()`);
  - el buzón viejo del cajón de la portada, que se guardaba en el
    navegador y tenía las opciones «Corrección de dato» y «Sugerencia»,
    duplicadas con Comunidad;
  - su copia en Participa › Garantías cívicas (Función 1), que ahora es un
    acceso a la puerta. `participa_html.APORTAR` quedó sin uso.
  - Los textos de orientación (motor y `participa.js`) dicen ahora que nada
    se guarda.
- **Lo que sigue igual:** el envío espera `CANAL_COMUNIDAD`. Los enlaces
  viejos `comunidad.html?pagina=…#error` siguen funcionando.

**Portada intacta y entrega 7 de Astra: Comunidad (10-10-2026, sello 20261010m).**
- **«Por dónde empezar» salió de la portada** por decisión del autor:
  «la plataforma queda intacta». Su contenido se reparte así:
  - **Investigaciones por tema y «Cómo verificamos»:** van al pie de cada
    `auditoria-*.html`, dentro de «Otras auditorías» (`temas()` en
    `auditorias.py`). El tema del caso va primero y marcado, y las tarjetas
    del mismo tema van antes.
  - **Los cuatro accesos** (Números, Calculadora, Megaobras e Índice) ya
    estaban en el menú y en el índice general.
  - `auditorias.portada()` ya solo escribe los `data-*` del carrusel.
  - Las reglas `.portada-guia*` de `civico.css` quedaron sin uso.
- **`comunidad.html`** (Participa › Comunidad, cuarta pestaña), generada por
  `comunidad()` en `apartados.py`. Tiene cuatro partes:
  1. **Propón un tema.**
  2. **Señala un error.** Pide el dato, lo que dice el documento oficial y
     su enlace, que es obligatorio.
  3. **Comparte el Estado de Cuenta.** Ofrece el menú nativo, WhatsApp, X,
     Facebook y copiar el enlace. Solo se comparte el enlace; el ingreso
     del lector nunca sale de su navegador.
  4. **Fe de erratas** (lista `ERRATAS`). Son cinco correcciones reales
     documentadas aquí: $15,000 de la Calculadora, 515,487 mdp del Tren
     Maya, programas sociales, marco legal y personajes.
     **Cada corrección nueva se agrega a `ERRATAS`**, como pide la
     política de independencia.
- **Formularios.** Los arma `assets/auditor/js/comunidad.js`, que es genérico
  para cada `form.cm-form`. Se firma con seudónimo y el correo es opcional.
  No envía nada mientras `CANAL_COMUNIDAD` esté vacío; se abre con el
  dominio, igual que `CANAL_SOLICITUD`.
- **«✏️ ¿Viste un error?»** está al pie de toda página generada
  (`error_pie()`): apartados, investigaciones, expedientes, estado de cuenta
  y pendientes. Lleva a `comunidad.html?pagina=<archivo>#error` con la
  página ya escrita.

Pendientes de la entrega 7:
- **El canal de envío** (`CANAL_COMUNIDAD`). Espera el dominio.
- **Perfiles, comentarios, expedientes privados, suscripciones y pagos.**
  Necesitan servidor, como dijo Astra.

**Política de independencia, versión 2 (10-10-2026, sello 20261010l).**
Decisiones del autor:
- **La plataforma está abierta a todos, sin exclusión.** Pueden usarla,
  contratarla o licenciarla la ciudadanía, las organizaciones, las
  universidades públicas y privadas, y también los gobiernos. Se puede
  vender o concesionar al gobierno. Lo que se protege es el propósito, la
  información y lo que se publica: nadie compra las conclusiones.
- **Hay un compromiso de transparencia anual:** encargos por tipo de
  cliente, y cuánto entra por cada vía (Pase, Servicios, licencias y
  donaciones). «Si el gobierno falla, nosotros ponemos el ejemplo.»
- **La plataforma podría financiarse con donaciones.**

Cambios:
- `INDEPENDENCIA` pasa de diez a trece compromisos. Se agregan:
  - abierta a todos con las mismas reglas;
  - lo que no está en venta;
  - las donaciones no compran contenido;
  - de qué responde la plataforma y de qué no (corrige en público; no
    responde del contenido de los documentos oficiales ni de las decisiones
    de terceros);
  - el método y las herramientas son de Auditavisión, y una licencia no da
    control editorial.
- **Quinto servicio:** «Licencia de las herramientas».
- **El Pase** (su página y su copia en `index.html`) ya no dice «sin dinero
  de gobiernos ni de partidos». Ahora dice «Abierta a todos; nadie compra lo
  que publicamos».

Pendientes de esta versión:
- **El canal de donaciones.** Espera el dominio y la forma jurídica.
- **La calidad de donataria autorizada ante el SAT.** Solo si el autor
  quiere dar recibos deducibles.

**Propuesta de Astra, entrega 5, parte editorial (10-10-2026, sello 20261010j).**
Toma los puntos 3 y 8 de la propuesta: cada investigación tiene una
lectura breve y otra ampliada, y se puede encontrar en buscadores sin
depender de una pestaña interna. La parte comercial (servicio pertinente,
«Solicita una investigación») espera la decisión del autor sobre el Pase y
los Servicios.
- **Lectura breve en las nueve `auditoria-*.html`.** Va escrita en el HTML,
  así que se lee sin JavaScript. Responde cinco preguntas:
  1. qué pasó;
  2. cuánto dinero, con sus etiquetas;
  3. quién interviene;
  4. qué documento lo acredita, con el enlace a cada informe;
  5. qué falta saber.

  La arma `lectura()` en `herramientas/auditorias.py` con los mismos datos
  de `window.AUDIT_DB` que usa el JavaScript (`expedientes.fichas`,
  `panoramaErario`, `cuenta_publica_asf`, `huachicol_fiscal`); no se
  teclea ni una cifra. La lectura ampliada sigue siendo la que pinta
  `auditoria-imagen.js`, y el paso 1 del recorrido («Entiende el caso»)
  ahora lleva a la lectura breve (`#auLectura`).
- **Dirección estable y tarjeta para compartir.** Cada página generada lleva
  `canonical` y etiquetas Open Graph y Twitter. Las investigaciones usan su
  imagen; las demás, una tarjeta sin imagen. Las arma `sociales()` en
  `apartados.py`; también la usan `auditorias.py` y `expedientes.py`.
- **`sitemap.xml`.** Lo escribe `herramientas/sitemap.py` al final de
  `apartados.generar()` y trae 48 páginas. Deja fuera la Enciclopedia y las
  que solo redirigen. No se escribe `robots.txt` porque el sitio vive en
  `/a/` y los buscadores solo leen el de la raíz del dominio: **el autor
  tiene que registrar el mapa en Google Search Console**
  (`https://uzoraproductos-arch.github.io/a/sitemap.xml`).

Pendientes de la entrega 5:
- **Páginas por tema** para los temas candidatos de Astra que aún no tienen
  la suya: medicamentos falsificados, proveedores y facturación.
  Necesitan documentos oficiales antes de escribirse.
- **Investigación de búsquedas en Google Trends.** Requiere acceso que la
  plataforma no tiene.
- **Enlace a un servicio pertinente.** Espera la decisión del autor.

**Propuesta de Astra, entrega 4: simuladores desde cero (10-10-2026, sello 20261010i).**
Corresponde al punto 6 de la propuesta: los importes arrancan en $0, hay
ejemplo oficial identificado, se pueden comparar escenarios, reiniciar en
cero y descargar la cuenta, y el lector siempre ve que es una simulación.
- **Simulador nuevo, `simulador-presupuesto.html`.** «Reparte el
  presupuesto, desde cero» es el cuarto tema de la Calculadora Cívica.
  - **Dónde vive.** La página la genera `simulador()` en `apartados.py` y
    la pinta `assets/auditor/js/simulador-cero.js`.
  - **Botones:** agregar entrada, agregar destino, repartir en partes
    iguales, cargar el ejemplo oficial (2026 aprobado o 2027 estimado),
    reiniciar en cero, guardar los escenarios A y B (la tabla los compara
    por concepto) y descargar el CSV con el origen de cada renglón.
  - **Reglas a la vista:**
    - el $0 tuyo no es un cero oficial;
    - la etiqueta «tuyo» o «cambiado por ti» frente a «oficial»;
    - dividir entre cero se explica en vez de calcularse;
    - no se comparan pesos contra millones;
    - una nota dice que no predice resultados sociales.
- **El ejemplo oficial.** Sale del cuadro II.6 de los CGPE 2027 (p. 67):
  - entradas: tributarios, no tributarios, petroleros, y organismos y
    empresas;
  - destinos: programable pagado, costo financiero, participaciones y
    Adefas.

  `herramientas/extraer_simulador.py` lo lee del PDF y escribe
  `investigaciones/simulador/cgpe2027-cuadro-ii6.json`. Se detiene si las
  partes no suman los totales del cuadro (ingresos, gasto neto pagado y
  balance), con 0.2 mdp de tolerancia. Con el ejemplo intacto, la página
  coteja su balance con el oficial y explica la diferencia de 0.1 por
  redondeo, que el propio cuadro advierte.
- **La Calculadora Cívica arranca en $0.**
  - **Cifra inventada retirada.** Ya no trae «15,000» escrito, y el
    comparador «Tú contra ellos» ya no usa $15,000 como referencia: esa
    cifra era inventada.
  - **Referencia sin ingreso escrito.** Mientras no escribes tu ingreso, el
    comparador usa el salario mínimo general mensual de 2026 ($9,451.20,
    CONASAMI), rotulado como ejemplo oficial.
  - **Botones nuevos.** «Cargar ejemplo oficial» carga ese salario y saca
    la cuenta. «Reiniciar a ceros» ahora también vacía el campo.
- **Ticket en negativo (Costo Ambiental).**
  - **Botones nuevos:** «Cargar ejemplo oficial» (el mismo salario mínimo)
    y «Reiniciar en cero». Este último está excluido del botón único,
    junto con `ccReiniciar`.
  - **Campo vacío.** El ingreso en $0 ya no se pinta con la etiqueta
    `pendiente`, porque un cero del lector no es un dato pendiente.
  - **Ejemplo retirado.** Se quitó el texto de ayuda «Por ejemplo, 15000».

Pendientes de la entrega 4:
- **Simuladores que faltan revisar.** El paquete económico (palancas), el
  PIB ecológico y las mesas de megaobras arrancan en la base oficial y ya
  traen «Reiniciar a ceros» o «Contabilizar». Falta revisar si alguno
  necesita también «Cargar ejemplo oficial» y descarga.
- **Juegos.** La trivia no tiene importes que editar; no se tocó.

**Aprende: el Diccionario en una sola pestaña (10-10-2026, sello 20261010h).**
Decisión del autor: las pestañas «Biblioteca hacendaria» y «Fuentes del
auditor» se juntan en una, «Diccionario del Gasto Público», con dos
tarjetas. Aprende queda con tres pestañas: Trivia, Diccionario y Noticias.
El orden es Aprende › Diccionario › Estante › Apartado:
- `biblioteca-hacendaria.html` lleva al glosario, al marco legal y a las
  preguntas frecuentes;
- `fuentes-del-auditor.html` lleva al compendio de fuentes y al pase.

Las dos páginas las genera `pagina_estante()` en `apartados.py`, a partir
de `ESTANTES`, que ahora trae el archivo de cada estante. `diccionario.html`
muestra solo las dos tarjetas de estante. Las anclas viejas
`aprende.html#biblioteca` y `#kit`, y las del Diccionario, llevan a su
estante. Las migas de cada apartado dicen Aprende › Diccionario › Estante (campo
`padre3`), y en la barra al
pie el nombre de cada estante es un enlace. El índice general las incluye.

**Regla del rango derivado (10-10-2026).** Decisión del autor: cuando un
dato solo tiene aproximación, se publica como rango (mínimo, máximo y punto
medio = media aritmética) con chip `derivado`, no como `pendiente`. Cada
cota debe salir de un documento oficial; si falta una, sigue `pendiente`.
La cifra exacta conserva su ficha en el Registro. Está en AGENTS.md §2.

Por aplicar (falta documentar las cotas, no se han inventado):
- **`costo_unitario_real` de las megaobras** (`megaobras_historicas`). Hoy
  son frases con cifras sin fuente, como «~$380 por pasajero» en el AIFA o
  «~$1,850 por boleto» en el Tren Maya. Cada una necesita un mínimo y un
  máximo con su fuente: subsidio en el PEF o en la Cuenta Pública entre
  usuarios de AFAC, de la ARTF o del operador.
- **El reloj de pérdidas de las megaobras** (`perdida_anual_consolidada_mdp`
  80,200.1 mdp). Es la suma de `perdida_anual_mdp` obra por obra, y la
  mayoría no tiene documento. Solo pasa a rango cuando cada sumando tenga
  sus dos cotas oficiales.

**Propuesta de Astra, entrega 3: Números y Estado de Cuenta (10-10-2026, sello 20261010f).**

**1. Corrección grave a la base.** `cuentaFederal2024` y `tren_maya_peritaje_2024` entraron en el
commit bd09252 (29-09-2026) sin cotejo («continúa en proceso», decía su
CONTEXT). Aun así se pintaban con el chip `oficial`, y no coincidían con
los documentos:

| Concepto 2024 | Lo que decía la base | Lo que dice el documento |
|---|---|---|
| Ingresos de la gestión | 5,074,180.2 mdp | 5,341,758.1 mdp (Tomo II, Estado de Actividades) |
| Intereses de la deuda | 1,154,230 mdp | 933,408.4 mdp (Tomo II, Estado de Actividades) |
| Producto Interno Neto Ecológico | 29.85 billones | 25.7 billones (ficha del INEGI que cita la propia base) |

Además, su sha256 era el texto `cp2024tomo2oficialshcp`.

Cómo quedaron los dos bloques:
- **`cuentaFederal2024`:** ahora es una lista `cifras` y cada cifra lleva
  `estado`, `fuente` o `motivo`, y `url`. Solo tres son `oficial`:
  - el aprobado PEF 2024 (9,066,045.8 mdp), que leí en el DOF;
  - los ingresos de la gestión y los intereses de la deuda, tomados del
    texto indexado del PDF oficial del Tomo II. **Falta abrir ese PDF y
    confirmarlos.**

  Todo lo demás es `pendiente`: modificado, devengado, pagado, capítulos,
  flujos y balance.
- **Conciliación:** muestra solo los pasos del método, sin importes.
- **`tren_maya_peritaje_2024`:** quedó como `estado: retirado`, con su
  motivo y un enlace al expediente de la ASF. En `index.html` se quitó la
  cifra de 515,487 mdp del recuadro del peritaje.
- **El motor:** `renderCuentaFederal`, `abrirConciliacionPresupuestoContable`
  y `abrirFichaPericialTrenMaya` se reescribieron para estos datos.
- **Por qué no se reemplazó con las cifras oficiales:** el portal de la
  Cuenta Pública no abre desde este entorno. El servidor no envía el
  certificado intermedio de Let's Encrypt (YR1) y el proxy bloquea
  letsencrypt.org.

**2. Estado de Cuenta Cívico** (`estado-de-cuenta.html` y
`estado-de-cuenta-2024-2027.csv`). Lo genera `herramientas/estado_cuenta.py`
con las cifras escritas en el HTML, así que los buscadores lo indexan.

A pedido del autor, compara **2024 observado, 2026 aprobado, 2026 cierre
estimado y 2027 propuesto**:
- **La unidad común es el % del PIB.** Junto a cada porcentaje van los
  millones de pesos de 2026 y 2027.
- **Los pesos de 2024 quedan `pendiente`.** El cuadro histórico solo da el
  porcentaje.
- **De dónde salen las cifras:** de los Criterios Generales 2027 que están
  en la raíz del repositorio (`criterios generales proyecto presupuesto.pdf`):
  - p. 55, «Ingresos y gasto del Sector Público»;
  - p. 52, RFSP y SHRFSP;
  - p. 67, cuadro II.6;
  - p. 33, programas sociales.
- **Cómo se extraen:** `herramientas/extraer_estado_cuenta.py cgpe.txt`
  (texto de `pdftotext -layout`) escribe
  `investigaciones/estado-de-cuenta/cgpe2027-comparativo.json`. Se detiene
  si un renglón no aparece.

Lo que contiene la página:
- **Las dos vistas.** «Tu aportación» enlaza a la Calculadora y al Ticket en
  negativo. «La cuenta pública» va en cuatro dimensiones:
  - presupuestaria;
  - financiera, con la contabilidad 2024 corregida;
  - social, con las becas verificadas y los programas 2027;
  - ambiental, con las CEEM 2024 y el Ramo 16 de 2026 y 2027.
- **Renglones que no se suman,** porque miden cosas distintas:
  - el déficit;
  - lo que la ASF dejó por aclarar en la Cuenta Pública 2024 (65,169.1 mdp);
  - el daño ambiental;
  - el subejercicio (`pendiente`).
- **La descarga** con periodo, alcance y fecha de revisión.

**3. Números.** El camino del dinero tiene ahora cinco pasos. El quinto, «Se
hace el balance», lleva al Estado de Cuenta. El índice y las novedades lo
incluyen.

**Pendientes de la entrega 3:**
- Cotejar el Tomo II de la Cuenta Pública 2024 para llenar los pesos de 2024
  y los estados financieros: devengado, flujos, balance y conciliación.
- Rehacer la ficha del Tren Maya con el Tomo VII y la ASF.
- El selector de año, territorio y programa del punto 4 de Astra. Va con el
  motor de Números; no se empezó.

**Propuesta de Astra, entrega 2: portada e índice (10-10-2026, sello 20261010e).**
El autor pidió seguir con la entrega 2. En la portada solo se agregaron
enlaces: nada se despliega, cada clic abre su página (§5 bis).
- **Tres acciones bajo el carrusel.** «Entiende el caso · Explora los
  números · Revisa la evidencia» cambian con la imagen visible:
  `updateShowcaseDisplay()` del motor lee `data-nombre`, `data-numeros` y
  `data-evidencia` de cada `.showcase-slide`.
- **«Por dónde empezar».** Una sección nueva después del carrusel con cuatro
  accesos: Números, Tu estado de cuenta (`herramienta-calculadora-ticket.html`),
  Simula las megaobras e Índice general. Debajo vienen las investigaciones por
  tema y la franja «Cómo verificamos».
- **Una sola fuente.** Los `data-*` de las diapositivas y la lista de temas
  (entre `<!-- TEMAS:inicio -->` y `<!-- TEMAS:fin -->`) los escribe
  `auditorias.portada()` desde `RUTAS` y `TEMAS`, en binario y sin tocar los
  CR. **No se editan a mano en `index.html`**: se cambian en `auditorias.py`
  y se corre `sello.py` o `apartados.py`. Correrlo dos veces no cambia nada.
- **Índice general (`indice.html`).** Lo arma `indice()` de `apartados.py`
  con las listas que ya existen, así que una página nueva aparece sola:
  - investigaciones por tema;
  - los capítulos de Números, cuyas tarjetas abren con `?abrir=`;
  - las cuatro herramientas con sus módulos;
  - Datos, Aprende, Participa y los Poderes;
  - «Cómo verificamos», con los tres estados y la advertencia de que una
    imagen no es evidencia;
  - las novedades, de la lista `NOVEDADES`, **que se actualiza a mano en
    cada entrega**.

  El pie de cada página generada enlaza al índice.
- El «Volver al Modo Inspector» de Expedientes ahora va a
  `herramienta-inspector.html`.
- **Queda fuera de la entrega 2:**
  - El acceso «Servicios / Solicita una investigación»: falta que el autor
    decida si el Pase convive con los Servicios, y hacen falta una política
    de independencia y la revisión legal.
  - La fecha y el territorio de cada investigación destacada: no hay un dato
    sostenido por caso en la base.
  - Los personajes políticos: se retiraron el 27-09-2026 y no se enlazan.

**Propuesta de Astra, entrega 1 (10-10-2026, sello 20261010d).**
El autor pidió ejecutar las consideraciones de Astra. Su propio plan pone
primero la entrega 1: inventario, corrección de datos y conexión de
Auditoría en imágenes con Números e Inspector. Las pestañas no cambian
(siguen siendo cinco), Auditoría en imágenes sigue siendo el bloque de la
portada y el Inspector vive en Herramientas.
- **Recorrido de cada investigación.** Las nueve `auditoria-*.html` abren con
  tres pasos: 📖 Entiende el caso (la lectura de la misma página),
  💰 Explora los números (`sigue-el-dinero.html?abrir=eb-…`, la tarjeta
  pertinente) y 🔍 Revisa la evidencia (el módulo del Inspector que toca).
  El mapa está en `RUTAS` de `herramientas/auditorias.py`; reutiliza el
  estilo `.camino` de Números con el modificador `.camino-tres`.
- **Programas sociales corregidos** (`cuentaFederal2024.evaluacion_social_mir`
  y la vista «Resultados sociales» del motor). Ahora hay columnas separadas
  de aprobado y devengado, con chip y fuente:
  - **Becas, separadas y verificadas.** S072 (básica): aprobado 49,869.8 y
    devengado 42,571.6 mdp. S311 (media superior): aprobado 39,366.6 y
    devengado 33,301.2 mdp. Fuente: el Estado Analítico de la SEP de la
    Cuenta Pública 2024, tal como lo reproduce la ASF (Auditoría
    2024-5-11O00-19-0113-2025, p. 8). Antes había un solo renglón de
    87,540 mdp sin documento.
  - **Pensión (S176): `pendiente`.** La cifra de 465,048 mdp estaba rotulada
    como devengado y es el aprobado; se retiró. El tomo III de la Cuenta
    Pública (Ramo 20) no se pudo abrir con conexión verificada, porque
    el servidor de Hacienda no envía su certificado intermedio (Let's
    Encrypt YR1) y el proxy bloquea letsencrypt.org. Falta de la
    plataforma, no de Hacienda.
  - **IMSS-Bienestar: `pendiente`** (clave, ramo y montos). Se retiraron los
    128,900 mdp, que no tenían documento. Al cotejar no hay que mezclar el
    programa con el presupuesto completo del organismo.
  - **Resultados, todos `pendiente`.** Se retiraron los porcentajes de
    cumplimiento, cobertura e impacto (101.4 %, 14.2 %, 8.5 pp, 707
    hospitales…), que no tenían documento citado. Propósito, cobertura e
    impacto se mostrarán por separado cuando se coteje la MIR y las
    evaluaciones del CONEVAL.
- **Ramo 28 y CDMX: ya cumplían.** El Ramo 28 por entidad dice «Estimación de
  participaciones 2026, Anexo 15» y la CDMX lleva `sinFuente` con motivo en
  los campos del INEGI.
- **Inventario automático.** `herramientas/inventario.py` escribe
  `docs/INVENTARIO.md`: 43 páginas, 0 enlaces rotos, 1 redirección, y los
  destinos `?ir=` que siguen en la portada (reporta 82, verificador 17,
  megaobras 14, ambiente 13, calculadora 11…). Se corre a mano; devuelve
  1 si hay enlaces rotos.
- **«Los tres presupuestos».** La frase no aparece en ningún archivo del
  repositorio. Ese recorrido no existe todavía con ese nombre.

Pendientes de la propuesta de Astra:
- **Entrega 1:** cotejar la pensión S176 e IMSS-Bienestar en el tomo III,
  bajando los PDF desde otra conexión, y la MIR o CONEVAL de los cuatro
  programas. También el cuadro 3 del libro, con edición y página.
- **Entregas 2 a 4** (portada con tres acciones, Estado de Cuenta en cuatro
  dimensiones y simuladores en $0 con «Cargar ejemplo oficial»): sin
  empezar.
- **Entregas 5 a 7** (páginas temáticas, servicios de pago, comunidad): antes
  el autor tiene que decidir si el Pase convive con los Servicios. Además
  falta una política escrita de independencia frente a clientes y una
  revisión legal del «análisis de indicios».

**El Circuito del Dinero ya no existe: es la pestaña Números (10-10-2026, sello 20261010c).**
Precisiones del autor:
- Las pestañas se quedan como están.
- **Auditoría en imágenes no es pestaña**: es el bloque de imágenes al
  inicio de la portada, y cada imagen lleva a su investigación.
- **El Modo Inspector vive en Herramientas.**
- **El Circuito del Dinero se convirtió en Números** (`sigue-el-dinero.html`).
  Nada debe llevar ya a él.

Inventario: los 10 bloques del módulo `presupuesto` (`eb-arquitectura`,
`cuanto`, `ingresos`, `equivale`, `ciegos`, `egresos`, `salud`,
`cuenta-federal` y `mapa`) ya tenían su tarjeta en Números. Faltaba la
entrada «El camino del dinero, en cuatro pasos», que ahora es el bloque
`CAMINO_NUMEROS` arriba de las pestañas. Conserva el mismo texto y las mismas
fuentes ([10] LIF, [11] PEF, [05] LCF), lleva sus términos al glosario y cada
paso manda a su capítulo; el cuarto va a «Qué encontró la ASF».

Accesos que todavía abrían el módulo viejo y ahora llevan a Números:
- `?ir=presupuesto` e `?ir=egresos`, con un script en el `<head>` de
  `index.html` que redirige antes de pintar la portada;
- `seleccionarModuloExplorer('presupuesto')`;
- el resultado «Ramo» del buscador;
- `irAAuditoriaInversiones`;
- el botón del radar «Ver de dónde sale el dinero, en Números (LIF)».

Todos usan `irANumeros(ancla)` del motor, que manda a
`sigue-el-dinero.html?abrir=eb-…`. `apartados.js` abre ahí la pestaña y el
visor de la tarjeta de ese bloque. El visor de Números sigue usando
`index.html?ir=presupuesto&ancla=…&visor=1`, que no se redirige.

Los rótulos «Circuito del Dinero» en `PROEMIOS`, `TAB`, la nota de la portada
y el `<h2>` del módulo dicen ahora «Números».

**Herramientas en módulos con página propia y motor 8 veces más rápido (10-10-2026, sello 20261010b).**
Pedido del autor: al entrar a cualquiera de las cuatro herramientas, la
pestaña «se quedaba actualizando cifras». Diagnóstico con el perfilador de
Chromium: cada pestaña abría `index.html?ir=...&visor=1` en un marco, y al
cargar la portada el motor pasaba unos 7 segundos en `autolinkAmbito`, que
enlaza los términos del glosario. Con los ámbitos que se enlazan después
sumaba unos 15 segundos. La causa: abría un `TreeWalker` por cada alias
(cientos) y revisaba los ancestros de cada nodo de texto en cada vuelta.

- **Motor:** `autolinkAmbito` recorre el árbol una sola vez, guarda los nodos
  válidos y actualiza la lista al partir un nodo. Se comparó contra la versión
  anterior: los mismos 116 enlaces, en el mismo lugar y con el mismo texto.
  La portada pasó de ~8 s a ~1 s. Los visores de Números y de los demás
  apartados se benefician igual (~0.7 s).
- **Reestructura (§5 bis):** `herramienta-*.html` ya no tiene pestañas ni
  despliega nada. Es la ruta de sus módulos numerados (`.herr-ruta`) y cada
  módulo abre su página `herramienta-<h>-<módulo>.html`, que hace
  `herramienta_modulo()` en `apartados.py`. Son 16 páginas, que cargan en
  0.4 a 1.5 s. Cada página lleva:
  - migas de dos niveles;
  - el módulo en el visor, a la altura de su contenido (`iframe[data-modulo]`
    en `apartados.js`);
  - «Abrir en el auditor completo»;
  - anterior y siguiente, los chips de todos los módulos y las otras
    herramientas.
- **Anclas viejas:** `#pulso`, `#inspentes` y las demás redirigen a la página
  del módulo (`hash_a_pagina`). `busca-y-verifica.html` va a
  `herramienta-inspector-entes.html`.

**Diccionario del Gasto Público en dos estantes (10-10-2026, sello 20261010a).**
Al autor no le gustó la fusión en una sola «Biblioteca del auditor»: se
perdieron los nombres «Biblioteca hacendaria» y «Fuentes del auditor», y el
Diccionario dejó de verse en Aprende. Queda así: el **Diccionario del Gasto
Público** (`diccionario.html`) es el nombre de la obra completa, con dos
estantes que salen de `ESTANTES` y `BIBLIOTECA` en `herramientas/apartados.py`:

- 🏛️ **Biblioteca hacendaria**, para entender: Glosario de Términos
  Hacendarios, Marco Legal Hacendario y Preguntas Frecuentes en Casillas
  Didácticas.
- 🧭 **Fuentes del auditor**, para verificar: Compendio de Fuentes Oficiales
  (el portal de referencias, `fuentes-oficiales.html`) y Pase del Auditor
  Cívico.

Aprende vuelve a tener las pestañas `#biblioteca` y `#kit`, cada una con la
nota «Forma parte del Diccionario del Gasto Público». La portada del
Diccionario muestra los dos estantes y la barra al pie de cada página también.
Las páginas ligeras no cambiaron. Se agregaron las anclas viejas
`diccionario.html#referencias` y `#pase`.

**Biblioteca del auditor: cuatro páginas ligeras y contenido cotejado (09-10-2026, sello 20261009za).**
Pedido del autor: las fichas «Biblioteca hacendaria» y «Fuentes del
auditor» de Aprende se trababan al abrirse («se queda calculando las
cifras») y repetían contenido (las preguntas frecuentes estaban en las dos y
en el Diccionario). Causa: cada tarjeta abría `index.html?ir=...` en el
visor, es decir, la portada entera (motor, mapas y padrón municipal, unos
4 MB de JavaScript) solo para mostrar texto.
- **Fusión**: las dos fichas son ahora una, «📚 Biblioteca del auditor»
  (`#biblioteca` en `aprende.html`), con cinco tarjetas que salen de la
  lista `BIBLIOTECA` de `herramientas/apartados.py`. Aprende queda con tres
  pestañas: Trivia, Biblioteca y Noticias.
- **Páginas propias** (generadas por `apartados.py`, pintadas por
  `assets/auditor/js/biblioteca.js` desde `window.AUDIT_DB`, sin el motor):
  `preguntas-frecuentes.html` (acordeón con buscador, temas y ancla por
  pregunta `#p-<casilla>-<n>`), `marco-legal.html` (el ciclo del dinero en
  cinco etapas que filtran, buscador por ley y fichas con el texto vigente;
  ancla `#precepto-<id>`), `fuentes-oficiales.html` (gráfica de barras por
  familia de fuentes, buscador y ancla `#ref-<id>` iluminada) y
  `pase-del-auditor.html` (antes un cuadro encima de la portada; la
  suscripción se marca «disponible en el lanzamiento»). El glosario ya
  tenía su página. Las cinco llevan al pie la barra «La biblioteca del
  auditor» (`bib_nav()`).
- **El Diccionario** (`diccionario.html`) deja las pestañas con visor: es
  la puerta de los cuatro apartados. Sus anclas viejas (`#glosario`,
  `#fuentes`, `#marco-legal`, `#preguntas`) mandan a la página nueva
  (`hash_a_pagina`).
- **El motor** ya no despliega esos apartados en la portada:
  `abrirCatalogoFuentes()`, `abrirDiccionarioSubtab()`, `goToRef('precepto-…')`,
  `openPaseCivicoModal()` y los destinos `?ir=fuentes|faq-marco-legal|faq-preguntas|faq-glosario|pase`
  llevan a las páginas (`irBiblioteca()`; desde el visor, a la ventana
  completa). Las notas [n] de los apartados (`libro_html`) y de `datos.js`
  apuntan directo a `fuentes-oficiales.html#ref-…`.
- **Marco legal cotejado palabra por palabra** con el texto vigente de la
  Cámara de Diputados (CPEUM, última reforma DOF 07-10-2026; LFPRH
  09-04-2026; LCF 03-01-2024; LDF 10-05-2022; LIF 2026) y el Manual de
  remuneraciones del PJF (DOF 27-02-2026). Se corrigieron citas que eran
  paráfrasis presentadas como texto oficial (25, 28, 73, 74, 79, 116, 127,
  94, 96, LFPRH 17-18, 42 y 54, LCF, LDF, LIF). Hallazgos: el 79 ya dice
  «Auditoría Superior de la Federación»; el 127, fr. II, se reformó el
  10-04-2026; la Corte puede funcionar en dos secciones (art. 94); la
  extinción de fideicomisos judiciales está en el transitorio **Décimo** del
  decreto de 2024, no en el Cuarto, y no menciona «13 fideicomisos» ni
  «$15,434 mdp». Se retiraron dos «preceptos» de la LIF que no existen
  (costo financiero y prohibición de condonar, que está en el art. 28
  constitucional) y entró el art. 28 de la LIF 2026 (Renuncias
  Recaudatorias). Quedan 27 preceptos, cada uno con `vigencia`, `etapa`,
  `grupo` y su ficha del catálogo (`ref`). Ya no se muestra
  `aplicacion_auditavision`, que remitía a pestañas de la Enciclopedia.
- **Preguntas frecuentes verificadas**: se quitaron cifras sin documento
  (predial 0.16% del PIB y 1.0% OCDE, $78,327 mdp del PJF, 80.2%, $34.2 mdp
  por ponencia, 35 colaboradores, salarios de ministros de antes) y se
  sustituyeron por cifras de la propia plataforma con chip: PEF 2026 Ramo 03
  ($70,005.6 mdp aprobado), Manual PJF 2026 ($134,310 netos al mes por
  ministro), INEGI EFIPEM 2024 (predial = 7.4 de cada 100 pesos municipales;
  transferencias federales = 71.1). Se corrigieron el procedimiento del
  pliego de observaciones (LFRCF arts. 39, 40, 41 y 71: la Auditoría no
  juzga ni sanciona) y la respuesta sobre EFOS (art. 69-B del CFF, sin
  especulación). Cada respuesta trae sus fichas del catálogo (`refs`).
- **Pendiente:** cuántos fideicomisos judiciales se extinguieron y cuánto
  se enteró a la Tesorería. El decreto no lo dice y la plataforma aún no
  integra el informe oficial que lo documente: falta nuestra.
  Tampoco se ha depurado el catálogo de fuentes, que tiene fichas dobles
  (`ref-lamparo` y `ref-ley-amparo`; `ref-pnt` y `ref-pnt-asesores-scjn`) y
  una ficha de la Auditoría que liga a su portada (`ref-asf-fideicomisos-pjf`).
  No se borraron porque otras partes las citan por su id.

**Trivia: la gran balanza de la Enciclopedia, en reactivos (09-10-2026, sello 20261009z).**
Pedido del autor: traer a la trivia de Aprende el tablero 5.4 de la
Enciclopedia («Versus General Don Porfirio Díaz»), con sus gráficas,
simuladores y rubros, como preguntas en lugar de etiquetas. La trivia
(`assets/auditor/js/trivia-presidentes.js`) pasa de 12 a 22 preguntas y
de 4 a 7 rondas:
- **La gran balanza** (4): primer superávit (1836-1837, no Limantour),
  peor déficit contra ingresos (Díaz, 1888-1889: 114.8%), deuda de 1870 a
  1911 (casi cinco veces) y dependencia de las aduanas (Santa Anna, Juárez,
  Díaz y 2025).
- **Los rieles** (2): pasajeros en la privatización (−95% de 1994 a 2000;
  la red no se redujo) y kilómetros sumados de 1910 a 2012 (6,979).
- **Hoy: el primer año de Claudia Sheinbaum** (4): balance 2025 (−3.9% del
  PIB), de dónde sale el dinero (ISR), costo financiero contra inversión
  física (3.7 contra 2.2) y la deuda más alta de la serie (52.6% en 2025).
- **Gráfica lineal**: en las preguntas con serie (`serie: true`) hay un
  selector Barras/Lineal; la traza se dibuja al contabilizar (`linea()`).
- **Estado de cuenta**: se agregan las fichas de Sheinbaum (primer año,
  se mide y no se califica), Juárez y Santa Anna; la del Porfiriato suma la
  deuda de 1890 y 1911.
- **Ninguna cifra del tablero 5.4 se copió**: la propia Enciclopedia lo
  marca «en revisión, sin fuente». Todo se rehízo con el INEGI
  (*Estadísticas históricas de México 2014*, cuadros 14.18, 16.3, 16.5 y
  16.16) y con Hacienda (Criterios Generales de Política Económica 2027,
  pp. 53 y 56). Lo que no se pudo sostener se explica en «Lo que
  corregimos»: los % del PIB del siglo XIX, el «−19,000 km» de Zedillo, el
  «88%» de ISR e IVA (fue 81.6%) y las cifras sexenales del tablero.
- **Pendiente:** el kilometraje de los trenes posteriores a 2013 (Maya,
  Interoceánico, El Insurgente). La Agencia Reguladora del Transporte
  Ferroviario publica su anuario y la plataforma aún no lo integra: es
  falta nuestra, no de la dependencia. Tampoco entraron los indicadores
  sociales del tablero (esperanza de vida, salario real, tierra): falta
  cotejarlos con CONAPO, CONASAMI y el INEGI.

**Imágenes de herramientas más limpias y más lejanas (09-10-2026, sello 20261009y).**
Pedido del autor: menos sombreado y menos zoom. Las imágenes son ahora
`herr-*-amplia.jpg`: la escena casi completa al centro, sobre un fondo hecho
de la misma imagen desenfocada, en 1200×670. En las tarjetas, el degradado solo
oscurece la franja del título (desde el 42 % del alto). En el encabezado de
`herramienta-*.html` la imagen va entera a la derecha (`auto 100%`) y el
degradado azul solo cubre el lado del texto.

**Nuevas imágenes de las herramientas (09-10-2026, sello 20261009w).**
El autor entregó cuatro imágenes ilustrativas que sustituyen a las de
`assets/auditor/img/herr-*.jpg` (recortadas a 1200×670). En el sello
20261009x cambiaron de nombre (`herr-megaobras-plataformas.jpg`,
`-calculadora-monedas`, `-inspector-foroptero`, `-ambiente-refineria`):
con el mismo nombre, los navegadores seguían mostrando la imagen vieja de su
caché. **Para cambiar una imagen, cámbiale también el nombre** (el CSS no
lleva sello en sus `url()`):
plataformas petroleras para Megaobras, una pila de monedas para la
Calculadora Cívica, un foróptero para el Modo Inspector y una refinería con
humo para el Costo Ambiental. Se ven en las tarjetas de Herramientas, en el
encabezado de cada `herramienta-*.html` y en la franja «Las otras herramientas».

**Diccionario y glosario con página propia; nada lleva a la portada (09-10-2026, sello 20261009v).**
Pedido del autor: los enlaces a la Enciclopedia (congelada) llegan ahora al
Diccionario del Gasto Público, y nada saca al lector a la portada salvo el
nombre «Auditavisión» y los botones de volver al inicio.
- `diccionario.html` (`DICCIONARIO` en `apartados.py`, padre: Aprende):
  la pestaña «faq» del auditor en su página, con cuatro pestañas
  (preguntas, glosario, marco legal, catálogo de fuentes). Tres abren su
  apartado en el visor; en el visor se esconden el título y las
  subpestañas de la portada (`civico.css`).
- `glosario.html` (`GLOSARIO` + `assets/auditor/js/glosario.js`): página
  nativa, sin marco, que lee `AUDIT_DB.glosario`: buscador, categorías y
  un ancla por término (`glosario.html#Huachicol-Fiscal`, la forma de
  `glosario_ancla()`). Los enlaces `index.html?ir=glosario` y
  `?ir=faq-glosario` del motor redirigen ahí.
- Los 13 enlaces a `enciclopedia.html` (insignia «Inspector Meteoro»,
  pie de la portada, nota de finanzas, ficha de referencia, debate,
  Porfiriato y presidentes) van al Diccionario o a su glosario.
- `apartados.js`: cualquier enlace `index.html?ir=...` que no sea tarjeta
  (p. ej. «Cuéntanos lo que viste», los de Auditoría en imágenes y las
  fichas de fuente) se abre en una ventana lateral ancha (`abrirMarco`,
  `.glos-drawer-marco`) con el auditor en modo visor. Se quitó «Pantalla
  completa» del visor, porque llevaba a la portada. En el visor, los
  cajones del auditor ocupan todo el marco y cerrar el reporte cierra la
  ventana.
- Pendiente: los enlaces *dentro* del visor que apuntan a otra página
  siguen abriéndose en la ventana completa (`target=_top`).

**El nombre de la cabecera lleva a la portada (09-10-2026, sello 20261009t).**
«Auditavisión · El gasto público, a la vista» es ahora un enlace a
`index.html` en todas las páginas (`cabecera()` en `apartados.py` y la
portada). El logotipo sigue abriendo la presentación «Quiénes somos».

**La nota del libro, en la ventana lateral (09-10-2026, sello 20261009s).**
Por pedido del autor se quitó el recuadro «Nota de referencia» de Números,
para que las pestañas queden parejas. Ahora es un enlace «📘 Nota de
referencia» bajo la entrada que abre la ventana lateral ancha. Trae el texto
con su llamado [119], los conceptos del glosario y la ficha del catálogo de
fuentes (`libro_enlace()` en `apartados.py`, plantilla `#tplNotaLibro`).

**Herramientas: tarjetas con imagen y una página por herramienta (09-10-2026,
sello 20261009r).** Pedido del autor.
- **Menú.** Los módulos ahora se llaman herramientas.
  - Se quitaron el título «Los cuatro módulos» y su párrafo; «elige una y
    pulsa Comenzar» pasó al paso 1 de «Cómo se usa».
  - Las cuatro tarjetas van en dos columnas, más grandes, con fotografía
    ilustrativa de fondo y el icono encima (`.herr-foto.rubro-*` en
    `apartados.css`).
  - Imágenes: copias ligeras en `assets/auditor/img/herr-*.jpg`, tomadas de
    `assets/img` (Tren Maya, Palacio Nacional, ciudad de noche y bosque). Van
    marcadas «Imagen ilustrativa».
  - Ojo: un `url()` dentro de una variable CSS se resuelve contra la carpeta
    de la hoja; por eso la imagen se pone por clase.
- **Páginas nuevas.** `herramienta-megaobras.html`, `-calculadora`,
  `-inspector` y `-ambiente` (lista `HERRAMIENTAS` en `apartados.py`, que no
  agrega pestañas al menú: siguen cinco).
  - Encabezado con la imagen y el proemio del módulo (copia de `PROEMIOS`
    del motor: **si cambia uno, cambia el otro**).
  - Una pestaña por tema. La primera llega abierta y la tarjeta de cada
    pestaña (`data-auto`) despliega su bloque en el visor sin pulsar otra
    vez. Al pie, las otras tres herramientas.
  - «Expedientes de casos» enlaza a `expedientes.html`.
  - `busca-y-verifica.html` ahora redirige a `herramienta-inspector.html#inspentes`.
- **Motor.** `visorFoco()` deja visibles las herramientas de «Busca y
  verifica»: su ancla es un rótulo `.insp-sep` y la herramienta son los
  hermanos que le siguen.
- **Nota «Qué son las finanzas públicas».** Ya no lleva a la portada: se
  abre en la ventana lateral, más ancha (`.glos-drawer-ancha`, 760 px).
  - Cifras de la base con su chip y su fuente (PEF 2026, anexos 1 y 8; ASF,
    Matriz de Datos Básicos CP 2024). `audit-database.js` se carga solo al
    abrir la nota.
  - Sus conceptos (gasto público, hacienda pública) se leen ahí mismo, con
    regreso a la nota.
  - El logotipo suma el botón a la nota. Copia de `abrirNotaPortada()`, con
    la lista de lugares al día.
- **Cabecera.** Se corrigió un bucle: al encogerse, el anclaje del
  desplazamiento subía la página y la volvía a agrandar. Ahora solo crece
  arriba del todo, y se mide ya compacta antes de desplazarse.
- Pendiente (§5 bis): los temas siguen cargando los módulos de la portada
  en el visor. Ya tienen página propia, pero el código vive en el motor.

**Números en pestañas y el libro como nota de referencia (09-10-2026, sello
20261009q).** El autor pidió para Números lo mismo que en Datos, Aprende y
Participa.
- `sigue-el-dinero.html` tiene seis pestañas, una por apartado de «En esta
  página»: De dónde sale, Quién lo decide, Quién lo gasta, A dónde baja,
  Cuánto debemos y ¿Cuánto te toca? (`'pestanas': True` en `apartados.py`).
- **Fichas.** Siguen siendo el visor (el módulo de la portada en un marco,
  modo `visor-foco`), desplegado debajo de su fila. Ahora el marco toma el
  alto de su contenido, sin franja en blanco (`ajustarMarco()` en
  `apartados.js`).
  - Se mide el fondo de los bloques del `body` del marco. Los cajones fijos
    (`position: fixed`) se ignoran, porque miden lo que el marco y lo harían
    crecer sin fin.
  - Un `ResizeObserver` vigila cada bloque, también cuando se encoge. Hay un
    tope de 40 ajustes.
- **El libro.** El recuadro pasó a ser una «Nota de referencia»
  (`libro_html()` en `apartados.py`).
  - Lleva la llamada [119], que enlaza a su ficha en el catálogo de fuentes
    (`index.html?ir=fuentes&ancla=ref-gomez-granillo-1995`).
  - Enlaza sus conceptos al glosario (`ir=glosario&ancla=<término>`).
  - Ficha nueva en `referencias_legales` (núm. 119, categoría nueva
    «doctrina», sin URL: el libro no tiene edición oficial digital). El
    filtro de categorías se deriva de los datos.
  - El motor: `IR_DESTINOS.fuentes` acepta un ancla `ref-…` y la resalta.
- Pendiente (§5 bis): las fichas aún cargan los módulos de la portada en el
  visor. Llevarlos a código propio de la página es trabajo mayor (17
  módulos del motor).

**Datos en pestañas, con fichas que se despliegan (09-10-2026, sello
20261009p).** El autor pidió para Datos lo mismo que en Aprende y Participa.
- `descarga-los-datos.html` tiene tres pestañas: Radar hacendario, Datos
  abiertos e Informes oficiales.
- **Radar.** Por pedido del autor, la barra «Equivalencia durante tu
  visita» va arriba y el radar de referencia queda debajo (la cinta «Datos
  de referencia» y las cifras en movimiento).
  - Volvieron los dos botones que tenía en la portada: «Ocultar
    estadísticas» y «Desglosar cifras».
  - El desglose (cómo se calcula cada cifra y de dónde sale) empieza
    cerrado. Tocar una cifra lo abre y lleva a su tarjeta.
  - Marcado: `herramientas/plantillas/radar.html`. Lógica:
    `radar-datos.js`.
- **Fichas.** Las cuatro fichas de Datos abiertos e Informes oficiales son
  botones (`fichas()` en `apartados.py`). Se despliegan debajo de su fila
  con el aspecto del visor y no abren la portada. Hay una abierta a la vez
  por pestaña.
  - Descarga en CSV: las siete bases con su botón y su diccionario.
  - EFIPEM: la descarga y una consulta por estado con la tabla de sus
    municipios. Solo muestra cifras del INEGI que ya estaban en
    `municipios-efipem.js`.
  - Informes de la Cuenta Pública: el `renderCuentaPublica()` completo, con
    sus ocho capítulos.
  - Diccionario: las siete bases con el diccionario abierto.
- `#ficha-<id>` abre la pestaña y la ficha. La tarjeta del radar «Ver lo que
  encontró la ASF» ahora apunta a `#ficha-asf`.
- El código es copia del motor (`DESCARGAS`, `descargarCSV`,
  `renderCuentaPublica`, `capMontar` y sus ayudantes) y vive en
  `assets/auditor/js/datos.js`. **Si cambia en el motor, cambia aquí.**
  - El botón «Ver en el Catálogo de Fuentes» enlaza a
    `index.html?ir=fuentes`, porque el catálogo sigue en la portada.
  - La lista 69-B del SAT solo se baja al pedir su CSV.
- Pendiente (§5 bis): que `ir=descargas`, `ir=diccionario` e
  `ir=csv-municipios` de la portada lleven a esta página.

**Participa con su contenido dentro de las pestañas (09-10-2026, sello
20261009o).** El autor pidió que cada pestaña muestre su contenido, como en
Aprende, y no tarjetas que mandaran a la portada.
- «Ágora cívica» tiene el portal de diálogo completo: el formulario, los
  filtros, los hilos y las réplicas.
- «Garantías cívicas» tiene, en este orden:
  - las tres rutas y «a dónde va lo que escribes»;
  - el formulario «Ayúdanos a fiscalizar», que en la portada vive en un
    cajón lateral;
  - los seis canales oficiales;
  - el decálogo.
- El marcado se tomó de `index.html` y vive en
  `herramientas/participa_html.py`.
- Las funciones son copia de las del motor y viven en
  `assets/auditor/js/participa.js`, que lee `window.AUDIT_DB` y expone su
  propio `window.AuditEngine` con los métodos de los `onclick`. **Si cambia
  el portal en el motor, cambia aquí.** Lo guardado en el navegador usa las
  mismas claves de `localStorage`, así que se comparte con la portada.
- `civico.css` agrega estilos de tema claro para el formulario y los hilos.
  Traían colores en línea para fondo oscuro, y el texto blanco no se veía.
- Pendiente (§5 bis): retirar el portal de la portada y redirigir sus
  `ir=portal` a `participa.html`.

**Dos columnas más de García Luna (09-10-2026, sello 20261009n).** Las pidió
el autor y se verificaron con la regla editorial. Quedan 18 columnas y 75
afirmaciones descartadas.
- «García Luna y los testigos colaboradores: lo que dice la ley de cada
  lado». Recupera la tesis del módulo retirado de la Enciclopedia, ya
  verificada:
  - el testimonio es prueba en los dos países (CNPP arts. 259 y 356;
    FRE 601);
  - la ley mexicana también premia al colaborador (LFDO art. 35; CNPP
    art. 256 fr. V) y pide valorarlo con prudencia y corroborarlo (LFDO
    arts. 35 Bis, 36 y 40);
  - **el CNPP no recoge el «testis unus, testis nullus»** que afirmaba el
    texto viejo, así que eso va a descartado.
  - Pendiente por falta de la plataforma: la jurisprudencia de la SCJN
    sobre el coimputado (sjf2 bloquea el entorno) y las transcripciones
    del juicio.
- «García Harfuch y la Policía Federal de García Luna». Lo que consta es la
  coincidencia institucional entre 2008 y 2012: el SIL, cuyos datos no ha
  confirmado el legislador, y el comunicado del DOJ. **La amistad y los
  vínculos no constan en ningún documento oficial** y la columna lo dice.
  Pendiente: abrir el PDF de la acusación sustitutiva del DOJ (19-576 S-1)
  para confirmar que no lo menciona. Los datos del DOJ se leyeron por el
  buscador porque justice.gov está bloqueado.

**Cabecera: más imagen y fija en todos los tamaños (09-10-2026, sellos
20261009g y 20261009h).** Decisión del autor. En `civico.css` (bloque «CABECERA
(09-10-2026)»). Primero se adelantó el desvanecido 3.5 cm, pero al agrandar
la imagen se veía menos; el autor pidió en su lugar (sello 20261009h) que
**la imagen ocupe la mitad derecha de la cabecera, a partir de media
pantalla, y que desde ahí arranque el desvanecido hacia los azules**. Sobre
la imagen el velo azul bajó de 0.46 a 0.10-0.16 para que se vea bien.
Después (sello 20261009k) el autor pidió la imagen **al centro de la página
completa, con su paneo, y desvanecida por los dos lados**: va centrada con
ancho `--cab-ancho` (62%; 74% en tableta, 92% en teléfono), el velo es de
0.20 al centro y crece hasta el azul sólido en los bordes; el paneo usa la
animación `cabecera-centro`. Los botones con borde
(Compartir, Inspector Meteoro, Menú) llevan un velo azul translúcido para
leerse sobre la parte clara de la foto. El paneo no cambia. La cabecera queda fija (`sticky`) en todas las páginas y anchos:
antes, en teléfono, la de la portada se iba con el desplazamiento. Sigue
compactándose al bajar (unos 70 px), así que en teléfono los destinos de
los saltos dejan 84 px arriba en lugar de 12.

**Cinco pestañas; «Sigue el dinero» pasa a llamarse «Números» (09-10-2026,
sello 20261009f).** El autor fijó el menú en cinco pestañas: Herramientas,
Números, Datos, Aprende y Participa (regla en AGENTS.md §5 bis). Cambió el
nombre visible de «Sigue el dinero» en el menú de la portada y de todas las
páginas generadas, en el título, las migas y el encabezado de su página, en
el texto de Herramientas y en el enlace de la trivia. El archivo conserva el
nombre `sigue-el-dinero.html` y sus anclas, para no romper enlaces; los
comentarios del código que dicen «Sigue el dinero» se dejaron como historia.

**«Busca y verifica» se fusiona con el Modo Inspector; Herramientas, con
los módulos al centro (09-10-2026, sello 20261009e).** Decisiones del autor:
- **Busca y verifica dejó de ser menú.** Sus herramientas ya vivían dentro
  del Modo Inspector (módulo 4 de la portada), así que el módulo se reordenó
  en dos partes con su índice: «Lo que revisó la Auditoría» (1 qué encontró
  la ASF, 2 radar por entidad, 3 expedientes) y «Busca y verifica» (4 auditor
  de entes públicos, 5 contrasta una nota, 6 lista negra del SAT). Los
  separadores de la parte B llevan `id="eb-inspentes|inspnota|inspefos"`
  para que `erarioIr` los alcance; el antiguo `#vnSeccion` (sin uso en el
  motor) pasó a `#eb-inspnota`. El proemio trae los seis temas.
  ComprasMX, que era tarjeta del menú, se enlaza en la cabecera de la parte B.
  No se agregó ningún desglose nuevo: solo se reordenó lo que ya estaba.
- `busca-y-verifica.html` ya no es apartado: `apartados.py` la genera como
  redirección (`REDIRECCIONES`) a `index.html?ir=verificador&ancla=moduloProemio`
  para no romper enlaces viejos. `expedientes.html` cuelga ahora de
  Inicio › Herramientas › Modo Inspector.
- **Herramientas:** los cuatro módulos van al centro, con icono grande y solo
  su título (Simulador de Inversión y Megaobras, Calculadora Cívica, Modo
  Inspector, Costo Ambiental) y el botón «Comenzar». La frase y la cifra de
  cada tarjeta se quitaron: lo que trae cada módulo se cuenta en su proemio
  al pulsar «Comenzar». La guía «Cómo se usa» quedó debajo (`'guia': 'abajo'`
  en `apartados.py`).

**Expedientes de casos por aclarar: página propia (sello 20261009d).** Por la
regla de AGENTS.md §5 bis, los diez expedientes dejaron de desplegarse en el
bloque 3 del Modo Inspector y viven en `expedientes.html`, que genera
`herramientas/expedientes.py` (lo llama `apartados.generar`, así que
`sello.py` la regenera) y pinta `assets/auditor/js/expedientes.js` con
`AUDIT_DB.expedientes` (estilos en `assets/auditor/css/expedientes.css`).
La página trae:
- un cuadro conceptual «Cómo nace un expediente» y un glosario de cuatro
  términos, sin cifras;
- filtro por tema e índice de tarjetas;
- cada caso completo con ancla `#exp-<id>`: cifras con chip, barras animadas
  de lo que quedó por aclarar en cada Cuenta Pública (derivado, suma de los
  informes), la tabla, los informes de la ASF, «Copiar ficha con fuentes» y
  el enlace a su página de Auditoría en imágenes cuando la hay.

En la portada, el bloque 3, su paso en el índice y el tema del proemio son
enlaces a esa página. `irAExpediente`/`expIr` y `index.html?ir=expediente&ancla=<id>`
llevan a `expedientes.html#exp-<id>`. Del motor se quitaron `expFichaHtml`,
`renderForensicDossiers`, `filtrarDossiers` y `expCopiar` (con sus
exportaciones). Las páginas de Auditoría en imágenes ya enlazan directo.

**Regla nueva: todo `pendiente` señala a la dependencia que no transparentó
(09-10-2026, sello 20261009c).** Decisión del autor: al marcar un dato como
pendiente no basta con decir que falta el documento oficial; hay que
justificar que falta porque la dependencia responsable no lo ha
transparentado, y nombrarla. Quedó en AGENTS.md §2. Se aplicó a la leyenda
«Cómo leer cada cifra» (portada) y a la guía de los apartados; al huachicol
fiscal (SAT y Hacienda) en el glosario, la pregunta frecuente, el radar, el
expediente y su página de Auditoría en imágenes; a Dos Bocas (Pemex no
publica los estados de la filial); al AIFA (costo de construcción y
proyección de subsidio, Sedena); a la matriz 2018 de la ASF; a la pérdida
de operación de las obras del simulador, y a la inversión de LEGO
(Gobierno de Nuevo León). **No se tocó**, a propósito, lo que es falta de
la plataforma y no de una dependencia: el simulador que «todavía no
documenta» cada costo, los datos de entidades «sin documento citado», la
cifra de la Ciudad de México fuera de la estadística del INEGI y las cifras
históricas del siglo XIX. Al revisar módulos, aplica la regla caso por caso.

**Regla nueva: la portada ya no despliega nada (09-10-2026).** Decisión del
autor, asentada en AGENTS.md §5 bis: la página principal queda como está y
todo clic lleva a una página propia. Lo que aún se despliega se irá mudando.
Ya se mudaron Auditoría en imágenes y el radar hacendario (abajo).

**«Descarga los datos» y «Datos de referencia», fusionados (09-10-2026,
sello 20261009b).** Una sola página, `descarga-los-datos.html`, con el
menú «Datos» y el título «Los datos: cifras de referencia y descargas». Su
primera sección, `#radar`, es el radar hacendario que vivía en el menú
desplegable de la portada: la cinta de datos, las cuatro cifras y el
desglose completo, con las mismas cifras y fuentes (se movió el HTML, no se
reescribió; vive en `herramientas/plantillas/radar.html` y lo inserta
`apartados.py`). El desglose ya no se pliega: está siempre a la vista, y
cada cifra es un enlace a su tarjeta. Lo anima
`assets/auditor/js/radar-datos.js`, sin motor: el reloj de la visita y las
equivalencias por segundo, con la tasa en `data-tasa` (2,062.75 megaobras;
49,850.12 deuda, las mismas que tenía el motor). Las tarjetas llevan a
Megaobras, a la página del reloj de los intereses, a la Cuenta Pública de la
ASF y a la página del huachicol. Salió el menú «Datos de referencia» de la
portada y de las páginas; `index.html?ir=datos` ahora redirige a
`descarga-los-datos.html#radar`. Las funciones del radar en el motor
(`toggleRadarStats`, `toggleRadarDesglose`, `updateRadarAlertaBar`...)
quedaron inertes: buscan elementos que ya no existen y salen sin error.
Pendiente menor: si cambia la pérdida de megaobras que calcula el motor
(`MEGAOBRAS_LOSS_RATE`), hay que actualizar a mano la tasa en la plantilla.

**Auditoría en imágenes: una página por imagen (09-10-2026, sello
20261009a).** Las nueve diapositivas del carrusel ya no abren el cuadro
«Descubrimiento» sobre la portada: son enlaces a `auditoria-<id>.html`
(tren-maya, dos-bocas, deuda-soberana, aifa, ramo-33, lego-cienega,
tren-toluca, megafarmacia, huachicol-fiscal). Las genera
`herramientas/auditorias.py` (lo llama `apartados.generar`, así que
`sello.py` las regenera) y las pinta `assets/auditor/js/auditoria-imagen.js`
con su hoja `auditoria-imagen.css`. La página carga solo `audit-database.js`
(y el padrón del INEGI en LEGO), sin el motor. Cinco piezas: (1) el dinero
paso a paso, un cuadro conceptual cuyas cifras suben de cero con «Ver gasto»;
(2) una escena: el monito 🐒 que avienta 40 monedas a los botes del rastro
(cinco mayores y «los demás»; cada moneda = total ÷ 40, chip derivado; antes
de repartir el lector apuesta por el bote mayor), el reloj de los intereses
de la deuda que corre desde que se abrió la página, o la fuga del huachicol
(un escenario de regla de tres con barra de 0 a 30 %, no una estimación);
(3) el rastro renglón por renglón con enlace al informe; (4) lo que se
encontró, lo pendiente y la fuente; (5) a dónde seguir, con enlaces
`index.html?ir=...`. Destinos nuevos en `IR_DESTINOS`, que ahora reciben el
ancla: `expediente`, `flujo` (egr-costofin, fed-*), `municipio` (NL-19012),
`radar` y `glosario`. Los constructores `sc*` y el cuadro
`#descubrimientoModal` salieron del motor y de `index.html`: viven solo en el
guion nuevo. Respeta «movimiento reducido».

**Pendiente del examen:** ingresos, gasto, inversión física y balance de cada
sexenio. No se encontró a nuestro alcance una serie oficial completa y
consistente de 1989 a 2024 (la ASF publica el RFSP por año desde 2010 y sus
cuadros no siempre coinciden: 2020 aparece como 3.9 y como 3.8 en el mismo
informe). El renglón sale como pendiente. Opciones: el anexo estadístico del
Informe de Gobierno o los informes anuales de Banxico, año por año.

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

### Hecho (entidades y municipios pasan a Acción Financiera; cuatro menús)

- **Menú superior:** se probó fundir «Descargar Datos» y «Consultar
  Recursos»; el autor pidió regresarlos separados. Quedan cinco: Búsqueda
  Forense, Acción Financiera, Descargar Datos, Consultar Recursos y Portal
  Digital.
- **Las 32 entidades (antes 1.2) y los 2,479 municipios (antes 1.3) se
  mudaron de la Enciclopedia a Acción Financiera de la plataforma**
  (`data-parent="accion-financiera"`, subpaneles `territorio` y
  `municipios`). El menú ya no manda a la Enciclopedia. En la Enciclopedia,
  las pestañas 1.2 y 1.3 quedan con un aviso y un botón que lleva a su nuevo
  lugar.
- `switchTab('territorio' | 'municipios')` abre esas secciones; desde una
  página que no las tiene, navega a `index.html#accion-financiera/…`. El
  buscador global usa esa ruta para estados y municipios.
- Un enlace `index.html#pestaña/subpestaña` abre los módulos plegados de la
  portada y baja a la subpestaña.

### Hecho (2.6: lo ya gastado, cierre 2025 y avance 2026)

- **Capítulo nuevo «Lo ya gastado»** en la 2.6 (ahora son siete): por cada
  unidad del Congreso y del Poder Judicial, el original y el ejercido de 2025
  (Cuenta Pública) y el aprobado, modificado y pagado al 30 de junio de 2026
  (avance del gasto AC01), con barra de avance y marca de la mitad del año.
  Lo legislativo trae además el ejercido 2025 por capítulo.
- **Fuentes:** bases de datos abiertas de Transparencia Presupuestaria
  (`CP2025`, `AV2T2026` en `poderes.fuentes`, con SHA-256). Se extraen con
  `python3 herramientas/extraer_ejercicio_poderes.py CP.csv AVANCE.csv` a
  `investigaciones/ejercicio-poderes.json`, que `integrar_poderes.py` lee.
- **Controles:** el aprobado 2026 del avance coincide al peso con el Anexo 1
  del PEF (Diputados 9,602,671,330; Senado 5,103,817,038; ASF 2,822,588,131);
  el cierre 2025 de la SCJN coincide al peso con su propio estado analítico
  (5,273,784,802 ejercidos).
- **Nota técnica:** el servidor de Transparencia Presupuestaria manda una
  cadena de certificados incompleta. Se descarga con `curl --http1.1
  --cacert` y un paquete que agrega el intermedio YR1 y Root YR de Let's
  Encrypt (del repositorio `letsencrypt/website`); nunca sin verificar.

### Hecho (Paquete Económico 2027 y costo ambiental, en Acción Financiera)

- **Cuarto renglón de «Presupuesto Federal»** en el menú de Acción
  Financiera: «Paquete Económico 2027 y Costo Ambiental», subpanel
  `proyeccion2027` de la plataforma. Reúne la antigua 1.4 (Constitución
  económica y lectura del Paquete Económico 2027) y la antigua 2.3 (Cuentas
  Económicas y Ecológicas del INEGI). En la Enciclopedia, 1.4 y 2.3 quedan con
  aviso y enlace.
- El autoenlace de las dos secciones ya no depende del nombre del subpanel:
  busca el panel que contiene sus contenedores.
- Al abrir una sección larga desde el menú, el desplazamiento se corrige una
  vez a los 900 ms si la página siguió creciendo.

### Hecho (El Costo Ambiental, en Acción Financiera)

- **Sección nueva `costo-ambiental`** (quinto renglón de «Presupuesto
  Federal» en el menú de Acción Financiera), en siete capítulos con índice
  de tarjetas: reloj en vivo del daño ambiental y de la basura; estado de
  cuenta ecológico (basura por persona, parte del daño y su peso contra el
  ISR de la calculadora); la basura como servicio municipal; protección
  contra daño y presupuesto del Ramo 16 (aprobado 2026, pagado al 30 de
  junio y proyecto 2027 por órgano); huella de las megaobras (pendiente);
  leyes aplicables; quién mide hoy cada dato.
- **Colección `ambiente`** en la base, generada por
  `herramientas/integrar_ambiente.py` a partir de
  `investigaciones/presupuesto-ambiental.json`
  (`herramientas/extraer_presupuesto_ambiental.py AVANCE.csv PPEF_2027.xlsx`).
  El costo del daño no se duplica: se lee de `cuentas_ecologicas`.
- **Fuentes nuevas:** Diagnóstico Básico para la Gestión Integral de los
  Residuos (SEMARNAT-INECC, abril de 2026); Censo de Gobiernos Municipales
  2023 (INEGI); proyecto de PEF 2027 en datos abiertos; Ley General de
  Residuos (reforma DOF 19-01-2026) y Ley General de Cambio Climático.
  Referencias 76 a 79.
- **Controles:** el Ramo 16 aprobado de Hacienda coincide al peso con el
  Anexo 1 del PEF 2026 ($45,564,073,902).
- **Nota técnica:** el CSV del proyecto 2027 que publica Hacienda viene
  cortado (1.1 MB, sólo los ramos 1 a 3); se usa el Excel.
- `integrar_poderes.py` ya no borra colecciones que vengan después de
  «poderes».

### Hecho (menús al cien y Módulo 5: El Costo Ambiental)

- **Menús superiores:** al tocarlos (pantallas táctiles) no abrían, porque la
  clase `open-mega-menu` se ponía en el desplegable y la hoja la espera en
  `.nav-menu-item`. Corregido; la apertura por cursor queda sólo para
  dispositivos con cursor (`@media (hover: hover)`), y un clic fuera cierra.
  `posicionarMegaMenu()` mantiene cada desplegable dentro de la pantalla (los
  de la derecha se salían y su segunda columna no se podía pulsar) y en
  teléfono lo pone a una columna con desplazamiento interno.
- **Cada vínculo aterriza en su bloque:** `seleccionarModuloExplorer(tab,
  ancla)`. Búsqueda Forense: «Auditor de Entes Públicos» (antes «Búsqueda
  avanzada de contratos», que prometía filtros inexistentes), «Radar de
  Banderas Rojas por Entidad» (antes «Auditoría de adjudicaciones directas»),
  Dossiers y 69-B, cada uno a su sección. `scroll-margin-top` evita que el
  destino quede bajo la barra fija.
- **Descargar Datos ya no tiene «Próximamente»:** ventana con seis bases en
  CSV (municipios EFIPEM, remuneraciones 2026, gasto de los Poderes,
  presupuesto ambiental, lista 69-B y catálogo de documentos) y su
  diccionario de columnas (`abrirDescargas`, `descargarCSV`).
- **En teléfono la barra superior deja de ser fija.**
- **Módulo 5: El Costo Ambiental** (`tab-panel-ambiente`, tarjeta en la
  portada): los siete capítulos y, debajo, «El PIB no alcanza» (Cuentas
  Económicas y Ecológicas). El renglón de Acción Financiera queda como
  «Paquete Económico 2027» (Constitución económica y paquete).
- Verificado: los 29 vínculos del menú en escritorio y en teléfono con
  toque; ninguno falla.

### Hecho (Portal Digital completo en la plataforma)

- **La pestaña 9 de la Enciclopedia se mudó al Portal Digital** de la
  plataforma: portada, las tres rutas con «a dónde va lo que escribe»
  (`comOrientacion`), los seis canales oficiales (ASF, SABG, FGR, SAT, PNT,
  OIC) y el decálogo (`decalogoWrap`), antes del foro. En la Enciclopedia
  queda un aviso «Se mudó» con liga a `index.html#portal`. El formulario
  «Ayúdanos a fiscalizar» sigue en el cajón lateral; la ruta 1 lo abre.
- **Menú Portal Digital:** la columna «Garantías Cívicas & Formación» ya no
  manda a la Enciclopedia: Privacidad, Canales oficiales, Decálogo y «Reporta
  lo que viste» (cajón).
- **Por qué se trababa:** los vínculos del foro hacían dos desplazamientos
  que competían, y la corrección de 900 ms regresaba al inicio del portal.
  Ahora cada uno pasa su ancla a `seleccionarModuloExplorer` y aterriza a la
  primera.
- «Ver los datos» de los hilos lleva, en la plataforma, a Presupuesto,
  Megaobras, Acción Financiera o Poderes; sólo Personajes va a la
  Enciclopedia. «Compartir» copia `index.html#portal`.

### Hecho (Consultar Recursos sin salir de la plataforma)

- **Catálogo de Fuentes Oficiales en la plataforma:** nueva subpestaña
  `faq-referencias` del Diccionario del Dinero Público, con el mismo formato
  de la Enciclopedia. Los filtros y el total se pintan desde la base
  (`refsPintarFiltros`): antes decían «27» con 79 fichas. `abrirCatalogoFuentes
  (refId)` abre el catálogo y, si recibe una ficha, la ilumina. «Compendio de
  Fuentes Oficiales», «Informes de la ASF y Documentos Oficiales» y el pie de
  página ya no mandan a la Enciclopedia; la ficha flotante de una cita ofrece
  «Ver en el Catálogo de Fuentes» en la misma página.
- La columna «Atlas Normativo & Formación Ciudadana» se llama ahora
  **«Kit del Auditor Ciudadano: Fuentes y Guías»**. La Enciclopedia sigue
  abriendo su archivo.
- **El Pase Cívico aparecía hasta abajo:** vivía dentro del pie, que lleva
  `backdrop-filter`, y eso hace que `position: fixed` se mida contra el pie.
  Al arrancar, las ventanas y cajones flotantes se cuelgan del `body`. Tenía
  el mismo defecto el cajón de detalle de las entidades (`auditDrawer`).

### Hecho (Informes de la Cuenta Pública, con cifras de la ASF)

- **Nueva sección «Informes de la Cuenta Pública (ASF)»** en Búsqueda Forense
  (`#cuentaPublicaASF`, `renderCuentaPublica()`, siete capítulos). El vínculo
  de Descargar Datos ya no manda a la Enciclopedia. Capítulos: qué es y
  calendario legal con cuenta regresiva a la siguiente entrega; la Cuenta
  Pública 2024 en cifras; dónde se concentra; su estado (selector y ranking de
  los 32); qué significa cada acción y los plazos; la Cuenta Pública 2025
  (primera entrega); documentos y descarga.
- **Datos:** colección `cuenta_publica_asf`, de la Matriz de Datos Básicos de
  la ASF (CP 2024, tres entregas, corte febrero de 2026; CP 2025, primera
  entrega, corte junio de 2026). `extraer_mdb_asf.py` lee el PDF y comprueba
  que grupos, sectores y estados sumen lo que dice el documento;
  `integrar_cuenta_publica.py` lo integra. Leyes verificadas en su texto
  vigente: LFRCF (DOF 14-05-2026), arts. 33, 35, 39, 40 y 41; CPEUM (DOF
  02-06-2026), art. 74 fr. VI.
- Cifras clave: 2,264 auditorías, 6,274 acciones (2,762 pliegos de
  observaciones), $2,005.6 mdp recuperados y $65,169.1 mdp por aclarar, 91 %
  de ellos en gasto federalizado.
- Nueva base en Descargar Datos: `asf-cp2024` (por estado y ente).
- Catálogo: fichas 80 (MDB 2024) y 81 (IR 2025, primera entrega); la 7 (LFRCF)
  citaba la reforma de 2021 y la 14 apuntaba a la portada de la ASF y hablaba
  de «2,100 pliegos»: corregidas.

### Hecho (glosario y bibliografía al día con las secciones nuevas)

- `herramientas/integrar_glosario_fiscalizacion.py` (idempotente) suma al
  glosario 24 términos que trajeron la Cuenta Pública y el Portal Digital:
  informe individual, entregas del Informe del Resultado, Informe General
  Ejecutivo, Matriz de Datos Básicos, universo seleccionado,
  representatividad de la muestra, observación solventada, R y RD, SA, PEFCF,
  PRAS, informe de presunta responsabilidad administrativa, denuncia de
  hechos, denuncia de juicio político, sugerencias a la Cámara, cuantificación
  monetaria, recuperaciones operadas, entidad fiscalizada, Comisión de
  Vigilancia, autonomía técnica y de gestión, plazos del seguimiento, Informe
  de Avance de Gestión Financiera, FEMCC y Transparencia para el Pueblo.
  Cada definición sale del texto de la LFRCF (reforma DOF 14-05-2026), del
  glosario de la MDB 2024 (pp. 518-519), de la LGTAIP de 2025 o del art. 102
  constitucional. El glosario pasa de 188 a 212 términos.
- Bibliografía: fichas 82 a 89 (MDB 2025 1.ª entrega, ASF Datos, portal de
  la Cuenta Pública de la SHCP, denuncias ASF, Alertadores, FEMCC, denuncias
  SAT, Transparencia Presupuestaria). Eran ligas que la plataforma ya usaba
  sin ficha. Pasa de 81 a 89.
- Citas corregidas: la ficha 30 decía LGTAIP de 2015 (abrogada; la vigente es
  del DOF 20-03-2025, arts. 65 a 82 y 144 a 148); «Observación, Recomendación
  y Promoción» citaba los arts. 49 a 52 de la LFRCF, que tratan otra cosa (las
  acciones están en el 40 y las recomendaciones en el 42); se precisó el
  fundamento de pliego de observaciones, muestra auditada, monto por aclarar,
  datos abiertos y recurso de revisión.
- 26 entradas nuevas en el autoenlazado (`AUTOLINK_TERMINOS`); las 199
  entradas se comprobaron: todo término existe y todo número de nota coincide
  con su ficha.
- Los conteos del diccionario (términos, preceptos, fuentes) ya no se
  escriben a mano: se leen de la base con `data-cuenta`. El pie decía «más de
  120 conceptos» y «25 preceptos»; hoy son 212 y 28.

### Hecho (Búsqueda Forense: Radar y Expedientes separados; íconos en los menús)

- El Radar de Banderas Rojas y los Expedientes caían en el mismo lugar: la
  barra de filtros de los expedientes estaba arriba del radar y el radar quedó
  metido entre esa barra y las fichas. Ahora cada uno tiene su encabezado
  (`#radarBanderasNacional` 🚩 y `#expedientesCasos` 📂), la barra de filtros
  va pegada a sus fichas y el menú lleva a cada uno por separado.
- El radar se reconstruyó con la Matriz de Datos Básicos de la ASF (CP 2024):
  los 32 estados ordenados, a elección, por lo que quedó por aclarar por cada
  $100 de muestra auditada (derivado; promedio nacional $2.58), por monto
  por aclarar (oficial) o por la parte que corresponde a los municipios
  (derivado). Cada tarjeta lleva a su estado en Informes de la Cuenta Pública.
  Se retiró la tabla `PCT_ADJUDICACIONES_ESTATALES` (porcentaje de
  adjudicación directa por estado): no tenía fuente y rellenaba con 60 % a
  quien no tuviera dato.
- `herramientas/integrar_asf_estados.py` (idempotente) reescribe en
  `DB.estados` los campos `asfMontoObservado`, `asfAuditorias` y
  `asfTipologia` con la matriz oficial y agrega `asfFuente`. Los montos
  anteriores no cuadraban con la ASF (Aguascalientes decía $428 mdp; la ASF,
  $343.3 mdp; Morelos, $890 contra $3,168.9) y las tipologías eran prosa sin
  fuente. Eso corrige a la vez el mapa, el comparador, el Auditor de Entes y
  el cajón de cada estado. El semáforo del cajón compara al estado contra el
  promedio nacional y ya no usa el porcentaje de adjudicaciones.
- Menús: «Módulo 5 · El Costo Ambiental» pasa a «El Costo Ambiental», y todos
  los vínculos de Búsqueda Forense, Acción Financiera y Descargar Datos llevan
  ícono, como ya los tenía Consultar Recursos. La descripción de Expedientes
  decía «$51,024 mdp observados»: cifra que no es la de la ASF; se retiró.

### Hecho (Expedientes de casos verificados contra la ASF y la SHCP)

- Las seis fichas vivían en el motor (`FORENSIC_DOSSIERS`) con cifras sin
  documento, un único enlace a la portada de la ASF y un botón de $79 que
  vendía un «expediente pericial» inexistente. Se sustituyeron por la
  colección `DB.expedientes`, armada con
  `herramientas/extraer_expedientes_asf.py` (lee 43 informes individuales en
  PDF, con su SHA-256, más el índice oficial de cada entrega y el libro del
  Sistema de Alertas) y `herramientas/integrar_expedientes.py` (idempotente).
  Los datos quedan en `investigaciones/expedientes-asf.json`.
- Qué cambió al verificar:
  - Tren Maya: la ficha decía «$540,000+ mdp (+246 %)» y «$1,480.6 mdp
    observados». En 14 informes (CP 2022 a 2024) la ASF dejó $785.3 mdp por
    aclarar, todos en la CP 2022 (45 % en el tramo 4); en 2023 y 2024 nada.
  - Segalmex: «$15,151 mdp» no se pudo sostener con los informes revisados.
    Las auditorías forenses de las CP 2022 y 2023 dejan $324.5 mdp por aclarar
    y 16 pliegos.
  - Dos Bocas: «$18,900 MDD» y «pagos dobles» sin documento. En 13 informes,
    $127.9 mdp por aclarar y $11.2 mdp recuperados (CP 2022 y 2023); la de
    2024 sólo emitió 3 recomendaciones.
  - Salud: se retiraron Fonsabi y CeNSIA (sin documento). En 7 informes de
    INSABI, IMSS e IMSS-Bienestar: sin montos por aclarar y 27 promociones de
    responsabilidad administrativa sancionatoria.
  - Deuda: «Coahuila 142 %», «NL 108 %», «QRoo 95 %» y «alerta amarilla» eran
    falsos. En el Sistema de Alertas con la CP 2025 (29-06-2026) los 31
    estados medidos están en endeudamiento sostenible; el más alto es Nuevo
    León con 97.8 %; suman $643,695.6 mdp.
  - Defensa: «84 % contratos clasificados» sin documento. En 7 informes (AIFA,
    Tren Maya S.A., fideicomiso de equipo militar, etc.) no quedaron montos ni
    acciones.
- `DB.estados`: `deuda` y `semaforoDeuda` salen ahora del Sistema de Alertas
  (nueve estados decían «Amarillo» sin serlo) y se agregan `deudaIld` y
  `deudaFuente`. El botón de $79 se cambió por «Copiar ficha con fuentes».

### Hecho (Ramos 28 y 33 de las 32 entidades anclados al DOF)

- **Las cifras por entidad ya tienen documento.** Salen del acuerdo con que
  Hacienda reparte ambos ramos (LFPRH art. 44): Ramo 28, Anexo 15 del
  DOF 12-12-2025 (ficha 106); Ramo 33, Anexo 16 en la versión de la
  modificación del DOF 09-07-2026, la última localizada (ficha 107). Las 32
  entidades más los renglones sin entidad cuadran **al peso** con el total de
  cada ramo: Ramo 28, $17,278.8 mdp no distribuibles; Ramo 33, $39,590.9 mdp
  no distribuibles geográficamente (FAM $23,447.4, FASP $9,941.2 y FASSA
  $6,202.3), $13,506.1 del componente indígena del FAIS y $541.5 para la ASF.
  Antes la base repartía $1,187,900 mdp de Ramo 28; eran cifras redondas sin
  fuente (la Ciudad de México tenía $112,000 contra $142,981.1 del DOF).
- `herramientas/anclar_ramos_entidades.py` (idempotente) guarda los pesos del
  DOF, comprueba el cuadre antes de escribir y crea `DB.fiscalEntidades`: el
  estado y la fuente de cada campo por entidad, los totales y los renglones
  sin entidad.
- **La lente «gasto» ahora es Ramos 28 + 33** (derivado), no un «gasto
  federalizado total» que mezclaba convenios sin fuente. «Por habitante» se
  recalcula con esa suma y queda `pendiente` por la población.
- **La línea de cuadre del mapa explica la diferencia renglón por renglón**
  en las lentes gasto, Ramo 28 y Ramo 33, con sus fichas.
- Escala de color por habitante reajustada a los nuevos valores ($15,636 a
  $23,757). Panel lateral, tarjeta de la 1.1, inspector, tooltip y buscador
  rotulan «Ramos 28 y 33» y pintan el chip de cada campo.

### Hecho (el simulador de megaobras, anclado a documentos)

- **Herramienta nueva `herramientas/integrar_megaobras_oficial.py`.** Lee 21
  archivos oficiales (comprueba su SHA-256): la cartera de inversión de
  Hacienda en ocho cortes (4T 2019 a 2T 2026, «Obra Pública Abierta»), las
  Cuentas Públicas 2014-2025 en datos abiertos y el PEF 2026 en datos
  abiertos. Transcribe con página las auditorías de la Matriz de la ASF (CP
  2024) y el estudio de la ASF sobre el costo del NAICM (marzo de 2021).
  Escribe `simulador_megaobras.verificacion`, marca cada obra campo por
  campo en `estado_campos` y recalcula los totales. Uso:
  `python3 herramientas/integrar_megaobras_oficial.py DIRECTORIO`. Las
  fuentes van dentro del bloque y no en `referencias_legales`, para no
  alterar la bibliografía de la Enciclopedia congelada.
- **Lo que cambió en cifras:**
  - Tren Maya: de $120,000 contra $515,000 mdp (+329.2 %, sin fuente) a
    **$167,341.6 mdp**, el último monto total de inversión registrado en la
    cartera (4T 2021), contra **$497,350.2 mdp** ejercidos bajo la clave
    2021W3N0001 en las Cuentas Públicas 2020-2025 (**+197.2 %**). Se revisó
    que no hay doble conteo: cada peso aparece en la dependencia que lo
    ejerció (Fonatur, Fonatur Tren Maya, Tren Maya S.A., INAH) y sin
    transferencias entre ellas.
  - Tren Interurbano México-Toluca: de $38,608 contra $105,000 mdp a
    **$76,346.8 mdp** (corte más antiguo en datos abiertos, 4T 2019) contra
    **$153,694.3 mdp** (2T 2026), **+101.3 %**, ambos de la misma cartera.
    Con recursos fiscales la Cuenta Pública registra $65,506.4 mdp de 2014
    a 2025.
  - AIFA + NAIM: el simulador sumaba los $331,996 mdp que la ASF publicó en
    febrero de 2021 y corrigió en marzo a **$113,327.7 mdp** (estudio del
    NAICM, pp. 46-48). El costo consolidado baja de $420,103 a $201,434.7
    mdp; los $88,107 mdp del AIFA siguen sin fuente y la obra queda
    pendiente.
  - Totales del simulador: inversión real $3,928,529.2 mdp, presupuestada
    $1,131,586.4 mdp, sobrecosto del conjunto 247.2 %. La pérdida operativa
    ($80,200.1 mdp al año) no cambia: sigue pendiente de documento.
  - Hallazgos inventados que se retiraron: «pagos duplicados por más de
    $1,400 mdp» (Tren Maya), «$3,200 mdp vía PTI» (Dos Bocas), «túneles
    falsos… $1,700 mdp» (Toluca). En su lugar, lo que dice la Matriz de la
    ASF de la CP 2024.
- **Incongruencias entre documentos oficiales**, en pantalla y atribuidas al
  gobierno:
  - La clave 2021W3N0001 del Tren Maya sale de la cartera pública tras el 4T
    2021, pero la Cuenta Pública sigue gastando bajo ella hasta 2025 y el PEF
    2026 le asigna $30,000 mdp.
  - El AIFA figura en la cartera solo en el 4T 2019 ($82,136.1 mdp); la Cuenta
    Pública registra bajo su clave $16,656.4 mdp (2019-2021) y luego nada.
  - Dos Bocas no aparece en la cartera en ningún corte de 2019 a 2026.
  - El Tren Interurbano movió su fecha de término de 2022 a 2026 y duplicó su
    monto total registrado.
- **En pantalla (2.2):** cada ficha lleva chips en presupuesto, costo real y
  sobrecosto; «pendiente» en pérdida, costos de operación y costo unitario; y
  un desplegable «Lo que dicen los documentos oficiales» con la serie de la
  cartera, lo ejercido año por año, el PEF 2026, las auditorías con página,
  la incongruencia y las ligas a cada fuente. Las siete obras sin documento
  lo dicen. La procedencia y la mesa de inventario cuentan cuántas obras ya
  tienen documento en vez del aviso general de antes.

### Hecho (revisión de las observaciones de Antigravity; la Enciclopedia, congelada)

- **Decisión del autor (27-09-2026): la Enciclopedia queda congelada.**
  `enciclopedia.html` no se toca, ni siquiera su sello; sirve solo como
  fuente de consulta de la que se jalan datos para el auditor. Todo el
  trabajo va a `index.html`, donde cada herramienta tiene que ser
  fidedigna y funcionar, y lo denso que hace falta para los cálculos se
  pliega en pestañas o desplegables en lugar de borrarse.
  `herramientas/sello.py` ya solo sube el sello de `index.html`.
- **Cotejo de lo que reportó Antigravity**, que trabajaba sobre una copia
  vieja (sello 20260925a):
  - «Los 2,479 municipios salen en verde»: falso. Las banderas solo se
    pintan en los 83 municipios con auditoría integral en la Matriz de la
    ASF, todos con cifra y chip oficiales.
  - «Adjudicaciones estatales al 60 % por defecto»: no existe en el código.
  - «$206,948 en el comparador»: el comparador ya usa $134,310 (DOF
    27-02-2026); el $206,948 solo aparece como «antes». Ver la advertencia
    de pendientes sobre las fichas 4.3 y 4.5 de la Enciclopedia.
  - «El Pase Cívico usa alert()»: cierto; se deja al final, como acordado.
- **Caracteres rotos** en el aviso de «enlace copiado» y en el título que
  se comparte (`compartirPlataforma`): «Â¡Enlace de AuditavisiÃ³n» ya dice
  «¡Enlace de Auditavisión».
- **Síntesis de textos del auditor, sin cambiar nombres de módulos ni
  pestañas:**
  - Módulo 1: la explicación de los cuatro pasos del dinero (LIF, PEF,
    Ramos 28 y 33, Cuenta Pública) se pliega en «El camino del dinero, en
    cuatro pasos», con sus ligas al glosario y sus fuentes intactas. El
    proemio del módulo se lleva ese desplegable junto con los párrafos
    (`pintarProemio` mueve ahora `P` y `.hero-mas`) y lo devuelve al salir.
  - Módulo 2: fuera «con rigor matemático y documental»; el texto dice lo
    que mide y que las fuentes obra por obra siguen en verificación.
  - Diccionario y Preguntas frecuentes: descripciones más cortas; «qué
    anomalías se detectan» pasa a «qué revisa la Auditoría Superior».
  - Menús: Megaobras ya no promete «sobrecostos» sin fuente; Glosario,
    Marco legal, Preguntas, Portal y Nuevo diálogo, en una línea llana.
  - Propuestas de Antigravity que no se tomaron: «a dedo» (la adjudicación
    directa es legal en los supuestos de la LAASSP), «$51,024 mdp en
    anomalías» (cifra retirada por no tener fuente; y lo por aclarar no es
    anomalía ni daño), «Tú vs. la clase política» (tono de AGENTS.md §6),
    y los conteos fijos («77 conceptos», «25 leyes»), que se desactualizan.

### Hecho (el inspector por poderes: Legislativo, Judicial y la SCJN)

El autor aclaró que las auditorías tocan a los tres niveles de gobierno y a
los tres poderes, y que en el Judicial el foco es la Suprema Corte. El nivel
federal tenía a cada poder como un solo ramo; ahora se abre por órgano.

- **Datos.** `herramientas/integrar_poderes_inspector.py CP2024.csv CP2025.csv
  AVANCE_2T_2026.csv` (verifica las tres huellas; idempotente) escribe el
  bloque propio `DB.inspector_poderes`, que no toca `inspector_federal`:
  `poderDeEnte`, siete `organos` y `judicialesEstatales2024`. Fichas nuevas
  **114** (INEGI, CNIJF-E 2025, reporte 43/25, con huella), **115** y **116**
  (estados analíticos de la SCJN, cierre 2025 y enero-junio 2026) y **117**
  y **118** (ASF, congresos de Nuevo León y Tlaxcala).
- **Órganos.** Diputados, Senado, ASF (Ramo 01); SCJN, Órgano de
  Administración Judicial (suma de las UR 110 del CJF y 120 del OAJ, porque
  la reforma de 2024 partió el mismo aparato), Tribunal Electoral (UR 210 y
  211) y Tribunal de Disciplina (Ramo 03). Cada uno con CP 2024 y 2025,
  avance 2026 y sus auditorías de la ASF a su nombre, transcritas de la
  Matriz CP 2024, p. 31 (la herramienta comprueba que suman el subtotal del
  sector). La SCJN suma su propio reporte al 31-08-2026.
- **Filtros por poder** en el nivel federal: Ejecutivo 30, Legislativo 4,
  Judicial 5, Autónomos 9. Los tribunales agrario y administrativo van con
  los autónomos: no son del Poder Judicial.
- **Cotejo entre emisores** (pregunta «¿cuadran sus cifras?»): cuando
  Hacienda, el INEGI y el propio órgano hablan del mismo dinero, se comparan;
  si difieren más que el redondeo, van al recuadro de incongruencias, y si
  coinciden se dice. Hallazgos: **el Consejo de la Judicatura reportó al
  INEGI $72,090.0 mdp ejercidos en 2024 y la Cuenta Pública dice $69,219.5**
  (+$2,870.5, +4.1 %; el Instituto de Defensoría que el INEGI dice incluir ya
  está dentro de la UR 110, así que no lo explica). **La SCJN coincide peso
  por peso** en 2024 (CP, INEGI y universo de la ASF: $5,665.8) y en 2025
  (CP y su propio cierre), pero para enero-junio de 2026 **ella reporta
  $2,101.3 mdp pagados y Hacienda $1,939.1** (+$162.2). El Tribunal
  Electoral coincide.
- **Casos especiales.** ASF: no se audita a sí misma; la revisa la Unidad de
  Evaluación y Control (art. 104 fr. II LFRCF). Tribunal de Disciplina: sin
  presupuesto aprobado en 2025 (todo por adecuaciones) y sin año auditable.
- **Estados.** El expediente estatal trae «Los tres poderes del estado»:
  gobierno (nombre `pendiente`), Congreso (CNPLE 2025, ya en la base) y Poder
  Judicial (CNIJF-E 2025, gráfica 7, p. 14; la herramienta comprueba que las
  32 cifras suman $53,516.3), con su lugar entre los 32 y las auditorías de
  la ASF a congresos locales que hay en la base.
- Sello 20260927h.

### Hecho (el inspector en los tres niveles: rendición de cuentas e incongruencias)

El autor pidió que el inspector diga, de cualquier autoridad, quién gobierna,
de qué partido, cómo fueron sus números, si rindió cuentas y, sobre todo,
**dónde no coinciden sus documentos**: «si los datos no coinciden, es
responsabilidad del gobierno». Los tres niveles responden ahora las mismas
preguntas con semáforo, y arriba de cada expediente va un recuadro nuevo,
**«Incongruencias en su rendición de cuentas»**: el mismo dinero en dos
documentos oficiales, lado a lado, con la diferencia en pesos y quién debe
explicarla.

- **Cinco fuentes nuevas, todas con huella SHA-256** en
  `herramientas/integrar_rendicion.py` (idempotente; referencias **111**
  `ref-shcp-cp2024-datos`, **112** `ref-shcp-srft-2024`, **113**
  `ref-inafed-presidencias`):
  - Cuenta Pública 2024 de Hacienda, clasificación geográfica: lo que la
    Federación pagó a cada entidad por Ramos 28 y 33.
  - INEGI, EFIPEM municipal 2016-2025 (el paquete completo, 96 MB): qué años
    entregó cada municipio su cuenta y, si no entregó la de 2024, la última.
  - SHCP, Sistema de Recursos Federales Transferidos, informe definitivo
    2024, sus dos componentes: *ejercicio del gasto* (lo recibido y pagado del
    FAIS y del FORTAMUN, según el municipio) y *destino del gasto* (las obras
    que registró con esos fondos).
  - INAFED, «Presidentas y presidentes municipales» (datos.gob.mx): nombre,
    partido o coalición y periodo. Registra, casi siempre, a la administración
    que gobernó la mayor parte de 2024; el expediente lo dice con fechas.
  - ASF, las 1,056 auditorías integrales a municipios de la CP 2024
    (`investigaciones/datos-matriz-asf2024.json`), ahora cruzadas todas.
- **Datos:** `assets/js/municipios-rendicion.js` (`window.AUDIT_MUN_RENDICION`,
  375 KB, se carga después de `municipios-efipem.js`; `sello.py` ya lo
  incluye) y el bloque `DB.inspector_estatal`.
- **Nivel municipal: de 83 a los 2,479 del catálogo.** Quién gobernó y con
  qué partido, cuatro preguntas (de qué vive, ¿rindió cuentas?, ¿cuadra lo
  que le dijo al INEGI con lo que le dijo a Hacienda?, ¿qué encontró la
  ASF?) y el círculo de salud cuando hay cuenta 2024 y auditoría integral.
  Filtros: *con incongruencias* (367, ordenados por pesos de diferencia;
  encabezan Coacalco, $269.6 mdp de FAIS: $34.6 al INEGI, $304.1 a Hacienda;
  Nogales y Zumpango), *con señal fuerte*, *no rindieron cuentas en 2024*
  (83, ordenados por lo que ellos mismos informaron a Hacienda haber
  recibido: El Salto, $268.7 mdp; Tlacoachistlahuaca, $247.0) y *sin informe
  a Hacienda* (46).
- **Nivel estatal:** cuadre entre lo que cada estado reportó al INEGI como
  recibido y lo que la Cuenta Pública registra como pagado. Casi todos
  cuadran a ±2 %; **Tamaulipas** reportó $4,049.7 mdp menos de
  participaciones (−10.9 %), **Quintana Roo** 8 % menos de aportaciones y
  **Nayarit** 4.9 % más de participaciones. Se añadió la pregunta de la
  deuda con el semáforo del Sistema de Alertas, tal cual.
- **Nivel federal:** lo ejercido por encima de lo modificado y lo ejercido
  sin pagar pasan también al recuadro de incongruencias.
- **Lo que se evitó publicar.** La primera versión marcaba «a Hacienda le
  reportó cero FAIS» a 87 municipios, Ecatepec entre ellos, con $404 mdp. Era
  falso: esos municipios informan el FAIS obra por obra en el componente de
  *destino*, no en el de *ejercicio* (Ecatepec registró $400.5 mdp). Con los
  dos componentes, «sin informe a Hacienda» bajó de 553 a 46, y un fondo que
  no aparece en ninguno se trata como **omisión** (pregunta de cuentas), no
  como contradicción.
- **Incongruencias de la propia fuente, dichas.** El INAFED registra a la
  misma persona en dos municipios en dos casos (Michoacán 16042 y Nayarit
  18006; San Pedro Mixtepec 20318 y 20319); el expediente no lo afirma y lo
  marca por confirmar. Dos San Pedro Mixtepec en Oaxaca: la ASF audita el del
  distrito de Juquila, clave 318 según el domicilio del propio INAFED.
- **Semáforos, con los umbrales a la vista.** «De qué vive» nunca es rojo:
  depender no es irregular. Estados: cuadre naranja desde ±2 %, rojo desde
  ±5 %. Municipios: cuadre naranja desde ±5 %, rojo desde ±25 % (se ignoran
  diferencias menores a $1 mdp); ASF rojo desde $50 mdp o 5 % del ingreso.
- **De paso:** dos fichas de la 1.3 decían «los 99 municipios que no
  reportaron y las dieciséis demarcaciones»; los 99 ya incluyen a las 16. Son
  83 municipios más 16 alcaldías.

### Hecho (nivel federal del Modo Inspector, reconstruido con Cuenta Pública y ASF)

El autor pidió que el inspector «sirva bien»: que la ciudadanía pueda auditar
cualquier autoridad de la que tengamos información y ver su salud financiera,
si rindió cuentas, si lo que reporta es cierto y qué irregularidades o
contradicciones hay. El nivel federal, retirado horas antes por no tener
fuentes, vuelve con **41 entes** y sólo datos oficiales.

- **Fuentes.** Cuenta Pública 2025 y avance del gasto al 2.º trimestre de 2026
  (datos abiertos de Hacienda; referencias nuevas **109**
  `ref-shcp-cp2025-datos` y **110** `ref-shcp-avance-2t2026`, con la huella
  SHA-256 del archivo) y la Matriz de Datos Básicos de la ASF para la CP 2024
  (ref. 80). `herramientas/integrar_inspector_federal.py` verifica las
  huellas antes de escribir `DB.inspector_federal` (idempotente). Lo de la
  ASF no se copia: el motor lo suma en vivo desde `cuenta_publica_asf.cp2024`
  con los nombres de sector de cada ente (`asfSectores`), excluyendo el grupo
  «Gasto Federalizado» (ahí «Salud» son fondos que ejercen los estados).
- **Entes.** Poderes, secretarías, autónomos, tribunales administrativos,
  IMSS, ISSSTE, Pemex y CFE. Fuera: los ramos generales (19, 23, 24, 25, 28,
  30, 33, 34), que son bolsas de transferencia, y el 47.
- **Cuatro preguntas con semáforo** (`inspFedDiagnostico`), umbrales a la
  vista en pantalla: ¿gastó lo que aprobó la Cámara? (±10 % / ±25 %),
  ¿rindió cuentas? (reportó CP y avance; tiene sector auditado), ¿cuadran sus
  propias cifras? (ejercido mayor que modificado = rojo; más de 5 % ejercido
  sin pagar; ritmo 2026 fuera de 80-110 % de su calendario a junio), ¿qué
  encontró la ASF? (por aclarar, pliegos, recuperaciones). Cada cifra con
  chip y referencia; ligas a los expedientes ASF del ente (`irAExpediente`).
  «Una señal no es una acusación: es algo que la autoridad debe explicar.»
- **Hallazgos que ya muestra.** Pemex: ejerció $720.5 mil millones con un
  modificado de $621.5 (el exceso, en inversión pública: $322 mil millones
  contra $215); Hacienda: +389.7 % sobre lo aprobado y 39.6 % de lo ejercido
  sin pagar al cierre; Energía +189 %; Presidencia −35.5 % y sin sector en la
  Matriz; Poder Judicial $284.6 millones por aclarar con 17 pliegos.
- **Calendario a junio**: columna `MONTO_MODIFICADO_MENSUAL` del avance. Hacienda
  no publica su diccionario en una liga accesible; se comprobó con los datos
  (en 179,385 renglones nunca supera al anual salvo uno, y suma el 52.7 % del
  modificado anual) y la columna se nombra en pantalla.
- **Contraste.** El marco del expediente pasa a `--bg-surface` con desenfoque
  y los textos de fórmula, fuentes y grupos a `--text-secondary`: sobre la
  fotografía de fondo no se leían (afecta también estatal y municipal).
- El inspector vuelve a abrir en «Federal»; buscador y encabezado
  actualizados en `index.html` y `enciclopedia.html`.

### Hecho (retiro de contenido sin fuente sobre personas y hechos, 27-09-2026)

Por instrucción del autor («iniciemos con lo más urgente o grave»), se
retiró todo lo que presentaba como hecho algo que ningún documento respalda.
Todo es recuperable en el historial de git (commits anteriores a este).

- **Verificador de noticias** (`FACTCHECK_KNOWLEDGE_BASE`, motor): seis
  titulares atribuidos a El Universal, Reforma y otros medios, con ligas que
  no llevan a ninguna nota y puntajes de «falso», más sus funciones y
  exportaciones. No se pintaba, pero estaba en el archivo público.
- **Nivel federal del inspector**: ocho expedientes (Pemex, CFE, Tren Maya,
  Dos Bocas, Salud, PJF, CONADE, SHCP) salían del mismo bloque, con cifras
  sin documento («>$515,000 mdp ejercidos, +243 %», un PJF de $78,327 mdp
  cuando el oficial es $70,005.6). Era el nivel que abría por defecto. El
  inspector abre ahora en «Estatal»; el nivel federal se reconstruye con la
  Cuenta Pública y la ASF (ver Pendiente).
- **Enciclopedia 5.1 a 5.3** (mandatarios, personajes secundarios, datos
  curiosos) y sus cuatro paneles de «argumento»: afirmaban desvíos «a
  cuentas suizas», vínculos de familiares con NXIVM y otras acusaciones
  sobre personas reales, sin una sola fuente (0 referencias en 70 KB). Se
  quitaron de la base (`personajes_politicos` conserva sólo
  `porfirio_diaz_versus`), del motor (funciones no-op porque siguen
  exportadas) y del HTML. La 5.1 muestra un aviso de revisión editorial.
- **Bitácora de noticias** (`DB.noticias`, Enciclopedia 2.5): siete notas con
  fecha y hora, sin liga, varias falsas (PEF «aprobado el 10 de enero»,
  operativo del SAT de $18,500 mdp, «142 empresas fantasma»). Vacía con
  aviso.
- **Foro del portal**: cuatro debates firmados por usuarios que no existen
  (@AuditorSureste, @CriminologiaJuridica...). Se quitaron de la base y se
  purgan del `localStorage` de quien ya los tenía (`DEBATES_SEMBRADOS`).

### Hecho (recaudación propia, convenios y dependencia de 31 entidades, INEGI 2024)

- **Tres campos por entidad dejan de ser cifras redondas sin documento.**
  Salen de la *Estadística de Finanzas Públicas Estatales y Municipales* del
  INEGI, conjunto de datos **estatal** (paquete
  `conjunto_de_datos_efipem_estatal_csv.zip`, versión del 13-08-2026),
  ejercicio **2024**, el último con cifras definitivas (2025 es preliminar).
  Referencia nueva **108**, `ref-inegi-efipem-estatal`.
  - `convenios` = concepto «Recursos federales reasignados», dentro de las
    aportaciones federales. Se lee tal cual: **oficial**.
  - `recaudacionPropia` = impuestos + cuotas de seguridad social +
    contribuciones de mejoras + derechos + productos + aprovechamientos:
    **derivado**.
  - `dep` = (participaciones + aportaciones federales) ÷ (total de ingresos −
    financiamiento) × 100: **derivado**. La deuda sale del denominador porque
    un préstamo no es autonomía: con ella, Quintana Roo, que contrató
    $19,306.8 mdp en 2024, habría salido como la entidad menos dependiente
    (51.7 %); sin ella queda en 72.2 %.
  - `federal2024` (campo nuevo) = participaciones + aportaciones de 2024,
    para que «por cada peso propio recibió» compare cifras del mismo año y no
    mezcle el Ramo 28/33 de 2026 con lo recaudado en 2024.
- **Las cifras viejas estaban lejos.** Chihuahua figuraba con $23,900 mdp de
  recaudación propia y recaudó $28,110.2; el Estado de México con $54,000 y
  recaudó $84,355.0; Aguascalientes con $5,200 y recaudó $4,032.2. Guerrero
  es la entidad más dependiente (97.1 %) y Quintana Roo la menos (72.2 %).
- **La Ciudad de México no está en el conjunto estatal en ningún año.**
  Conserva sus tres cifras con chip `pendiente` y `federal2024` en nulo.
  `fiscalEntidades.campos[k]` gana `sinFuente` (lista de entidades) y
  `motivo`; `campoEntidadChip(campo, abbr)` y el helper nuevo
  `campoSinFuente(campo, abbr)` pintan el chip por entidad en el panel, la
  tarjeta de la 1.1, el cuadro de las 32 bajo la lente de dependencia y el
  inspector.
- **Punto ciego «Los estados administran mucho y recaudan poco»:** decía
  «ronda el 84 %» sin fuente. Ahora: en 2024, de cada 100 pesos que
  ingresaron los 31 gobiernos estatales sin contar deuda, 84.6 llegaron de la
  Federación y 14.1 los cobraron ellos. Chip `derivado` y referencia 108; la
  tarjeta de puntos ciegos acepta ahora `estado` y `ref` opcionales.
- Etiquetas con el año: «Recaudación propia local (2024)», «Dependencia de la
  Federación (2024, sin deuda)», «Convenios (2024)», lente «Dependencia de las
  transferencias federales (2024)» con nota y referencia.
- `herramientas/anclar_ingresos_entidades.py` (idempotente) guarda los pesos
  de 2024 capítulo por capítulo, comprueba que en cada entidad sumen al peso
  el total de ingresos y escribe los campos, el bloque `fiscalEntidades` y la
  ficha 108.
- **Corrección de cifras mutiladas del commit anterior.** Al generar
  `anclar_ramos_entidades.py` con un heredoc sin comillas, la terminal se
  comió los `$1`, `$2`, `$6` y `$9` de siete cifras: «$23,447.4» quedó
  «3,447.4», «$1,456,045.9» quedó «,456,045.9», «$988,254.4» quedó
  «88,254.4». Afectaba las fichas 106 y 107 y el renglón «No distribuible»
  del cuadre del Ramo 33. Corregidas en la base y en la herramienta. Lección:
  los textos con `$` se escriben con el editor de archivos, no con heredoc.

### Hecho (equivalencias del módulo 1 con cifras oficiales)

- **Las tres equivalencias del bloque 1.2 ya no usan costos supuestos.**
  Antes comparaban contra un hospital «tipo» de $550 mdp, una beca de
  $2,800 al mes y el Tren Maya de $120,000 → $515,000 mdp con un subsidio de
  $79.27 por segundo, y ninguna de esas cifras tenía documento. Ahora cada
  una divide o suma cifras que la plataforma ya cita, con chip `derivado`:
  1. Costo financiero de la deuda ($1,572,073.3 mdp, PEF 2026 Anexo 8, [11])
     ÷ Poderes y órganos autónomos ($142,300.0 mdp, CGPE 2027 p. 39, [64])
     = 11.05 veces.
  2. Gasto federalizado ($2,810,800 mdp, PEF 2026) ÷ 134.4 millones de
     habitantes (CONAPO, mitad de 2026, `DB.poblacion`) = $20,914 por
     habitante.
  3. Tren Maya: $785.3 mdp por aclarar y 14 pliegos de observaciones en la
     CP 2022, suma de los informes individuales de la ASF ya reunidos en
     `DB.expedientes` (tramo 4, 45 %). Un botón abre ese expediente.
- **Nueva función `irAExpediente(id)`** (exportada): lleva al bloque 3 del
  módulo 5, quita el filtro si ocultaba el caso y despliega su ficha.
- La nota metodológica explica por qué no se compara contra costos «tipo»
  mientras no tengan documento propio.
- **El reloj «Pérdida operativa de las doce megaobras»** de la calculadora
  llevaba chip `derivado`; ahora `pendiente`, igual que en el radar, porque
  sale del simulador 2.2 sin fuentes obra por obra. La nota de los relojes
  lo aclara.
- Queda abierta la población de CONAPO como referencia puntual (ya estaba
  anotada en `DB.poblacion.pendiente`) y las cifras del simulador 2.2 (ver
  Pendiente, «Cifras que no coinciden entre secciones»).

### Hecho (leyenda del mapa y los 83 municipios anclados a la ASF)

- **La leyenda del mapa de la 1.1 dice la verdad.** Antes el rótulo decía
  siempre «Gasto Federalizado Total» y la escala eran las palabras «Mínimo,
  Medio, Máximo» sobre un degradado que el mapa no usa. Ahora una sola tabla,
  `ESCALAS_MAPA` (más `SEMAFORO_MAPA` para la deuda), pinta las entidades y
  rotula la leyenda: el nombre de la lente activa y una muestra por clase con
  su rango real y cuántas entidades caen en ella (las clases suman 32).
  `renderLeyendaMapa()` corre al arrancar y en cada `setMetric`. Los CR
  sueltos de las dos páginas se conservaron (56).
- **Los 83 municipios, anclados a su auditoría de la ASF.** Montos, estatus y
  «obras fiscalizadas» no tenían fuente, y los montos no coincidían con la
  ASF: Tijuana decía $285 mdp y la matriz da $0 por aclarar; Ecatepec, $420
  contra $231.4. `herramientas/anclar_asf_municipios.py` los cruza (83 de 83,
  por nombre exacto) con las 1,056 auditorías integrales municipales de la
  Matriz de Datos Básicos CP 2024 (`investigaciones/datos-matriz-asf2024.json`):
  - `observacionesASF` = recuperaciones + por aclarar, en mdp (la misma
    definición que la serie nacional);
  - `estatusAuditoria` con el número de auditoría, entrega, resultados,
    acciones y montos; campos nuevos `asfAuditoria`, `asfFuente`, `asfEstado`;
  - `proyectosAuditados` se vació: ninguna obra tenía documento.
  - La auditoría integral puede no ser la única: en Chiapas la ASF hizo 38
    auditorías a municipios y 29 son integrales. El texto lo dice.
  La tarjeta municipal lleva chip `oficial`, y las banderas rojas citan la
  matriz. El eje «limpieza en la cuenta» del Inspector ya calcula con cifras
  oficiales.

### Hecho (pendientes del glosario, la bibliografía y el tema claro)

Segunda vuelta sobre la lista de pendientes, con lo que no requería decisión
del autor. Script idempotente: `herramientas/glosario_fundamentos.py`.

- **26 definiciones antiguas con su artículo exacto**, leídas contra el texto
  vigente de LeyesBiblio (26-09-2026): Denuncia Ciudadana, Alertador, OIC,
  Ramo 28, LDF, ADEFAS, Techo de Endeudamiento, Subastas y Tasa de Banxico,
  Ingresos Presupuestarios, Sistema de Alertas, Adecuación, Anexo Transversal,
  Pp, Fideicomiso Público, Testigo Social, Convenio Modificatorio, Versión
  Pública, Auditoría de Desempeño, Pobreza Multidimensional, IVA, IEPS, ISAN,
  Gasto Programable, SEC y Ramo. Lo que la ley ya no decía se corrigió:
  - La pobreza la mide el **INEGI** desde la reforma a la LGDS del
    16-07-2025 (arts. 36 y 81); el CONEVAL se extinguió. También se corrigió
    la mención del art. 26 constitucional en la base.
  - La denuncia ante la ASF no se prevé anónima (LFRCF 60, reforma
    14-05-2026): la ASF protege la identidad. Anónima sí puede serlo ante el
    OIC (LGRA 91).
  - LAASSP y LGTAIP son leyes nuevas de 2025: testigo social en licitaciones
    de más de 5 millones de UMA (art. 38; $586.6 mdp, derivado), convenios
    hasta 20 % (art. 74), versión pública (LGTAIP art. 3, fr. XXI).
  - Techo 2026 (LIF art. 2o.): $1.78 billones internos y 15,500 mdd
    externos. ADEFAS: tope nuevo del art. 54 LFPRH (DOF 09-04-2026).
  - IEPS: suma videojuegos con violencia y bebidas energetizantes (LIF 2026).
    IVA: se retiró el «es regresivo» sin matiz.
- **Subsidio para el empleo con su decreto**: DOF 31-12-2025, código 5777649
  (ficha nueva 105). Hallazgo: el decreto dice que 15.02 % de la UMA son
  $536.22, pero con la UMA publicada el 9 de enero da **$535.65**; la
  definición lo explica. La calculadora enlaza la ficha.
- **Fichas 35 y 37 con documento**: la sentencia de la AI 164/2024 (copia del
  TEPJF, 303 pp.) y el Acuerdo General 7/2025 en el DOF (19-09-2025).
- **Fichas 23, 25 y 26 marcadas «por cotejar»**: sus cifras ($15,434 mdp en
  13 fideicomisos; 32-38 plazas y más de 70 colaboradores por ministro;
  54,500 plazas) no se localizaron en documento oficial. La 23 atribuía a la
  ASF la extinción de los fideicomisos, que dispuso el decreto del
  27-10-2023.
- **`--navy` definida** en el tema claro (#0b3a6e). El botón flotante se
  quedaba sin fondo y con letra blanca al pasar el cursor.
- **Titular de la ASF**: la Gaceta Parlamentaria del 10-03-2026 (Anexo V,
  acuerdo CVASF/LXVI/007/2026) publica la terna encabezada por Aureliano
  Hernández Palacios Cardel; la prensa reporta su designación ese día
  (472 votos) para 2026-2034. La plataforma no nombra al titular en ningún
  texto, así que no hubo nada que cambiar.

### Hecho (glosario y bibliografía al día con los cinco módulos)

- **Rastreo de palabras sin subrayar.** Se abrieron todos los bloques de los
  cinco módulos, se leyó su texto y se buscaron los conceptos que aparecían
  sin enlace al glosario. Los enlaces automáticos pasaron de 31 a 45 en el
  módulo 1, de 67 a 121 en Acción Financiera (módulos 2 y 3), de 20 a 33 en
  el Inspector y de 16 a 30 en Costo Ambiental.
- **28 términos nuevos** (`herramientas/integrar_glosario_modulos.py`,
  idempotente): Paquete Económico, CGPE, Resolución Miscelánea Fiscal,
  aguinaldo, prima vacacional, salario mínimo (CONASAMI), subsidio para el
  empleo, retención del ISR, cuota obrera del IMSS, SHCP, SAT, INEGI, CONAPO,
  SEMARNAT, CONAGUA, IMSS, rescate bancario (FOBAPROA e IPAB), Ramo 16,
  sobrecosto, ente público, sexenio, promedio por habitante, bandera roja,
  residuos sólidos urbanos, cambio climático, gases de efecto invernadero,
  impuesto al carbono y CEEM. Cada definición cita el artículo vigente,
  leído del texto de la Cámara de Diputados (septiembre de 2026), o el
  documento oficial (PEF 2026, CGPE 2027, Manual del PJF 2026, tabla de la
  CONASAMI). El glosario pasa de 215 a 243 términos.
- **19 definiciones corregidas.** Afirmaban cifras sin documento o cosas que
  la ley vigente ya no dice:
  - «Partida Secreta / Ramo 23 / Subvenciones Opacas» decía que eran bolsas
    «para sobornos o moches, extinguidas». La partida secreta la prohibió la
    Constitución en 2021 (art. 74 fr. IV) y el Ramo 23 sigue vivo: $167,652.2
    mdp en 2026. Ahora se llama «Ramo 23 (Provisiones Salariales y
    Económicas) y la Partida Secreta».
  - Costo financiero: ahora con el Anexo 8 del PEF 2026 (Ramo 24, empresas
    públicas y Ramo 34; total $1,572,073.3 mdp).
  - FASSA: con el art. 29 de la LCF y el 77 bis 16 A de la LGS (convenios
    con IMSS-Bienestar), en lugar de «recientemente absorbido».
  - Ramo 03: decía «cifras récord de $78,000 a $84,000 mdp»; el aprobado
    2026 es $70,005.6 mdp.
  - Tope salarial (art. 127): la Presidenta gana $134,290 netos al mes en
    2026 (PEF, Anexo 23.1.2), no $134,310. Se corrigió también la ficha 20,
    que además decía que el 127 prohíbe seguros médicos y de separación.
  - SGMM y SSI: ahora con los numerales 8.1.3 y 8.1.4 del Manual del PJF
    2026 (mando medio y operativo; aportación del 2 al 10 %). Antes hablaban
    de «hospitales de alta gama» y «sumas ilimitadas» sin fuente.
  - Haber de retiro: con el transitorio séptimo de la reforma de 2024.
  - Ponencia, secretario de estudio y cuenta, asesoría de ponencia (antes
    «Récord de Plazas (Más de 70 asesores)»), capítulo 1000, fideicomisos,
    CJF y gestión social: se retiraron cifras y adjetivos sin documento.
  - Auditoría forense: con el tipo «De Cumplimiento Forense» de la MDB 2024.
  - Declaración 3 de 3 (arts. 32 y 33 LGRA: no obliga a candidatos),
    periodos de sesiones (arts. 65 y 66) y concejalías (sin cifras sin cita).
- **Hallazgo legal al redactar «Sobrecosto»:** la reforma a la Ley de Obras
  Públicas del 16 de abril de 2025 quitó del art. 59 el tope del 25 % para
  los convenios modificatorios. La definición lo dice.
- **Tres categorías nuevas** en el glosario: 🌎 Medio Ambiente (17 términos,
  12 de ellos movidos de Hacendario), 👷 Trabajo y Salario (9) y
  🏢 Instituciones (12). Sus chips están en la plataforma y en la
  Enciclopedia; los conteos se leen de la base.
- **15 fichas bibliográficas nuevas (90 a 104):** LFT, LOAPF, LSNIEG, Ley
  General de Población, Ley de Aguas Nacionales, Ley de Protección al Ahorro
  Bancario, Ley General de Salud, RMF 2026 y su Anexo 8 (DOF), UMA 2026
  (DOF), tabla de salarios mínimos 2026 (CONASAMI), manuales de
  remuneraciones de Diputados y Senado 2026, listados 69-B del SAT, ComprasMX
  y el boletín de empleo del IMSS. Todas las ligas se abrieron desde el
  entorno de trabajo. Eran documentos que la plataforma ya citaba sin ficha.
- **Autoenlazado:** 75 entradas nuevas o corregidas en `AUTOLINK_TERMINOS`
  (de 199 a 268). «ASF» y «Auditoría Superior de la Federación» abren ahora
  su propia entrada y no la de «Fiscalización Superior». Se comprobó que
  cada término existe y que cada número de nota coincide con su ficha.

### Hecho (módulo 5, Costo Ambiental, en cuatro bloques; simulación y ticket en negativo)

- **Cuatro bloques** con la mecánica de los módulos 1 a 4 (claves `amreloj`,
  `amticket`, `ambasura`, `ampib`; el 1 nace abierto porque el reloj corre;
  el proemio lleva a cada uno):
  1. **El reloj del daño y un año en veinte segundos.** El reloj en vivo de
     siempre (`#amReloj`) y una simulación animada nueva (`renderAmCarrera`,
     `amCarreraPlay`, `amCarreraFin`): cuatro cifras anuales oficiales se
     acumulan día por día en una sola escala en pesos, con fecha, barra de
     avance, pausa, cierre del año, tabla con documento y remate derivado
     («por cada peso del Ramo 16, $34.5 de intereses y $30.3 de daño»).
     Series: intereses de la deuda 2026 (PEF, Anexo 8), daño ambiental 2024
     y gasto en protección ambiental 2024 (INEGI, CEEM) y presupuesto del
     Ramo 16 2026 (PEF). La nota dice que mezcla 2024 y 2026 y que reparte
     parejo por día.
  2. **Su ticket ciudadano en negativo** (`renderAmTicket`, `amTicketEmitir`,
     `amTicketCopiar`): con el ingreso neto del lector (lo toma del módulo 3
     si ya lo calculó) reparte por habitante (CONAPO 2026): intereses de la
     deuda, daño ambiental y, dentro, el de la basura; total del año en días
     de ingreso y en «de cada $100»; saldo de la deuda pública total en meses
     de ingreso; abonos (Ramo 16 y protección ambiental); basura en kilos; y
     el balance por cada peso abonado. Se imprime renglón por renglón y las
     cifras cuentan hacia el negativo. Sustituye a la «huella» del capítulo 2.
  3. **La basura y lo que se gasta en proteger:** el resto de
     `renderCostoAmbiental`, ya sin el índice de capítulos (`capMontar` solo
     se usa si la página no trae los bloques).
  4. **El PIB no alcanza:** la cascada y el desglose crecen al abrir el
     bloque (animación CSS); el simulador suma una gráfica PIB contra PINE
     que se mueve con transición desde el cero al mover los controles.
- **Dato nuevo:** colección `ticket_negativo`
  (`herramientas/integrar_ticket_negativo.py`) con el SHRFSP estimado al
  cierre de 2026, $20,062,321.6 mdp, 54.0 % del PIB, oficial: CGPE 2027,
  p. 67, cuadro «Estimación de las finanzas públicas, 2026-2027» (extracto y
  SHA-256 en `investigaciones/fuentes-ambiente/`).
- **Corrección:** en el Paquete 2027 la cifra «2026» de cada renglón es la
  del presupuesto aprobado, no el cierre estimado; ahora dice «2026 aprobado».
- Colores de serie `--am-c1..4`, validados en claro y oscuro (banda de
  luminosidad, croma, daltonismo y contraste).

### Hecho (módulo 4, Modo Inspector, en tres bloques; tarjetas 4 y 5)

- **Tarjeta 4:** se llama «Modo Inspector» y, en lugar del monto por aclarar,
  muestra «5,417 irregularidades · Señaladas por la ASF · CP 2024». Es la
  suma, derivada, de las acciones correctivas de la Matriz de Datos Básicos
  CP 2024 (p. 11): 174 solicitudes de aclaración + 2,762 pliegos de
  observaciones + 2,203 promociones de responsabilidad administrativa + 278
  avisos al SAT. Quedan fuera las 857 recomendaciones (R y RD), que son
  preventivas. La operación está en el `title` de la cifra.
- **Tarjeta 5:** se llama «Costo Ambiental» (también en el menú, el proemio,
  el encabezado «Módulo 5: Costo Ambiental» y la nota de portada) y, como la
  del módulo 1, pregunta «¿Cuántos billones? · Descúbrelo al comenzar».
- **Tres bloques** con la mecánica de los módulos 1 a 3 (claves `inspasf`,
  `inspradar`, `inspexp`; nacen cerrados; el proemio lleva a cada uno):
  1. ¿Qué encontró la Auditoría Superior en el gasto de 2024?
     (`#cuentaPublicaASF`, `renderCuentaPublica`).
  2. Radar de banderas rojas por entidad (`#radarBanderasNacional`).
     `radarVerEstado` abre el bloque 1 antes de saltar al capítulo del estado.
  3. Expedientes de casos por aclarar: dejan de ser tarjetas verticales en
     rejilla y pasan a una **lista numerada, un caso por renglón**
     (`ol.exp-lista`, `details.exp-fila`): número, tema, título, ente y hasta
     tres cifras en fila; al pulsar se abre el desglose completo. El número
     es el del caso en la lista completa y no cambia al filtrar. `expIr`
     abre el renglón. La Enciclopedia usa el mismo formato.
- El Auditor de Entes Públicos y el verificador 69-B siguen después de los
  bloques, sin cambios.

### Hecho (módulo 3, Calculadora Cívica, en tres bloques; comparador ampliado)

- **Tarjeta de la portada:** en lugar de «2,479 municipios» dice «Saca tu
  estado de cuenta · Tu impuesto, peso por peso».
- **Tres bloques** con la mecánica de los módulos 1 y 2 (`erarioPlegToggle`,
  `erarioIr`, claves `ccticket`, `cccompara`, `ccreloj`); los apartados A/B
  desaparecen de la plataforma (`switchApartadoCalculadora` se conserva y
  ahora abre el bloque). El bloque 1 nace abierto porque ahí se escribe.
  1. **Su estado de cuenta cívico:** 1.1 su ingreso, 1.2 lo que le retienen,
     1.3 a dónde va cada peso y 1.4 la emisión del estado de cuenta (con
     aviso mientras no hay cuenta). La numeración 1.x solo se usa en la
     plataforma (`ccPaso`); la Enciclopedia conserva sus 1–4.
  2. **Usted contra ellos:** filtros por Poder (`cmpFiltrar`) y 15 cargos,
     con el neto del bloque 1 como referencia. Nueva colección
     `AUDIT_DB.comparador_salarial` (`herramientas/integrar_comparador.py`,
     extractos en `investigaciones/fuentes-comparador/`):
     - Ejecutivo: Presidenta (Anexo 23.1.2–23.1.3), secretarios de Estado
       (límite del grupo G, Anexo 23.1.1, $168,860 netos al mes) con la
       lista de las 22 dependencias del art. 26 LOAPF, y subsecretarios.
     - Congreso: senadores (dieta neta 2026 $132.9 mil, Manual del Senado,
       DOF 27-02-2026) y asesores parlamentarios (niveles 34, 30 y 29);
       diputados federales (dieta neta 2026 $79,846.35, Manual DOF
       27-02-2026, p. 144) y su personal homólogo de asesoría, más los
       3,433 contratos de honorarios ($1,042.6 mdp; promedio derivado bruto).
     - Judicial (Manual PJF 2026, Anexo B): ministros, secretarios de estudio
       y cuenta, asesores de la SCJN, magistrados de circuito, jueces de
       distrito y secretarios proyectistas de tribunal y de juzgado. Su neto
       anual es derivado (12 × mensual + aguinaldo y prima + pago por riesgo
       + asignaciones, todos netos, con el máximo de cada rango) y parcial.
     - Diputados locales: tarjeta `pendiente` (ver Pendiente).
     - **Prestaciones:** cuenta personal derivada (aguinaldo 15 contra 40
       días; prima vacacional 3 contra 10 días) y cuadro de cinco renglones
       contra la LFT (arts. 76, 80 y 87), con el documento de cada celda.
       Hallazgos: la Cámara de Diputados paga el ISR del aguinaldo de sus
       diputados ($67,785, Anexo 23.3.4, nota 4); el aguinaldo del Senado
       reportado en el Anexo 23.2.2 equivale a unos 60 días, no a los 40 del
       Manual (marcado pendiente de aclarar).
  3. **El reloj de la deuda y de lo perdido** (antes bloque 4), sin cambios
     de cálculo; el puente desde la 2.2 abre el bloque antes de saltar.

### Hecho (módulo 2, bloque 3: tablas comparativas con cifras cotejadas)

- Nueva colección `DB.evaluacion_sexenal` (la escribe
  `herramientas/integrar_evaluacion_sexenal.py`; extractos de cada página en
  `investigaciones/fuentes-sexenal/`). Convención: a cada presidente se le
  asignan sus seis años calendario (López Obrador 2019–2024).
  - **PIB** (INEGI, PIBT año base 2018, `PIBT_2.xlsx`, sha256 anotado):
    tasa media anual, derivado. Zedillo 3.48, Fox 1.81, Calderón 1.38,
    Peña 1.94, López Obrador 0.82 (2023–2024 preliminares). Salinas
    pendiente: la serie empieza en 1993.
  - **Deuda (SHRFSP, % PIB) al cierre:** 2000 30.7, 2006 29.1, 2012 36.8
    (ASF, IR CP 2012, Tomo Ejecutivo, p. 67, con datos SHCP); 2018 44.9 (ASF,
    IGE CP 2022, p. 150); 2024 51.4 (SHCP, Comunicado 4/2025). 1994 pendiente.
  - **Empleo formal (IMSS, diciembre contra diciembre):** 2000, 2006 y 2012
    del Anexo Estadístico del Quinto Informe de Gobierno (p. 530); 2018 y 2024
    de los comunicados IMSS 008/2019 y 009/2025. Fox 1,240,732; Calderón
    2,383,551; Peña 4,017,322; López Obrador 2,159,014. Salinas y Zedillo
    pendientes (la serie empieza en 1997).
  - **Auditorías de la ASF:** 2000–2018 de la gráfica del IGE CP 2018
    (p. 313); 2019–2024 de las Matrices de Datos Básicos.
  - **Recuperaciones operadas** (IGE CP 2022, p. 16, corte 31-ene-2024): la ASF
    publica 2001–2008 en una sola cifra ($41,091.6 mdp), que no separa a Fox
    de los dos primeros años de Calderón; se dice así.
  - **Monto por aclarar:** solo CP 2019–2024 (misma definición).
- Las métricas de déficit, gasto e ingresos salieron de la trivia: no se
  pudieron cotejar y además cambian de definición entre épocas (con y sin
  inversión de Pemex). Siguen en la 5.1 de la Enciclopedia como estaban.
- La trivia queda en dos grupos, Crecimiento (economía, deuda, empleo) y
  Fiscalización (auditorías, recuperado, por aclarar). Quien no tiene dato no
  entra a la barra ni a las opciones y se lista abajo con su motivo. Tras
  «Ver resultados» aparece una nota «Para leerlo bien».
- Dos tablas comparativas (`peTabla`): se desbloquean al responder las tres
  trivias de su grupo; botón único «Contabilizar la tabla» / «Reiniciar a
  ceros» (`peTablaAlternar`, exportado). Celdas con chip `pendiente`,
  «No aplica» o «Conjunta», notas agrupadas por motivo y fuentes con liga.
  Primera columna fija al desplazar en celular.
- Hacienda (secciones.hacienda.gob.mx, presto) no respondió desde el
  entorno; la API del INEGI pide credencial y no se usó.

### Hecho (módulo 2, bloque 3: la evaluación de los presidentes con trivia)

- El bloque 3 queda en dos partes: 3.1 «Las megaobras de cada sexenio» (el
  simulador sexenal de siempre) y 3.2 «La evaluación de los presidentes:
  adivine y compruebe» (`renderPresEval`, traída de la 5.1 de la
  Enciclopedia y reorganizada).
- Seis métricas en pestañas: economía (PIB), deuda al cierre, déficit,
  tamaño del gasto, ingresos y lo que la ASF dejó por aclarar. Cada una hace
  primero una pregunta de trivia con los seis presidentes (o las seis Cuentas
  Públicas, en la de la ASF); el contabilizador está bloqueado 🔒 y las
  barras veladas hasta responder. Después, un solo botón «Ver resultados» /
  «Reiniciar a ceros»; reiniciar reabre la pregunta para volver a jugar. Un
  marcador lleva los aciertos. Claudia Sheinbaum no entra: sexenio en curso.
- **Estado de los datos:** la métrica de la ASF es oficial (Matrices de Datos
  Básicos 2019–2024, con liga por renglón). Las cinco macro vienen de
  `porfirio_diaz_versus.mandatarios_comparativa`, que declara su serie
  (INEGI, SHCP) pero no se ha cotejado cifra por cifra: llevan el chip
  `pendiente` y lo dicen al pie (ver Pendiente).
- Las gráficas de la 5.1 con «irregularidades ASF acumuladas» por sexenio no
  se trajeron: no tienen fuente (ya estaba en Pendiente). El expediente de
  cada presidente se consulta en la 5.1 de la Enciclopedia, que sigue igual.
- Corrección: el periodo de López Obrador terminaba el 30 de septiembre de
  2024, no el 30 de noviembre (art. 83 CPEUM, reforma DOF 10-feb-2014).

### Hecho (módulo 2, bloque 2: filtros en dos pasos y simulación en vivo)

- **Panel de filtros** (`.sim-filtros`): «Paso 1 · Industria» (el mosaico de
  sectores, con «Todas las industrias») y «Paso 2 · Mandato presidencial»,
  ahora tarjetas con el color del sexenio, el periodo y cuántas obras le
  tocan (`.sim-mdt`), en lugar de pastillas.
- **Filtro activo:** sustituye la cabecera del mundo 🌐 con «Contar de nuevo» y
  «Quitar los filtros». Dice en una línea qué se ve (industria · mandato · N
  de 12 obras), trae un solo botón Contabilizar / Reiniciar a ceros
  (`simCabAlternar`) para sus tres cifras y muestra «Quitar filtros» solo
  cuando hay alguno puesto.
- **Pestaña «Simulación en vivo»** al final de «Ordenar y medir por»: muestra
  las fichas vivas (pérdida operativa día con día y su acumulado) y «Contra
  qué se compara este dinero» (`#simVistaVivo`); las otras pestañas muestran
  la lista comparativa. Pulsar un renglón de la lista abre la pestaña en vivo
  y lleva a la ficha. En la Enciclopedia (sin `#simVistaVivo`) la pestaña no
  aparece y todo sigue como estaba; las tarjetas de mandato sí se comparten.

### Hecho (módulo 2, Inversión y Megaobras, en cuatro bloques)

- Índice de cuatro pasos y cuatro bloques desplegables, con la misma
  mecánica del módulo 1 (`erarioPlegToggle`, `erarioIr`): 1 El pulso del
  gasto (tira de cifras y cadencias de pérdidas y subsidios), 2 El desglose
  obra por obra: sector e industria (antes parte A), 3 Administración
  presidencial (antes parte B) y 4 De cero al resultado (antes parte C). Las
  pestañas A/B/C desaparecen de la plataforma; `setSimParte` ya no oculta
  nada si no hay pestañas. La Enciclopedia conserva las suyas.
- «Por qué a veces verá 12 obras y a veces 13» pasa a una nota de método en
  la ventana lateral: 📖 junto al título del proemio
  (`abrirNotaConteoObras`, texto en la plantilla `tplConteoObras`), con un
  botón al reparto por administración.
- Los saltos a la ficha de una obra abren su bloque; la pastilla flotante del
  contador no aparece con el pulso plegado.
- Corrección del botón único: el de reinicio seguía visible porque el estilo
  del botón le ganaba al atributo `hidden`; ahora se oculta con estilo.

### Hecho («el rastro del gasto público» en el glosario)

- Junto al título «Descubre el rastro del gasto público» de Auditoría en
  imágenes, un 📖 abre en la ventana lateral la nueva entrada del glosario
  «Rastro del Gasto Público» (partida que lo aprobó, contrato o transferencia,
  a quién se pagó y qué encontró la ASF; fundamento: art. 134 CPEUM, art. 38
  LGCG y LFRCF). El glosario llega a 215 términos.

### Hecho (un solo botón en los simuladores y la tarjeta del módulo 1 sin cifra)

- **Tarjeta del módulo 1 en la portada:** en lugar de «$10.19 billones» dice
  «¿Cuántos billones? · Descúbrelo al comenzar»; la cifra se entrega dentro
  del módulo. No se usó «récord» o «presupuesto histórico» porque la base no
  tiene los totales del PEF de años anteriores con su fuente (ver Pendiente).
- **Botón único, como en Auditoría en imágenes:** todos los simuladores
  arrancan en ceros y tienen un solo botón. El primer toque cuenta o evalúa y
  el botón pasa a decir «↺ Reiniciar a ceros»; el segundo regresa a cero.
  `erarioBarraMandos` (las siete barras del módulo 1 y del mapa) lo hace de
  origen; los demás (megaobras, sexenios, tablero de Díaz, San Lázaro,
  Senado, prestaciones y los otros de la Enciclopedia) los funde
  `botonUnicoAplicar`, que esconde el botón de reinicio y lo invoca desde el
  principal. La calculadora cívica se deja con sus dos botones: ahí el botón
  rehace la cuenta con los datos que el lector cambia.
- **Sin arranque automático:** los tableros de la Enciclopedia que se
  animaban solos al entrar en pantalla (`vsxAutoArranque`) ahora esperan el
  botón (`VSX_ARRANQUE_AUTOMATICO = false`).

### Hecho (módulo 1, Circuito del Dinero, en tres bloques)

- **Párrafo del proemio:** «auditar», «presupuesto federal», «Ley de Ingresos
  de la Federación», «ramos», «Ramo 28», «Ramo 33», «Cuenta Pública» y
  «Auditoría Superior de la Federación» abren su definición en la ventana
  lateral. Las siglas se escriben completas y se explica qué es un ramo y qué
  distingue al 28 (participaciones de libre uso) del 33 (aportaciones
  etiquetadas). El glosario suma «Auditar (Auditoría Gubernamental)» y
  «Auditoría Superior de la Federación (ASF)» (214 términos).
- **Índice de tres pasos** bajo el proemio y, en el proemio, tres botones que
  abren cada bloque (`erarioIr`).
- **Bloque 1 · Arquitectura del flujo del erario federal:** el esquema del
  flujo y «Las cuatro etapas» se fundieron en una sola tira de cuatro
  tarjetas con flecha (se recauda → se aprueba → se ejerce → se rinden
  cuentas). Cada una lleva su cifra y el botón «Qué ley la gobierna», que
  abre debajo el fundamento, el plazo y quién responde (datos de
  `panoramaErario.circuito`). La etapa 4 muestra lo por aclarar de la CP 2024
  ($65,169.1 mdp, oficial, ref. [80]). Dentro: 1.1 «¿Cuánto margen tiene el
  presupuesto?» (barra proporcional y termostato) y 1.2 «¿A qué equivale?».
- **Bloque 2 · Cuánto dinero es:** la tira de cinco cifras y, dentro, 2.1 De
  dónde sale, 2.2 En qué se va y 2.3 A dónde baja (mapa y 32 entidades).
- **Bloque 3 · Lo que la cifra grande no dice:** los cinco puntos ciegos.
- Los saltos desde menús, radar y proemio abren los bloques que envuelven al
  destino (`erarioAbrirAncestros`); el mapa se vuelve a medir al abrirse.
- **Equivalencias corregidas y marcadas pendiente:** decía «12.5 millones» de
  becas, pero $2,810,800 mdp ÷ $33,600 da 83.6 millones; y «2,850
  hospitales», cuando $1,572,073.3 ÷ $550 mdp da 2,858. Ahora se muestra la
  operación, y las tres llevan el chip `pendiente` porque sus supuestos no
  tienen documento citado (ver Pendiente).

### Hecho (logotipo propio: la moneda inspectora, con su presentación)

- El ⚖️ de la cabecera se sustituyó por un logotipo en SVG
  (`assets/img/logo-auditavision.svg`). Primero fue un billete verde con alas;
  desde el sello 20260927t es **una moneda de oro** grande, con canto acuñado y
  gráfila de perlas, dos ojos (el derecho agrandado por la lupa), cejas,
  bigote, sonrisa, sombrero de bombín, un sello de lacre rojo con la palomita
  de «verificado» y alas de ángel amplias, de dos hileras de plumas blancas.
  Conserva la proporción 128 × 100 del anterior, así que no cambió ningún
  `width`/`height` de quien lo usa. Va en la barra de la plataforma y en la
  cabecera de la Enciclopedia; aletea un poco al pasar el cursor (salvo con
  «reducir movimiento»).
- Al picarlo se abre «Quiénes somos» en la ventana lateral
  (`abrirPresentacion`): el nombre palabra por palabra (Audita · visión ·
  Sistema · Cívico · Fiscalización), el propósito, cinco principios, cuatro
  compromisos y su fundamento (arts. 6º A, 8º, 79 y 134 constitucionales). No
  lleva cifras. Al pie: Decálogo del ciudadano auditor y Catálogo de fuentes
  (en la Enciclopedia, «Ir a la plataforma») y la nota de finanzas públicas.
- El texto «Auditavisión / Sistema Cívico de Fiscalización» sigue llevando al
  inicio de la página.
- `herramientas/sello.py` acepta ya dos letras: después de la «z» sigue la
  «za» (el sello de este cambio es 20260926za).

### Hecho (encabezado de la portada más limpio, con nota en ventana lateral)

- Título: «Explora el panorama de las finanzas públicas en México» (antes «del
  gasto público»), con un libro 📖 que abre la nota «Las finanzas públicas» en
  la ventana lateral (`abrirNotaPortada`): qué son, por qué importan (PEF,
  gasto federalizado, costo de la deuda y lo por aclarar de la CP 2024, leídos
  de la base), qué hay en cada uno de los cinco módulos, cómo leer los tres
  estados de una cifra y su fundamento constitucional (arts. 31 fr. IV, 74 fr.
  IV y VI y 134). Al pie: Enciclopedia, «gasto público» y «hacienda pública»
  del glosario.
- El párrafo largo bajo el título se redujo a una frase; su contenido vive en
  la nota.
- Los tres botones que iban entre el título y los módulos (Enciclopedia,
  Comienza a explorar y Pase Auditor Cívico) se retiraron de la portada, por
  decisión del autor: la Enciclopedia sigue en «Consultar Recursos», el Pase
  en su menú y las cinco tarjetas hacen de «comenzar».
- El recuadro «Fiscalización ciudadana del gasto público» es translúcido y sin
  desenfoque (deja ver la ciudad del fondo); título y frase llevan una sombra
  suave para leerse. Las tarjetas de módulo conservan fondo sólido.

### Hecho (la ASF en cifras oficiales 2019-2024 y la cinta de datos verificada)

- **Serie histórica oficial.** `herramientas/extraer_serie_asf.py` lee el
  renglón Total de la Matriz de Datos Básicos consolidada de las Cuentas
  Públicas 2019 a 2023 (cada PDF verificado por sha256; se detiene si las seis
  acciones no suman el total o si observado ≠ recuperado + por aclarar) y
  escribe `investigaciones/asf-mdb-serie.json`. `integrar_cuenta_publica.py`
  lo suma a `DB.cuenta_publica_asf.serie` con la fila de 2024.
  Por aclarar, en mdp: 2019 99,396.6 · 2020 60,834.1 · 2021 61,840.3 ·
  2022 29,765.9 · 2023 51,979.0 · 2024 65,169.1. Desde la CP 2023 la matriz
  ya no publica el «monto observado»: se deriva y se marca `derivado`.
- **Hallazgo:** la antigua serie del simulador graficaba el *observado*
  (63,010 / 64,834 / 32,894…), no el *por aclarar*, y para 2019 y 2023 traía
  cifras que no son las del documento; su «% resuelto» no tenía fuente.
- **Capítulo nuevo** en «¿Qué encontró la Auditoría Superior?»: «Seis años de
  revisiones», con selector (por aclarar, observado, recuperado, auditorías,
  pliegos), liga a la página de cada matriz y la lectura derivada: de lo
  observado en 2019-2024 se recuperó el 3.6 % durante las auditorías.
- **Enciclopedia, Legislativo, bloque 3 (ASF):** se retiró el simulador de
  «salud financiera» (tacómetro, ROI contra un presupuesto de $3,200 mdp y
  «tasa de recuperación de los $51,024 mdp») y el análisis por «tipologías»
  con montos sin fuente, con todo su código. En su lugar va la misma sección
  oficial de la Cuenta Pública (`#cuentaPublicaASFLeg`). La tarjeta usa el
  presupuesto aprobado de la ASF, $2,822.6 mdp (PEF 2026, Anexo 1), 2,264
  auditorías y $65,169.1 mdp por aclarar de la CP 2024; el titular queda
  `pendiente` de verificar (nombramiento de 2018 por ocho años).
- **Cinta de datos de referencia (portada y Enciclopedia):** se retiraron
  «recaudación SAT récord $4.95 billones» (la LIF 2026 estima $5.42 billones
  de ISR, IVA e IEPS), «deuda subnacional $715,420 mdp», «12,867 empresas
  aportan el 52 %», «dependencia fiscal 84.0 %», «predial 0.16 % del PIB» y
  «CETES 28d», todos sin fuente. Ahora lleva siete datos con su documento en
  `title`: PEF, gasto federalizado, lo por aclarar de la CP 2024, ISR+IVA+IEPS
  de la LIF, Ramo 28, costo financiero de la deuda y la deuda de los 32
  gobiernos estatales ($643,695.7 mdp, suma del Sistema de Alertas).

### Hecho (radar: cada cifra explica qué es y cómo se calcula)

- Pulsar una cifra del radar (o su ícono) ya no salta a otra sección: abre
  la ventana lateral del glosario (`abrirRadarConcepto(clave, origen)`) con
  «Qué significa», «En qué consiste», «Cómo se calcula» y la fuente. Se
  abre también con Enter o espacio; Escape cierra y el foco vuelve a la
  cifra.
- **Megaobras:** las 12 obras del simulador ordenadas por pérdida, cada una
  con «operar − ingresos»; los cuatro pasos del cálculo hasta la
  equivalencia de la visita, y el aviso de que FOBAPROA/IPAB aporta el
  61.4 % del total y es un rescate, no una obra. Estado `pendiente`.
- **Costo de la deuda:** definición del glosario, los cuatro componentes del
  Anexo 8 (`DB.panoramaErario.egresos` → `egr-costofin`, suman
  $1,572,073.3 mdp), la equivalencia por segundo, minuto, hora y día, y
  «Qué no incluye» (amortizaciones, art. 2º fr. XXV LFPRH).
- **Por aclarar ante la ASF:** definición del glosario, los seis grupos de
  la matriz de la CP 2024 (el gasto federalizado concentra el 91.1 %), cómo
  se obtiene la cifra, por qué no corre por segundo y los plazos de
  solventación con su fundamento.
- Todo se lee de la base; los botones del pie llevan a la sección o al
  glosario completo si el lector quiere seguir. La ventana es la misma del
  glosario (`glosDrawerShell`, `glosDrawerAbrir`).

### Hecho (guion editorial, entrega A: significado y promesas)

El autor entregó un guion editorial (sobre la versión 20260926q). Su
prioridad 1, corregir lo que dice más de lo que es, queda así:

- **Radar sin suma.** Se retiró «Erosión patrimonial», que sumaba el déficit
  de megaobras, el costo de la deuda y lo observado por la ASF como si fuera
  una sola pérdida. Ahora son tres conceptos separados, cada uno con su
  estado: megaobras (`pendiente`: la cifra de $80,200.1 mdp viene del
  simulador, sin fuentes por obra), costo financiero de la deuda (`oficial`,
  PEF 2026 Anexo 8) y lo por aclarar ante la ASF (`oficial`, $65,169.1 mdp
  CP 2024, MDB p. 11), este último **fijo, sin contador por segundo**.
- **Tasa corregida:** $1,572,073.3 mdp ÷ 31,536,000 s = $49,850.12/s (decía
  $49,849.80). La tira del desglose muestra ahora esa sola cifra oficial
  repartida por segundo, minuto, hora y día, cada una `derivada`. Antes
  rotulaba «Monto Anual PEF $1,703,297 mdp» a la suma de los tres conceptos.
- La tarjeta de megaobras citaba Mexicana de Aviación y el Corredor
  Interoceánico, que no están entre las 12 obras del simulador. Corregida.
- Rótulos: «Radar hacendario · cifras en perspectiva», «Datos de
  referencia» (antes «Notificación en vivo»), «Equivalencia durante tu
  visita». La cinta dice $65,169.1 mdp por aclarar (CP 2024) en lugar de
  $51,024 mdp.
- **Botones honestos:** «Enviar Observación Cívica» → «Guardar en este
  navegador»; «Publicar argumento en el Portal» → «Guardar argumento en este
  navegador». El Portal ya no promete «100% protegidos» ni diálogo en vivo:
  dice que lo escrito se guarda sólo en este navegador.
- **Frases absolutas:** «Toda cifra está respaldada», «Cero
  especulaciones», «rigor inexpugnable» y la «Regla de Diseño Permanente»
  pasan a «cada cifra muestra su fuente o su estado de verificación», con los
  tres estados explicados.
- El chip de preceptos cuenta desde la base (28); decía 25.
- «Audita en tiempo real» y «Pérdidas en tiempo real» se reescribieron.

### Hecho (un solo encabezado por módulo e íconos más grandes)

- **Sin título repetido.** Al pulsar «Comenzar», el proemio absorbe el
  encabezado de la sección de entrada del módulo (`PROEMIO_HERO`): la
  etiqueta de esa sección pasa al renglón superior («Módulo 1 · Panorámica
  del Erario · Ejercicio Fiscal 2026») y su párrafo, con sus ligas a
  fuentes, se muda al proemio. El encabezado de abajo se oculta. Aplica a
  los cinco módulos (1.1 Panorámica, 2.1 Megaobras, 2.4 Calculadora,
  Inspector y Costo Ambiental).
- El párrafo se mueve, no se copia: `#ccEntrada` de la calculadora sigue
  siendo el mismo nodo. Al salir del módulo (`proemioSoltarHero`) vuelve a
  su lugar y el encabezado reaparece, así que quien entra por el menú ve la
  sección como antes. El texto propio de `PROEMIOS` queda de respaldo.
- Íconos: 112 px en las tarjetas (antes 84) y 128 px en el proemio (antes
  96); 100 px en teléfono.

### Hecho (Auditoría en imágenes: regreso desde el expediente)

- Los botones internos de la ventana de cada obra (abrir el expediente,
  el padrón municipal, la ficha de la deuda o del Ramo 33, la calculadora)
  ahora encienden la barra de regreso: «Llegó aquí desde Auditoría en
  imágenes · <obra>», con «↩︎ Volver a donde estaba», «⬆️ Inicio» y ✕ para
  descartarla.
- «Volver a donde estaba» cierra la ficha lateral que se hubiera abierto,
  regresa a la altura de la página y reabre la ventana de la misma obra. Si
  el lector ya había pulsado «Ver gasto», las cuentas aparecen hechas
  (`scMostrarCuentas`); si no, en cero. `navOrigen` admite ahora una receta
  `retorno` para orígenes que no son una pestaña.
- La barra sube a `z-index: 99998`: antes la tapaban las fichas laterales
  (99995). Con una ficha abierta en pantalla ancha se corre a la izquierda.
- Las ligas «↗» a los informes de la ASF abren el PDF en otra pestaña; la
  plataforma se queda donde estaba.
- Probado: 11 botones de las 8 obras, ida y vuelta, sin errores.

### Hecho (glosario en ventana lateral, al estilo de USAspending)

- **La palabra enlazada ya no lleva nota al pie en línea.** El enlazado
  automático (`autolinkAmbito`) marca el término con un libro 📖
  (`button.glos-term`). Al pulsarlo se abre una ventana lateral (drawer) en la
  misma página, con categoría, «Qué significa», «Fundamento» y «Fuente»: la
  referencia [NN] con su cita APA y la liga al documento oficial.
- **El glosario sigue siendo la fuente única** (`DB.glosario`). La ventana
  termina con «Ver en el glosario completo», que hace el salto de siempre
  (ahora `irAlGlosario`, con su barra de regreso a la palabra de origen).
- `goToGlossary(term)` abre ahora la ventana; así, todos los botones
  «📖 Glosario» y «Qué significa» de la plataforma la usan sin tocarlos. Si
  el término no está en el glosario, cae al salto de siempre.
- Se cierra con ✕, con Escape o al pulsar fuera, y devuelve el foco a la
  palabra. La ventana se construye en el momento, por eso funciona igual en
  `index.html` y en `enciclopedia.html`.

### Hecho (vitrina de módulos al estilo del explorador de USAspending)

- **Tarjeta limpia:** cada uno de los cinco módulos de la portada muestra sólo
  ícono grande en círculo, título, una frase breve, su cifra y el botón
  «Comenzar». Se retiró la etiqueta «Módulo N» y el párrafo descriptivo.
- **Proemio al abrir:** el texto que salió de la tarjeta vive ahora en
  `#moduloProemio`, al inicio del espacio de módulos: ícono, «Módulo N ·
  Proemio», título, subtítulo (el subtema), el texto, los temas del módulo y
  «↑ Ver todos los módulos». Lo pinta `pintarProemio(tabKey)` desde
  `PROEMIOS` en `audit-engine.js`; `switchTab` quedó envuelto
  (`switchTabNucleo`) para pintarlo una sola vez con la pestaña pedida, y se
  oculta en las pestañas que no son de la vitrina.
- **Cifra corregida en la tarjeta del Inspector:** decía «$51,024 mdp por
  aclarar», cifra sin sostén (ver la bitácora de noticias, abajo). Ahora dice
  $65,169.1 mdp por aclarar en la CP 2024, de la Matriz de Datos Básicos de
  la ASF (consolidado, feb. 2026, p. 11), la misma que usa la sección de la
  Cuenta Pública. Cada cifra de tarjeta lleva su fuente en `title`.
- **Tema claro:** la variable `--navy` no está definida en la hoja; los
  botones de las tarjetas salían invisibles. Las reglas nuevas usan
  `var(--navy, #0b3a6e)`. El resto de usos de `--navy` en la hoja sigue
  igual (pendiente abajo).

### Hecho (Auditoría en imágenes: simulador «Ver gasto» con cifras de la base)

- **El carrusel ya no lleva cifras propias.** `showcaseData`, con montos sin
  fuente que contradecían a otras secciones, se sustituye por `SHOWCASE`: cada
  diapositiva arma sus cifras al abrirse desde la base (fichas de Expedientes,
  Panorama del Erario, matriz de la CP 2024 y padrón EFIPEM). Cada cifra lleva
  su chip `oficial` o `derivado` y la ventana cita su documento.
- **Simulador «Ver gasto».** Las cuentas nacen en cero y sólo suben al pulsar
  el botón (motor compartido `simAnimarZona`); un segundo toque las regresa a
  cero. Debajo, «el rastro del dinero»: una barra por informe de la ASF (o por
  fondo, o por componente) con liga al PDF.
- **Los botones azules llevan a su contenido.** Antes mandaban a la
  pestaña genérica de megaobras o a una clave que no existía (`inspector`).
  Ahora: Tren Maya, Dos Bocas, AIFA, Tren Interurbano y Megafarmacia abren su
  ficha en Expedientes (`expIr`), resaltada; la deuda abre la ficha del costo
  financiero en la 1.1 y la calculadora en el bloque de intereses; el Ramo 33
  abre el padrón municipal y la ficha del Ramo 33; LEGO abre Ciénega de Flores
  en el padrón (`munIrA('NL','19012')`) y el expediente de El Cuchillo II.
- **Preguntas reescritas** para lo que los documentos sí responden. Las
  anteriores afirmaban sobrecostos («más del doble», «triplicó») sin fuente.
- **Cuatro expedientes nuevos (10 en total):** Tren Interurbano (10 informes,
  CP 2022 a 2024), AIFA (5), El Cuchillo II (3) y Birmex (auditoría forense
  234 de la CP 2023). `defensa` cede el informe del AIFA 2024 a su ficha.
  `extraer_expedientes_asf.py` lee además cifras literales del informe de
  Birmex (precio del inmueble de Huehuetoca, equipamiento, pagos de 2023,
  pagos a almacenes privados) y de El Cuchillo II (106 km, 5,371,290
  usuarios); si una frase no aparece, se detiene.
- **Imágenes rotuladas:** las cinco con C2PA de IA dicen «Ilustración
  generada con IA»; las otras tres, «Imagen ilustrativa». Los `alt` ya no
  las presentan como lugares reales.
- **Defecto corregido de paso:** la integración de la copia local del 25 de
  septiembre borró de `index.html` las ventanas laterales `flujoFichaDrawer` y
  `munFichaDrawer`. Pulsar un renglón de la 1.1 o un municipio de la 1.3 no
  abría nada. Se restauraron desde `enciclopedia.html`.
- Accesibilidad: las diapositivas se abren con Enter o espacio; la ventana se
  cierra con Escape o al pulsar fuera, y se desplaza por dentro en teléfono.

### Hecho (planes de Astra y Antigravity, cruzados con el código: entrega 1)

El autor pidió analizar dos planes de mejora. Se contrastaron contra el
código (commit c3e044e, sello 20260927j); Antigravity había trabajado sobre
un commit anterior (d496a18). Resultado y lo que se aplicó:

- **Buscador global** (`initSearch`): lo escrito se pinta con `escHtml`
  (una consulta con etiquetas se muestra, no se ejecuta); compara sin
  acentos ni mayúsculas (`munPlano`); recorre **el padrón completo de 2,479
  municipios** (`inspEntes('municipal')`, el mismo del Inspector) con su
  entidad y clave INEGI, para distinguir homónimos (Juárez en cinco
  estados); el municipio abre su expediente en el Inspector. Flechas, Enter
  y Escape; lo que empieza con la consulta va primero; tope de 12 con aviso
  de cuántas coincidencias más hay; «sin coincidencias» se dice como tal.
- **Historial:** la subpestaña elegida a mano entra como `#pestaña/sub`;
  Atrás y Adelante la restauran, y una dirección desconocida vuelve a la
  portada (antes `popstate` ignoraba todo lo que tuviera `/`).
- **Avisos honestos:** el formulario de comunidad y el foro dicen cuando el
  navegador no dejó guardar y conservan el texto; `copyDebateLink` y
  `copiarTextoPlano` solo anuncian la copia si ocurrió, y si no ofrecen el
  texto para copiarlo a mano; tema y apoyos ya no truenan sin almacenamiento.
- **«5,417 irregularidades» → «5,417 acciones promovidas»**: la suma de la
  Matriz de la ASF (p. 11) cuenta acciones, no irregularidades probadas.
- **Bandera municipal de la ASF:** el verde exige número de auditoría; sin
  él, chip blanco «pendiente, no limpio». Hoy los 83 municipios de la base
  tienen auditoría integral, así que nada cambia a la vista: la observación
  de Antigravity sobre «saldos blancos» no se sostiene con la base actual.
- **Rechazado de los planes, por regla:** renombrar módulos o pestañas;
  bajadas con «$51,024 mdp» (ya retirada) y «FARAC: 12 obras, $211,000 mdp»
  (sin fuente); la leyenda «proviene exclusivamente de fuentes oficiales»
  tal cual (hay cifras pendientes); reorganizar el motor en componentes.
- **Ya existían:** descarga CSV con BOM (`descargarCSV`) y ticket PNG.
- **No se tocó y queda documentado:** el comparador SCJN con $206,948,
  aguinaldo $588,000 y «póliza VIP» (`SCJN_CALCULOS_GLOBALES_DATA`) solo se
  pinta en la Enciclopedia congelada; ver «Cifras de la Enciclopedia que NO
  deben pasar al auditor».

### Hecho (decisiones del autor: leyenda de tres estados y panel lateral)

Decisiones del autor (27-09-2026): trato de **tú** al lector; la
información densa va en **panel lateral** (drawer), como propuso
Antigravity; la leyenda de estados va en «Principio y Compromiso».

- **Leyenda «Cómo leer cada cifra»** en el pie (`.leyenda-estados`): los
  tres chips con su significado — oficial (del documento, con liga),
  derivado (cálculo nuestro con la operación dicha) y pendiente (se sabe
  o se ha dicho, pero no se ha verificado en documento oficial).
- **Panel lateral de contexto** (`abrirContexto`, `ctxBoton`): reutiliza la
  ventana del glosario (`glosDrawerShell`) con la marca «Contexto y
  método» y 560 px de ancho. Un botón `.ctx-abrir` guarda a su lado un
  `.ctx-contenido` oculto y lo muestra en el panel. Ya usan el panel: «El
  camino del dinero, en cuatro pasos» (módulo 1), la guía de la lista del
  SAT y «Lo que dicen los documentos oficiales» de cada megaobra.
- **Solo en el auditor:** `index.html` lleva `<body data-pagina="auditor">`
  y `esAuditor()` decide. La Enciclopedia sigue con sus plegables
  `<details>` intactos (verificado: 5 `details.sim-ver` allá, 0 acá).
- **Segunda tanda al panel (sello 20260927n):** `pdPlegable(titulo,
  cuerpo, extra, ico)` sustituye a los nueve `details.pd-det` del motor.
  En el auditor se abren en el panel: las seis tablas de Poderes
  (capítulos de las cámaras, 32 circuitos judiciales, personal de
  Diputados, Senado por capítulo, 32 congresos locales, congresos
  auditados por la ASF), la tabla de la carrera ambiental, «¿Quién recoge
  la basura de tu municipio?» y «De dónde sale cada renglón» del ticket.
  En la Enciclopedia la función devuelve el mismo `<details>` de antes.
  Verificado en 1366 y 375 px: 0 `pd-det` en el auditor, los 9 abren el
  panel sin desbordar, 0 errores; Enciclopedia idéntica byte a byte.
- De paso, dos restos de usted («de su ISR» en Poderes y en la tarjeta
  ambiental) pasan por `tuUd`.
- Quedan como plegables, a propósito: el renglón de cada expediente
  (`exp-fila`), la lista de dependencias de una tarjeta del comparador y
  el diccionario de columnas de Descargas; son detalle de una fila, no
  bloques de contexto.

### Hecho (Auditoría en imágenes: la novena, huachicol fiscal)

Pedido del autor (27-09-2026). Sello 20260927zb. Diapositiva 9 del carrusel,
con su punto, y la misma mecánica que las otras ocho (`SHOWCASE`,
`scHuachicol()`):
- Cuatro contadores que arrancan en cero: IEPS de combustibles esperado en
  2027 ($538,549.2 mdp, oficial), cada 1 % ($5,385.5 mdp, derivado), cada
  día de ese 1 % (derivado) y la cuota por litro de gasolina menor a 91
  octanos ($6.7001, oficial).
- Barras «Lo que está en juego y lo que se ha dicho», cada una con su chip:
  lo oficial es lo que se espera cobrar; la estimación del Observatorio
  Ciudadano de Energía y lo detectado por la ANAM van **pendientes**. No es
  un rastro de gasto sino de impuesto que no entra, y así se dice.
- «Ver gasto» / «Reiniciar a ceros», hallazgo con la cita de la Ley de
  Ingresos 2027, aviso pendiente y fuente.
- Botones: abrir el expediente completo (el panel lateral del huachicol,
  con la barra de regreso a la ficha), la Calculadora Cívica, el glosario y
  la Iniciativa de Ley de Ingresos 2027.
- **Imagen provisional**: ilustración vectorial propia
  (`assets/auditor/img/showcase_huachicol.jpg`), rotulada «Ilustración
  provisional», hasta la etapa de imágenes.
- Defecto encontrado al probar en celular: la barra «Regresar al punto de
  lectura» (capa 99998) tapaba los botones de la ficha (capa 10000). Se
  oculta mientras la ficha está abierta.
- Corregidos 14 saltos LF sueltos que había dejado la sección «Lo que dice
  la ley» del panel del huachicol.

### Hecho (la población del CONAPO pasa a pendiente; restos de «usted»)

Sello 20260927z. Al revisar una nota de Antigravity sobre las cifras que
no se estiman apareció una incongruencia real: la población de 134.4
millones llevaba chip **oficial** aunque su propia nota decía que nunca se
había cotejado en el cuadro del CONAPO. Se volvió a intentar: el portal
del CONAPO devuelve un reto de JavaScript y la base abierta da 404. Pasa a
**pendiente**, como el padrón de 63.2 millones.
- Bajo el reloj de la calculadora, una línea dice con qué divisores se
  reparte «por habitante» y «por contribuyente», cada uno con su chip.
- El ticket ambiental avisa que la población está pendiente de cotejo.
- Barrido de trato de tú en todas las pestañas, leyendo también el texto
  oculto: se corrigieron «su parte» (reloj, tarjetas, ticket ambiental),
  «que paga», «Saque la cuenta», «Su estado de cuenta ecológico», «entre
  su ingreso» (comparador salarial) y «que usted elige» (simulador de las
  Cuentas Ecológicas). Los «su» que quedan son de tercera persona.

**La nota de Antigravity (27-09-2026), cotejada:** no subió nada a la rama;
editó CONTEXT.md solo en su copia local y con saltos CRLF (aquí es LF).
Dos afirmaciones no corresponden al auditor: dice que las obras con estados
financieros son Tren Maya, Dos Bocas y Megafarmacia, y son **Tren Maya, AIFA
y FOBAPROA** (`simulador_megaobras.operacion_oficial`); y habla de un
sobrecosto de +460.1 % del AIFA que no existe en el código actual. El resto
(nueve megaobras sin pérdida, FOBAPROA 1998-2013, padrón y calendario de
publicaciones) coincide con esta lista de pendientes.

### Hecho (huachicol fiscal: el plan de Antigravity, cotejado con la ley)

Antigravity entregó (27-09-2026) una investigación con propuestas para
integrar el huachicol fiscal. Se cotejó contra los textos vigentes de la
Cámara de Diputados (LIEPS, reforma DOF 07-11-2025; LCF, DOF 03-01-2024;
CFF, DOF 09-04-2026). Sello 20260927y. Script:
`herramientas/integrar_huachicol_ley.py` (idempotente, solo el auditor).

**Integrado (oficial, con artículo y documento):**
- `huachicol_fiscal.marco_legal`: cuotas de IEPS por litro 2026 (menor a
  91 octanos $6.7001, 91 o más $5.6579, diésel $7.3634; art. 2o., fr. I,
  inciso D); cuotas del art. 2o.-A para estados (59.1390, 72.1605 y 49.0817
  centavos); reparto (LCF arts. 2o., fr. VII, y 4o.-A, 9/11 a las
  entidades); controles volumétricos (CFF art. 28, fr. I, apartado B);
  contrabando y penas (CFF arts. 102, 103 fr. XXIII y 104).
- Panel lateral del huachicol: nueva sección «Lo que dice la ley».
- Glosario: «Huachicol Fiscal», «Controles Volumétricos», «Contrabando
  (Delito Fiscal)».
- Preguntas frecuentes, casilla 4: «¿Qué es el huachicol fiscal y cómo te
  afecta si no tienes una gasolinera?».

**Rechazado o corregido, y por qué:**

| Propuesta de Antigravity | Dictamen |
|---|---|
| Cuotas de $6.17 a $6.78 por litro | Erróneas. La ley vigente dice $6.7001, $5.6579 y $7.3634 |
| $177,000 mdp al año, $485 mdp diarios, $14,700 mdp al mes | Sin documento oficial. La única estimación con nombre es la del Observatorio Ciudadano de Energía ($123,000 mdp, 2025), ya marcada pendiente |
| $550,000 a $600,000 mdp acumulados 2019–2024; «30 % a 35 % del IEPS» | Sin fuente |
| Importaciones de «aceites» crecieron 1,000 % a 2,000 % | Sin fuente |
| Descuento de $2 a $4 por litro | Sin fuente |
| 350 hospitales, IMSS-Bienestar, Ramo 36 | Equivalencias montadas sobre una cifra sin fuente |
| Expediente forense #7 con monto «observado» | No hay auditoría de la ASF con ese monto; los expedientes son auditorías. Queda pendiente buscar si la ASF auditó a la ANAM por combustibles |
| «Contador de 6 a 7 casos», `assets/js/...` | Antigravity trabaja con una copia vieja: el auditor ya tiene 10 expedientes y sus archivos están en `assets/auditor/`. `assets/js` es de la Enciclopedia congelada |
| «50 aduanas», «Trazabilidad Integral del IEPS», reforma de responsabilidad de agentes aduanales | Sin cotejar; no se publica hasta tenerlo del documento |

### Hecho (el auditor, separado de la Enciclopedia)

Decisión del autor (27-09-2026): la Enciclopedia es un proyecto aparte,
solo de referencia; nada de lo que se haga en el auditor debe tocarla,
cargarla ni revisarla. Sello 20260927x.

- Hasta hoy las dos páginas cargaban los mismos archivos de `assets/`, así
  que cualquier cambio en el motor o en la hoja de estilos le llegaba a la
  Enciclopedia. Para separarlas **sin abrir `enciclopedia.html`**, el
  auditor pasó a tener copias propias en `assets/auditor/` (css, js, datos
  del 69-B del SAT y logotipo). La Enciclopedia sigue con `assets/css`,
  `assets/js` y `assets/data`, que quedan congelados tal como estaban en el
  commit b5f8fa8.
- Las fotografías de `assets/img/` (fondo de ciudad y carrusel) siguen
  compartidas porque no se editan; la hoja del auditor las pide con
  `../../img/`.
- `herramientas/sello.py` y todos los `herramientas/integrar_*`,
  `anclar_*` y `actualizar_69b.py` escriben ya en `assets/auditor/`.
- Las pruebas dejan de abrir la Enciclopedia.

### Hecho (ancho uniforme de los bloques de portada)

Pedido del autor (27-09-2026, con imagen marcada en rojo y morado).
Sello 20260927x.

- «Auditoría en imágenes» y «Fiscalización ciudadana del gasto público»
  eran más angostos que el espacio donde se desglosa un módulo al pulsar
  «Comenzar» (1440 px frente a 1560 px, 20 px de margen frente a 24).
  Ahora toman el mismo ancho y márgenes que `.main-wrapper`. Medido: los
  tres bordes coinciden al píxel en 360, 768, 1366 y 1920 px.
- De paso: «Saca tu estado de cuenta» y «5,417 acciones promovidas» se
  salían de su tarjeta y chocaban entre sí; ahora se parten en dos
  renglones. Sin desbordes en ningún ancho.

### Hecho (sello de emisión en los tickets)

Pedido del autor (27-09-2026): que los tickets lleven el sello de
Auditavisión. Sello 20260927u. Solo en el auditor (`selloEmision()`).

- Sello circular de documento, no marca de agua: doble anillo,
  «AUDITAVISIÓN» arriba y «SISTEMA CÍVICO DE FISCALIZACIÓN» abajo, la
  moneda al centro, «EMITIDO», la fecha y el folio, girado 12 grados.
- **Estado de cuenta cívico:** esquina superior derecha de la cabecera,
  en pantalla y en la imagen para compartir (`selloCanvas()` lo traza
  en el canvas, con el logotipo). Arriba porque abajo la imagen de
  1080×1350 no tiene hueco libre.
- **Ticket ambiental:** esquina inferior derecha, al final, como se sella
  un recibo. Tinta dorada oscura sobre el papel.
- De paso, el estado de cuenta todavía hablaba de usted («a dónde fue su
  ISR», «Le queda», «veces su ingreso», «su constancia»); pasa por
  `tuUd`. Barrido de los dos tickets emitidos: sin usted.

### Hecho (Contrasta una nota: el verificador honesto)

Decisión 1 del autor (27-09-2026). Sello 20260927r. Modo Inspector, entre
el explorador de entes y la lista del SAT (`#vnRaiz`,
`renderVerificadorNotas`, `vnBuscar`, `vnElegir`, `vnContrastar`,
`vnCopiar`).

- Tres pasos: pegar la liga de la nota (opcional; no se abre ni se lee),
  elegir la cifra oficial y escribir lo que afirma la nota con su unidad
  (pesos, miles, millones, miles de millones o billones en el sentido
  español).
- **Catálogo** armado en el navegador con lo que la base ya documenta:
  relojes de deuda (PEF y LIF 2026), totales de la ASF (CP 2024), los
  renglones de finanzas del Paquete 2027 (propuesta 2027 y aprobado
  2026), IEPS de combustibles 2027, Tren Maya, AIFA, IPAB, Tren
  Interurbano y NAIM, Ramos 28 y 33, deuda y monto por aclarar de los 32
  estados, gasto de los entes federales (CP 2025 y PEF 2026) y los
  ingresos 2024 de los municipios con cifra del INEGI. Cada renglón lleva
  su chip y su documento. Lo que no está en el catálogo no se contrasta.
- **Veredicto:** coincide (≤ 1 %), se acerca (≤ 10 %, con las causas
  típicas: otro año, aprobado contra ejercido, pesos reales contra
  nominales), no coincide (> 10 %), error de unidades (mil veces más o
  menos; detecta el «billón» del inglés) y «no se puede contrastar» si
  nuestra cifra está pendiente.
- Copia un contraste en texto plano con la liga, la cifra, el documento
  y el veredicto. La liga se valida (solo http o https) y todo se
  escapa: probado con `javascript:` y con etiquetas en la liga.
- El viejo verificador (retirado en d36e030) inventaba titulares y
  calificaciones sin leer la liga; este no califica medios, compara
  cifras.

### Hecho (huachicol fiscal, en primera plana y sin cifras inventadas)

Pedido del autor (27-09-2026): que el huachicol fiscal esté en portada y en
la calculadora, la deuda y las obras. Sello 20260927p.

- **Colección `huachicol_fiscal`** en la base (la Enciclopedia no la lee),
  con cuatro fuentes y el estado de cada dato:
  - Oficial: la Iniciativa de Ley de Ingresos 2027 (Gaceta núm. 7121,
    Anexo A; SHA-256 8048a912…), pp. CXXI-CXXV: el Gobierno Federal
    reconoce el robo y la sustracción ilegal de combustibles como «una de
    las principales fuentes de evasión del pago del IEPS» y propone la
    fracción XIX del art. 25 (IEPS sobre los litros vendidos de más).
  - Oficial: IEPS de combustibles automotrices estimado para 2027,
    **$538,549.2 mdp** (art. 1o., p. CLX). Derivado: cada 1 % equivale a
    $5,385.5 mdp (regla de tres, no estimación de la evasión).
  - Oficial: el art. 30 (p. CCLXXI) obliga al SAT a publicar estudios de
    evasión a más tardar 35 días después de terminar 2027. Ahí debería
    salir la primera cifra oficial.
  - Oficial desde el sello 20260928h (cotejado en el PDF del Segundo
    Informe, ver abajo): 3,109 casos de clasificación arancelaria
    incorrecta (p. 46), 109.4 millones de litros no declarados con $4,600
    mdp de recaudación asociada, 3,434 sellos, 118 denuncias (p. 260).
  - Pendiente: Observatorio Ciudadano de Energía, $123,000 mdp en 2025
    ($56,000 Pemex + $67,000 impuestos). Organismo civil, no autoridad.
- **Dónde aparece:** cuarto indicador del radar de la portada («sin cifra
  oficial todavía»), cuarta tarjeta del desglose del radar, explicación
  completa en el panel lateral (`radarConcepto('huachicol')`), aviso junto
  al costo de la deuda en la Panorámica y aviso en el reloj de la
  calculadora.
- **Por qué no se suma:** es ingreso que no entra, no gasto. Sumarlo a la
  deuda o a las obras sería mezclar cuentas; se dice en pantalla. Tampoco
  se integró a las fichas de megaobras: no hay relación documentada.

### Hecho (megaobras: la pérdida anual, con estados financieros oficiales)

Sello 20260927o. Solo en el auditor (`megaobrasOficialBase()`, en memoria);
la Enciclopedia congelada conserva sus cifras de antes.

- **Datos nuevos** en `simulador_megaobras.operacion_oficial` (la
  Enciclopedia no lee esa llave):
  - Tren Maya, S.A. de C.V. (H0M), Estado de Actividades 2024, Cuenta
    Pública 2024, Tomo VII: ingresos por servicios $275.8 mdp, gasto total
    $2,837.2 mdp, transferencias federales $13,335.4 mdp, otros ingresos
    $12,890.3 mdp, resultado contable +$23,664.3 mdp. Sin transferencias ni
    otros ingresos: **−$2,561.4 mdp** (derivado). Sus ingresos cubren el
    9.7 % de su gasto (el simulador decía 6.9 %, sin fuente).
  - AIFA, S.A. de C.V. (HZI), mismo documento: ingresos $2,578.2 mdp,
    gasto $2,288.1 mdp, transferencias $1,510.2 mdp. Sin transferencias,
    **+$290.2 mdp**: no tuvo pérdida de operación en 2024 (el simulador le
    ponía $1,460 mdp al año).
  - IPAB: bonos por **$1,086,952.8 mdp** al 31-12-2025 (corto plazo
    $208,920.9 + largo $878,031.9), estados financieros del IPAB, p. 3
    (SHA-256 e577ee96…). Ramo 34 ejercido en 2024: **$62,489.4 mdp**
    (oficial, Cuenta Pública); suma 2014-2025: $431,289.2 mdp (derivado).
- **Pérdida anual documentada: $65,050.8 mdp** (derivado), $2,062.75 por
  segundo, sobre 3 de las 12 obras. Antes: $80,200.1 mdp sin fuente. Las
  otras nueve entran con cero y la marca `perdida_pendiente`: dicen
  «pendiente» en la ficha, la mesa 2, la lista comparativa y el radar, y
  no inflan la suma. El reloj de la calculadora y el radar de la portada
  toman la cifra nueva.
- **Textos retirados del auditor por no tener fuente:** desgloses de costos
  de las doce obras (sustituidos por los capítulos del estado de
  actividades donde lo hay), proyecciones («120 años para el punto de
  equilibrio», «300 recetas al día», «hasta 2070», «$620 mdd», «700
  hectáreas»), hallazgos atribuidos a la ASF en siete obras sin informe
  cotejado («60 % de equipos inservibles», «sobreprecio del 111 %») y tres
  etiquetas de estatus con juicio sin documento.

### Hecho (el auditor habla de tú)

- **`index.html`**: instrucciones, descripciones, placeholders y títulos
  de bloque pasan a tú («Pulsa», «Elige», «Escribe», «Tu ingreso», «Tú
  contra ellos»). Las citas de ley no se tocan.
- **Motor**: `tuUd(ud, tu)` con `esAuditor()`. 142 literales envueltos
  (calculadora, ticket, comparador, inspector, megaobras, foro, avisos);
  la Enciclopedia sigue mostrando la versión de usted (verificado en el
  navegador: 0 «usted» en la calculadora del auditor, 11 en la de la
  Enciclopedia, igual que antes).
- **Base de datos**: seis textos de la calculadora y del comparador se
  ajustan en memoria con `tuteoBase()` al arrancar, solo en el auditor; el
  archivo `audit-database.js` no cambia.
- Barrido de todas las pestañas del auditor con sus plegables abiertos:
  sin imperativos ni posesivos de usted a la vista.
- De paso: el texto del foro que decía «los hilos que vea publicados son
  ejemplos sembrados» era falso desde que se retiraron los sembrados; ahora
  dice que son los que tú publicaste en tu navegador.
- AGENTS.md §6 recoge la regla.

### Hecho (revisión de la versión 20260927ze de Antigravity, sello 20260928a)

Antigravity subió el commit 425651f (sellos zd y ze) con cinco vistas en el
simulador «Un año de cuentas en veinte segundos» del módulo 5. Se revisó
contra la regla editorial y se corrigió con visto bueno del autor:

| Lo que traía | Qué pasaba | Qué quedó |
|---|---|---|
| 6 cifras de «Obras por sector 2024–2026» ($341,013, $190,847, $114,483, $49,550, $43,060, $32,460 mdp) | No están en ningún documento del repositorio; chip `derivado` sin operación | Vista retirada hasta tener datos oficiales |
| Poder Ejecutivo $10,033,149 mdp, 98.4 % | Sin fuente; ni siquiera cuadra con el PEF menos los otros dos Poderes | «Todo lo demás del Presupuesto» = PEF 2026 $10,193,683.7 − Judicial $70,005.6 − Legislativo $17,529.1 = $10,106,149.0 mdp, `derivado` con la operación a la vista; Judicial y Legislativo, `oficial` (avance del gasto 2T 2026, lo aprobado) |
| Huachicol $600,000 mdp como flujo anual en la carrera y en los remates («se fugaron…», «supera N veces…») | Lo dijo la Procuradora Fiscal el 2-10-2025 (La Jornada, 3-10-2025), pero la Presidenta lo desmintió el 10-10-2025 (El Financiero) y no es anual. Fuente original: portada de la Gaceta, sin documento | Sale de la carrera; queda en el expediente del huachicol como `pendiente`, con la declaración, las querellas por $16,000 mdp y el desmentido, cada uno con su liga. Se quitó «102 denuncias», que no se pudo verificar |
| `pff` puesta primero en `huachicol_fiscal.estimaciones` | La diapositiva 9 lee la estimación del OCE en ese lugar y tronaba; el expediente pintaba «$NaN mdp» | La diapositiva busca la del OCE por su fuente; el expediente pinta cada tipo de estimación con su formato |
| `reconocimiento.practicas` reescrita (pedimentos clonados, salto arancelario…) | Se presentaba como cita de la Ley de Ingresos 2027 y esas palabras no están ahí | Texto textual restaurado; también el «Qué es» del expediente |
| Valores de respaldo escritos a mano en el motor (daño $1,387,414, protección $196,419) | No coinciden con la base (CEEM: $1,382,214 y $232,882) | Retirados: el motor lee solo la base |
| «Ilustración editorial» en la diapositiva 9 | La imagen es provisional | «Ilustración provisional» |

Se conservan: la botonera de vistas (ahora «Deuda y ambiente» y «Los Poderes
de la Unión»), el segundo botón del expediente hacia el circuito del dinero y
el texto del reparto del IEPS. Se quitaron los colores `--am-c5..8`, que ya no
se usan. Verificado en 1366 y 390 px: ambas vistas, expediente sin NaN,
diapositiva 9 con el OCE, sin desborde, 14 pestañas sin errores.

### Hecho (trivia de los presidentes: desglose de cada cifra; barrido de clics, sello 20260928b)

- **Falla reportada por el autor:** en la trivia (módulo 2, bloque 3, 3.2)
  no se podía desglosar la información de la última tabla. Causa: la
  operación, la nota del asterisco y el motivo de cada «pendiente» solo
  vivían en el `title` de la celda, que se lee al pasar el cursor; en un
  teléfono no hay cursor y en computadora no había nada que pulsar. Además,
  a 390 px la tabla mostraba dos columnas sin avisar que se desliza.
- **Corrección:** las 42 celdas de las dos tablas comparativas son botones
  (`data-pe-ref`, teclado con Enter o espacio) que abren `peDesglose` en el
  panel lateral: cifra y chip, «Cómo se calculó», la tabla por Cuenta
  Pública cuando existe `porCuenta` (con su suma), la resta de asegurados
  del IMSS, la nota, el motivo del pendiente y la fuente con liga. Aviso
  «Toca cualquier cifra… desliza la tabla» sobre cada tabla.
- **Barrido de funcionalidad:** 372 botones pulsados en las 14 secciones del
  auditor, 0 errores; ningún `onclick` apunta a una función no exportada.
  Las preguntas frecuentes se muestran abiertas por diseño (no son
  plegables).

### Hecho (Birmex como contexto de la Megafarmacia, sello 20260928c)

- Cuenta Pública 2024, Tomo VII, Birmex (clave NEF, archivo
  `12NEF.02.01.xls`, SHA-256 085ef8bd…3350): ingresos de la gestión
  $7,114.8 mdp, otros ingresos $111.8, gasto total $7,943.9, resultado del
  ejercicio **−$717.3 mdp**; no recibió transferencias.
- Es el resultado de **toda la empresa** (compra, produce y distribuye
  vacunas y medicamentos), no de la Megafarmacia sola, y la Cuenta Pública
  no la separa. Por eso la pérdida de la Megafarmacia **sigue pendiente**
  y no entra en la suma (sigue en $65,050.8 mdp, 3 obras documentadas). El
  dato aparece como contexto en la ficha («Lo más cercano en un documento
  oficial…») y en el catálogo del verificador de notas
  (`operacion_oficial.contexto_entidad.megafarmacia`, fuente `ef_nef`).
- Mismo criterio para Dos Bocas: el estado de Pemex Transformación
  Industrial (Tomo VIII) abarca todas las refinerías; no sirve para la obra
  sola. Falta el informe de la ASF o un estado de la refinería.
- Intentado sin éxito: el boletín de la Cámara sobre la ratificación de la
  Procuradora Fiscal (el portal de Comunicación Social responde 503 y su
  certificado no valida desde aquí). Queda en la lista del autor (B1).

### Hecho (informes de la ASF de cinco megaobras y series de Salinas, sello 20260928d)

Documentos guardados con su huella en `investigaciones/asf-historico/` y
`investigaciones/series-historicas/` (índice en el `README.md` de cada una).
Scripts: `herramientas/integrar_megaobras_asf_historico.py` y
`herramientas/integrar_series_historicas.py` (comprueban la huella antes de
escribir; solo tocan la copia del auditor).

| Obra | Antes (sin fuente) | Ahora | Documento |
|---|---|---|---|
| Estela de Luz | $398 → $1,304 mdp, +227.6 % | $393.5 → $1,304.9 mdp, +192.0 % (oficial) | ASF, informe especial 2009-2011, pp. 3 y 13 |
| Refinería Bicentenario (Tula) | $12,400 mdp | autorizado $3,714.0, ejercido $1,127.6 mdp (derivado, suma de dos claves) | ASF, CP 2014, aud. 315, pp. 10-11 |
| Agronitrogenados y Fertinal | $7,500 → $33,500 mdp | en pesos sigue pendiente; en dólares: 475 → 760 millones (+60.0 %), Fertinal 635 millones | ASF, CP 2015 aud. 498 (p. 27) y CP 2016 aud. 468 (pp. 2 y 31) |
| Enciclomedia | $18,000 → $40,000 mdp | autorizado 2005-2010: $21,398.3 mdp (oficial); lo pagado sigue pendiente | ASF, CP 2005, tomo VI vol. 2, aud. 584, p. 264 |
| FARAC | $60,000 → $162,000 mdp | costo sigue pendiente; deuda en bonos $27,491.2 (1997) → $225,500.2 mdp (2017) | ASF, CP 2017, aud. 96, pp. 5-6 |

- Se retiraron cuatro «hallazgos de la ASF» que no estaban en ningún
  informe (sobreprecio del 111 % en el acero, hectáreas ejidales de Tula,
  60 % de equipos inservibles, aforos sobreestimados del FARAC). Cada obra
  muestra ahora el hallazgo del informe y, en el panel «Lo que dicen los
  documentos oficiales», una tabla dato · cifra · página con su chip.
- La inversión total de las 12 obras pasa de $3,928,529.2 a $3,917,257.7
  mdp y el sobrecosto del conjunto de 247.2 % a 247.8 % (se siguen sumando,
  no se escriben). La pérdida anual documentada no cambia ($65,050.8 mdp).
- **Evaluación de los presidentes, Salinas:** PIB +3.91 % anual (+25.87 %
  acumulado), con el cuadro 8.6 de *Estadísticas históricas de México
  2014* (precios de 1993, valores básicos; esa serie da 3.42 % a Zedillo
  contra 3.48 % con la de 2018). Deuda al cierre de 1994: 36.9 % del PIB,
  Informe Anual 1994 de Banxico, p. 80; es la deuda neta «económica amplia»,
  no el SHRFSP, e incluye la devaluación de diciembre (promedio del año
  24.8 %). Las dos salvedades van en la nota de cada celda, en el subtítulo
  de la métrica y en las advertencias. La lección de la trivia del PIB se
  corrigió: el promedio más alto ahora es el de Salinas.
- **No se encontró (sigue pendiente):** el Búnker de la SSP (ningún informe
  de la ASF localizado con su costo), el costo total del AIFA (la ASF CP
  2022, aud. 342, solo da lo erogado ese año: $18,141.2 mdp de obra y
  predios), el registro de 2013 del Tren Interurbano, y los asegurados del
  IMSS de 1988 y 1994 (Banxico solo da variaciones; el INEGI solo
  derechohabientes, que es otro concepto; la serie de la STPS pide
  verificación de navegador).
- Verificado: 14 paneles sin errores, 42 celdas de la trivia abren su
  desglose a 1366 y 390 px, barrido de clics sin errores, las cinco tablas
  de la ASF se pintan en el panel lateral.

### Hecho (simulador «Un año de cuentas en veinte segundos» con cinco pestañas, sello 20260928e)

El autor señaló que el simulador del módulo 5 estaba incompleto: la
versión de Antigravity (425651f) tenía cinco pestañas y la revisión del
27-09 (5b881a3) la dejó en dos por falta de fuentes. Se restauran las
cinco con cifras rastreables:

| Pestaña | Barras | Fuente |
|---|---|---|
| 🌿 Deuda y ambiente | intereses, daño ambiental, gasto en protección, Ramo 16 | igual que antes |
| 🏛️ Los Poderes de la Unión | Ejecutivo $10,050,444.1 · autónomos $55,704.9 · Judicial $70,005.6 · Legislativo $17,529.1 mdp | CSV del PEF 2026; el Ejecutivo es el gasto neto del decreto menos los otros tres (derivado; Antigravity tenía $10,033,149 sin cálculo) |
| 🏗️ Obra pública por sector | Pemex y CFE $279,605.0 · trenes, carreteras y puertos $199,674.5 · Ramo 33 $137,074.9 · Conagua $21,761.9 · IMSS e ISSSTE $12,941.0 · resto $1,904.1 (total $652,961.4 mdp) | CSV del PEF 2026, «gasto de obra pública» (tipo de gasto 3); sustituye los seis promedios 2024-2026 sin fuente |
| ⛽ Huachicol fiscal | la cifra mencionada ($600,000 mdp, **pendiente**, barra gris rayada) contra obra, Poderes y Ramo 16; recaudación de $4,600 mdp (oficial) | Segundo Informe 2026, p. 260 (PDF 284), cotejado en la entrega del autor; aclaración de Presidencia del 9-10-2025 |
| 🌐 Todo junto | 15 barras | las anteriores |

- Datos en `DB.ritmo_vistas`, escritos por
  `herramientas/integrar_ritmo_vistas.py` (comprueba la huella del CSV,
  6dec5f3a…). El color sigue al grupo (deuda, gasto público, ambiente y
  huachicol, Poderes); lo pendiente es gris rayado y lleva su chip.
- Cada pestaña tiene su cierre del año y su nota de método. La del
  huachicol dice que la barra rayada no entra en ninguna cuenta.
- **Corrección:** la aclaración de la Presidenta sobre los $600,000 mdp fue
  el **9** de octubre de 2025 en su conferencia (versión estenográfica
  oficial), no el 10; la nota de El Financiero del 10 la reportó. La
  estimación `pff` ahora cita la estenográfica y la frase textual.
- Verificado: las cinco pestañas a 1366 y 390 px, sin NaN ni desborde; 14
  paneles y barrido de clics sin errores; Enciclopedia intacta.

### Hecho (módulo 2: la «Simulación en vivo» corre con lo que cada obra nos cuesta, sello 20260928f)

El autor pidió que el simulador en vivo de Megaobras (2.2) dejara de estar
lleno de pendientes y operara con las fuentes que ya hay, como
**interpretación propia**, declarada, de documentos oficiales. Antes solo
corrían 2 de 12 fichas; ahora corren 7 y las otras 5 dicen qué lo impide.

- **Qué mide cada ficha («Lo que nos cuesta», chip derivado):** lo que el
  erario le pone este año (PEF 2026, datos abiertos) más lo que sigue
  costando el dinero ya perdido en ella (sobrecosto, cancelación o gasto
  sin obra documentados por la ASF o Hacienda) a la **tasa implícita de la
  deuda**: costo financiero del PEF 2026 ($1,572,073.3 mdp) ÷ SHRFSP
  estimado 2026 de los CGPE 2027 ($20,062,321.6 mdp) = **7.84 %**.
  Los intereses van marcados como **estimación propia**, con su supuesto
  (que ese dinero se financió con deuda al costo promedio).

| Obra | Al año (mdp) | Componentes |
|---|---:|---|
| Tren Maya | 56,616.8 | PEF 2026 $30,744.1 + 7.84 % de $330,008.6 de sobrecosto |
| FOBAPROA/IPAB | 35,553.4 | Ramo 34 del PEF 2026 (sin intereses aparte); contexto: pasivos netos del IPAB $1,023,571 al 31-12-2025 |
| FARAC | 21,998.1 | $351,969.6 que la ASF estimó por pagar 2018-2033 ÷ 16 años (estimación propia: reparto parejo) |
| Tren Interurbano | 13,472.0 | PEF 2026 clave 13093110008 $7,408.0 + 7.84 % de $77,347.5 de crecimiento del costo reconocido en cartera |
| AIFA/Texcoco | 9,629.6 | PEF 2026 $744.7 + 7.84 % de $113,327.7 de la cancelación del NAIM (ASF) |
| Refinería de Tula | 88.4 | 7.84 % de $1,127.6 gastados sin refinería (ASF) |
| Estela de Luz | 71.5 | 7.84 % de $911.4 sobre el contrato (ASF) |

  Total: **$137,429.8 mdp al año, unos $4,358 por segundo**, con contador
  conjunto arriba de las fichas y tabla de método en el panel lateral.
- **No corren, con la limitación concreta** (categorías: no localizado, sin
  desglose por proyecto, acceso fallido, salvedad documentada): Dos Bocas
  (Pemex no separa la refinería; TRI se extinguió el 19-03-2025),
  Megafarmacia (**dictamen de Birmex 2024 con denegación de opinión**; el
  auditor no fue invitado al inventario del CEFEDIS y desconoce cómo se
  controla en la contabilidad, párrafos III a V), Agronitrogenados (solo
  en dólares), Enciclomedia y Búnker (no localizado).
- «Pérdida de operación» pasa a llamarse **déficit antes de transferencias
  y otros ingresos** en los textos del auditor, con la aclaración de que en
  un servicio público no prueba por sí solo desperdicio.
- Datos en `DB.costo_vivo_megaobras`, escritos por
  `herramientas/integrar_costo_vivo_megaobras.py` (comprueba la huella del
  CSV del PEF 2026). El motor calcula los intereses con la tasa.
- Verificado a 1366 y 390 px sin desborde; 14 paneles, barrido de clics y
  trivia sin errores; Enciclopedia intacta.

### Hecho (Dos Bocas y Megafarmacia entran a la simulación en vivo, sello 20260928g)

Del reporte de fuentes que Antigravity le entregó al autor se cotejó lo
que tiene documento; lo demás quedó anotado en
`investigaciones/costo-vivo/README.md` y no se usa.

- **Dos Bocas** corre con **$42,696.7 mdp al año**: lo que Pemex TRI le
  aportó en 2024 a PTI Infraestructura de Desarrollo, la filial de la
  refinería (estados financieros de Pemex TRI 2024, nota 12, p. 47). Es
  estimación propia (supone que 2026 sigue el ritmo de 2024, porque desde
  el 19-03-2025 no hay estados separados). Contexto en el panel: pérdida
  neta de la filial en 2024, $1,473.7 mdp; capital acumulado, $363,619.9
  mdp.
- **Megafarmacia (CEFEDIS, clave 2312NEF0001, de las notas de Birmex al
  3T 2024)**: la cartera de Hacienda da $3,614.6 mdp de inversión al 4T 2023
  y $3,948.6 al 4T 2025 (78 % de avance, «en proceso de modificación»);
  sustituyen los $1,400 / $3,500 sin fuente del simulador (oficial; +9.2 %
  derivado). Corre con $363.9 mdp al año: operación y mantenimiento
  previstos ($10,806.4 mdp ÷ 32 años de horizonte, estimación propia) más
  intereses del crecimiento. No aparece en los cortes 4T 2024 ni 2T 2026.
- Ahora corren **9 de 12**: **$180.5 mil millones al año, $5,723 por
  segundo**. No corren Agronitrogenados, Enciclomedia y Búnker.
- Totales del simulador recalculados: inversión real $3,917,706.3 mdp,
  presupuestada $1,128,508.8, sobrecosto del conjunto 247.2 %.
- Scripts: `herramientas/integrar_cefedis.py` (comprueba huellas de cuatro
  cortes de cartera) y `integrar_costo_vivo_megaobras.py`.

### Hecho (población, padrón y huachicol en aduanas, cotejados en sus originales, sello 20260928h)

Con los originales de `investigaciones/entregas/` (huellas comprobadas por
`herramientas/integrar_poblacion_padron_anam.py`, que solo toca
`assets/auditor/js/audit-database.js`):

- **Población:** 134.4 millones pasa de `pendiente` a **derivado**:
  134,407,258 personas, suma de las 32 entidades, 110 edades y ambos sexos
  del año 2026 en el CSV de datos abiertos del CONAPO (no trae fila
  nacional). Se reproduce con `investigaciones/entregas/derivar_poblacion.py`.
- **Padrón:** los 63.2 millones sin fuente se sustituyen por **88.1
  millones, oficial**: 88,085,311 contribuyentes con RFC activo en abril de
  2026 (SAT, padrón por situación del RFC; 52,932,127 son asalariados).
  Cambia en la calculadora (`parametros.padron`) y en el catálogo `macro`
  (mesa 3 de la 2.2). La opción del reloj dice ahora «inscritos en el SAT»,
  no «que tributan»: estar activo no es haber pagado. Las cifras por
  contribuyente bajan en consecuencia.
- **Huachicol en aduanas:** pasa a **oficial**, cotejado en el PDF del
  Segundo Informe (sha cc95e5…). Conceptos corregidos: los 3,109 son casos
  de clasificación arancelaria incorrecta, no «posible contrabando» ni
  decomisos (p. 46, 70 del PDF); los $4,600 mdp son **recaudación
  asociada**, no «impuestos que se intentó evadir» (p. 260, 284 del PDF);
  sellos y denuncias los atribuye el Informe a «las autoridades
  competentes». El panel lateral lo muestra en «Lo que informa el Gobierno»,
  separado de lo no verificado; el campo `evasion_mdp` se llama ahora
  `recaudacion_mdp`.

### Hecho (población de las 32 entidades, CONAPO 2026, sello 20260928i)

- `herramientas/integrar_poblacion_entidades.py` lee
  `investigaciones/entregas/CONAPO_Poblacion2026_derivada.csv` (huella
  comprobada) y pone en cada entidad `pob` (millones, dos decimales) y
  `pobPersonas` (exacta). Recalcula `pc` = Ramos 28 y 33 × 1e6 ÷ población.
  `fiscalEntidades.campos.pob` y `.pc` pasan de `pendiente` a **derivado**.
- Las cifras viejas (≈ censo 2020) subestimaban la población, así que lo
  que cada entidad recibe por habitante baja: rango $15,805 (Puebla) a
  $23,137 (Guerrero). El inspector estatal ya no dice «población pendiente
  de fuente»: muestra las personas exactas con su chip.
- Promedio nacional de la portada: $2,810,800 mdp ÷ 134,407,258 = $20,913
  (antes $20,914, dividido entre 134.4 redondeado).

### Hecho (Agronitrogenados corre en la simulación en vivo, sello 20260928j)

Con la auditoría 492-DE de la ASF a Pemex Fertilizantes (CP 2017, en
`investigaciones/entregas/`, sha d1f61d…), que da montos en pesos:

- Sin flujo anual: el PEF 2026 no tiene renglón de la planta (el programa
  «Fertilizantes para el Bienestar» es de Agricultura, no de ProAgro).
- Corre con los intereses de lo que Pemex **reconoció como perdido**
  (estimación propia, tasa implícita 7.84 %): deterioro por baja de las
  tres plantas ociosas de ProAgro, $4,206.0 mdp (pp. 37 y 40; la p. 44 dice
  $4,206.7) → $329.8 mdp al año; deterioro del crédito mercantil de
  Fertinal, $4,007.0 mdp (p. 37) → $314.1 mdp al año. Total **$643.9 mdp
  al año, $20.42 por segundo**.
- En el panel, como contexto y sin sumarse: compra de $5,427.2 mdp (2013),
  inversión aprobada de $14,998.9 mdp, $8,271.1 mdp erogados en
  rehabilitar la urea hasta 2017, deuda con Nafin de $7,696.8 mdp.
  Límite «No localizado»: resultados de ProAgro y Fertinal después de 2017.
- Ahora corren **10 de 12**: **$181.1 mil millones al año, $5,744 por
  segundo**. No corren Enciclomedia y el Búnker.
- Sin tocar todavía: los campos de inversión de la ficha ($7,500 y $33,500
  mdp, `pendiente`) siguen sin fuente; la 492-DE los resolvería solo para
  Agronitrogenados, no para Fertinal.

### Hecho (Fertinal se separa de Agronitrogenados: 13 obras, sello 20260928k)

Decisión del autor. `herramientas/separar_fertinal.py` (comprueba las huellas
de las auditorías 492-DE CP 2017 y 468-DE CP 2016) divide la ficha:

- **Plantas Chatarra Agronitrogenados**, en pesos: presupuestada $7,894.2 mdp
  (costo total estimado al aprobar el proyecto, 19-07-2013, p. 4, oficial);
  real $13,698.3 mdp = compra $5,427.2 (p. 4) + rehabilitación erogada
  09-2014 a 12-2017 $8,271.1 (pp. 43-44), derivado; sobrecosto 73.5 %,
  derivado. Sustituyen los $7,500 / $33,500 sin fuente. Corre en vivo con
  $329.8 mdp al año (intereses de la baja de tres plantas, $4,206.0 mdp).
- **Compra de Grupo Fertinal**, ficha nueva (EPN, energía): $13,121.6 mdp,
  los 635 millones de dólares de créditos de la compra (CP 2016, p. 11),
  oficial; sin sobrecosto de compra documentado (0 %, derivado). Corre en
  vivo con $314.1 mdp al año (intereses del deterioro del crédito
  mercantil, $4,007.0 mdp, CP 2017, p. 37). Contexto: pérdida integral de
  2016 de 565.7 millones de dólares ($11,690.6 mdp, p. 31) y «no es un
  negocio rentable» (p. 38), sin sumarse.
- Totales: inversión real $3,911,026.2 mdp, presupuestada $1,142,024.6,
  sobrecosto del conjunto 242.5 %. El sobrecosto acumulado de la
  calculadora ya no se lee del número fijo $3,069,647 (estaba viejo): el
  motor lo toma de los totales del simulador.
- Textos: 12 → 13 obras (tarjeta de portada, radar, bloque 1, nota del
  conteo, que ahora explica 13 expedientes y 14 en el reparto por mandato
  por el FARAC). Donde se pudo, el número sale de `sim.obras.length`.
- Simulación en vivo: corren **11 de 13**, $181.1 mil millones al año,
  $5,744 por segundo (el total no cambia: solo se repartió).

### Hecho (Enciclomedia y el Búnker corren en vivo: 13 de 13, sello 20260928l)

`herramientas/integrar_enciclomedia_bunker.py` comprueba las huellas de siete
informes de la ASF, guardados en `investigaciones/asf-historico/`.

- **Enciclomedia, lo pagado:** $32,315.7 mdp de 2001 a 2011 (derivado).
  Suma lo que la Cuenta Pública reportó como ejercido según la ASF:
  - 2001-2006: $6,417.8 (CP 2006, aud. 99, p. 586).
  - 2007: $7,145.8 (aud. 438, p. 170).
  - 2008: $5,817.7 (aud. 274, p. 589).
  - 2009: $3,548.4 (aud. 338, p. 1).
  - 2010: $4,665.5 (aud. 923, p. 1).
  - 2011: $4,720.6 (aud. 388, p. 1).

  En 2007 y 2008 solo cuenta la partida 3414, que concentra el 99.0 % del
  programa, así que la suma es un piso. Sobrecosto contra los $21,398.3 mdp
  autorizados para 2005-2010: 51.0 % (derivado). La definición aclara que
  lo ejercido incluye piezas que esa autorización no cubría. Sustituye los
  $40,000 mdp sin fuente.
- **Enciclomedia, costo en vivo:** $855.9 mdp al año. Son los intereses
  sobre lo pagado por encima de lo autorizado ($10,917.4 mdp). Contexto:
  dictamen negativo de 2009 y donación de los equipos en 2011.
- **Búnker, lo que documenta la ASF:** la ASF auditó en la CP 2009
  (aud. 1053) el contrato de obra del «Edificio de Plataforma México».
  - Adjudicación directa a TRADECO por $347.4 mdp con IVA, reducida a
    $289.1 mdp.
  - Erogados $206.0 mdp más IVA a agosto de 2010.
  - $23.4 mdp por recuperar.

  Es un contrato, no el costo del edificio: presupuestada y real siguen
  pendientes. Los $1,200 y $3,346 no tienen documento y así lo dice la
  definición. Que ese edificio sea el «búnker» se declara como lectura
  propia.
- **Búnker, costo en vivo:** $480.1 mdp al año, suma de dos renglones:
  - el programa P048 «Plataforma México» del PEF 2026, $478.3 mdp en tres
    unidades de la SSPC (estimación propia: el PEF no separa el inmueble);
  - los intereses sobre los $23.4 mdp observados.
- **Totales:** inversión real $3,903,341.9 mdp y sobrecosto del conjunto
  241.8 %. En vivo corren **13 de 13**: $182.5 mil millones al año, $5,786
  por segundo. El método del cajón menciona los pagos observados.
- **Sin corregir:** Enciclomedia sigue en el sector «Salud, Logística y
  Medicamentos», porque no existe uno de educación. Moverla es decisión del
  autor.

### Hecho (Diputados locales: 4 de 32 congresos con documento de 2026, sello 20260928m)

`herramientas/integrar_diputados_locales.py` llena la tarjeta «Diputada o
diputado local» del comparador salarial, que estaba pendiente. Comprueba la
huella de cada documento (`investigaciones/congresos-locales/`).

| Congreso | Neto al mes | Bruto al mes | Documento |
|---|---|---|---|
| Guanajuato | $144,097.16 (oficial) | $224,437.56 (oficial) | Tabulador 2026, nivel 20 |
| Jalisco | $69,906.28 (derivado) | $109,069.76 (derivado) | Nómina de la 1.ª quincena de septiembre de 2026 (38 diputados) |
| Querétaro | $56,885.72 (oficial) | $89,774.00 (oficial) | Art. 66 fr. VII, 2.º trimestre de 2026 (25 diputados) |
| Tabasco | $50,000.00 (oficial) | $68,577.90 (oficial) | Periódico Oficial núm. 8590-C, 8-11-2025, p. 3 |

- Jalisco sale de su nómina, no de un tabulador:
  - bruto = 2 × $54,534.88;
  - neto = 2 × (quincena − ISR − pensiones).
- La tarjeta muestra el rango neto ($50,000 a $144,097) y una lista
  «Congreso por congreso», cada fila con su chip, sus conceptos y su
  fuente. No se promedia ni se extrapola.
- Neto anual parcial: 12 × el máximo (Guanajuato), sin aguinaldo (derivado).
- Motor: `cmpTarjeta` pinta `c.entidades` cuando existe.
- **Faltan 28 congresos:**
  - Michoacán: su tabulador está en `congresomich.site`, dominio que el
    entorno no alcanza.
  - Solo tienen años anteriores en su portal: Ciudad de México (2019),
    Nuevo León (2021), Sinaloa (2016), Chiapas (2018) y Tamaulipas
    (2.º trimestre de 2025).
  - Los demás no se localizaron todavía.
  - La PNT no es accesible desde el entorno.

### Hecho (Diputados locales: 12 de 32 congresos, sello 20260928n)

Ocho congresos más, cada uno con su documento de 2026 guardado en
`investigaciones/congresos-locales/` y su huella comprobada por
`herramientas/integrar_diputados_locales.py`. Dos vías funcionaron: el
formato de remuneraciones en el portal propio del congreso y el presupuesto
estatal 2026, que por ley trae el analítico de plazas o el tabulador de cada
poder.

| Congreso | Neto al mes | Bruto al mes | Documento |
|---|---|---|---|
| Sinaloa | pendiente | $140,941.34 (oficial) | Manual de remuneraciones 2026-2027, Anexo 4, p. 23 |
| Tlaxcala | pendiente | $111,243 a $135,923 (derivado) | Presupuesto 2026, Anexo 42, p. 469 |
| Nayarit | pendiente | $111,057.64 (derivado) | Formato art. 33 fr. VIII, 1.er trim. 2026 |
| Colima | $67,113.68 (derivado) | $92,476.60 (derivado) | P.O. 21-02-2026, supl. 2, pp. 9-10 (quincenal × 2) |
| Campeche | pendiente | $61,952.00 (oficial) | Presupuesto 2026, Anexo 19 |
| Oaxaca | $42,000.00 (oficial) | $51,448.51 (oficial) | Formato LGTA70FVIIIA 2026, 1.er y 2.º trim. |
| Yucatán | pendiente | $50,880.00 (oficial) | D.O. 29-12-2025, tomo de autónomos, p. 187 |
| Guerrero | $40,188.00 (oficial) | $50,060.00 (oficial) | Formato 08A-VIIIA, 1.er trim. 2026 |

- **Tlaxcala:** el decreto no dice la periodicidad. Es mensual porque la
  partida 1111 Dietas ($33,669,060) ÷ 25 ÷ 12 = $112,230 cae dentro del rango.
- **Nayarit:** el bruto suma sueldo ($32,651) y dieta ($78,406.64). El neto
  de la dieta no se reporta, así que el neto queda pendiente.
- **Motor:** una fila sin neto dice «neto no publicado» con chip
  `pendiente`, y `brutoHasta` pinta el rango de Tlaxcala.
- **Tarjeta:**
  - Rango neto $40,188 (Guerrero) a $144,097 (Guanajuato), entre los 7 que
    publican el neto.
  - En bruto, los 12 van de $50,060 a $224,437.56.
  - La lista se ordena por bruto.
- **Revisados y no integrados:**
  - Durango: su presupuesto 2026 da un rango de $78,890.56 a $113,285, sin
    periodicidad y sin partida de dietas para cruzarlo.
  - Baja California Sur: 4.º trim. 2025. Zacatecas: 3.er trim. 2025.
  - Quintana Roo: su portal llega a 2018.
  - Chihuahua: los tomos del presupuesto 2026 no traen el tabulador del
    Congreso.
  - Aguascalientes: su portal remite a la PNT, y su presupuesto 2026 no
    trae el tabulador del Congreso.
  - Veracruz y Coahuila: el portal no respondió (conexión reiniciada o
    agotada).
  - Hidalgo: certificado incompleto; su intermediario está en un dominio
    bloqueado.
  - Campeche: su portal de transparencia enlaza por tinyurl, dominio
    bloqueado; se usó el presupuesto.
- **Truco de descarga:** Guerrero devuelve 403 sin un User-Agent de navegador
  completo y el `Referer` de su página.


### Hecho (Olmeca, CEFEDIS y Búnker con lo que sí documentan, sello 20260928o)

`herramientas/integrar_olmeca_cefedis_bunker.py` comprueba seis huellas y
solo toca `assets/auditor/js/audit-database.js`. El motor ganó un desglose
«de lo más cercano con documento» para obras sin estados propios, con su
título dicho en la ficha (`contexto_entidad[id].desglose`, `.texto`, `.extra`).

- **Olmeca, costo real anclado:** $357,887.3 mdp de obra en proceso que la
  filial PTI Infraestructura de Desarrollo registró al 31-12-2024 para la
  refinería (ASF, CP 2024, aud. 247, p. 8). Pasa a `oficial`; el
  presupuesto original ($160,000) y el sobrecosto siguen pendientes.
  Totales: inversión real $3,911,229.2 mdp, sobrecosto del conjunto 242.5 %.
- **Olmeca, desglose:** lo que pagó la filial en 2024, $41,998.3 mdp sin IVA
  por 192 contratos ($15.6 de servicios administrativos); aportaciones de
  Pemex $42,696.7; IVA devuelto $14,463.2. Operación: primer tren en febrero
  de 2025 y segundo en mayo, pico de 313 mil barriles diarios (Pemex, CP
  2025, pp. 54-55); 188 mil de promedio de septiembre de 2025 a junio de
  2026 y 263 mil en diciembre, 77 % de su capacidad (Segundo Informe, p.
  378). Pemex consolida a la filial sin estados propios desde 2025 (p. 35),
  así que costo de operación y resultado siguen pendientes. La filial
  también lleva la reconfiguración de Salina Cruz: sus resultados no son
  solo de Olmeca, y así lo dice la ficha.
- **CEFEDIS, desglose:** estructura del registro 2312NEF0001 en la cartera
  (4T 2025): inversión $3,948.6, operación y mantenimiento en 32 años
  $10,806.4, otros $992.8, total $17,635.8 mdp; la cartera no detalla
  $1,888.0 (resta de Auditavisión). Ejercido 2025 bajo la clave: $0. Toda
  la inversión física de Birmex en 2025: $10.1 mdp (Segundo Informe,
  anexo). El dictamen 2025 de Birmex (20-03-2026, escaneo leído página por
  página) **vuelve a denegar opinión**: sin balanzas confiables, no validó
  inventarios, almacenes ni activo fijo.
- **Búnker:** la ASF (CP 2008, aud. 957, pp. 88-90) estimó $432.7 mdp para
  construir y equipar las instalaciones de todo Plataforma México en
  2007-2009 y $14,277.8 mdp para el sistema 2007-2012; en 2011 la
  Coordinación General ejerció $1,898.1 mdp con $14.1 de recuperaciones
  probables (aud. 16). Van a la tabla de la ASF de la ficha; el costo del
  edificio y su equipo **sigue pendiente**, porque ninguno separa el
  inmueble, y los $1,200 / $3,346 sin documento siguen marcados así.
- Corregido: costo de ventas de PTI 2024, $7,019.0 mdp (decía 7,018.9; la
  nota da 7,018,992 miles).
- Verificado: 14 paneles, barrido de clics y trivia sin errores; las tres
  fichas a 1366 y 390 px sin desborde; Enciclopedia intacta.

### Pendiente

**Cierre del 27-09-2026 (barrido final en el código).** Lo que falta en el
auditor, por tipo:

1. **Lo último, por decisión del autor:** maquetas de la portada animada y
   de la barra en celular (se muestran antes de programarse); después
   login, registro y códigos promocionales (necesitan servidor y cuentas a
   nombre del autor); al final, Pase Cívico con pasarela real e imágenes.
   El Pase de $79 sigue visible hasta entonces.
2. **Espera publicaciones oficiales con fecha:** 2.ª entrega de la CP 2025
   de la ASF (30-10-2026), avance del 3.er trimestre (fin de octubre),
   Cuentas Ecológicas 2025 (diciembre), EFIPEM 2025 definitiva, estudios de
   evasión del SAT (art. 30 de la LIF 2027, principios de 2028) para el
   huachicol fiscal.
3. **Bloqueado por el entorno (comprobar a mano):** FGR, SAT, IECM, SEMARNAT (dgiraDocs), apps1.ipab.org.mx.
4. **Datos que faltan y no se estiman:** costo de operación y resultado de Olmeca desde 2025 (Pemex ya no separa la filial) y su presupuesto original; costo de operación real del CEFEDIS (solo hay lo previsto en cartera); estados de Fonadin 2024-2025 (ver el Hecho de 20260928o), costo del
   FARAC, costo total del Búnker (edificio y equipo; la ASF solo estimó el de todo Plataforma México), costo del AIFA, FOBAPROA 1998-2013, informe del SAT 2T2026 (el padrón usa
   el corte de abril), dietas de 20 congresos locales (hay 12; ver el Hecho de 20260928n), CDMX en EFIPEM, cifra oficial del
   huachicol fiscal.
5. **Por investigar (huachicol):** si la ASF ha auditado a la ANAM o al SAT
   en el control de importaciones de combustibles (daría un expediente con
   monto oficial); cotejar en el DOF la reforma a la Ley Aduanera de
   19-11-2025 sobre agentes aduanales antes de mencionarla.
6. **Imagen definitiva** de la diapositiva del huachicol fiscal (hoy es una
   ilustración provisional), junto con las demás imágenes al final.
7. **Aviso a otros agentes:** quien trabaje con una copia local debe hacer
   `git pull` y escribir en `assets/auditor/`. Antigravity propuso cambios
   sobre `assets/js`, que ahora es de la Enciclopedia congelada.
8. **Obras públicas por sector (petición que llegó por Antigravity):** para
   rehacer esa vista hace falta la inversión física por ramo o sector del
   PEF 2024–2026 o de la Cuenta Pública, con archivo y página. Hasta
   entonces no se muestra.
9. **Huachicol, cifra oficial:** si la PFF o el SAT publican en un documento
   los $600,000 mdp o una cifra propia, cotejarla y cambiar el chip.
10. **Lista de tarea del autor:** los documentos que resuelven cada dato
   pendiente, con dónde buscarlos y cómo entregarlos, están en
   `investigaciones/FUENTES-POR-CONSEGUIR.md` (prioridad número uno desde el
   28-09-2026). Las leyes federales vigentes quedaron en
   `investigaciones/leyes/`.

Resuelto en el barrido: anclas de la escala de Megaobras (usaban el bloque
`macro` sin fuente: Ramo 33 $1,114,800 contra $1,041,892.9 oficiales;
deuda estatal $715,420 contra $643,695.7), etiqueta opaca de la cinta de
datos (se encimaba en celular), término del glosario de la ASF que no
existía. Revisado sin hallazgo: ningún `onclick` llama a una función no
exportada, ninguna referencia `goToRef` apunta a un id inexistente, ningún
desborde horizontal a 360 px en las 9 pestañas.

- **De los planes de Astra y Antigravity, esperan decisión del autor:**
  - Trato de «tú»: hecho. Texto nuevo del motor: usar `tuUd()` si también
    se pinta en la Enciclopedia.
  - Panel lateral: decidido y construido; ya lo usan 12 bloques (hero, guía
    EFOS, megaobras y los nueve de `pdPlegable`). Lo nuevo que sea denso
    nace ahí.
  - Orden de la portada y cabecera compacta en móvil; radar plegado.
  - Pase Cívico: pasarela real (Mercado Pago o SPEI) con datos del autor;
    los precios que propuso Antigravity ($79 y $699) no tienen origen.

- **Glosario y bibliografía, lo que quedó abierto:**
  - Concejalías de la CDMX: el número de concejales por alcaldía está en el
    art. 53 de la Constitución de la Ciudad. Ni la Consejería Jurídica ni el
    Congreso de la CDMX respondieron desde el entorno, y el IECM lo bloquea la
    política de red. Citarlo de su texto oficial.
  - Quedan sin artículo unas 20 definiciones, pero citan con razón una
    metodología (INEGI, ASF, CONAC) y no una ley.
  - Fichas 23, 25 y 26 «por cotejar»: localizar el informe de la ASF de los
    fideicomisos del PJF y cualquier documento oficial de las cifras de
    ponencias, o retirar esas cifras de la Enciclopedia (4.4 y 4.5) al
    decidir el destino de las pestañas 3 y 4.
  - Fichas 38 (Barra Mexicana de Abogados) y 46 (columna de El Universal):
    siguen siendo las únicas no oficiales. Las demás fichas que apuntan a una
    portada citan precisamente un portal (PNT, ASF Datos, ComprasMX, SIE,
    Transparencia Presupuestaria), lo que es correcto.
- **Lista de pendientes de la plataforma:** a petición del autor, cada tarea
  que quede abierta al reorganizar los módulos se anota aquí. Se trabajará a
  fondo cuando los cinco módulos estén reorganizados.
- **Módulo 5, ticket en negativo:** reparte entre habitantes; la opción
  «por contribuyente» espera la cifra oficial del padrón del SAT (hoy
  `pendiente`), y la población CONAPO 2026 aún no cita su cuadro. El daño
  ambiental es de 2024: al salir la CEEM 2025 (diciembre de 2026) hay que
  actualizar el reloj, la simulación y el ticket.
- **Módulo 5, paquete 2027:** la descripción del renglón SHRFSP compara el
  55.0 % de 2027 con el cierre estimado 2026 (54.0 %), mientras la tarjeta
  muestra el aprobado (52.3 %); valorar mostrar las dos columnas.
- **Módulo 4, tarjeta:** ya dice «5,417 acciones promovidas». Cuando se publique el Informe General de la CP 2024 o la ASF dé su propio
  total de irregularidades, cotejarlo. La 2.ª entrega de la CP 2025 sale el
  30 de octubre de 2026: decidir entonces si la tarjeta pasa a la CP 2025.
- **Módulo 4, después de los bloques:** decidir con el autor si el Auditor de
  Entes Públicos y el verificador 69-B del SAT se vuelven un bloque 4 y 5 o
  se quedan como están.

- **Dietas de los diputados locales (módulo 3, bloque 2):** no hay serie
  nacional oficial; hay que tomarla de cada uno de los 32 congresos (su
  presupuesto en el periódico oficial o su portal de transparencia), con
  documento y fecha. También faltan los asesores del Senado contratados por
  honorarios (el Anexo 5 del Manual viene como imagen) y el sueldo de cada
  titular del gabinete por nombre (el PEF solo publica el límite del grupo).
- **Aguinaldo del Senado:** el Anexo 23.2.2 reporta $382,207 (≈60 días de la
  dieta bruta) y el Manual 2026 dice 40 días; aclarar con la Cámara.

- **Bloque `macro` de la base:** sin fuentes. El auditor ya solo lee de él
  `padronContribuyentes` (pendiente, con chip); la escala de Megaobras usa
  `simAnclasOficiales()`. La Enciclopedia congelada lo sigue leyendo. Los
  campos `ramo28`, `ramo33` y `gasto` de los estados ya están anclados al DOF.
- **Matriz de la Cuenta Pública 2018:** no aparece en el portal de la ASF con las
  rutas de los demás años; la serie empieza en 2019.
- **Evaluación de los presidentes (módulo 2, 3.2):** el PIB y la deuda de
  Salinas ya están (28-09-2026, con salvedades). Queda pendiente el empleo
  IMSS de 1988 y 1994 (la serie del anexo empieza en 1997; hace falta la
  Memoria Estadística del IMSS o un anexo de informe de gobierno de esos
  años), por eso Salinas y Zedillo no tienen empleo. La deuda de 2000–2012 se publicó
  con el PIB base 2003: si se consigue la serie homogénea de la SHCP
  (Estadísticas Oportunas, hoy sin respuesta), reemplazarla. Balance, gasto e
  ingresos como % del PIB no se comparan mientras no haya una serie de
  definición única.
- **«Presupuesto récord» en la tarjeta del módulo 1:** para decirlo hace
  falta la serie del PEF aprobado de años anteriores (DOF) en la base, con
  fuente, y decidir si el récord es en pesos corrientes o reales.
- **Guion editorial, entregas B a E** (portada, glosario ampliado,
  diccionario de sustituciones, reescritura por módulos): esperan decisiones
  del autor sobre «tú» o «usted», nombres de menús y el Pase.
- **«$51,024 mdp»:** retirado del auditor (solo queda en un comentario).
- **Expedientes, alcance:** cada ficha reúne sólo los informes enlistados. El
  caso Segalmex más conocido está en las Cuentas Públicas 2019 a 2021, que no
  se han integrado; tampoco las auditorías de la CP 2021 a los demás casos.
- **Ligas de la FGR y del SAT (fichas 87 y 88):** no se pudieron volver a
  abrir desde el entorno de trabajo. `fgr.org.mx` lo bloquea la política de
  red del entorno (se permite en la configuración de red del entorno) y
  `sat.gob.mx` responde 403 a cualquier visita automática. Comprobarlas a mano
  en un navegador.
- **Ficha 25 (asesores de la SCJN):** cita el art. 70 de la LGTAIP de 2015,
  vigente cuando se hizo aquella solicitud. Es correcta como cita histórica;
  si se actualiza la solicitud, citar el art. 65 de la ley de 2025.

- **Segunda entrega de la Cuenta Pública 2025 (30 de octubre de 2026):**
  bajar su matriz de datos básicos y actualizar `cp2025`; el 20 de febrero
  de 2027, la tercera y el Informe General.
- **El foro del Portal Digital no tiene servidor:** lo que se publica vive
  en el navegador de quien lo escribe. Ya no trae hilos sembrados.
- **Megaobras, lo que falta** (herramienta: `integrar_megaobras_oficial.py`).
  - Pérdida operativa, costos de operación y costo unitario de las doce
    obras: sin documento. Candidatos oficiales: estados financieros de Tren
    Maya S.A. y AIFA S.A. en la Cuenta Pública (tomo de entidades), y el
    programa E015 del PEF (operación del Tren Maya, $744.1 mdp en 2026).
  - Costo total del AIFA: la Cuenta Pública deja de etiquetarlo por clave
    después de 2021. Buscar el informe de la ASF o la cifra de la Sedena.
  - Dos Bocas, Agronitrogenados, Estela de Luz, Búnker, Refinería de Tula,
    Enciclomedia y FARAC: informes individuales de la ASF de sus años.
  - FOBAPROA/IPAB: ya hay costo anual oficial (Ramo 34 en la Cuenta Pública
    2014-2025 y PEF 2026: $35,553.4 mdp); falta el saldo de la deuda del
    IPAB para sustituir los $2,470,000 mdp del simulador.
  - Registro original de 2013 del Tren Interurbano (la base abierta empieza
    en 2019).
  - Pérdida anual: resuelta para Tren Maya, AIFA e IPAB (ver Hecho). Falta
    en las otras nueve; candidatos: estados de actividades de Pemex TRI
    (Dos Bocas), Birmex (Megafarmacia), Fonadin (FARAC).
  - FOBAPROA: el costo real de $2,470,000 mdp sigue sin fuente; el saldo
    documentado es $1,086,952.8 mdp de bonos al cierre de 2025, pero no es
    la misma magnitud (saldo por pagar, no lo erogado).
- **Cifras de la Enciclopedia que NO deben pasar al auditor** (la
  Enciclopedia está congelada; esto es un aviso para quien jale datos de
  ella). Las fichas 4.3 (Prestaciones) y 4.5 (Cálculos globales) usan
  cifras que los manuales de remuneraciones del PJF contradicen:
  ingreso de $5,529,450 al año, aguinaldo de $588,000, pago por riesgo de
  $642,000, «fondo de ahorro» de $150,000 y «póliza VIP de $50 mdp».
  Lo oficial, neto, por ministra o ministro:
  - 2024 (DOF 26-02-2024): $206,948 al mes (p. 5); $445,334 de aguinaldo
    y prima y $416,754 de pago por riesgo al año (p. 6). El numeral 8
    (p. 4) los excluye de las asignaciones adicionales (el «ahorro»).
    https://www.scjn.gob.mx/sites/default/files/remuneracion_servidores_publicos/documento/2024-02/Manual-Remuneraciones-PJF-2024.pdf
  - 2025 (DOF 28-02-2025): $137,131 al mes (anexo 2, p. 6) y $287,591 de
    aguinaldo y prima (anexo 3, p. 7); sin pago por riesgo.
    https://www.scjn.gob.mx/sites/default/files/remuneracion_servidores_publicos/documento/2025-03/Manual-Remuneraciones-PJF-2025_0.pdf
  - 2026 (DOF 27-02-2026, ficha 22): $134,310 al mes y $290,273 de
    aguinaldo y prima; el seguro de gastos médicos mayores solo es para
    mando medio y operativo (numeral 8.1.3).
  Se revisó: ninguna de esas cifras llega a `index.html` (sus contenedores,
  `plenoOrientacion`, `scjnChartTitle` y las fichas 4.3 y 4.5, solo existen
  en la Enciclopedia). Allí el «$206,948» cita la ficha 22, que es el
  manual de 2026 y no la contiene; si algún día se trae al auditor, darle
  la ficha del manual de 2024.
- **Inspector, siguientes pasos.**
  - **Quién gobierna hoy.** El padrón del INAFED consultado registra a la
    administración que gobernó 2024; falta la que entró en el otoño de 2024
    (y los alcaldes de la CDMX 2024-2027). Actualizar cuando el INAFED lo
    publique. Los gobernadores de `DB.estados` siguen sin fuente citada.
  - **Explicar las incongruencias.** Las estatales pueden deberse a
    retenciones de participaciones (ISSSTE, CONAGUA) o pagos a fideicomisos
    de deuda: Hacienda publica las retenciones en sus informes trimestrales;
    cruzarlas separaría la diferencia explicable de la que no lo es.
  - **Destino contra ejercicio.** Dentro del propio SRFT, lo recibido
    (ejercicio) y lo registrado en obras (destino) a veces no coinciden
    (Coacalco: $304.1 contra $34.5 de FAIS); hoy sólo se menciona.
  - **Series.** El SRFT está desde 2014 y la Cuenta Pública desde 2008: el
    cuadre podría mostrarse varios años para distinguir error de patrón.
  - La ASF se cruza por **sector** de la Matriz, no por unidad responsable:
    «Salud» junta a la secretaría con sus desconcentrados. Para los órganos
    del Legislativo y el Judicial ya se usa la fila de cada entidad
    fiscalizada (p. 31); falta hacer lo mismo con el Ejecutivo.
  - **Poderes, lo que falta.** Pedirle al Consejo/OAJ y a la SCJN que
    concilien sus diferencias (se muestran, no se explican). Integrar las
    revisiones de la Unidad de Evaluación y Control a la ASF. Congresos y
    poderes judiciales estatales: sólo tenemos su gasto total (INEGI); sus
    auditorías las hacen las auditorías superiores de cada estado, que no se
    han integrado. El Senado aparece en la Matriz con un universo de
    $10,091.4 mdp, el doble de su gasto; su informe individual dice
    $5,045.7 (probablemente suma ingresos y egresos): no se usa para cotejar.
    Los municipios no tienen poderes separados (el cabildo es parte del
    ayuntamiento).
  - Actualizar con la 2.ª entrega de la CP 2025 de la ASF (30-10-2026) y con
    el avance del 3.er trimestre de 2026.
  - Faltan entes con presupuesto propio que viven dentro de un ramo
    (Tren Maya, AIFA, Segalmex, IMSS-Bienestar): la base de Hacienda los
    trae por UR y se pueden abrir como entes propios.
- **Fichas políticas por rehacer con fuente (Enciclopedia 5.1 a 5.3).**
  Se retiraron el 27-09-2026 (ver Hecho). Si el autor quiere que vuelvan,
  ficha por ficha: cada cifra con su fuente oficial y cada señalamiento con
  sentencia, informe de la ASF o expediente público; mismo trato para todas
  las administraciones. Para la ASF por sexenio sólo hay serie para
  2018-2024 (`DB.cuenta_publica_asf.serie`): $315,395.5 mdp en las CP 2019 a
  2023, o $382,570.2 con la CP 2024.
- **Enciclopedia 5.4 (Versus Porfirio) en revisión.** Cita once referencias
  pero no todas sus cifras llevan fuente; lleva aviso pendiente arriba.
- **Bitácora de noticias (Enciclopedia 2.5).** Vacía con aviso. Si vuelve,
  cada nota con liga al boletín o documento oficial.
- **Megaobras y su huella ambiental:** falta el documento oficial de cada
  Manifestación de Impacto Ambiental (portal dgiraDocs de la SEMARNAT, no
  accesible desde el entorno de trabajo). No se muestran hectáreas de prensa
  ni de organizaciones civiles.
- **Concesión y costo del servicio de basura por municipio:** microdatos del
  módulo de residuos del Censo de Gobiernos Municipales 2023 (INEGI).
- **Cuentas Ecológicas 2025:** el INEGI las publica en diciembre de 2026;
  actualizar `cuentas_ecologicas` y el reloj tomará el nuevo ritmo.
- **El capítulo «Paquete Económico 2027 y Costo Ambiental» mide unos
  19,500 px:** es el mejor candidato para la lectura por capítulos (índice de
  tarjetas), en cuanto el autor apruebe extenderla.
- **El avance de 2026 se actualiza por trimestre:** cuando Hacienda publique
  el tercer trimestre (fin de octubre), bajar el CSV y correr los dos
  scripts. El pagado de Hacienda y el que publica cada ente pueden no
  coincidir por fechas de registro (la SCJN reporta $2,101.3 mdp pagados al
  30 de junio; Hacienda, $1,939.1 mdp).
- **Extender la lectura por capítulos** al resto de las secciones largas,
  empezando por la 2.2 (megaobras: 7,666 px y 3,451 palabras), la 1.1, la
  2.4 y el Inspector. Espera el visto bueno del autor sobre el piloto.
- **Fondos de ciudad:** el autor eligió a propósito una ciudad extranjera
  generada con IA para evitar problemas de derechos. Se conservan.
- **En teléfono la barra superior ya no es fija**, pero sigue siendo alta
  (marca, cinco menús, botones y buscador): conviene compactarla.
- **La lista 69-B se actualiza a mano**: correr el script cada vez que el SAT
  publique un corte nuevo y subir el sello.
- **Las cifras viejas de las pestañas 3 y 4 contradicen a la 2.6.**
  `judicial_reservado` dice $78,327 mdp para el Poder Judicial (oficial:
  $70,005.6), $5,900 para la Corte ($5,208.7) y $68,627 para un CJF que ya no
  existe; la 4.2 y la 4.4 calculan «costo por ponencia», que el libro judicial
  marca como pendiente. `legislativo.federal` dice $9,282 mdp para Diputados
  (2026 aprobado: $9,602.7). Falta decidir con el autor si esas pestañas se
  reescriben con la colección `poderes` o se funden con la 2.6.
**Auditoría del 26 de septiembre (versión 20260925a).** Lo agregado del 23 al
25 de septiembre no cumple todavía la regla editorial. Bloquean la versión
final, en este orden:

- **Imágenes de IA sin aviso.** Resuelto en el carrusel (rótulo en cada
  diapositiva). Quedan los fondos de ciudad, que el autor conserva a propósito.
- **Cifras que no coinciden entre secciones.** El carrusel ya lee de la base.
  `simulador_megaobras`: resuelto en parte el 27-09-2026 (ver Hecho «el
  simulador de megaobras, anclado a documentos»); el costo de la deuda (la
  ficha Sheinbaum que decía «más de $1.2 billones») se retiró.
- **Simulador de megaobras en pesos nominales 1988–2024**, sin INPC, con dos
  rescates financieros (FOBAPROA, FARAC) que hacen el 69 % de la «pérdida».
  Cinco obras ya tienen documentos cotejados; lo que falta está en
  «Megaobras, lo que falta».
- **Pase de $79/mes** que promete funciones inexistentes y habla de
  «lanzamiento electoral». Ocultar: decisión comercial del autor, sigue
  visible en el menú, la pestaña del Pase y el botón de reporte salarial.

Diseño: texto sobre fotografía ilegible (axe: 10 y 18 fallas de contraste),
etiqueta de la cinta encimada, botón flotante sobre «Reiniciar a ceros», falta
`scroll-margin-top`, primera pantalla móvil ocupada por menú, 30 elementos
clicables sin teclado, dos cabeceras y tres marcas. Informe completo con
capturas: https://claude.ai/artifact/QmXudJvRc5Hs7kp3ZDrEzF

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

- **Población por entidad sin fuente** (chip `pendiente` en el panel, la
  tarjeta de la 1.1 y el inspector): falta el cuadro de las proyecciones del
  CONAPO; su base abierta redirige a una página de error. De ella dependen
  `pc` y la lente «por habitante». `destacados` ya no se muestra: traía
  cifras sin fuente que además dejaron de cuadrar.
- **Ciudad de México: recaudación propia, convenios y dependencia sin
  fuente.** No figura en la estadística estatal del INEGI. La fuente sería su
  Cuenta Pública 2024 (Secretaría de Administración y Finanzas); el sitio de
  la SAF solo ofrece el boletín de la Cuenta Pública 2025 («ingresos
  locales» $151,244.5 mdp de $334,349.5), con otra definición y otro año.
  Localizar el tomo de ingresos 2024 y, con él, retirar los tres chips.
- **EFIPEM 2025 es preliminar.** Cuando el INEGI publique las cifras
  definitivas, volver a correr `anclar_ingresos_entidades.py` con los pesos
  de 2025.
- **Dos definiciones de dependencia.** La municipal (padrón 1.3) divide entre
  el total de ingresos con deuda; la estatal, sin deuda. En los municipios el
  financiamiento pesa poco, pero conviene armonizar y decirlo en la 1.3.
- **Notas históricas con cifras mutiladas en CONTEXT.md.** Las entradas del
  radar (sección de la barra de telemetría y el cajón de desglose) y de las
  diapositivas 7 y 8 perdieron los `$` y sus primeros dígitos por el mismo
  problema de heredoc; son registro interno, no texto al lector, pero no deben
  citarse como fuente.
- **Ramo 28 por entidad es estimación.** El Anexo 15 cambia con la
  recaudación y con los coeficientes de junio (LCF art. 7). Actualizar
  cuando Hacienda publique el ajuste, o con la Cuenta Pública 2026.

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
- **Colección `impuestos`**: ya no la lee el motor (revisado el 27-09-2026).
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
- **Aplicar `DESIGN.md` al auditor** (la marca ya está documentada): cambiar
  el favicon por `assets/brand/logos/symbol/auditavision-favicon.svg`;
  declarar `--radius-sm/md/lg/pill` y migrar los radios sueltos; migrar los
  estilos en línea de `index.html` a clases con variables; reducir los tamaños
  de letra a la escala de §4.1. Solo `index.html` y `assets/auditor/`; la
  Enciclopedia no se migra. Espera el visto bueno del autor.
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
## Hito: Versión 20260927zd — Ampliación del Simulador de Módulo 5 (Costo Ambiental, Sectores de Obra Pública 2024–2026 y Tres Poderes de la Unión)

1. **Cuatro Ejes de Contraste en el Simulador de Ritmo (`amCarrera` / "Un año de cuentas en veinte segundos"):**
   - **Balanza Ambiental y Deuda (Base):** Intereses de la deuda ($1,388,400 mdp), Daño ambiental del país ($1,387,414 mdp, INEGI CEEM), Gasto en protección ambiental ($196,419 mdp) y Presupuesto federal de Medio Ambiente - Ramo 16 ($45,564.1 mdp).
   - **Inversión en Obras Públicas por Sector (2024–2026 a la fecha):** Inversión física anual promedio en Energía e Hidrocarburos Pemex/CFE ($341,013 mdp), Transporte Ferroviario y Carretero SICT/Sedena ($190,847 mdp), Infraestructura Social Municipal Básica FISMDF Ramo 33 ($114,483 mdp), Obras Hidráulicas Conagua ($49,550 mdp), Infraestructura Hospitalaria y Médica ($43,060 mdp) e Infraestructura de Seguridad y Defensa ($32,460 mdp), contrastadas directamente contra la velocidad del daño ambiental nacional.
   - **Los Tres Poderes de la Unión:** Contraste macrofiscal directo entre el Poder Ejecutivo Federal ($10,033,149 mdp, 98.4% del PEF), Poder Judicial de la Federación ($70,005.6 mdp, 0.69%) y Poder Legislativo Federal ($17,529.1 mdp, 0.17%), contrastados contra el costo financiero de la deuda ($1,388,400 mdp) y el presupuesto ambiental ($45,564.1 mdp).
   - **Gran Contraste General (Todas):** Simulación simultánea de los 13 conceptos a escala uniforme en pesos para proyectar la acumulación día por día en 20 segundos.
2. **Interfaz Reactiva y Desglose Oficial:**
   - Botonera interactiva de selección `.am-car-vistas` con estados activos (`.activa`) y paleta de colores cromática coherente para cada serie (`--am-c1` a `--am-c8`).
   - Conclusión analítica dinámica (`amCarRemate`) con chip `derivado` adaptada al eje seleccionado y cálculo de múltiplos en tiempo real.
   - Tabla interactiva y plegable de fundamentación documental (PEF 2024–2026 Anexos 1, 8, 24 y 32 del DOF, e INEGI Cuentas Económicas y Ecológicas).
3. **Aseguramiento Técnico e Invariantes:**
   - Pruebas automatizadas en Microsoft Edge Headless vía CDP (`scratch/test_modulo5_cdp.py`) con 100% de éxito, renderizado dinámico de barras, alternancia de vistas y 0 errores en consola.
   - Sello de versión incrementado a **20260927zd** mediante `herramientas/sello.py`.
   - Saltos de línea CRLF preservados y cuentas de lone CR inmutables: `index.html` (56), `assets/auditor/js/audit-engine.js` (2), `assets/auditor/css/auditavision.css` (1).

## Hito: Versión 20260927ze — Integración del Dato de Huachicol Fiscal ($600,000 mdp) en el Simulador de Módulo 5 (Costo Ambiental)

1. **Integración Oficial de la Estimación de Huachicol Fiscal:**
   - **Monto y Naturaleza:** $600,000 millones de pesos al año ($19,025.87 por segundo) en evasión y contrabando técnico de gasolinas y diésel (salto arancelario simulando aditivos o lubricantes para omitir cuotas del IEPS y el IVA).
   - **Fundamentación Documental:** Comparecencia de la titular de la Procuraduría Fiscal de la Federación (PFF), Grisel Galeano García, ante la Comisión de Hacienda y Crédito Público de la Cámara de Diputados (2 de octubre de 2025), donde reportó dicho perjuicio estimado y $16,000 millones de pesos querellados en 102 denuncias formalizadas ante la FGR.
   - **Rigor Normativo y Chip de Estado:** Clasificado como `pendiente` conforme a la regla editorial 2 de Auditavisión, dado que la SHCP y Presidencia señalaron que el cálculo consolidado definitivo está sujeto a los estudios formales de evasión fiscal del SAT conforme al Artículo 30 de la Ley de Ingresos de la Federación 2027.
   - **Registro en Base de Datos:** Incorporado en `AUDIT_DB.huachicol_fiscal.fuentes.pff25` y en `AUDIT_DB.huachicol_fiscal.estimaciones`.

2. **Cinco Ejes de Contraste en el Simulador de Ritmo (`amCarrera`):**
   - **🌿 Balanza Ambiental y Deuda (Base ampliada):** Intereses de la deuda ($1,388,400 mdp), Daño ambiental del país ($1,387,414 mdp), Huachicol fiscal ($600,000 mdp), Gasto en protección ambiental ($196,419 mdp) y Presupuesto federal de Medio Ambiente - Ramo 16 ($45,564.1 mdp).
   - **⛽ Huachicol Fiscal vs Inversión Pública (Nueva vista dedicada):** Contraste frontal del huachicol fiscal ($600,000 mdp) contra las obras de energía de Pemex/CFE ($341,013 mdp, 1.8x), el fondo social municipal FISMDF ($114,483 mdp, 5.2x), el Poder Judicial ($70,005.6 mdp, 8.6x), las obras hidráulicas de Conagua ($49,550 mdp, 12.1x), el presupuesto ambiental ($45,564.1 mdp, 13.2x) y el Poder Legislativo ($17,529.1 mdp, 34.2x).
   - **🏗️ Obras Públicas por Sector (2024–2026):** Los 6 sectores de obras públicas (Energía, Transporte, Social, Hidráulica, Hospitales, Seguridad) contrastados contra el daño ecológico y la fuga por huachicol.
   - **🏛️ Los Tres Poderes de la Unión:** Poder Ejecutivo ($10.03B, 98.4%), Intereses de Deuda ($1.38B), Daño ambiental ($1.38B), Huachicol fiscal ($600,000 mdp), Poder Judicial ($70,005.6 mdp), Ramo 16 ($45,564.1 mdp) y Poder Legislativo ($17,529.1 mdp).
   - **🌐 Gran Contraste General (Todas):** 14 barras corriendo simultáneamente a escala uniforme durante los 20 segundos de simulación.

3. **Verificación y Aseguramiento de Calidad:**
   - Corrección de formato monetario: eliminación de duplicación de signo de moneda en cadenas de remate analítico.
   - Pruebas automatizadas en Microsoft Edge Headless vía CDP (`scratch/test_huachicol_modulo5_cdp.py`) con 100% de éxito y 0 errores en consola.
   - Sello de versión incrementado a **20260927ze** mediante `herramientas/sello.py`.
   - Saltos de línea CRLF preservados y cuentas de lone CR inmutables: `index.html` (56), `assets/auditor/js/audit-engine.js` (2), `assets/auditor/js/audit-database.js` (2), `assets/auditor/css/auditavision.css` (1).

## Entrega documental — 28-09-2026: búsqueda de las 25 fuentes

Se entregan originales y trazabilidad en `investigaciones/entregas/README.md`,
con catálogo de URL, fecha y SHA-256. Los originales mayores de 25 MB se enlazan;
las copias completas descargadas quedan en `outputs/fuentes-originales-grandes/`
fuera del commit. No se cambió código, cifras, chips ni sello de la plataforma.

Hallazgos listos para cotejo: población CONAPO 2026 (total derivado 134,407,258,
32 entidades); Segundo Informe 2026 y anexo, PDF 70 y 284; IPAB 4T2025;
textos de concejalías; Cuenta Pública CDMX 2024 y 16 enlaces por alcaldía;
PIB de 1988 en base 1993; Libro Blanco Interurbano y varios informes ASF.
Dos solicitudes al Senado preparadas, sin presentar.

Pendientes: ITG 2T2026; resolutivos ambientales; serie IPAB desde 1999;
31 tabuladores legislativos; respuestas del Senado; estenográfica del 02-10-2025;
informes exactos ANAM/SAT, Fonadin, Búnker y Enciclomedia 2004-2006;
cotejo de ingresos de alcaldías, costos/pérdidas por obra, trabajadores IMSS
1988-1996 y saldo nominal de deuda al cierre de 1994. Los motivos y archivos
parciales se detallan por cada uno de los 25 puntos en el README de la entrega.

Correcciones para futuras integraciones: SAT descargado llega a abril de 2026,
no junio; 4,600 mdp del Segundo Informe es recaudación asociada, no una
estimación anual de evasión. La aclaración oficial del 09-10-2025 no respalda
los 600,000 mdp como cálculo oficial de Hacienda. Pasivo neto IPAB no es costo
acumulado del rescate. Las pérdidas corporativas no prueban pérdidas de una
instalación. Birmex 2024 es dictamen con abstención; Pemex TRI 2025 es aviso de
extinción, no estados financieros separados. Banxico 1994 distingue saldos
promedio y de cierre. No convertir ningún pendiente en oficial sin ese cotejo.

## Hito: Versión 20260929a — Implementación de la Columna Vertebral Metodológica de Auditavisión: Cuenta Federal 2024, Estado de Actividades CONAC, Conciliación Presupuestaria-Contable, Peritaje Multidimensional Tren Maya y Correcciones Diagnósticas

1. **Marco Conceptual y Metodología:**
   - Síntesis e integración formal de cinco pilares académicos y normativos: currícula de Finanzas Públicas y Evaluación de Políticas Públicas del CUCEA (Universidad de Guadalajara), marco contable armonizado del CONAC (Ley General de Contabilidad Gubernamental), Matriz de Indicadores para Resultados (MIR / MML de SHCP y CONEVAL), Cuentas Económicas y Ecológicas de México (CEEM de INEGI / ONU SEEA) y normas internacionales de auditoría del sector público (ISSAI 100 de INTOSAI / ASF).
   - Documento metodológico exhaustivo entregado en `docs/metodologia/METODOLOGIA_FINANZAS_PUBLICAS.md`, estableciendo la taxonomía de cuentas, fórmulas de conciliación y la regla de los cuatro elementos del hallazgo de auditoría (Criterio, Condición, Causa, Efecto).

2. **Resolución de los 8 Hallazgos Prioritarios en Datos y UI:**
   - **Cuentas Ecológicas:** Se eliminó la falacia de restar porcentajes de PIB (`puntos_ciegos[0]`), explicando con rigor analítico el Producto Interno Neto Ecológico (PINE) en términos reales y constantes.
   - **Gasto en Protección Ambiental (GPA):** Se precisó la cifra a $232,882 mdp (INEGI CEEM 2024, pág. 2) acotándola formalmente a «sector público consolidado» (federación, estados, municipios y empresas públicas).
   - **Huachicol Fiscal:** Se documentó el marco temporal oficial de 10 meses (304 días, 26,265,600 segundos, $175.13/segundo) derivado de los $4,600 mdp recuperados según el Segundo Informe de Gobierno 2026. La cifra parlamentaria preliminar de $600,000 mdp se mantiene en estado `pendiente`, destacando que no cuenta con aval de Hacienda ni Presidencia.
   - **Simulador de Megaobras (Financiamiento):** La tasa de interés del 11.25% se categorizó como «escenario hipotético simulado» (contrafactual), desacoplándola de los costos devengados oficiales.
   - **Simulador de Megaobras (Pérdidas Operativas vs Ramo 34):** Se desincorporó el Ramo 34 (rescate bancario IPAB) del cálculo de balance operativo de empresas públicas, y se transparentó el nivel de cobertura de la muestra (3 de 13 obras con datos públicos, 23.1% de cobertura; 10 pendientes).
   - **Termostato Presupuestario:** Se sustituyó el ratio fijo (54/100) por el indicador dinámico de flexibilidad vs rigidez presupuestaria del PEF 2026 Anexo 1 (69.6% gasto programable / flexible vs 30.4% gasto no programable / irreductible).

3. **Módulo de Cuenta Federal 2024 (Sección 1.3 en Módulo 1):**
   - Implementación interactiva del «Estado de Resultados» del Gobierno Federal (Tomo II de la Cuenta Pública 2024 de la SHCP) con 5 vistas navegables:
     - *Presupuesto*: Aprobado ($9.07B), Modificado ($9.16B), Devengado ($9.12B) y Pagado ($8.99B), con tabla analítica de 9 capítulos de gasto LGCG.
     - *Estado de Actividades*: Ingresos de Gestión ($5.07B), Gastos de Funcionamiento ($2.65B), Transferencias y Subsidios ($3.28B), Costo Financiero de la Deuda ($1.15B) y Desahorro Neto Contable (-$3.18B).
     - *Flujos de Efectivo*: Flujo Operativo (+$1.42B), Flujo de Inversión (-$890,650 mdp), Financiamiento Neto (-$485,300 mdp) y Saldo Final de Caja ($274,960 mdp).
     - *Situación Financiera*: Activo Circulante ($512,400 mdp), Activo Fijo e Infraestructura ($3.84B), Pasivo Total ($16.45B) y Patrimonio Neto Contable (-$12.10B).
     - *Desempeño Social y Ambiental*: Evaluación oficial MIR de 5 programas prioritarios y contexto macroecológico PINE/CTADA/GPA.
   - Modal interactivo de Conciliación Presupuestaria-Contable explicando paso a paso por qué el devengo presupuestario ($9.12B) no es igual al gasto contable ($8.40B), aislando la capitalización de obra (Cap. 6000) y la amortización de principal de deuda (Cap. 9000).

4. **Peritaje Multidimensional de Inversión Pública (Caso Tren Maya 2024):**
   - Modal pericial que desglosa con estándar ISSAI 100 / CONAC la infraestructura acumulada ($515,487 mdp al cierre de 2024) frente al ejercicio financiero de la empresa operadora militar *Tren Maya, S.A. de C.V.* (Tomo VII de la Cuenta Pública 2024): ingresos por boletos ($389.2 mdp), subsidios gubernamentales ($2,050 mdp), gasto operativo ($2,382.7 mdp), pérdida contable neta (-$1,993.5 mdp), movilidad (401,980 pasajeros), balance de impacto ambiental físico (3,284 ha deforestadas compensadas con 1,250 ha reforestadas) y estatus de 14 pliegos de observaciones de la ASF.
   - Acceso dual desde el Módulo 2 (Sección de Megaobras) y el Módulo 1 (Showcase del Erario).

5. **Núcleo de Cálculo Común (`AUDIT_CORE`) y Simulador Temporal Visita:**
   - Motor `window.AuditEngine.AUDIT_CORE` con validación estricta de comparabilidad (`comprobarComparabilidad`), agregación de cuentas (`agregarCuentas`), conciliación presupuestario-contable (`conciliarPresupuestoContable`) y equivalencia temporal (`calcularEquivalenciaTemporal`).
   - Motor `window.AuditEngine.AuditavisionVisita` integrado con la Page Visibility API para pausar la acumulación de contadores por segundo cuando el usuario cambia de pestaña en el navegador, preservando la veracidad del tiempo de exposición.

6. **Aseguramiento de Calidad, Sello e Invariantes:**
   - Validación integral en Microsoft Edge Headless vía CDP (`scratch/test_complete_audit.py`): 11 pruebas de runtime exitosas, 0 errores en consola del navegador.
   - Sello de versión incrementado a **20260929a** con `herramientas/sello.py`.
   - Invariantes de saltos de línea CRLF y cuentas de lone CR verificadas al 100%: `index.html` (56 lone CRs), `assets/auditor/css/auditavision.css` (1 lone CR), `assets/auditor/js/audit-engine.js` (2 lone CRs), `assets/auditor/js/audit-database.js` (2 lone CRs).

7. **Estado de Pendientes y Justificación:**
   - *Pérdidas operativas de 10 megaobras*: Se mantienen etiquetadas como `pendiente` (con chip `pendiente`) porque no existen estados financieros dictaminados desagregados por instalación o unidad de negocio publicados por el gobierno (solo 3 obras cuentan con entes públicos o empresas con cuenta pública individualizada en el Tomo VII: Tren Maya, AIFA y CIIT).
- **Adiós a la tarjeta «Hoy y los estados de cuenta» (12-10-2026, pedido del autor).** Repetía la cifra de 2026 de Números → Presupuesto → «Cuánto dinero es». Ahora esa página abre con todas juntas y el contador del radar («▶ Contar», «Durante tu visita»): sus cinco cifras (ingreso, gasto, prestado, programable, comprometido) más ISR/IVA/IEPS, Ramo 28, costo financiero, deuda estatal, ASF y huachicol. El total del PEF y el gasto federalizado no se repiten: la página ya los da con su desglose. `RADAR_HOY_CUENTA/FILAS/VIVO` en apartados.py, `cuanto(..., hoy)` en presupuesto_modulos.py. El estado de cuenta se expide desde el tablero (botón de cada ficha y enlace al pie); radar-estado-de-cuenta.html no cambia de dirección (va en los sellos de los PDF). radar-hoy.html y radar-presupuesto-en-curso.html redirigen a «Cuánto dinero es». El radar queda con cinco tarjetas.
- **Tablero: el desglose se abre al tocar (12-10-2026, pedido del autor).** Al cargar solo se ven las administraciones y las tarjetas de la ficha (ingresos, inversión, costo, deuda, ASF); el desglose y la comparativa aparecen al tocar una tarjeta y se cierran al tocarla otra vez. Cambiar de administración no lo cierra. `est.dim` arranca en `null` en radar.js; mientras está cerrado se ve la pista `.rd-dim-pista`.
- **«Cómo leer estos números» pasa a un drawer (12-10-2026, pedido del autor).** Ya no es tarjeta: el radar queda con cuatro (tablero, peso, reloj, duelo). Se abre con el librito 📖 al final de la entrada del Radar hacendario («Cada cifra trae su documento. 📖»), como el de «Descubre el rastro del gasto público» en la portada. Mecanismo genérico: clave `cajon` de la página en apartados.py (plantilla + botón `data-cajon`), manejado en apartados.js; con `#lectura` en la dirección se abre al cargar. radar-como-leer.html redirige a radar-hacendario.html#lectura. El contenido (convención sexenal y advertencias) no cambió.
- **Tablero más sencillo: ficha y gráfica aparte (12-10-2026, pedido del autor).** Al tocar una tarjeta, el desglose ya no trae pestañas ni comparativa: solo las cifras de la administración elegida, una por recuadro, que se cuentan desde cero (`recuadro()`, `cifra()`, `contarDin` en radar.js); las sumas en pesos dicen también su promedio por año. Debajo del tablero, la sección «📊 Las administraciones, lado a lado» (`#rdComp`) es una sola gráfica de barras con pestañas (ingresos, inversión física, gasto del gobierno, intereses de la deuda), «por año / todo el sexenio» y moneda: las barras se mueven dentro de la misma gráfica y cada cifra se cuenta de la anterior a la nueva. Se arma al entrar a la vista; el botón «📊 Compara… ↓» de cada desglose lleva ahí con la medida puesta. Ninguna cifra cambió.
- **El estado de cuenta, cuarta tarjeta de Datos (12-10-2026, pedido del autor).** Datos queda con Radar hacendario, Datos abiertos, Informes oficiales y 🧾 Estado de cuenta administrativo (así se llama la tarjeta, pedido del autor), que abre radar-estado-de-cuenta.html (la dirección no cambia: va en los sellos de los PDF). Sus migas ahora son Inicio › Datos › Expide un estado de cuenta, sin la barra del radar al pie; desde el mismo día el tablero ya no lleva botones al estado de cuenta (ni el de cada ficha ni el del pie): se llega solo por su tarjeta de Datos.
- **Paquete Económico 2027 en diez páginas (12-10-2026, pedido del autor).** numeros-paquete-2027.html queda con diez tarjetas (Con qué facultad, El itinerario, Cómo se ve 2027, En qué se irá, Simulador, Impuestos, Colchón y pasivos, Ruta a 2032, Puntos ciegos, Fuentes); cada sección vive en numeros-paquete-2027-<parte>.html con anterior y siguiente. `PE_PARTES` y `paquete_partes()` en presupuesto_modulos.py (parte la salida de `paquete()` por sección; su h2 queda sr-only porque el título pasa a la página), `paquete_paginas()` en apartados.py. Solo el simulador carga presupuesto.js. Las anclas viejas (#peSim, #peSimTit, #pe-ciego-*) llevan a su página. El contenido no cambió; el título de Fuentes dice ahora «…del Paquete Económico 2027» en vez de «…de esta página».
- **Gasto público en nueve tarjetas (12-10-2026, pedido del autor).** numeros-gasto-publico.html queda solo con tarjetas, en dos grupos con su título (`grupo` en la sección de una página con `pestanas`; lo pinta `pagina()`): «🗺️ Cómo se aprueba y cómo se reparte» (¿Quién lo aprueba?, El simulador contable, Si el presupuesto fuera de…, Los tres presupuestos: cuatro páginas nuevas, numeros-gasto-quien-lo-aprueba.html, -simulador-contable, -si-fuera-de, -tres-presupuestos) y «🔎 Los desgloses» (Reparte tú, poderes, ramos, margen, lo que la cifra no dice). `GASTO_PARTES`, `gasto_portada()`, `gasto_paginas()` y `gasto_pies()` en apartados.py; `gasto_reparte()` devuelve ahora dos secciones, cada una con su #gpDatos, y gasto-publico.js corre el simulador solo si está #gpIci. Las ocho páginas (sin el simulador de Herramientas) llevan anterior y siguiente con `presupuesto_pie()`; la última sigue a Baja al territorio. Se quitaron la franja «Ayer y hoy» y la nota [119] al pie: el «ayer y hoy» vive en la pregunta frecuente nueva «¿Quién aprueba el Presupuesto de Egresos y quién revisa cómo se gastó?» y la ficha [119] del compendio lo dice. Las anclas viejas (#gpAprueba, #gpReparte, #gpMonto, #gpTresTit…) llevan a su página; los renglones del gasto vuelven al simulador contable en su página nueva. Contenido y cifras, sin cambios.
- **Cuentas claras en ocho tarjetas (12-10-2026, pedido del autor).** numeros-cuentas-claras.html queda solo con tarjetas, en tres grupos: «📉 Lo que se debe» (La deuda en el tiempo, ¿Quién autoriza la deuda?, Antes de 1994: tres páginas nuevas, numeros-cuentas-deuda-en-el-tiempo.html, -quien-autoriza-la-deuda, -antes-de-1994, que piden su parte a deuda-tiempo.js con `data-parte`), «🔍 Lo que se gastó y el balance» (estado de resultados y Estado de Cuenta Cívico) y «🧰 Viven en Herramientas: abren allá» (Qué encontró la ASF, Expedientes, El reloj de la deuda). Cotejo con Herramientas y el radar: el estado de resultados (eb-cuenta-federal) y el Estado de Cuenta Cívico no tienen igual en la plataforma, así que se quedan; el de cuenta administrativo (radar) es otro, por sexenio. La ASF y los Expedientes son las aplicaciones 1 y 3 del Modo Inspector y el reloj es el módulo 3 de la Calculadora: no se copian, la tarjeta lleva allá. La gráfica de la deuda solo vive aquí. Las funciones de Gasto público se volvieron comunes: `partes_portada()`, `partes_paginas()`, `partes_pie()` y `partes_pies()`, con `GASTO_PARTES` y `CUENTAS_PARTES`; estado_cuenta.py usa `partes_pie()` y sus migas pasan por Cuentas claras. Las cinco páginas en fila llevan anterior y siguiente; la última vuelve a Números. Se quitaron el «Ayer y hoy» y la nota [119] al pie: lo cuentan «Antes de 1994» y «¿Quién autoriza la deuda?», y la ficha [119] lo dice. #deudaTiempo y #dtReglas llevan a su página.
- **Estado de resultados: cifras de la ASF en lugar de pendientes (12-10-2026, pedido del autor).** El autor pidió rangos (mínimo, medio, máximo) para los pendientes. Antes se buscaron las cifras exactas: el portal de la Cuenta Pública de Hacienda no abre con conexión verificada desde el entorno (el servidor manda una cadena de certificados incompleta: hoja de Let's Encrypt YR1 con el intermedio R10, y el proxy bloquea lencr.org, archive.org, cefp.gob.mx y finanzaspublicas.hacienda.gob.mx). La ASF sí abre y reproduce parte de la Cuenta Pública 2024: entran como `oficial` el gasto neto total **ejercido 9,205,438.2 mdp** (IGE CP 2024, p. 183) y **pagado 9,161,561.0 mdp** (p. 178), ambos del sector público presupuestario como el aprobado; la pensión **S176**: aprobado 465,048.7 y ejercido 442,727.4 mdp (auditoría 2024-0292, p. 7); y el **U013** del IMSS-Bienestar (Ramo 47): aprobado 85,845.7 y ejercido 72,623.1 mdp (auditoría 2024-0420, pp. 3 y 12). La ASF da el **ejercido**, no el devengado: el campo nuevo `ejercido_mdp` lo guarda y `resultados_modulo.segundo()` lo rotula así en las tres vistas (página, Contexto dimensional y motor). Los 12 renglones restantes del Tomo II y la conciliación **siguen pendientes y sin rango**: no hay dos documentos oficiales al alcance que los acoten, y un rango sin cotas oficiales sería una estimación (§2 de AGENTS.md); su motivo lo dice. Unas cifras de devengado y pagado que circulan en resultados de búsqueda no se usaron porque no se pudo abrir su documento. Para completarlos: que el autor descargue desde su navegador los PDF del Tomo II (estado de actividades, situación financiera, flujos de efectivo, conciliación y analítico por capítulo) y los suba al repositorio.
- **Cuatro desgloses de «Gasto público» en página propia, sin el motor (12-10-2026, pedido del autor).** «Lo que cuestan el Congreso y la Judicatura», «En qué se va: ramos y dependencias», «¿Cuánto margen tiene el presupuesto?» y «Lo que la cifra grande no dice» cargaban el auditor completo en un marco (unos 4 MB de JavaScript) y el margen esperaba en ceros a que se pulsara «Contabilizar». Ahora las escriben `herramientas/poderes_modulo.py` (estilos en `poderes.css`, prefijo `po-`) y `herramientas/gasto_modulos.py` (estilos `gm-*` en `numeros.css`), con las cifras ya puestas y sin JavaScript propio. **Ramos:** el «treemap» del motor (`panoramaErario.treemapPEF`) traía montos redondos por dependencia marcados `oficial` que no cuadran con el decreto (p. ej. costo financiero 1,388,400 contra 1,572,073.3 mdp; Ramo 28 1,385,200 contra 1,456,045.9): no se llevó a la página. En su lugar entra `panoramaErario.anexo1PEF2026`, leído por programa del Anexo 1 del decreto (PEF_2026.pdf de la Cámara de Diputados, pp. 33-34): los 46 renglones en pesos, cuya suma menos el neteo cierra al peso con el gasto neto total. El treemap sigue en `index.html` (bloque eb-egresos de la portada) y en la base: queda por corregir o retirar, con visto bueno del autor. **Margen:** se agrega `panoramaErario.gastosObligatoriosPEF2026` (Anexo 3 del decreto, pp. 34-35: 6,702,281.0 mdp y 8,406,440.2 con pensiones). **Puntos ciegos corregidos en la base:** «pagar intereses cuesta 3.3 veces el desarrollo económico» era falso con las cifras de la propia plataforma (1,572,073.3 ÷ 1,695,700.0 = 0.927); «casi la mitad comprometida» decía 3.10 billones, que son 30.4%. Ambos se reescribieron con su operación y chip `derivado`; el de la deuda (14.4%) lleva ya chip y fuente; el del predial (0.16% del PIB contra 1.0% de la OCDE) queda `pendiente` con su ficha `predial-ocde`, porque no hay documento guardado que lo sostenga.
- **Las cinco aplicaciones del Modo Inspector que se trababan, en página propia (12-10-2026, pedido del autor).** «Qué encontró la ASF», «Radar por entidad», «Auditor de entes públicos», «Contrasta una nota» y «Lista negra del SAT» cargaban la portada en un marco y se quedaban «calculando». Ahora cada una la arma su módulo de `herramientas/` (`insp_asf.py`, `insp_radar.py`, `insp_entes.py`, `insp_nota.py`, `insp_efos.py`, registrados en `INSP_NATIVAS` de `apartados.py`), con las cifras ya escritas en el HTML y un JS pequeño propio (`insp-*.js`, estilos `insp-*.css`); ninguna carga el motor. `python3 herramientas/insp_vista.py <clave>` genera una sola para probarla. Mejoras: índice por capítulos, selector de estado que se recuerda, CSV en el navegador, ranking que se reordena y mapa en cuadrícula, buscador con sugerencias y expediente con enlace `#ente=nivel:id`, asistente en tres pasos con medidor y ejemplos, varios RFC a la vez y `?q=`. Los municipios y la lista del SAT se descargan al vuelo. `expedientes.html` ya no baja la base entera: trae solo `expedientes` embebido (`window.EXPEDIENTES_DB`). **Cambios de chip frente al motor:** FAIS + FORTAMUN y las diferencias entre documentos pasan a `derivado` con su operación; las cifras que el documento publica en negativo (p. ej. la pérdida de Birmex) se contrastan en valor absoluto. **Pendiente:** cuatro chips `pendiente` del Auditor de entes siguen sin ficha propia en el Registro, como en el motor (gobernador sin documento citado, municipio sin informe al SRFT, revisión de la UEC a la ASF, informes de las auditorías superiores estatales): falta redactar su porqué y su responsable. El radar municipal del motor no cuenta las «Alcaldías» de la CDMX (`radarMunicipal`); la página nueva sí.
- **Calculadora Cívica: tres aplicaciones en página propia y la flecha Atrás (13-10-2026, pedido del autor).** La herramienta dice «aplicaciones» (`HERR_PALABRA`). «Tu estado de cuenta», «Tú contra ellos» y «El reloj de la deuda» ya no cargan el motor en un marco: las arman `cc_ticket.py`, `cc_compara.py` y `cc_reloj.py` (en `INSP_NATIVAS`; `insp_vista.py ccticket` también sirve) con `cc-*.js`/`cc-*.css`. El sueldo se comparte entre ellas en localStorage, clave `auditavision_cc_sueldo` = `{monto, periodo, tipo}`. **Flecha Atrás:** dentro del marco (`modo-visor`) el motor apilaba historial con `pushState` al cambiar de pestaña, y Atrás volvía dentro del marco (p. ej. a «Números») en vez de salir de la página; ahora en el visor usa `replaceState` (`audit-engine.js`), lo que arregla también Megaobras y Costo Ambiental, que siguen con marco. **Correcciones frente al motor:** reloj de la ASF = suma de `estados[].asfMontoObservado` = 59,362.8 mdp (`derivado`), no los 46,122.0 de la base; la deducción anual de honorarios se divide entre 12; «Tú contra ellos» compara siempre neto contra neto; el folio del estado de cuenta es `AV-EC-` + 8 caracteres de su huella SHA-256 y se verifica en la misma página con `?verifica=`; porcentajes del reparto `derivado`, montos del PEF `oficial`. **Pendiente:** `herramienta-inspector-verifica.html` aún no reconoce los folios `AV-EC-` (habría que mandarlos a la página del ticket); el reloj de la ASF viejo sigue en `audit-database.js` y en el motor; la fecha del PEF 2026 aparece como DOF 21-11-2025 en el motor e `integrar_comparador.py` y como 28-11-2025 en `ref-pef2026`: falta confirmar cuál es; el sobrecosto de las 13 obras es `derivado` aunque 5 tengan componentes `pendiente` (decisión del autor).
- **Inversión y Megaobras: sus cuatro aplicaciones en página propia (13-10-2026, pedido del autor).** La herramienta dice «aplicaciones» (`HERR_PALABRA`). «El pulso del gasto», «Sector e industria», «Las obras de cada sexenio» y «De cero al resultado» ya no cargan el motor en un marco: las arman `mo_pulso.py`, `mo_sector.py`, `mo_sexenios.py` y `mo_cero.py` (en `INSP_NATIVAS`; `insp_vista.py <clave>` genera una sola) con `mo-*.js`/`mo-*.css`. Cifras cotejadas contra el motor con las mismas entradas. Novedades: modo «Solo lo documentado» (pulso y cero), CSV, filtros en la liga `?industria=&mandato=&orden=` y ancla `#obra-<id>` (sector), ficha `#sexenio-<id>` y comparador `#comparar-<a>-<b>` (sexenios), mesas que se revelan renglón por renglón con la operación a la vista (cero). Las anclas cambian con `replaceState`. **Correcciones frente al motor:** las sumas y cifras sin chip ahora llevan `derivado` con su operación y los `pendiente` llevan `data-pend` a su ficha (`obra-<id>`, `reloj-megaobras`, `costo-unitario-megaobras`, `tren-maya-ficha`); el motor decía «déficit de operación de las 13 obras», pero solo 3 tienen documento, AIFA no tiene déficit y el Ramo 34 es apoyo, no déficit: se dice componente por componente; la mesa 3 de «De cero» ya no suma el sobrecosto (saldo 1988-2024) con la pérdida de un año (flujo); el divisor de contribuyentes es el padrón SAT con fuente (88,085,311), no el 88.1 sin fuente de `macro`; la operación de las obras sale de la Cuenta Pública 2024 (tomo VII) y el Ramo 34, no «de los informes de la ASF»; el costo por sexenio separa la parte con documento de la pendiente; la deuda de las 32 entidades es `derivado`. **Pendiente:** el 72.5 % del costo del conjunto ($2.35 de los $2.77 billones del sobrecosto) descansa en cifras `pendiente` (FOBAPROA, FARAC, AIFA + NAIM, Búnker, Dos Bocas): el autor debe decidir si esos totales siguen como `derivado`; las fichas `obra-*` del Registro solo citan la página de sector (faltan sexenios, cero y pulso en «dónde aparece»); dos chips `pendiente` de sector sin ficha propia («hallazgo ASF sin cotejar», «el costo en vivo no corre»), hoy sin obras que caigan en ellos; el texto fijo de `megaobrasOficialBase` del motor dice $2,194.4 mdp y el cálculo da $2,561.4.
- **Costo Ambiental en página propia y la portada al día (16-10-2026, pedido del autor).** «El reloj y el año», «Tu ticket en negativo», «Basura y protección» y «El PIB no alcanza» las arman `am_reloj.py`, `am_ticket.py`, `am_basura.py` y `am_pib.py` (en `INSP_NATIVAS`) con `am-*.js`/`am-*.css`; **ya ninguna página de herramienta carga la portada en un marco**. El ticket comparte el sueldo con la Calculadora (`auditavision_cc_sueldo`). **Correcciones:** agotamiento por componente con los montos oficiales de la Tabla 1 del comunicado 150/25 del INEGI (CEEM 2024): hidrocarburos 66,319, forestales 40,848, agua subterránea 36,853 mdp (antes se derivaban de porcentajes redondeados); «casi seis pesos» de daño por peso de protección (5.94); las emisiones al aire son 60.3% de la cuenta, no «casi dos terceras partes»; el gasto en protección es del sector público consolidado, no «de todo el país»; el remate del huachicol separa lo `oficial` de lo `derivado`; con PIB negativo el veredicto ya no dice «crece»; el PINE se escribe «25.7 billones» como lo publica el INEGI, y el capital fijo y el PIN que se restan de él van como rango. **Portada (motor y base):** reloj de la ASF = suma de las 32 entidades (59,362.8 mdp); el texto de la pérdida de megaobras se calcula (2,561.4 mdp; AIFA sin déficit; el Ramo 34 es apoyo, no déficit); `radarMunicipal` cuenta las Alcaldías de la CDMX; la mesa 3 de «De cero» ya no suma saldo con flujo y usa el padrón SAT con fuente; la operación de las obras cita la Cuenta Pública 2024 (tomo VII) y el Ramo 34, no a la ASF. El verificador del Modo Inspector reconoce los folios `AV-EC-` y manda la liga completa a «Tu estado de cuenta». Las fichas `obra-*` y `reloj-megaobras` del Registro citan las cuatro aplicaciones de Megaobras. **Pendiente:** el reparto ambiental por habitante usa 134.4 millones (como el motor), no los 134,407,258 exactos; 25.7 ÷ 33.5068 da 76.7% y el INEGI publica 76.6% (falta integrar el consumo de capital fijo exacto: falta de la plataforma); siguen sin datos los permisos ambientales de las megaobras (SEMARNAT) y las concesiones de la basura (microdatos del censo municipal del INEGI); la frase «El dato de 2025 lo publica el INEGI en diciembre de 2026» no tiene fuente propia.
- **Contexto dimensional, en seis páginas (12-10-2026, pedido del autor).** El «Estado de Cuenta Cívico» se llama ahora **Contexto dimensional** (🧭); su archivo sigue siendo estado-de-cuenta.html para no romper enlaces. Su página queda con seis tarjetas y cada una abre la suya: contexto-dimensional-presupuestaria, -financiera, -social, -ambiental, -renglones y -descarga (.html), con anterior y siguiente; la última vuelve a la portada. Las anclas viejas (#social, #financiera…) llevan a su página. `estado_cuenta.generar()` escribe las siete. Se cambió el nombre visible en Cuentas claras, el recorrido de Números, Comunidad (compartir), el índice general, el Registro de pendientes, el estado de resultados y el motor (enlace del bloque eb-cuenta-federal). El «Estado de Cuenta Cívico» personal de la Calculadora (la imagen que se descarga) es otro y conserva su nombre. Ninguna cifra cambió.
- **Lo que vive en Herramientas sale de Números (12-10-2026, pedido del autor).** Cuentas claras queda con cinco tarjetas en dos grupos: se quitó el grupo «🧰 Viven en Herramientas» (Qué encontró la ASF, Expedientes, El reloj de la deuda) y el recuadro final «🧮 Y a ti, ¿cuánto te toca? · Abrir la calculadora» (`numeros_cierre()` se borró). El Estado de Cuenta Cívico perdió su sección «👤 Tu aportación» (Tu estado de cuenta y Tu ticket en negativo) y su entrada ya no habla de dos vistas. Todo eso sigue en Herramientas, sin cambios.
- **El estado de resultados, en página propia (12-10-2026, pedido del autor).** numeros-estado-de-resultados.html ya no carga el auditor en un marco: la escribe `herramientas/resultados_modulo.py` desde `cuentaFederal2024` y `cuentas_ecologicas`, con las cifras en el HTML, y `resultados.js` solo mueve las seis pestañas (presupuesto, actividades, flujos, situación, resultados sociales y conciliación; `#actividades` y demás abren la suya) y el «¿Cuánto crees?»: de cada $100 de ingresos de la gestión, $17.47 se fueron en intereses (933,408.4 ÷ 5,341,758.1 × 100, `derivado`). Arriba, «Si el Gobierno Federal fuera una empresa…» empata cada estado con su equivalente, y un medidor dice cuántas cifras ya tienen documento (3 de 17, `derivado`). Las becas S072 y S311 muestran lo devengado contra lo aprobado (85.4% y 84.6%, `derivado`). Ninguna cifra es nueva; los pendientes llevan su ficha (cp2024-tomo2, prog-montos-*, prog-resultados). El bloque eb-cuenta-federal del motor sigue en la portada, sin cambios.
- **Tablero: el dinero primero (12-10-2026, pedido del autor).** En Ingresos, Inversión y Costo del gobierno, la comparativa «lado a lado» abre con la suma en pesos (pestaña 💵) y en **pesos de hoy** por omisión. Cada renglón da cuánto por año, en promedio (suma ÷ años con dato, `derivado`), cuánto en todo el sexenio, y el % del PIB como escala. Botones «Por año» / «Todo el sexenio» y las cuatro monedas; las cifras cuentan desde cero. Salinas (falta 1989) da su promedio con 1990–1994 y su suma sigue `pendiente`; en euros, Zedillo solo con 2000. Ninguna cifra cambió.
   - *Cotejo documental de 25 fuentes (28-09-2026)*: Continúa en proceso conforme al catálogo de trazabilidad de `investigaciones/entregas/README.md`.

- **El pulso del gasto: sus cuatro partes en página propia (17-10-2026, pedido del autor).** La página de la aplicación 1 (`herramienta-megaobras-pulso.html`) queda con el arranque, el contador y cuatro tarjetas; cada tarjeta abre su página: `herramienta-megaobras-pulso-cifras.html` (las cuatro cifras), `-ritmo.html` (la temporalidad), `-composicion.html` (de qué está hecho el total y las 13 obras) y `-calculo.html` (cómo se calcula). Las arma `mo_pulso.py` (`PARTES`, `subpaginas()`); `apartados.insp_subpaginas()` las escribe para cualquier aplicación nativa que traiga `subpaginas()`, con migas «… › El pulso del gasto › parte». `mo-pulso.js` solo pinta lo que hay en cada página; las anclas viejas (`#mpCifras`, `#mpRitmo`, `#mpCompo`, `#mpComo`) redirigen con `location.replace`, y la burbuja del contador ya no apila historial. Los chips del pulso suben a 12 px. `pendientes.py` lista las cuatro partes en «dónde aparece».

- **Megaobras: cifras pendientes deducidas de documentos oficiales y «La cuenta de cada obra» (17-10-2026, pedido del autor).** `herramientas/integrar_cuenta_megaobras.py DIRECTORIO` toma los renglones investigados con su documento, página y huella (JSON con el esquema de la investigación: obra, campo, estado, valor o min/max/medio, operación, fuentes) y escribe `simulador_megaobras.cuenta` (por obra: primer presupuesto documentado, ingresos esperados y reales, gasto de operación, intereses, resultado, costo hundido y datos de uso; estados `oficial`, `derivado` —con `min`/`max`/`medio` si es rango—, `pendiente` con responsable, y `no_aplica` con su porqué). Limpia la jerga de trabajo de las notas (`LIMPIEZA`). Corrige además los campos principales de seis obras y guarda las cotas en `rangos_campos`: **AIFA + cancelación del NAIM** (aprobado 79,305.0 oficial, ASF 66-GB; costo entre 96,214.5 y 107,656.0, medio 101,935.3 = AIFA 74,480.2 derivado de la ASF + cancelación entre 21,734.3 y 33,175.8; ya no suma los 79,907.7 de obra del NAIM de 2014-2018 ni los 88,107 sin documento); **Dos Bocas** (aprobado entre 154,098.4 = 8,000 MUSD × FIX 19.2623 del 9-05-2019 y 160,000.0, dichos ese día en la versión estenográfica; sobrecosto entre 123.7 % y 132.3 %); **Búnker** (contrato 347.4; costo entre 236.9 y 289.1 con IVA de 15 %, ASF 1053; los 1,200/3,346 no tenían documento); **Fertinal** (aprobado 12,532.0, acuerdo CA-209/2015: +4.7 %); **FOBAPROA** (552,300 presentado al Congreso; costo comprometido 1,734,494.3 = Ramo 34 a ahorradores 1999-2025 + pasivos netos del IPAB 2025); **FARAC** (indemnizaciones 57,756.6, ASF 99; costo documentado mínimo 153,851.5 = indemnizaciones + pérdida acumulada 1997-2017; 23 concesiones, no 52). Ya no queda ningún costo `pendiente`: total 3,064,992.6, aprobado 1,139,993.2, sobrecosto 168.9 %. Nueva quinta parte del pulso, `herramienta-megaobras-pulso-cuenta.html` (#cuenta-<id>), con la suma de resultados documentados y los intereses. `pendientes.py` crea fichas `cuenta-<id>` y conserva `obra-<id>` cuando hay rango. **Pendiente para el autor:** (1) el sobrecosto de FOBAPROA y FARAC se calcula, pero no es sobrecosto de obra (mezcla pagos de décadas con saldos); conviene separar los rescates o rotularlos aparte; (2) el FARAC sigue con «Carlos Salinas / Ernesto Zedillo»: la ASF fecha el rescate en 1997 (Zedillo); cambiarlo mueve la nota de 13/14 obras de la portada y de Sexenios; (3) la regla única de presupuesto (primer monto documentado) cambiaría Tren Maya a 139,072.4 (+257.6 %), Toluca a 34,114.9 (+350.5 %) y Tula a 7,613.3: hoy se muestra en la cuenta, no en la cifra principal; (4) el contador sigue con el Ramo 34 del FOBAPROA; la investigación propone su resultado sin transferencias (−84,900.5 en 2024); (5) la versión estenográfica del 9-05-2019 (gob.mx) no tiene huella guardada; (6) del informe de uso (D1-D22) siguen abiertos los de Sector: dos «costos en vivo» con intereses supuestos, ceros falsos al reordenar, contadores sin pausa y chips no enfocables.
- **Megaobras: decisiones del autor sobre el método (17-10-2026).** `herramientas/integrar_decisiones_megaobras.py` (corre después de `integrar_cuenta_megaobras.py`; idempotente). **(1) Los rescates van aparte:** FOBAPROA y FARAC llevan `tipo: rescate` y `sobrecosto_etiqueta` («Crecimiento frente al pasivo presentado en 1998» / «frente a las indemnizaciones de 1997»). `totales_consolidados` mide las 11 obras (costo 1,176,646.8; aprobado 529,936.6; sobrecosto 122.0 %) y guarda `rescates` (1,888,345.8 frente a 610,056.6) y `con_rescates` (3,064,992.6). Pulso (cifras con bloque «Aparte: los 2 rescates», composición), Sector («todas las industrias» suma solo obras; la loseta de rescates dice «Se cuentan aparte»), De cero (la mesa 1 y el inventario sin rescates; la mesa 2 sí los suma), Sexenios (cada sexenio dice qué parte de su costo son rescates), el reloj de la Calculadora («Construir las 11 obras…») y `simAgregados()` del motor siguen la misma regla. **(2) El FARAC va con Ernesto Zedillo (1994–2000):** el rescate se hizo en 1997 (ASF CP 2015 aud. 99; CP 2017 aud. 96, p. 6); el campo `antecedente` dice que las concesiones se otorgaron con Salinas. Ya no se cuenta dos veces: el reparto por sexenio suma 13 y Salinas queda sin obras evaluadas. La nota de la portada (`tplConteoObras`, botón «Por qué los rescates van aparte y el FARAC con Zedillo») y la de Sexenios se reescribieron. **(3) Base del presupuesto:** no cambia la cifra principal; `herramientas/mo_base.py` arma el desplegable «¿Con qué presupuesto se mide?» en la cuenta de cada obra y en la ficha de Sector: primer monto documentado, su fuente y el sobrecosto medido contra él (Tren Maya +257.6 %, AIFA +39.4 %, Tren México-Toluca +350.5 %, Tula −85.2 %). **(4) El contador** toma del FOBAPROA lo que el Fondo pierde antes del apoyo del presupuesto: déficit 2024 (22,411.1) + Ramo 34 que recibió (62,489.4) = 84,900.5 `derivado` (IPAB, estados financieros dictaminados 2025, PDF p. 33; `operacion_oficial.obras.fobaproa.resultado_sin_transferencias`, fuente `ipab_ef25`). Pérdida anual documentada: 2,561.4 + 84,900.5 = **87,461.9 mdp, $2,773.40 por segundo**. Corregido además el texto «214.1 %» del FOBAPROA (es 214.0 %). **Pendiente:** los defectos de uso de Sector (D1-D22: dos «costos en vivo», el de Sector con intereses supuestos; ceros falsos al reordenar; contadores sin pausa; chips no enfocables) y la versión estenográfica del 9-05-2019 sin huella guardada.
- **Contrasta una nota lee la nota (pedido del autor, 21-10-2026).** La aplicación 5 del Modo Inspector ya no pide elegir la cifra a mano: el lector pega la liga de una noticia, revista o publicación (o su texto) y la página la lee, encuentra sus cifras en pesos, las empata con el catálogo y da un veredicto con el documento de cada una. Tres pasos, cada uno en su página: `herramienta-inspector-nota-liga.html`, `-cifras.html` y `-veredicto.html` (las genera `herramientas/insp_nota.py`; el código, `assets/auditor/js/insp-nota-lee.js`). Cómo funciona:
- **Contrasta una nota en una sola página, con sello (pedido del autor, 21-10-2026, el mismo día).** Los tres pasos se juntaron en `herramienta-inspector-nota.html`: arriba el portal (pestañas «Pegar la liga» / «Pegar el texto» y el botón Verificar) y, debajo, el veredicto. Las páginas `-nota-liga.html`, `-nota-cifras.html` y `-nota-veredicto.html` redirigen ahí con su `?liga=` (`apartados.REDIRECCIONES`). El veredicto es un dictamen con el sello de Auditavisión, como los estados de cuenta: encabezado con logo, folio `VN-AAAAMMDD-XXXXXXXX` y fecha, y la leyenda «No es un documento oficial»; al pie, el sello circular, la versión, la huella SHA-256 del veredicto (nota, empates y resultados: si cambia un empate, cambian huella y folio) y la leyenda completa. El folio no se registra en «Verifica un estado de cuenta». Lleva semáforo (rojo, ámbar, verde), el medidor animado, las cuentas como filtros, la justificación de cada cifra con su selector «¿No es esta la cifra oficial? Cámbiala» y «Lo que tenemos sobre este tema» (`insp_nota.TEMAS`, enlaces internos que la generación comprueba). **Notas fuera de tema:** si la nota no suma 2 puntos de palabras de finanzas públicas (`insp_nota.FISCAL`) y no se contrastó ninguna cifra, dice «Esta nota no se identifica dentro de los supuestos ni de las investigaciones de la plataforma» y no la califica; si habla de dinero público sin cifras, o con cifras fuera del catálogo, lo dice, sin veredicto. De un video se lee el título y la descripción, no lo que se dice: se pide la transcripción. **Navegación compacta:** la aplicación declara `NAV_COMPACTA` y `apartados.insp_nativa()` cambia el pie grande (anterior/siguiente en tarjetas, las ocho aplicaciones en chips y las otras herramientas) por una fila de cuatro botones (`nav_compacta()`: anterior, todas las aplicaciones, siguiente, índice) y quita del pie de página «Volver al auditor / Índice general» (`pie_corto`). El mismo día el autor la pidió para **todas las aplicaciones**: `apartados.pagina()` pone la fila compacta (`nav_de_pagina()`) en cada aplicación de las cuatro herramientas (también las que son página aparte: simulador, Expedientes, Servicios, Crisis ambientales, Verifica), en sus subpáginas (El pulso del gasto, el catálogo de la ASF: «← Volver» a su aplicación, sin anterior ni siguiente) y en Pregúntale al Auditor; `expedientes.py` la toma de ahí. Las portadas de las herramientas y Grandes investigaciones conservan la navegación grande: son índices, no aplicaciones. **Cómo leemos la nota** ya no es un desplegable: es un botón que abre la ventana lateral de la plataforma (plantilla `tplInComo`, la abre `apartados.js` por `button[data-cajon]`; con `#como-leemos` se abre al cargar), en siete secciones.
- **Qué encontró la ASF: un capítulo por página (pedido del autor, 21-10-2026).** La portada de la aplicación (`herramienta-inspector-asf.html`) quedó con el arranque (lo por aclarar, la cuenta regresiva) y el índice de los nueve capítulos; cada tarjeta abre su página: `herramienta-inspector-asf-calendario`, `-cifras`, `-serie`, `-donde`, `-estado`, `-acciones`, `-2025`, `-catalogo` (la que ya existía) y `-documentos.html`. Las arma `insp_asf.subpaginas()` con `capitulos()`; el JSON `iaDatos` va solo en serie, estado y documentos, e `insp-asf.js` ya no lo exige para la cuenta regresiva. El pie de cada capítulo es `apartados.nav_capitulos()` (clave `cap_nav`): capítulo anterior, los 9 capítulos, capítulo siguiente, índice. Los enlaces viejos con ancla (`#ia-estado`, `#ia-estado-t`…) se redirigen a la página del capítulo desde la portada (`data-ia-ancla`). La portada pasó de 93 KB a 23 KB.
- **Inversión y Megaobras en capítulos, con tabla general en vivo (pedido del autor, 21-10-2026).** La tarjeta de Herramientas ya no dice «Simulador de Inversión y Megaobras», solo «Inversión y Megaobras». Las cuatro aplicaciones (el pulso, sector e industria, los sexenios y de cero al resultado) repetían contador, cifras de conjunto, filtros y enlaces «Sigue con»: se fundieron en una sola herramienta de **9 capítulos** agrupados por pregunta (`herramientas/mo_capitulos.py`, de donde salen los temas de `HERRAMIENTAS`, el lema «capítulo k de 9» y el pie `nav_capitulos()`): ¿En qué invirtió cada presidente? (1 Los seis sexenios, 2 La tabla general en vivo), ¿Cuánto costó? (3 De cero al resultado, 4 Las cuatro cifras y los rescates, 5 Obra por obra por industria, 6 De qué está hecho el total), ¿Gana o pierde? (7 La cuenta de cada obra, 8 El ritmo de la pérdida) y ¿Cómo se sabe? (9 Cómo se calcula). Las direcciones de las páginas no cambiaron. **Nuevo:** `herramienta-megaobras-tabla.html` (`herramientas/mo_tabla.py`, `mo-tabla.js`, `mo-tabla.css`): por sexenio, cada obra con su aprobado, costo y sobrecosto, y su resultado del año publicado (el mismo renglón `resultado_anual_mdp` que suma La cuenta de cada obra) con contador en vivo: verde si gana, rojo si pierde, gris con su porqué si no se publica o no aplica. No hay cifra nueva. La portada de la herramienta lleva tres cifras clave, el contador de la balanza y las tarjetas de capítulo (`apartados.megaobras_portada()`). La página del pulso (`herramienta-megaobras-pulso.html`) redirige a la portada; sus partes las genera `apartados.megaobras_pulso()` sin la fila de partes; sus anclas viejas (`#mpCifras`…) llevan a su capítulo. Se quitaron los «Sigue con» de cero, sector y sexenios. **Verificación, pendiente de decisión del autor:** (a) la «pérdida anual» del contador del pulso y de la mesa 2 (87,461.9 mdp: FOBAPROA antes del Ramo 34 + Tren Maya) no usa los resultados oficiales publicados de Dos Bocas (−1,473.7, 2024) ni de Fertinal (−3,600.1, 2024), que sí entran en La cuenta de cada obra (−25,429.2): son conceptos distintos (déficit antes de transferencias contra resultado del ejercicio) y conviene decirlo o unificarlo; (b) el FOBAPROA aparece con −84,900.5 (pérdida 2024 antes del apoyo) y con −7,519.9 (resultado 2025): mismo motivo; (c) la «simulación en vivo» de Sector (PEF 2026 + intereses a tasa implícita) es otra medida más y sus intereses son estimación propia; (d) aún quedan cuatro maneras de filtrar por industria y presidente (sexenios, sector, cero, composición) que podrían ser una sola.
- **Inversión y Megaobras en cuatro aplicaciones (pedido del autor, 21-10-2026, el mismo día).** Objetivo que dio el autor: que el lector haga su propia investigación, con filtros, contadores, simuladores y tablas, de lo que invirtió cada sexenio, el resultado de cada obra, sus estados de resultados, lo que nos sigue costando, el daño ambiental y los rescates. Los 9 capítulos se fundieron en 4 aplicaciones (`herramientas/mo_capitulos.py`, lema «aplicación k de 4», pie «Las 4 aplicaciones»): **1 En qué invirtió cada presidente** (`herramienta-megaobras-tabla.html`): el contador y las tres cifras clave que tenía la portada (el «simulador inicial»), la tabla general en vivo y, debajo, los seis sexenios (`mo_sexenios`, sin su portadilla: línea del tiempo, sexenio en detalle y comparación). **2 Obra por obra, por industria** (`herramienta-megaobras-sector.html`): sector + «De qué está hecho el total» (`#mpCompo`). **3 Las cuatro cifras y los rescates** (`herramienta-megaobras-cero.html`): las cuatro cifras con los rescates (`#mpCifras`, `#mpRescates`) arriba y De cero al resultado debajo. **4 La cuenta de cada obra y el ritmo de la pérdida** (`herramienta-megaobras-pulso-cuenta.html`, el nombre lo puso el agente: el autor no lo dio). **«¿Cómo se calcula?»** dejó de ser capítulo: es un botón que abre la ventana lateral (`mo_pulso.cajon_calculo()`, `button[data-cajon]` de apartados.js) en las cuatro aplicaciones y en la portada; con `#como-se-calcula` se abre al cargar. La portada ya no lleva contador: dice qué se puede investigar (seis accesos, entre ellos la huella ambiental de las megaobras en Costo Ambiental) y abre las 4 aplicaciones. Redirigen (REDIRECCIONES, el ancla viaja): `-sexenios` → tabla, `-pulso-cifras` → cero#mpCifras, `-pulso-composicion` → sector#mpCompo, `-pulso-ritmo` → pulso-cuenta#mpRitmo, `-pulso-calculo` → cero#como-se-calcula. No hay cifra nueva. Después (pedido del autor, sello 20261021r) las obras de cada sexenio se ven una sola vez, en la tabla general: se quitó «El sexenio que elijas, en detalle» (`#mxFicha`, `mo_tabla._sexenios()`); tocar un sexenio en la línea del tiempo, o llegar con `#sexenio-<clave>`, lleva a `#mt-sx-<clave>` de la tabla (`mo-sexenios.js`).
- **«Haz tu propia investigación» es la aplicación 1 de Megaobras y las cuatro herramientas usan el mismo formato (pedido del autor, 21-10-2026, sello 20261021s).** El cuadro que abría la portada de Inversión y Megaobras es ahora `herramienta-megaobras-investiga.html` (`herramientas/mo_investiga.py`, `mo-investiga.js`, `mo-investiga.css`), así que la herramienta tiene **5 aplicaciones** (las otras corren de la 2 a la 5). Es un investigador en tres pasos: eliges presidente (o los seis) y una de seis preguntas (en qué invirtió, si gana o pierde, su estado de resultados, cuánto nos sigue costando, los rescates, la huella ambiental) y lees la respuesta con su chip y el enlace a la aplicación donde se investiga a fondo. Las 42 respuestas se escriben en Python con las mismas funciones de `mo_tabla` y `mo_base`; «al mes» y «al día» son el resultado del año ÷ 12 y ÷ 365 (derivado); las obras de construcción son `am_basura.OBRAS_FISICAS`. El ancla `#inv-<presidente>-<pregunta>` abre una respuesta y se puede copiar. No hay cifra nueva. **El formato, en las cuatro herramientas:** `apartados.apps_rejilla()` pinta las aplicaciones de Megaobras, Calculadora Cívica, Costo Ambiental y las Grandes investigaciones del Modo Inspector como tarjetas en dos columnas («Aplicación k», ícono y nombre, qué hace, su cifra o su frase y «Abrir →»; estilos `.herr-app*` en apartados.css), con el título «N aplicaciones · cada una abre su página». En Megaobras cada tarjeta lleva su cifra (`mo_tabla.cifras()`); en las demás, su frase (la frase que comparten varias, como «Busca y verifica», no se repite). El pie de cada aplicación dice «← Aplicación anterior · Las N aplicaciones · Aplicación siguiente →» (`nav_compacta`). Pendiente: dar a las tarjetas de Calculadora, Costo Ambiental y Modo Inspector una cifra propia, como las de Megaobras, cuando cada aplicación tenga una cifra con fuente que la resuma.
- **Las aplicaciones de cada herramienta vuelven a listarse numeradas y en vertical (pedido del autor, 22-10-2026, sello 20261022a).** Las tarjetas en dos columnas del 21-10-2026 se quitaron: Inversión y Megaobras, Calculadora Cívica, Costo Ambiental y el Modo Inspector usan otra vez la ruta `herr-ruta` (número, ícono, frase, nombre, qué hace y «Abrir»), con el título «Las N aplicaciones». `apps_rejilla()` en `apartados.py` produce esa lista; la portada de Megaobras conserva su botón «¿Cómo se calcula?» y ya no muestra la cifra de cada aplicación. Se mantienen la aplicación 1 «Haz tu propia investigación» y el pie «Aplicación anterior · Las N aplicaciones · Aplicación siguiente».
- **Calculadora Cívica, aplicación 1: las cuatro cuentas en páginas propias (pedido del autor, 22-10-2026, sello 20261022b).** `herramienta-calculadora-ticket.html` solo presenta la calculadora y cuatro tarjetas numeradas; cada una abre su página: `-ingreso`, `-retienen`, `-reparto` y `-estado` (`cc_ticket.subpaginas()`, pie «Cuenta anterior · Las 4 cuentas · Cuenta siguiente»). Cada página lleva la calculadora entera con solo su parte a la vista; el ingreso pasa de una a otra por el almacenamiento del navegador (como antes, nunca sale de él). Sin ingreso, las cuentas 2 a 4 piden escribirlo o usar el salario mínimo oficial. Las ligas de verificación viejas (`?verifica=`) y las anclas `#ctPaso1-4` de la portada redirigen a su página. Las cuatro tarjetas van en fila con flechas (`.ct-flujo`, sello 20261022c), para no confundirlas con la lista vertical de las aplicaciones: cuatro en escritorio, dos por renglón en tableta y celular.
- **El Estado de cuenta administrativo pasa de Datos a la Calculadora Cívica (pedido del autor, 22-10-2026, sello 20261022d).** Es su quinta aplicación (🏛️, tema `radar-estado-de-cuenta.html` en `HERRAMIENTAS`): la dirección no cambia porque va impresa en los sellos de los PDF. Sus migas son Inicio › Herramientas › Calculadora Cívica y su pie, el de las aplicaciones («Aplicación anterior · Las 5 aplicaciones»). Datos queda con tres tarjetas (Radar hacendario, Datos abiertos, Informes oficiales); su ancla vieja `#estado-de-cuenta` lleva a la página. Las ligas «Sigue con la calculadora» de Tu estado de cuenta y Tú contra ellos ya la incluyen.
- **Costo Ambiental reestructurada; su parte informativa pasa a Datos → Medio ambiente (pedido del autor, 22-10-2026, sello 20261022e).** La herramienta se queda con lo que el lector calcula y audita, en seis aplicaciones: 1 Tu ticket en negativo, 2 El reloj y el año, 3 ¿Cuánto del crecimiento es real? (`herramienta-ambiente-pib.html`, ahora solo el simulador del PINE), 4 Simulador de inversión ambiental (nueva, `am_inversion.py`: en cuántos años alcanzaría el gasto en protección al costo del daño con el supuesto del lector, y los intereses o la deuda nueva de 2026 medidos en años del presupuesto de cada órgano del Ramo 16), 5 Auditor ambiental (nueva, `am_auditor.py`, como el Auditor de entes públicos: ficha del ramo y de sus siete órganos con PEF 2026, avance al 2T, proyecto 2027, Cuenta Pública 2025 y calendario del ramo, lo que observó la ASF en el sector —por sector, no por órgano— y el expediente El Cuchillo II de la Conagua; preguntas que deja la ficha, CSV y enlace #aa-<ur>) y 6 Crisis ambientales. Datos tiene una cuarta tarjeta, 🌎 Medio ambiente (`datos_ambiente.py`, `datos-medio-ambiente.html`), con nueve páginas `datos-ambiente-*.html` en cuatro grupos: el PIB que no alcanza, qué se acabó y qué se ensució, lo que se gasta en proteger, la basura, el presupuesto ambiental, la huella de las megaobras, las leyes, puntos ciegos y quién lo mide. No se reescribió ninguna cifra: cada página toma su bloque del HTML de `am_basura.construir()` y `am_pib._completo()` (`am_cortes.py`); `am-pib.js` ahora arranca cada parte solo si está. `herramienta-ambiente-basura.html` redirige a la portada de Medio ambiente y sus anclas (#abLeyes…) a su página. Pendiente de proponer al autor: un «Contrasta una nota ambiental» y las metas oficiales de clima (NDC) contra lo cumplido, que necesitan documentos que la plataforma aún no integra.

- **«Pregúntale al Auditor» contesta como chat (pedido del autor, 23-10-2026, sello 20261023a).** «Que funcione literalmente como un chat… que responda a cualquier pregunta sobre márgenes, porcentajes, estados, municipios», en lenguaje coloquial, sin sellos ni fichas técnicas salvo que el lector las pida. Ahora la respuesta es una burbuja corta con la cifra, qué quiere decir y su lugar; «📎 De dónde sale» (un `<details>`) muestra los chips a la vista y las fuentes a un toque; la nota técnica sellada (folio y huella SHA-256, la misma de antes) solo se arma con el botón «🧾 Generar ficha técnica». Archivos: `assets/auditor/js/asistente-charla.js` (nuevo) entiende la pregunta y arma la respuesta: estados (deuda, semáforo, ILD, ASF, radar, Ramos 28 y 33, por habitante, dependencia, recaudación propia, población; lugar, ranking, top N, «el peor/el mejor», comparación de 2 a 4 estados, total y porcentaje del total, y por habitante derivado para deuda y ASF), municipios (EFIPEM 2024 desde `municipios-efipem.js`, que la página ahora carga: ingresos, predial, FORTAMUN, FAIS, propios, dependencia, lugar en su estado, homónimos), sueldos de los cargos contra el salario mínimo, las siete administraciones (deuda, intereses, gasto, ingresos, inversión, ASF), el país (SHRFSP, costo financiero y deuda nueva al día, ingresos, gasto), el presupuesto 2026 de 36 dependencias (con siglas: Sedena, IMSS, Pemex…), cuántos municipios tiene cada estado y una calculadora (X % de Y, qué porcentaje es, cambio porcentual, división, producto, suma y resta). Entiende apodos y siglas (CDMX, Edomex, chilango, regio…) y palabras como «lana», «varo», «feria», «se clavaron», y recuerda la pregunta anterior («¿y Nuevo León?», «¿y por habitante?», «¿y el que menos?», «compáralo con Jalisco», «¿y su predial?»). Lo que no entiende pasa a la búsqueda de siempre (`asistente.js`), que ahora también contesta en corto (glosario, pendientes, páginas, expedientes, cifras del catálogo) y prefiere el glosario en «¿qué es…?» y el caso sobre su pendiente en un nombre a secas. Regla editorial intacta: no escribe cifras propias; todo lugar, suma, diferencia, porcentaje o «al día» va como `derivado` con su operación; la CDMX sin dato del INEGI sale `pendiente`; los sueldos de gobernadores y alcaldes, que la plataforma no integra, se dicen como faltantes de la plataforma, sin culpar a nadie. `asistente.py` escribe en la base el bloque `dat` (`_charla()`: métricas con estado y fuente, los 32 estados, cargos, salario mínimo y administraciones) y ya no los municipios compactos. Se ocultan los ejemplos al empezar la plática, hay indicador de «escribiendo» (sin animación con `prefers-reduced-motion`) y en escritorio el hilo corre por dentro. **No es una IA generativa**: una conversación abierta como la de un asistente comercial necesitaría un modelo de lenguaje con servidor y llave de API, que GitHub Pages no tiene; sigue como decisión pendiente del autor, con la regla de que no escriba cifras fuera de las fichas.

- **El bot como auditor de toda la plataforma; ahora verifica (pedido del autor, 23-10-2026, sello 20261023b).** El autor fijó el objetivo: el bot integra todas las herramientas, datos, estadísticas, estados de cuenta, sueldos, márgenes, porcentajes, presupuestos, impuestos, glosario y referencias; localiza, interpreta, verifica y lo muestra en sencillo, con la ficha técnica solo si el lector la pide. Quedó como regla en AGENTS.md §5 ter. Hecho hoy: (1) **verifica afirmaciones**: «¿es cierto que…?», «dicen que…», un párrafo con montos o la liga de una nota (que manda al verificador de notas con `?liga=`). El motor de «Contrasta una nota» se apartó a `assets/auditor/js/verificador.js` (`window.AuditorVerifica`), que ahora cargan la aplicación y el bot; el bot recibe el catálogo con sus claves en `dat.nota`. Si el catálogo no empata la cifra, el bot contesta la pregunta de fondo y juzga la cifra contra ese dato (`juzgaDicho`, mismos umbrales: redondeo, «más de», aproximación, error de unidades, ±10 %), con «al día» y «al año»; si no hay documento, lo dice sin llamarlo falso y lo anota en «Lo que aún no sé». (2) Entraron al bot los **27 artículos de ley cotejados** (`preceptos_legales`, tipo `ley`) y las **14 preguntas del Diccionario con referencias** (`preguntas_casillas`, tipo `faq`); las `faqs` viejas no entraron porque no citan documento. (3) La fuente principal se ve sin abrir nada («📎 Fuente: … y N más»). **Plan del bot (decisión del autor en cada fase):** fase 2, consultar portales externos en vivo (Transparencia Presupuestaria, DOF, ASF, INEGI, Banxico): necesita un servidor intermedio, porque el navegador no puede leer esos portales directo; fase 3, una capa de IA que redacte y entienda preguntas libres con las fichas como única fuente (servidor + llave de API + costo por pregunta); fase 4, aprender de las preguntas: hoy «Lo que aún no sé» vive en cada navegador, y un registro central también necesita servidor. Noticias y desabasto: hoy solo se verifican sus cifras de dinero público; lo demás espera la fase 2.
- **El bot ya sabe todo lo de la pestaña Números (pedido del autor, 23-10-2026, sello 20261023c).** «Verifica e integra toda la información de la pestaña de números a nuestro auditor», pestaña por pestaña; esta es la primera. Revisión de las 64 páginas de Números: el bot conocía la deuda, los intereses y las dependencias, pero no los renglones. Nuevo `herramientas/asistente_numeros.py` (→ `dat.num` de la base del bot), con 248 renglones, cada uno con su estado, documento y página: los 16 orígenes del ingreso (LIF 2026) y sus desgloses (IEPS por producto, ventas de Pemex/CFE/IMSS/ISSSTE, deuda interna…), los 8 renglones del gasto, programable y no programable, gastos obligatorios (Anexo 3), gasto federalizado y los 8 fondos del Ramo 33, lo municipal (FORTAMUN, FISMDF, predial nacional 2024), los 55 ramos y unidades del Anexo 1 con subtotales y neteo, los Poderes (aprobado 2026, ejercido 2025, pagado al 30-06-2026 y gasto por capítulo), los congresos estatales 2024 (INEGI), el Paquete 2027 (finanzas, finalidades, programas sociales, inversión, colchón, pasivos contingentes y supuestos macro), la Cuenta Pública 2024 y las series 1990–2025 del Radar hacendario. **Verificado:** cada una de las cifras aparece igual en la página a la que el bot remite (prueba automática). **Fuera, a propósito:** `panoramaErario.treemapPEF` y `macro` (montos sin documento; el 12-10-2026 se sustituyeron por el Anexo 1 en Números) y `legislativo.congresosEstatales` (sin fuente). **Ojo:** el bloque del treemap todavía existe en `index.html` (portada, que no se toca); conviene que el autor decida si se retira. El bot contesta con la cifra, su parte del total, cuánto es al día o por persona, el año contra 2027 o 2025, listas ordenadas («¿qué impuesto deja más?», «¿en qué se gasta?»), el resumen del Paquete 2027 y años de 1990 a 2025; si un renglón de 2027 todavía no existe, lo dice. «Presupuesto 2026» ahora da el gasto neto total del decreto ($10.19 billones) y aclara que Hacienda publica además el gasto neto pagado ($10.11). **Regla de redondeo corregida** (en el bot y en «Contrasta una nota»): un redondeo solo coincide si no esconde más de 10 %; «2 billones de IVA» por $1.59 billones queda en ámbar («redondeo demasiado grueso»), antes salía verde. «Contrasta una nota» sigue en 100 de 100 con su nota de prueba. Siguiente pestaña: la que diga el autor (Herramientas, Datos, Aprende o Participa).
- **El cuadro de árbol del gasto (portada, 2.2 «En qué se va») ya no tiene montos sin documento (pedido del autor, 23-10-2026, sello 20261023d: «en cuanto al punto 3… sí, corrígelo»).** `panoramaErario.treemapPEF` traía montos redondos marcados `oficial` que no cuadraban con el decreto (Sedena $259,400 mdp contra $170,753 del Anexo 1; costo financiero 1,388,400 contra 1,572,073.3). Se borró de `audit-database.js` y el motor arma el árbol con `treemapDatos()` desde `panoramaErario.egresos`, la misma fuente de la lista de barras: nivel 1, los 8 renglones del gasto (clasificación funcional de los Criterios 2027 y Anexos 1 y 8 del PEF 2026), con su chip, «Ver en Números ➔» y «Ver fuente ↗»; nivel 2, el desglose oficial donde existe (costo financiero: Ramo 24, Pemex y CFE, Ramo 34). Ya no hay «programas insignia» ni dependencias con montos inventados. El autor autorizó tocar `index.html` para esto (solo cambió el rótulo del nivel).
- **El bot ya sabe todo lo de la pestaña Datos (pedido del autor, 23-10-2026, sello 20261023d).** «Continúa verificando la información que se encuentra en la pestaña de datos.» Revisión de sus 29 páginas (Radar hacendario y El peso en el tiempo, Datos abiertos, Informes oficiales y Medio ambiente). Nuevo `herramientas/asistente_datos.py`, que suma sus renglones a `dat.num.filas` (116) y trae `dat.datos` (peso, descargas, plazos, leyes y quién mide): **medio ambiente** (PIB, PINE, consumo de capital fijo y PIN como rango, costo ambiental y sus 7 renglones, gasto en protección y la razón 5.94), **basura** (generación, recolección y su serie 2010–2022, separada, disposición final, 52 rellenos, 2,250 sitios, 150 municipios sin servicio, 1.076 kg por persona, camiones), **Ramo 16** (los 7 órganos: aprobado, pagado contra modificado al 30-06-2026 y proyecto 2027), **la ASF** (Cuenta Pública 2019 a 2024 y la 1.ª entrega de 2025: auditorías, pliegos, recuperado, por aclarar y observado año por año; las demás acciones de 2024 y 2025; universo, muestra y representatividad; los seis años juntos; por grupo de gasto y los diez renglones con más por aclarar; los plazos de la ley). **El peso** (dólar y euro de hoy, inflación de 12 meses, por año desde 1989, dólar y euro promedio de cada año, la proyección de Hacienda a 2032 y la máquina del tiempo: «¿cuánto valen 1,000 pesos de 2000 hoy?»). **Los sexenios**, además: inflación acumulada, dólar y euro de cada uno, el reloj (deuda, intereses, inversión, ingresos o gasto por segundo, hora y día) y las sumas en pesos de hoy, dólares o euros; los años sin dato (1989 de Salinas) y el sexenio en curso lo dicen. También contesta qué bases se descargan, qué es la lista 69-B y qué leyes ambientales aplican y quién mide cada dato. **Verificado:** cada cifra aparece igual en la página a la que remite (prueba automática; las series de la ASF que la página no grafica año por año —acciones y PRAS de 2019 a 2023— se dejaron fuera, y la basura separada va en % porque la página no da las toneladas). Batería anterior: 129 preguntas, sin cambios salvo dos que se ajustaron para quedar como antes. **Corregido de paso:** «Compara Peña Nieto con López Obrador» hablaba de inversión porque «Obrador» contiene «obra». **Fuera, a propósito:** el costo de las megaobras de `datos-ambiente-megaobras.html` (viene del registro del simulador; se revisa con la pestaña Herramientas).
- **«Cómo platicar conmigo» pasa a un cajón lateral (pedido del autor, 23-10-2026, sello 20261023e).** «Que se hiciera como un drawer de desglose… para ampliar más todo el chat.» La tarjeta que iba a la derecha del chat en `herramienta-inspector-pregunta.html` (la guía, «En mejora continua», «Lo que aún no sé» y el aviso) ahora es un cajón `.glos-drawer` que sale del costado con el botón «❓ Cómo platicar conmigo» de la cabecera del chat; se cierra con ✕, Esc o tocando fuera. El chat ocupa todo el ancho. La liga «Lo que aún no sé» de las respuestas abre el cajón en esa sección. El HTML lo arma `pagina()` en `asistente.py`; el comportamiento, `asistente.js`; el estilo, `asistente.css`. No cambió ninguna cifra ni respuesta.
- **El bot sabe del Poder Legislativo y de las elecciones (pedido del autor, 23-10-2026, sello 20261023f).** «Tomemos la pestaña de poder legislativo [de la Enciclopedia]… para que también pueda resolver cuestiones del poder legislativo, como cuántos curules son, las próximas elecciones.» La Enciclopedia sigue congelada: solo se leyó como guía de temas y **no se copió ninguna cifra**. Nuevo `herramientas/asistente_legislativo.py` (lo lee el bot como `D.leg`), cotejado contra la Constitución vigente (última reforma DOF 07-10-2026), la LGIPE (DOF 02-06-2026), la LFPRH (DOF 09-04-2026), los acuerdos del INE publicados en el DOF (INE/CG469/2026, INE/CG478/2026, precampañas del 16-10-2026, inicio del proceso del 13-10-2026), el DOF 10-02-2014 y el Censo Nacional de Poderes Legislativos Estatales 2025 del INEGI (tabla 8). Contesta: las 500 curules (300 + 200, 5 circunscripciones de 40), los 128 senadores, los 628 del Congreso, los plurinominales y sus candados (art. 54), la Comisión Permanente (37), los periodos de sesiones (y si hoy el Congreso sesiona), las fechas del paquete (8 sep, 20 y 31 oct, 15 nov), las elecciones del 6 de junio de 2027 (500 diputaciones, 32 entidades, 17 gubernaturas, precampañas del 4 de enero al 12 de febrero, campañas y veda), la elección judicial movida a 2028, la reelección (prohibida desde 2030; en 2027 rige la regla de 2014), los 32 congresos locales (1,122 en activo; uno por uno, el más grande y el más chico), los ayuntamientos (hasta 15 regidurías) y las reformas de 2025 y 2026. **Lo que la Enciclopedia decía y no se sostuvo** (no entra al bot; queda en su base congelada y en el bloque heredado `legislativo`/`geografia_electoral_ine` de `audit-database.js`, que el auditor no pinta): San Lázaro $9,282 mdp (el PEF 2026 le aprobó $9,602.7), Senado $5,365 mdp, los desgloses por capítulo, las «~4,200 plazas», las partidas de «gestión social», «1,098 curules locales» (el INEGI cuenta 1,122 en activo) y la distritación atribuida a INE/CG130/2023 (ese es el de las circunscripciones; los distritos son del INE/CG875/2022). **Pendiente** (`elecciones-2027-cargos` en el Registro): la lista de las 17 gubernaturas y el conteo de cargos locales de 2027, que están en el INE/CG480/2026; el portal del INE no abrió con conexión verificada. Batería anterior (146 preguntas y las 66 de Datos): sin cambios.
- **«Saber más», «Generar dictamen» y la página del Congreso (pedido del autor, 23-10-2026, sello 20261023g).** El autor pidió que el botón «Generar ficha técnica» se llame «Generar dictamen» y lleve a una página propia con el dictamen pericial de Auditavisión, sellado en encabezado y pie, y que cada respuesta traiga «Saber más» hacia la página donde está la información (ejemplo suyo: de dónde sale el dinero → los 16 orígenes del ingreso en Números). Hecho así: (1) `herramienta-inspector-dictamen.html` (`asistente.dictamen_pagina()` + `apartados.herramienta_dictamen()`; la lógica en `asistente.js`, modo `#dicApp`): el enlace lleva solo la pregunta y hasta cuatro previas para el contexto; la página vuelve a contestar con la misma base y arma el dictamen en seis o siete capítulos (planteamiento, respuesta, hallazgos, lo que falta, fundamento documental, método, alcance), con folio `DP-AAAAMMDD-XXXXXXXX`, sello y huella SHA-256 de la ficha; se imprime o guarda en PDF sin el marco del sitio. Abre en otra pestaña para no perder la plática. (2) «📖 Saber más · destino» en toda respuesta con datos; se agregaron destinos a sueldos (Tú contra ellos), municipios (numeros-los-municipios.html) y Legislativo. (3) `congreso-y-elecciones.html` (Aprende, cuarta pestaña), generada desde `asistente_legislativo.secciones()`: los 13 temas con sus fuentes y la tabla de los 32 congresos; el bot manda ahí con `#leg-<tema>`. Pruebas: 202 preguntas con respuesta idéntica a 82b186e; 9 sin «Saber más» (saludos, aritmética y lo que no hay). **Pendiente, decisión del autor:** base de datos segura y escalable con API (ver la respuesta del 23-10-2026): GitHub Pages no puede ocultar datos; requiere servidor, llaves y costo.
- **El Poder Judicial en el bot y los dos Poderes en Datos (pedido del autor, 23-10-2026, sello 20261023h).** El autor pidió integrar al Auditor la pestaña del Poder Judicial de la Enciclopedia, replicarla en Datos «así como la del Poder Legislativo», y que cada subpestaña quede en su propia página. Hecho así: (1) `herramientas/asistente_judicial.py`: 20 temas (estructura, 32 circuitos, OAJ, Tribunal de Disciplina, Tribunal Electoral, la Corte, sus nueve integrantes, requisitos, sueldos, haber de retiro, presupuesto, gasto de la SCJN, fideicomisos, elección 2025 y 2028, amparo, controversias, jurisprudencia y plazos). Cotejado contra la Constitución vigente (DOF 07-10-2026) y los transitorios de 2024, los acuerdos INE/CG563/2025 (votos y asignación de la SCJN) e INE/CG564/2025 (881 cargos en 32 circuitos), el Manual de remuneraciones del PJF 2026 (anexo B) y la colección `poderes`. El bot lo lee como `D.jud` (`judResp()` en `asistente-charla.js`, antes del Legislativo). (2) Datos tiene dos pestañas nuevas: `datos-poder-legislativo.html` (4 páginas: Cámaras; sesiones, presupuesto y reformas; elecciones; congresos locales y ayuntamientos) y `datos-poder-judicial.html` (6 páginas: estructura y circuitos; la Suprema Corte; sueldos y el tope del 127; presupuesto; elección judicial; cómo decide un juez), armadas con `apartados.poderes_paginas()` y el mismo texto del bot. `congreso-y-elecciones.html` redirige con su ancla y salió de Aprende. (3) No se sostuvo de la Enciclopedia: $206,948 mensuales del ministro, $5,529,450 anuales, la ponencia «promedio», $78,327 millones del Ramo 03, «$35 a $42 millones» por despacho y «$15,434 millones en 13 fideicomisos». (4) Punto ciego anotado sin calificarlo: el tabulador neto de ministra o ministro ($134,310) queda $20 arriba del límite neto de la Presidenta ($134,290, PEF Anexo 23.1.2); no se ha cotejado que midan lo mismo. Pendientes nuevos en el Registro: `judicial-2025-participacion`, `judicial-2025-costo` y `judicial-fideicomisos-monto` (el sitio de cómputos del INE no abrió con conexión verificada). Pruebas: 184 preguntas distintas idénticas a 07f837a salvo «¿Cuándo es la elección judicial?» (ahora más completa); 207 páginas, 0 enlaces rotos; sin desborde a 390 px; consola limpia.
- **Índice general al día otra vez (pedido del autor, 23-10-2026, sello 20261023j).** Faltaban 53 subpáginas creadas desde el 12-10: las 6 del Contexto dimensional, las 10 del Paquete 2027, las 4 de Tu estado de cuenta de la Calculadora, los 11 capítulos de Expedientes de la ASF, el dictamen pericial, las 3 de El peso en el tiempo, las 9 de Medio ambiente y las 10 de los dos Poderes. Ya no se escriben a mano: `_hijas(base, ref)` en `apartados.py` las saca de las mismas listas que arman cada página (`estado_cuenta.construir()`, `PE_PARTES`, `cc_ticket.PASOS`, `insp_asf.subpaginas()`, `RADAR_PESO_PARTES`, `datos_ambiente.PARTES` y `PAGINAS` de cada Poder), y `_grupo(..., hijas=)` las pone debajo de su página, una sola vez aunque esa página salga en dos grupos. El grupo «Los Poderes» ya no lleva a `index.html?ir=poderes`: enlaza las dos portadas de Datos y `numeros-lo-que-cuestan-los-poderes.html`. Once novedades nuevas, del 12 al 23-10. El sello sube porque la base del bot indexa el índice. Comprobado: ninguna página fuera del índice salvo `enciclopedia.html`; 207 páginas, 0 enlaces rotos; sin desborde a 1280 ni a 390 px; consola limpia.
- **Las preguntas de ejemplo del bot rotan (pedido del autor, 23-10-2026, sello 20261023k).** `EJEMPLOS` en `asistente.py` pasa de 13 a 31 preguntas, en un orden que alterna temas (estados, sueldos, impuestos, Poderes, conceptos, verificación). Cada una se probó en el chat y contesta con su dato y su fuente; se descartaron «¿Cuánto cuesta la deuda al año?» (contesta con la deuda como ingreso, no con el costo financiero) y «¿Cuánto se gasta en pensiones?» (contesta con el gasto total): son dos huecos del bot por atender. En pantalla se ven por tandas, 6 en computadora y 4 en celular: una barra marca el tiempo (8 s), la tanda se desvanece y entra la siguiente, chip por chip. Se detiene si pasas el cursor o el foco por ellas; «🔄 Otras preguntas» cambia la tanda a mano, y con «Reducir movimiento» no rota sola. La caja reserva el alto de la tanda más alta para que el chat no brinque. Sin JavaScript se ven todas.
- **El menú queda en tres pestañas (pedido del autor, 23-10-2026, sello 20261023l).** Auditor Virtual (`herramientas.html`), Enciclopedia (`enciclopedia-auditavision.html`, página nueva con tres tarjetas: Números, Datos y Aprende) y Comunidad (`participa.html`, antes Participa). La tarjeta «Comunidad» de esa página (`comunidad.html`) se llama ahora «Participa», y sus cinco páginas dicen «Comunidad › Participa» en las migas. Ningún archivo cambió de nombre: los enlaces viejos siguen sirviendo. Las pestañas salen de `MENU` en `apartados.py` (marca como actual la pestaña de la página o de su sección), la portada se cambió a mano y las migas de todo lo que cuelga de Números, Datos o Aprende pasan por «Enciclopedia». El índice general, el bot y AGENTS.md §5 bis están al día. Probado a 1280 y 390 px en 14 páginas: sin errores en consola ni desborde; 208 páginas, 0 enlaces rotos. **Punto ciego:** el nombre «Enciclopedia» ya era el del proyecto congelado (`enciclopedia.html`); por eso la página nueva lleva otro archivo. Si algún día se publica ese proyecto, habrá dos cosas llamadas igual. **Quedan por revisar** algunos textos de cara al lector que todavía dicen «en Herramientas» o «en Datos» como lugar (p. ej. en `asistente_datos.py` y algunos módulos); siguen siendo ciertos porque esas páginas existen, pero ya no son nombres de pestaña.
- **«Cuéntanos lo que viste» es la cuarta pestaña del menú plegado (pedido del autor, 23-10-2026, sello 20261023m).** En pantalla angosta (≤ 1100 px) el recuadro grande «¿Viste algo raro con el dinero público?» que cerraba el menú se quitó: en su lugar, «📢 Cuéntanos lo que viste» aparece como cuarta pestaña, debajo de Comunidad, y al final del menú solo quedan Compartir e Inspector Meteoro. Al tocarla, el menú se pliega y se abre el mismo cajón de siempre (`data-puerta` en las páginas, `openAyudanosFiscalizar()` en la portada). En pantalla ancha no cambia nada: los tres botones siguen arriba a la derecha. Viven en `cabecera()` de `apartados.py`, en `index.html` y en `civico.css` (`.nav-menu-cuentanos`).
- **La pestaña Auditor Virtual abre en «Pregúntale al Auditor» y las herramientas son un botón del chat (pedido del autor, 23-10-2026, sello 20261023n).** La pestaña lleva a `herramienta-inspector-pregunta.html` (`AUDITOR_VIRTUAL` en `apartados.py`; la portada tiene su copia a mano). En la cabecera del chat, junto a «Cómo platicar conmigo», el botón «🧰 Herramientas» despliega cuatro tarjetas, en el orden que pidió el autor: Modo Inspector (va directo a `herramienta-inspector-investigaciones.html`, las Grandes investigaciones), Costo Ambiental, Calculadora Cívica e Inversión y Megaobras (`HERR_MENU`, `asistente.pagina(..., herramientas)`, `asistente.js`, `asistente.css`). Se cierra con Escape o al tocar fuera. Las migas de toda herramienta dicen «Auditor Virtual» y llevan al chat; `herramientas.html` sigue viva como índice, ahora llamada «Herramientas» (Inicio › Auditor Virtual › Herramientas). **Puntos ciegos:** la página del chat sigue con el archivo `herramienta-inspector-*` y su pie «Volver al índice de Modo Inspector»; si el autor quiere que el chat deje de verse como parte del Modo Inspector, falta decidirlo.
- **Las imágenes de la portada abren el chat con la pregunta escrita, y Auditoría en imágenes es capítulo del Modo Inspector (pedido del autor, 23-10-2026, sello 20261023o).** Cada diapositiva enlaza a `herramienta-inspector-pregunta.html?p=<su pregunta>` (la que se ve en la imagen); `?p=` solo la escribe en la caja, y el lector decide enviarla (`?q=` sigue contestando al abrir). La página de la investigación pasó a `data-caso`, y el motor la usa para «Entiende el caso». Lo escribe `auditorias.portada()`, que lee las preguntas del propio `index.html`. El bot trae aparte (`B.inv`, fuera de la búsqueda general) una ficha por investigación (`auditorias.bot_fichas()`, con las cifras y el estado de la lectura breve): si la pregunta comparte 3 de cada 4 palabras con la de una diapositiva, contesta con ella, «Saber más» lleva a `auditoria-<id>.html` y, si hay, enlaza su expediente. En los Expedientes de casos de la ASF (aplicación 1 del Modo Inspector) se agregó el capítulo 2 de 12, `herramienta-inspector-asf-imagenes.html` (`auditorias.capitulo_inspector()`): no repite cifras; es la puerta a cada investigación, a su expediente (6 de 9 lo tienen) y al chat. **Puntos ciegos:** el chat contesta en corto y no salta solo a la página (se necesita tocar «Saber más»); si se cambia la pregunta de una diapositiva en `index.html`, hay que correr `sello.py` para que el bot la reconozca.
- **Objetivo: dos partes, y el Auditor Virtual rediseñado (decisión del autor, 24-10-2026, sello 20261024a).** La Enciclopedia es la parte de consulta y el Auditor Virtual la de uso, que le resuelve todo al usuario (AGENTS.md §0). El Modo Inspector queda solo con las Grandes investigaciones: `herramienta-inspector.html` muestra sus seis aplicaciones (ya no «Dos maneras de entrarle») y el pie del chat lleva a Herramientas, Grandes investigaciones y Enciclopedia. Rediseño del chat: un solo logo (la cabecera del título usa 💬 y las burbujas no llevan avatar), punto «En línea», respuestas con aire (fuente en panel, «Saber más» como botón principal, dictamen en contorno, «No era lo que buscaba» discreto, «Sigue preguntando» separado), ejemplos sin barra de tiempo ni rotación automática, «Regresar» (quita la última pregunta con su respuesta, la deja escrita y rehace el contexto) y «Limpiar». La plática se guarda en la pestaña (`av-chat`) y «Volver al Auditor» (`volver-auditor.js`) aparece en la página a la que llevó un enlace de una respuesta; en celular va encima de «Cuéntanos lo que viste». El 24-10-2026 (sello 20261024b) el título de la página pasó a «Auditor Virtual» (también la pestaña del navegador y las migas); el chat de adentro sigue llamándose «Pregúntale al Auditor». **Puntos ciegos:** la plática guardada dura lo que la pestaña (no pasa a otra pestaña ni a otro día); «Volver al Auditor» no aparece en las páginas que se abren en otra pestaña (portales oficiales, dictamen), que no la necesitan; las páginas de redirección viejas no cargan el script.
- **Las Grandes investigaciones son el Modo Inspector (decisión del autor, 24-10-2026, sellos 20261024c y d).** «Modo Inspector: realizar grandes investigaciones a través de seis aplicaciones». `herramienta-inspector.html` muestra las seis; `herramienta-inspector-investigaciones.html` es redirección (`REDIRECCIONES`). Las migas de las aplicaciones quedan Inicio › Auditor Virtual › Modo Inspector › aplicación (sin el nivel «Grandes investigaciones»), y «Las 6 aplicaciones» del pie lleva a la página del Modo Inspector. Imagen nueva del autor: `assets/auditor/img/herr-inspector-rostros.jpg` (en celular, velo completo para que el texto se lea); el Auditor Virtual y el dictamen conservan el foróptero con la clase `foto-auditor`. El bot entiende «grandes investigaciones» como el Modo Inspector (sinónimo en `SINON` de `asistente.js`; antes contestaba con Casas Grandes). **Punto ciego:** la imagen trae la firma «ashow» de su autor; falta confirmar el permiso de uso o poner el crédito.
- **Imagen del Modo Inspector: cámaras con ojos (decisión del autor, 24-10-2026, sello 20261024e).** La de los rostros, firmada «ashow», se quitó del repositorio (`herr-inspector-rostros.jpg` borrado) porque no había permiso del artista. La nueva es `herr-inspector-camaras.jpg`: collage de cámaras de vigilancia con ojos sobre texto, vertical (736 × 1308), elegida por el autor. El encabezado del Modo Inspector toma su carbón (`#1f1819`) y no el gris; el chat conserva el foróptero. **Punto ciego:** esta imagen tampoco trae autor ni licencia a la vista (circula en Pinterest y similares); el autor debe confirmar su origen o se reemplaza por una propia o libre de derechos.
- **El Auditor abre los estados de cuenta y los mapas, relojes y simuladores (pedido del autor, 24-10-2026, sello 20261024f).** Nuevo `herramientas/asistente_recursos.py` con dos catálogos que van a `AUDITOR_BASE.rec`: `ESTADOS_CUENTA` (9: cívico, ambiental, presidentes, congreso local, diputación federal, senaduría, Corte, estado, municipio) y `RECURSOS` (16: mapa del gasto federalizado, circuito de cada estado, padrón municipal, fiscalización por estado y por caso, Auditor de entes, relojes de la deuda, de cada administración y del daño ambiental, contador del PIB, tablero, duelo, máquina del tiempo del peso, simulador del presupuesto, estado de cuenta administrativo, megaobras). Comprueba al generar que cada archivo y ancla existan y que haya congreso local para las 32 entidades (las claves difieren: MÉX → `dip-loc-mex`, TAM → `dip-loc-tams`, TLAX → `dip-loc-tlx`; se cruzan por nombre en `dl`). En `asistente.js`: `pideRecurso()` («el mapa de la deuda de los estados», «el reloj de la deuda», «¿qué mapas tienes?»), `estadoDeCuenta()` (un cargo manda sobre el estado: «diputado local de Tamaulipas» abre su congreso; si la plática ya contestó con datos y lleva al documento, se queda esa respuesta) y `recursosPara()` que pinta «Explóralo a fondo» (máximo 3, con el estado elegido por `?e=`, sin repetir el destino de «Saber más»). «Tu ticket en negativo» se llama ahora **«Tu estado de cuenta ambiental»** (archivo sin cambio: `herramienta-ambiente-ticket.html`). Las preguntas de ejemplo abren con los estados de cuenta y suman mapas y relojes. **Puntos ciegos:** (1) los estados de cuenta del estado y del municipio son la ficha técnica del Auditor de entes, no un documento con folio como el administrativo; (2) los recursos se eligen por palabras compartidas, no por significado: una pregunta rara puede traer un recurso de más o quedarse sin él; (3) los relojes son equivalencias al ritmo promedio, no dinero que se mueva en vivo, y así lo dice cada página.
- **Cada estado y cada municipio con sus cuatro documentos (pedido del autor, 24-10-2026, sello 20261024g).** La ficha técnica del Auditor de entes (`herramienta-inspector-entes.html#ente=estatal:JAL`, `#ente=municipal:14120`) abre con «Sus documentos»: **Estado de cuenta** (la sección «Su estado de cuenta», antes «Ficha»), **Salud financiera** (el círculo), **En vivo** y **Generar dictamen**, que abre `herramienta-inspector-dictamen.html?q=Estado de cuenta de <estado>` o `?q=Estado de cuenta del municipio <municipio>, <estado>` en otra pestaña. Corrige el punto ciego (1) de la entrada anterior: la ficha ya llevaba folio (`AV-FT-…`), sello y huella SHA-256. **El ritmo, en vivo** (`insp-entes.js`, `vivoHtml()` y `arrancarVivo()`): cifra anual oficial ÷ 365 = al día; ÷ 24 = por hora; ÷ 60 = por minuto; ÷ 60 = por segundo (la misma base de 31,536,000 segundos que `cc_reloj.py`), todo `derivado`. Para un estado, Ramos 28 y 33 de 2026, y el contador corre desde el 1 de enero de 2026 a las 0:00 del centro (UTC−6); al pasar el año se detiene en el total. Para un municipio, ingresos totales de 2024 (INEGI), y el contador corre desde que se abre la ficha, porque la cifra no es de este año. Sin cifra (alcaldías de la CDMX, municipios que no entregaron cuenta) no hay contador y se dice por qué. El contador no entra en la huella: el folio de cada ficha no cambió. En la plática, «Zapopan, Jalisco» o «Benito Juárez, Quintana Roo» ya llevan al municipio y no al estado (`asistente-charla.js`: un municipio del mismo estado que se nombra cuenta aunque no se diga «municipio»). **Puntos ciegos:** (1) el contador es un promedio parejo: Hacienda paga las participaciones cada mes y las aportaciones según sus calendarios del DOF, así que el saldo real de un día cualquiera puede estar arriba o abajo; (2) el del municipio usa 2024 porque es lo último que el INEGI tiene completo; (3) para que fuera «en vivo» de verdad haría falta leer cada día los datos abiertos de Transparencia Presupuestaria y los informes trimestrales de la SHCP (ver la propuesta en la respuesta al autor: una tarea programada de GitHub Actions que descargue y regenere, sin servidor propio); es decisión del autor.
- **Comunidad en tres tarjetas y adiós al Pase (pedido del autor, 24-10-2026, sello 20261024h).** La pestaña Comunidad (`participa.html`) queda con **tres tarjetas: Ágora cívica, Garantías cívicas y Donaciones** (primero quedó en cuatro; el autor precisó el mismo día que «Cuéntanos lo que viste» sale de la pestaña). La tarjeta «Participa» (`comunidad.html`) se fundió con el botón «Cuéntanos lo que viste» de la cabecera, que es ahora su única puerta: la página se llama así, conserva sus cinco partes (reporta, error, tema, compartir, erratas) y sus migas ya no pasan por Comunidad. En el índice general tiene su propio grupo. **El Pase del Auditor Cívico se retira** (decisión del autor): `pase-del-auditor.html` redirige a `donaciones.html` (REDIRECCIONES), se quitaron `PASE` y `PASE_HTML` de `apartados.py`, y los botones «Pase Cívico» y «Descargar Reporte Salarial ($79)» de las calculadoras (`cc_ticket.py`, `cc_compara.py` y las copias del motor) dicen ahora «🐷 Sostén la plataforma» y llevan a Donaciones. Servicios y la política de independencia ya no lo mencionan; Donaciones apunta a Servicios como la otra vía. La evaluación de cómo sostener la plataforma (donaciones, Servicios del Auditor Virtual por suscripción o créditos, y por qué no criptotokens) está en `docs/LANZAMIENTO.md` §4.4; la decisión es del autor (0.5). **Puntos ciegos:** (1) el modal `#modalPaseCivico` sigue escrito en `index.html` (copia a mano, CRLF), pero ya nada lo abre: `openPaseCivicoModal()` lleva a Donaciones; se puede borrar en la próxima edición de la portada; (2) las entradas viejas de esta bitácora que hablan del Pase se dejan como historia.
- **El cajón de «Cuéntanos lo que viste» con sus cinco rutas (pedido del autor, 24-10-2026, sello 20261024j).** El botón de la cabecera (arriba a la izquierda) sigue abriendo el cajón, no una página (el autor lo pidió como página y lo corrigió enseguida: «todo eso lo integramos como el drawer»). Al cajón se sumaron **Comparte el Estado de Cuenta** y **Fe de erratas** a las tres rutas de antes, así que todo lo que tenía `comunidad.html` se abre desde ahí, y Comunidad (`participa.html`) ya no enlaza a esa página. En `apartados.py`, `RUTAS` tiene cinco renglones y `compartir_html()` / `erratas_html()` sirven igual a la página y al cajón; los estilos `.cm-errata*`, `.cm-compartir` y `.cm-nota` se mudaron de `servicios.css` a `puerta.css` (que carga en todas las páginas), y `.pt-cuerpo` lleva `grid-auto-rows: max-content` para que ninguna ruta se aplaste. **Punto ciego:** `comunidad.html` y sus cinco páginas siguen vivas (enlaces viejos, el bot y el índice general las usan), pero ya no hay tarjeta que lleve a ellas.
- **«Los tres presupuestos» pasa a Presupuesto, que queda en seis tarjetas (pedido del autor, 24-10-2026, sello 20261024k).** La tarjeta salió de «Gasto público» (`GASTO_PARTES`, que queda en ocho: tres en «Cómo se aprueba y cómo se reparte» y cinco desgloses) y es ahora la **primera** de `numeros-presupuesto.html`: Los tres presupuestos, Cuánto dinero es, Los 16 orígenes del ingreso, ¿A qué equivale?, El camino del dinero y el Paquete Económico 2027. La página conserva su dirección (`numeros-gasto-tres-presupuestos.html`, para no romper enlaces) y su contenido (`numeros_tres()`, sin cambios); ahora la arma `numeros_modulo()` como renglón `gp-tres` de `NUMEROS_MODULOS` (parte `origen`), con migas, «← Volver a Presupuesto» y «Siguiente → Cuánto dinero es». Las anclas viejas `numeros-gasto-publico.html#gpTres` y `#gpTresTit` llevan a ella. **El bot** (§5 ter) los conoce como grupo `tres26` de `asistente_numeros.py` (del Estado, derivado; nacional y social, oficiales; las mismas cifras de `numeros_datos()`): «¿cuáles son los tres presupuestos?», «¿cuánto es el presupuesto social?», y «Saber más» lleva a su página; antes esa pregunta caía en los ocho renglones del gasto. `numGrupo()` de `asistente-charla.js` los reconoce. De paso, la nota de «Lo que aún no sé» del chat ya no manda a «Comunidad › Un tema…», sino al botón «📢 Cuéntanos lo que viste» (abre el cajón en esa ruta). **Punto ciego:** el nombre del archivo sigue diciendo «gasto» aunque la tarjeta ya vive en Presupuesto.
- **La Biblioteca del Erario Público, al día (pedido del autor, 24-10-2026, sello 20261024l).** Auditoría de sus cinco páginas: ninguna ancla rota al Diccionario ni a Referencias, pero **la plataforma citaba ~170 documentos oficiales con liga directa que no tenían ficha** (sobre todo de Poderes, elecciones, Megaobras, IPAB y Cuenta Pública). **Referencias** (`referencias_legales` de `audit-database.js`) suma 28 fichas, de la [126] a la [153]: INE/CG563/2025 e INE/CG564/2025 (elección judicial); INE/CG469/2026, el acuerdo de Consejos Locales (DOF 13-10-2026) y el de precampañas (DOF 16-10-2026), en la familia nueva **«Elecciones e INE»** (categoría `electoral`, `FAMILIAS` de `biblioteca.js`); la reforma político-electoral (DOF 10-02-2014); IPAB (estados dictaminados 2025, notas cortas a marzo de 2026, Plan Anual de Financiamiento 2026); Cuenta Pública 2024 (estado de actividades del Gobierno Federal, Tren Maya, AIFA, Birmex, Pemex TRI) y 2025 (Pemex consolidado); datos abiertos del PEF 2026 y del PPEF 2027; Obra Pública Abierta; Ramo 03 por unidad responsable; informe trimestral de deuda 4T 2025; Segundo Informe de Gobierno; CONAPO; padrón del SAT; AFAC; FIX de Banxico; ASF sobre el NAICM y la Estela de Luz, y el PEF 2024. Cada cita sale del texto con que la página ya la citaba; las ligas del DOF, IPAB, ASF, AFAC y Banxico se comprobaron el 24-10-2026; las de Hacienda no abren desde este entorno (certificado) y la ficha lo dice. **Diccionario:** cinco términos (los tres presupuestos, clasificación funcional del gasto, pasivo contingente, Proceso Electoral Federal 2026-2027, estado de actividades), con textos que ya estaban en la plataforma; quedan 251. **Fe de erratas:** la ficha [11] y la página «¿Quién lo aprueba?» decían que el PEF 2026 salió en el DOF el 28-11-2025; el propio PDF de la Cámara dice 21-11-2025. **Bot:** `calcula()` de `asistente-charla.js` ya no toma un folio o una fecha como división («INE/CG564/2025» daba «564 ÷ 2,025»); ahora abre la ficha. **Puntos ciegos:** (1) las páginas siguen citando esos documentos con su liga y todavía no con su nota [n]; cambiar las citas en `megaobras*.py`, `asistente_judicial.py`, `asistente_legislativo.py` y los relojes es el siguiente paso; (2) quedan sin ficha, a propósito, los documentos de un solo uso: cada informe individual de la ASF (unos 80, que viven en sus catálogos), los tabuladores de los congresos locales de la Calculadora y la serie año por año del IPAB; (3) Marco Legal y Preguntas Frecuentes no cambiaron: no les faltaba nada de lo nuevo, salvo que se quiera una pregunta sobre la elección de 2027.
- **El Modo Inspector, dentro del chat (pedido del autor, 24-10-2026, sello 20261024m).** «Que las seis aplicaciones del Modo Inspector se integren de forma directa al Auditor Virtual en el chat»: quien no quiera ir a la herramienta investiga desde la plática. **Cómo:** `inspector()` de `asistente.js` (después de las investigaciones de Auditoría en imágenes y antes de la plática) reconoce lo que el lector trae y cada aplicación por su nombre o por lo que hace; el catálogo lo escribe `_inspector()` de `asistente.py` en `B.dat.insp` desde `HERRAMIENTAS` (y detiene la generación si una aplicación no tiene página). (1) **Lista negra del SAT, contestada por el chat:** un RFC (o varios en un mensaje, hasta 50) o «¿está en la lista negra…?» con un nombre; la primera vez descarga `assets/auditor/data/sat-69b.js` (1.5 MB) y contesta con la situación, el oficio y su fecha, chip `oficial`, «no aparecer no certifica a nadie» y «es determinación administrativa, no condena penal»; trae dictamen. (2) **Folio o huella** (`AV-…`, 64 hexadecimales, o la liga `?verifica=` de un PDF): abre «Verifica un estado de cuenta» con el folio ya puesto (los `AV-FT-` van al Auditor de entes; los `AV-EC-` piden su liga completa; los folios de dictamen `DP-` se explica que se comprueban con su enlace). (3) **La liga de una nota:** abre «Contrasta una nota» con `?liga=` y la lee ahí mismo (antes era un botón a otra página). (4) **Un ente federal** («diagnóstico de Pemex», «auditor de entes: Marina»): su ficha en corto y el Auditor de entes abierto en `#ente=federal:…`; los estados y municipios los sigue contestando la plática. (5) **Un expediente** («expediente de Segalmex», «casos por aclarar del AIFA»): la ficha del caso y `expedientes.html#exp-…` abierto. (6) **Servicios de investigación** («quiero pedir una investigación sobre…»): el formulario con `?tema=` ya escrito (o la pregunta anterior si dice «esto»). Y «¿qué puedo investigar?» lista las seis. **El marco:** las aplicaciones no se copiaron: se abren en un `iframe` de la respuesta llamado `av-en-chat`; `volver-auditor.js` (cargado en todas las páginas) lo reconoce, pone la clase `av-en-chat` (en `civico.css` oculta cabecera, menú, migas y pie) y manda los enlaces a otras páginas a la pestaña entera con la seña de «Volver al Auditor». El marco crece con la aplicación hasta ¾ de pantalla (en computadora, hasta el recuadro de la plática), con «Verla completa» y «Cerrar». **Además**, toda respuesta cuyo «Saber más» lleva a una de las seis (p. ej., «¿Cuánto debe Jalisco?» → Auditor de entes) trae su tarjeta con «▶️ Úsala aquí, sin salir del chat». La plática guardada en la pestaña guarda los marcos cerrados. Siete preguntas nuevas entre los ejemplos y un punto nuevo en «Cómo platicar conmigo». **Puntos ciegos:** (1) el veredicto del folio y de la nota se lee en el marco, no en el texto de la burbuja: el dictamen de esas respuestas no existe todavía, porque la verificación corre en la página de la aplicación; (2) la lectura de ligas depende de los lectores externos que ya usaba «Contrasta una nota» (r.jina.ai, allorigins): si fallan, ahí mismo se pega el texto; (3) la búsqueda por nombre en la lista negra es por palabras («Nuevo León» encuentra empresas con esas palabras en su razón social, no las del estado): la respuesta lo dice y recomienda el RFC; (4) Servicios sigue «próximamente»: el formulario se arma y se guarda, pero el envío se activa con el lanzamiento.
- **Inversión y Megaobras, dentro del chat (pedido del autor, 24-10-2026, sello 20261024n).** «Que toda la información y contenido de la herramienta de inversión y obra se pueda programar con el auditor virtual, así como sus vinculaciones directas hacia los portales correspondientes, visualizaciones de los mapas, salud financiera, cuestiones de los presidentes, e integrar preguntas predeterminadas». **Antes** el chat no la sabía leer: «¿Cuánto costó el Tren Maya?» contestaba con el Paquete 2027 y «¿Qué megaobra tiene más sobrecosto?», con el glosario. **Cómo:** `herramientas/asistente_megaobras.py` escribe `B.dat.mo` sin una cifra nueva: las 13 obras y rescates como las pinta «Obra por obra» (`mo_sector.obras_oficiales`: aprobado, costo real y sobrecosto con su estado, su rango y su «de dónde sale»), la medida única de gana o pierde (`mo_base`), lo que dijo la ASF, sus documentos, los seis sexenios con sus sumas (`mo_tabla._datos`) ligados al estado de cuenta de cada presidente, las cuatro cifras del total y las cinco aplicaciones. Los textos de cifra salen con los formatos de las páginas (`mo_pulso.mdp`, `sim_mdp`): se leen igual en el chat que en la herramienta. La generación se detiene si falta un ancla (`#obra-`, `#cuenta-`, `#mt-`, `#mt-sx-`), una página de aplicación, el estado de cuenta de un presidente o si la dependencia a cargo no la nombran los documentos de la obra (`ENTE`). `megaobras()` de `asistente.js` (después del Modo Inspector y antes de la plática) contesta: (1) **una obra** por su nombre de calle (`ALIAS`: «Dos Bocas», «Santa Lucía», «el búnker»…; los que también son municipio, como Texcoco o Tula, piden contexto de obra), con lo que se pregunta al frente (sobrecosto, aprobado, costo, gana o pierde, la ASF) y «¿y su sobrecosto?» sigue a la obra anterior; (2) **dos obras** frente a frente, en tabla; (3) **un presidente** («¿en qué obras invirtió Calderón?») o dos («compara las obras de Calderón y Peña Nieto», que abre `#comparar-a-b`), y **todos** («¿en qué invirtió cada presidente?»); (4) **rankings**: más o menos sobrecosto, la más cara, la que más pierde, la que gana (los rescates se apartan o se marcan); (5) **el total** («megaobras», «¿cuánto han costado?») con sus cuatro cifras, la medida y las cinco aplicaciones. Cada respuesta trae dictamen, «📎 Fuente» con cada chip, los **portales oficiales** de la obra (Obra Pública Abierta, Cuenta Pública, ASF…) y, en «Explóralo a fondo», su ficha, su cuenta, el **estado de cuenta de su presidente**, la **salud financiera de la dependencia a cargo** en el Auditor de entes (Defensa, Pemex, Salud, SEP, SSPC) y su **expediente de la ASF** si lo hay. Las cinco aplicaciones entran al catálogo de marcos del Modo Inspector (`appHtml` ahora dice de qué herramienta es cada una) y se abren con «▶️ Úsala aquí» en la ficha de la obra o en el sexenio. Cuatro recursos nuevos en `asistente_recursos.py`: el contador en vivo, la línea del tiempo, el duelo de sexenios y la huella ambiental. Siete preguntas de ejemplo, un punto en «Cómo platicar conmigo» y una línea en la descripción de la herramienta. **Segunda vuelta (pedido del autor, mismo día, sello 20261024o):** «no hay mapas pero sí simuladores», «la salud financiera de las obras se saca con un estado de resultados básico… positivo verde, negativo rojo», «habrá que ajustar inflación, tenemos un simulador ya hecho, y revisar bien cifras». (a) **Simuladores en lugar de mapas:** cada obra lleva a la simulación en vivo de «Obra por obra» ya filtrada por su industria y su sexenio (`herramienta-megaobras-sector.html?industria=…&mandato=…#ms-vivo`, parámetros que `mo-sector.js` ya leía); cada sexenio, a la misma con `?mandato=`; los rankings, a la comparativa ordenada (`?orden=sobrecosto|inversion|perdida#ms-comparativa`); el total, al ritmo de la pérdida (`#mpRitmo`) y a «de la cifra a tu bolsillo» (`#mcMesa3`). «Simulador del Tren Maya» o «simulador de megaobras» abren el simulador en el marco del chat. Tres renglones nuevos tipo `simulador` en `asistente_recursos.py`. (b) **Salud financiera = estado de resultados básico** (`estado_resultados()` de `asistente_megaobras.py`): ingresos, costos y gastos de operación, ganancia bruta (solo si ingresos y gasto son del mismo año y no es rescate: ingresos − gasto, `derivado`), cuánto cubren los ingresos del gasto, intereses, resultado neto (la medida única, no una resta nuestra) e inversión; ▲ verde suma, ▼ rojo resta (el color nunca va solo). Cada renglón sale de la cuenta de la obra con su año, su estado y su documento; lo que falta, con su porqué y su ficha del Registro. «Salud financiera del Tren Maya» o «estado de resultados del AIFA» lo ponen al frente y abren «La cuenta de cada obra». En celular la tabla se lee renglón por renglón. (c) **Inflación con el simulador que ya existía:** el mismo INPC de la máquina del tiempo del peso (`dat.datos.peso`, Banxico SP1): cada renglón del estado de resultados en pesos del mes más reciente = monto × INPC del mes ÷ INPC promedio de su año (`derivado`, con su operación; coincide con lo que contesta «¿cuánto valen … de 2024 hoy?»). El costo de una obra suma pagos de varios años, así que solo se ajusta cuando la base trae lo ejercido año por año y la suma es el costo real (el Tren Maya: $569,619.0 mdp de septiembre de 2026, año por año); en las demás se dice por qué no y se ofrece la máquina del tiempo. (d) **Cifras revisadas:** un cotejo automático de 90 cifras del chat (aprobado, costo, sobrecosto y resultado de cada obra, los renglones de su cuenta, los seis sexenios y las cuatro cifras) contra las páginas de la herramienta: 0 diferencias. (e) **Correcciones:** el máximo del sobrecosto de Dos Bocas decía 132.3 % en su definición y en su operación; la cuenta da 132.2 % (357,887.3 ÷ 154,098.4 − 1 = 132.25 %), así que se corrigió en `audit-database.js` y en `integrar_cuenta_megaobras.py`, y el punto medio dice «128.0 % (127.96 con todos los decimales)». «¿Cuánto le llega a Tula?» ya contesta Tula de Allende y ofrece Tula, Tamaulipas (`MUN_CORTO` en `asistente-charla.js`: un nombre corto que la gente dice sin su apellido). **Puntos ciegos que siguen:** (1) **no hay mapa geográfico de las obras**: la herramienta no guarda dónde está cada una, así que el chat no puede llevar al mapa de un estado desde una obra (las «visualizaciones» que ofrece son el contador, la línea del tiempo y el duelo); (2) la salud financiera es la de la **dependencia** a cargo, no la de la obra, y queda sin liga en el Tren Interurbano, la Estela de Luz, el FOBAPROA y el FARAC, porque sus documentos no nombran a una dependencia que el Auditor de entes tenga; (3) los años del resultado no son iguales para todas (2017, 2024, 2025) y las cifras son nominales: el chat lo dice, pero un ranking de «la que más pierde» mezcla años; (4) el ajuste por inflación del costo de una obra solo existe para el Tren Maya: para las demás falta lo ejercido año por año (la plataforma tiene Cuenta Pública por clave de cartera del Tren Interurbano y del AIFA, pero su suma no es el costo real que se usa).
- **Verificación del Auditor Virtual: las cuatro herramientas, las investigaciones y la Enciclopedia (pedido del autor, 24-10-2026, sello 20261024q).** «Verifica si el chat ya está vinculado con todas las herramientas, el contenido, las investigaciones, las aplicaciones y las referencias de la Enciclopedia». **Cómo se verificó:** (1) toda página real del sitio aparece en la base del chat; las 27 que no aparecen son redirecciones; (2) una batería de 42 preguntas en el navegador, a 390 px, una o más por aplicación. **Lo que faltaba (16 de 42 sin el destino correcto, aunque contestaban):** (a) las **nueve investigaciones** de Auditoría en imágenes solo salían con la pregunta exacta de su diapositiva: «megafarmacia», «huachicol fiscal», «Ramo 33», «Dos Bocas» o «Tren Interurbano» contestaban con megaobras o el glosario y nunca ofrecían la investigación; (b) **Costo Ambiental y la Calculadora Cívica** solo llevaban a su página: sus aplicaciones no se abrían en el chat como las del Modo Inspector y las de Inversión y Megaobras; (c) «Gano 15000 al mes, ¿cuánto me retienen?» contestaba lo que recauda el ISR en la Ley de Ingresos, no la cuenta personal. **Qué se hizo:** (a) `TEMA_BOT` en `auditorias.py` (frases de cada investigación; la generación se detiene si falta una) y `conInv()` de `asistente.js`, que pone «📖 Ver la investigación» al frente de «Explóralo a fondo» cuando la pregunta o la respuesta toca su tema; (b) `_apps_de()` y `ALIAS_APPS` en `asistente.py` escriben `B.dat.amb` y `B.dat.calc` desde `HERRAMIENTAS`, y `herramienta()` de `asistente.js` (después de megaobras) abre cada aplicación en el marco por su nombre o su alias, y «costo ambiental» o «calculadora cívica» listan sus aplicaciones con la primera lista para usarse; (c) un ingreso personal («gano», «mi sueldo», «me pagan»… sin cargo público de por medio) abre «Lo que te retienen» de la Calculadora con `?m=&p=&n=`, que `cc-ticket.js` ahora lee: el chat no calcula el ISR, lo calcula la calculadora con su tarifa. **Resultado:** 36 de 36 en la segunda batería, sin errores de consola ni desbordes a 390 px; 210 páginas, 0 enlaces rotos. **Puntos ciegos:** (1) las aplicaciones abiertas en el marco no traen «Generar dictamen» (igual que las del Modo Inspector): su cuenta corre en la página; (2) el ingreso se lee de la primera cifra del mensaje («gano 15 mil y tengo 2 hijos» usa 15,000), y el régimen queda en sueldos y salarios hasta que el lector lo cambie; (3) «Ver la investigación» se elige por frases: una pregunta sobre «deuda pública» la ofrece aunque trate de otra cosa de la deuda, lo que se acepta porque la investigación es justo sobre su costo.
- **Dictamen de las aplicaciones y lectura del ingreso (pedido del autor, 24-10-2026, sello 20261024r).** «Haz el pendiente 1 y 2». **(1) «Generar dictamen» en las aplicaciones usadas en el chat:** `conApp()` de `asistente.js` le da a toda respuesta que abre una aplicación (Modo Inspector, Megaobras, Costo Ambiental y Calculadora Cívica) una ficha de tipo `app`; el dictamen agrega el capítulo «La aplicación y tu resultado», con el enlace que repite la cuenta (con los datos del lector si los trae, p. ej. `?m=15000`). El dictamen **no repite el resultado**: la cuenta la hace la aplicación; respalda método y documentos. Las fuentes las junta `_fuentes_app()` de `asistente.py` desde la página de la aplicación y sus subpáginas (referencias de `fuentes-oficiales.html`, enlaces a dominios de gobierno y URLs de sus datos; si la página remite a una de Datos, Números o Aprende, de ahí), hasta 15 y «N documentos más». `servicios.html` no cita fuentes (es un formulario) y su dictamen lo dice. **(2) El ingreso:** `sueldoDe()` toma la primera cifra después de «gano», «me pagan», «facturo»… y descarta la que cuenta hijos, años, días o personas; «a la quincena» se convierte a mes con la operación a la vista (`derivado`: × 2); «a la semana» no se convierte (los meses no tienen semanas exactas) y se pide la cifra mensual. `regimenDe()` reconoce plataformas (Uber, DiDi, Rappi → transporte; Airbnb → hospedaje; Mercado Libre, Amazon → bienes), RESICO, arrendamiento («rento mi…», «cobro renta»; «pago renta» no cuenta) y honorarios; «facturo» sin más pide elegir entre RESICO y actividad empresarial. La liga lleva `&r=&pl=` y `cc-ticket.js` los aplica. Si el mensaje habla de hijos o familia, el chat aclara que la tarifa del art. 96 de la LISR no tiene descuento por dependientes y que algunos gastos se deducen en la anual (art. 151). **Pruebas:** 14 preguntas nuevas, 36 de 36 en la batería anterior, 0 errores de consola, sin desborde a 390 px. **Punto ciego:** dos preguntas con la misma liga dan el mismo folio, porque el folio sale de la ficha y la ficha es la misma.
- **La base de datos, construida (pedido del autor, 24-10-2026: «respecto al 3 se necesita construir la base de datos»).** El pendiente 3 del Auditor (portales externos y capa de IA) necesitaba servidor; se construyó la fase 3 de `docs/LANZAMIENTO.md` en `supabase/`, explicada en **`docs/BASE-DE-DATOS.md`**. **Migración** (`supabase/migrations/20261024000001_auditavision.sql`): 12 tablas y 2 vistas, seguridad por renglón en todas; `envios` (lo que escribe la gente, una tabla con su tipo), foro, perfiles, alertas, suscripciones, donaciones (públicas), `preguntas_bot` («Lo que aún no sé» con la vista `preguntas_por_atender`), `portales_cache` (copia con dirección, fecha y SHA-256), `consultas_ia` (bitácora de la IA) y `limites` (`limite_ok()`). **Ninguna cifra fiscal vive en la base.** **Funciones** (Deno): `recibir-formulario`, `pregunta-bot`, `portales` (Banxico SIE, endpoint verificado: sin llave contesta «Token inválido»; INEGI BIE por verificar, no respondió desde aquí) y `auditor-ia` (Claude `claude-opus-5-5`, esfuerzo bajo, JSON con esquema, `fallbacks: "default"`; cuatro candados: lee las fichas del sitio publicado por número, solo esas fichas, **coteja cada cifra** de la respuesta contra ellas (`_comun/cotejo.ts`) y anota todo en `consultas_ia`). **Pruebas:** `python3 herramientas/prueba_base_datos.py` levanta un PostgreSQL local con lo mínimo de Supabase y corre 26 pruebas de permisos (todas pasan); `deno test supabase/pruebas/cotejo_test.ts` (3 de 3); `deno check` limpio en las cuatro funciones. **Pendiente, del autor:** crear el proyecto en Supabase y poner los secretos (`SITIO`, `SAL_IP`, `TURNSTILE_SECRET`, `BANXICO_TOKEN`, `INEGI_TOKEN`, `ANTHROPIC_API_KEY`); hasta entonces la página no llama a las funciones. **Puntos ciegos:** la IA no se probó contra la API real (sin llave); Transparencia Presupuestaria y el DOF no tienen API de consulta y entran por la fase 4 (Actions semanal); el candado de cifras es estricto: una respuesta fiel que escriba una cifra con otro formato que el cotejo no reconoce (p. ej. «785 millones 300 mil») se rechaza y el Auditor contesta sin IA, que es el lado seguro.
- **Noticias relevantes y los personajes, en el chat (pedido del autor, 24-10-2026: «que se integre también al chat lo de noticias relevantes (…) para que al ingresar el nombre de algún personaje político se le dé una información no tan evidente (…) así como cuestiones que se puedan localizar en internet»).** Sin una cifra nueva: todo sale de `assets/auditor/js/columnas.js`. **`herramientas/asistente_personajes.py`**: (1) las 18 columnas entran a la búsqueda como fichas `columna` (balazo, dato curioso, cifras con su estado y su documento, nota de presunción de inocencia; «Saber más» abre `noticias-relevantes.html#col-<id>`); (2) `PERSONAJES`, 26 personas con cómo se dicen en la calle: cada una lleva sus columnas y **lo que circula y no se pudo sostener** (el `DESCARTADO` de columnas.js, con su motivo; por nombre o por tema con `DESC_TEMAS`). Si un nombre no aparece en ninguna columna ni en lo descartado, la generación se detiene. **Chat** (`personaje()` de `asistente.js`): «García Luna», «¿Quién es Omar García Harfuch?», «Noticias de Abelina López» contestan con sus columnas, sus cifras y fuentes, «🧺 Lo que circula y no pudimos sostener», el estado de cuenta si fue presidente y otras fichas de la plataforma que lo nombran; un presidente a secas sigue yendo a su estado de cuenta y un nombre que también es lugar (Benito Juárez) solo se toma como persona si se pregunta «quién fue», «noticias de»… «Noticias relevantes» lista los personajes. **Internet:** cada respuesta de un personaje, y cualquier nombre propio que la plataforma no tiene («¿Quién es Rocío Nahle?», «Ricardo Monreal Ávila»), trae «Búscalo en internet»: búsquedas ya armadas en gob.mx, DOF, ASF, SCJN/CJF, Congreso, INE y Google Noticias, rotuladas «sin verificar» y con la liga a Contrasta una nota; el chat no lee ni afirma lo que salga. Un nombre propio desconocido ya no se contesta con lo que se le parece (antes «Ricardo Monreal Ávila» daba el municipio Teteles de Ávila Castillo). **Fase IA:** función `buscar-web` (Claude `claude-opus-5-5` con `web_search_20260209`, `allowed_domains` = sitios oficiales + lista editorial de prensa en `_comun/web.ts`, máx. 3 búsquedas): **devuelve solo los enlaces del buscador**, nunca un texto redactado; tabla pública `busquedas_web` (migración `20261024000002`, copia de un día, tope 5/min y 30/día). **Pruebas:** 30 preguntas de personajes, nombres y lugares con nombre de persona, dictamen con el capítulo de cifras y fuentes de la columna; `bateria2` 36/36 y `bateria` 33/42 idéntica línea por línea a la de antes del cambio; `prueba_base_datos.py` 30 de 30; `deno test` 6 de 6; `deno check` limpio en las cinco funciones. **Pendiente:** la lista de prensa de `_comun/web.ts` es editorial y la decide el autor; `buscar-web` no se probó contra la API real (sin llave) y la página aún no la llama (etapa 7); los personajes sin columna (López Beltrán, Romero Deschamps, Raúl Salinas, Olán…) solo tienen lo descartado: sus columnas faltan porque los documentos oficiales no se pudieron abrir desde aquí (falta de la plataforma).
- **Verificamos: lo que circula en redes, cotejado y dentro del Auditor (pedido del autor, 26-10-2026: «quiero que el auditor tenga ese contenido en la enciclopedia y que al momento de preguntar cuente con esa información y sus fuentes para nosotros interpretarla y plasmarla en nuestro dictamen»).** Nueva sección **Verificado** («Verificamos») en `columnas.js`: cada columna trae `circula` (el texto que circula, la cuenta, la red y la fecha) y `cotejo` (afirmación por afirmación: ✅ consta, ⚠️ consta con matices, ❌ sin documento oficial o ⏳ pendiente, con su explicación y su documento). Tres columnas: **Ley de Ingresos 2027** (publicación de @pajaropolitico: techo de deuda interna de 1.7 billones y perdón de multas a grandes contribuyentes; Canal del Congreso y versión estenográfica de Presidencia; falta el pleno del Senado y el DOF), **HR Ratings baja a México a BBB** (comunicado 82 de la SHCP; las proyecciones de la calificadora quedan pendientes porque su reporte no abrió desde aquí) y **la renuncia de Guadalupe Taddei al INE** (mensajes del INE del 24 y 25-10-2026 y fallo LP-INE-001/2025; el video, la suma de 245 mdp y las frases solo están en prensa). `asistente_personajes.py` pasa `cir` y `cot` al chat, agrega lo no sostenido del cotejo a «Lo que circula» del personaje y suma a Guadalupe Taddei a `PERSONAJES`; el chat muestra el cotejo, el dictamen lo trae en el capítulo «Cotejo de lo que circula» y `pendientes.py` anota los cotejos pendientes (`red-<columna>-<n>`, 4 nuevos). **Pendiente:** el comunicado de la ASF sobre el INE, los contratos de Cajas Graf (INE e IEE Sonora), el reporte de HR Ratings y el nombramiento del secretario de Hacienda: los documentos existen y no se pudieron abrir desde la plataforma (falta nuestra). «¿Cuánta deuda autoriza la Ley de Ingresos 2027?» todavía contesta con la Ley de Ingresos 2026 de la pestaña Números: la columna sale con «Ley de Ingresos 2027 deuda y multas» o al preguntar si es cierto.
- **Verificamos: seguir el dinero, empresas contratistas y protocolo (pedido del autor, 26-10-2026: «que nuestro auditor pueda resolver el seguimiento de ese dinero (…) estar actualizando con futuros agentes o programadores (…) integrar esas empresas, esas contratistas, dentro de nuestro portal de búsquedas del SAT o de la UIF»).** Cuarta columna de Verificamos, **medicinas y ventiladores del IMSS** (transcripción de un video): consta que el IMSS de Hidalgo devolvió en 2020 los ventiladores sin pagarlos porque no cumplían el contrato (comunicado del 13-05-2020) y que la SFP inhabilitó 27 meses a Cyber Robotic Solutions (DOF, circular 11/2020); el monto de 31 mdp, la adjudicación directa y el dueño solo están en prensa; los más de 800 mdp atribuidos a Amílcar Olán quedan pendientes (contratos en ComprasMX sin integrar) y el «robo hormiga» como explicación oficial del desabasto no consta. Campo nuevo `sigue` en las columnas (🗓️ Lo que sigue, también en el chat y el dictamen). `EMPRESAS` en `asistente_personajes.py` (Cyber Robotic Solutions, Cajas Graf) con búsquedas en ComprasMX, directorio de sancionados, DOF, ASF, UIF y OFAC (`WEB_EMPRESA`); la respuesta de la lista negra del SAT avisa si la empresa ya está en Noticias relevantes. Manuel Bartlett entra a `PERSONAJES`. Protocolo para el autor y futuros agentes: `docs/VERIFICAMOS.md`. **Pendiente:** la Lista de Personas Bloqueadas de la UIF no es pública y no se puede integrar; los contratos de ComprasMX (IMSS, IMSS-Bienestar, INE) son el siguiente paso para seguir el dinero con montos oficiales; lo dicho en el video sobre la atención del IMSS en Culiacán es testimonio, no se coteja; «mi tío Rorro» no se pudo identificar.
- **Verificamos Guaymas, pilares y seguimiento de casos (pedido del autor, 26-10-2026: una publicación y un discurso en tribuna del Congreso de Sonora sobre el comodato de 54 hectáreas a la empresa del proyecto de gas AMIGO; «que queden como soporte de nuestros pilares», «ser ese periodista virtual», «activar una herramienta de alarmas» e «integrar la aplicación de seguimiento de auditor ambiental»).** Quinta columna de Verificamos, `guaymas-comodato-amigo-gnl`: consta la ubicación (Parque Industrial Pesquero «Rodolfo Sánchez Taboada») y lo que presentó la Secretaría de Energía el 21-10-2026 (41.7 ha, 60 buques al año, el 4 % del tránsito, 290 mil m³), lo que dijo la Presidenta el 16-10-2026 (amparos, «no hay ningún daño ambiental») y el exhorto del Congreso de Sonora del 12-02-2026 (Gaceta 2104, turnado a comisión); las 54 ha y «Texas a Asia» tienen matices; el contrato de comodato y el resolutivo de impacto ambiental quedan pendientes (`red-guaymas-comodato-amigo-gnl-1` a cargo del Gobierno de Sonora, `-8` falta de la plataforma); Puente Colorado y megafarmacia no constan. `PERSONAJES` suma a Alfonso Durazo y `EMPRESAS` al proyecto AMIGO. El caso entra como cuarta ficha de **Crisis ambientales** (`crisis_ambientales.py`, «En litigio»), con enlace a la ficha de la ASEA del Auditor ambiental (`#aa-G00`). **Pilares:** página nueva `pilares.html` (`PILARES` de `apartados.py`), nueve pilares para el lector; AGENTS.md §0 ter. **Seguir un caso:** botón «🔔 Seguir este caso» en cada columna y panel «Tus seguimientos» (`#seguimientos`) en `columnas.js`; se guarda en el navegador (`localStorage` `av-sigo`) y avisa cuando cambia el `actualizado` de la columna. **Pendiente:** avisos por correo o al celular necesitan la base de datos (Supabase) con cuenta del autor; el expediente del Departamento de Energía de EE. UU. (FE 20-31-LNG), N+ Focus y la ASEA no abrieron desde la plataforma.
- **Contratos públicos de ComprasMX (pedido del autor, 26-10-2026: «Sí, integra los contratos de ComprasMX»).** Fuente: Datos Abiertos de ComprasMX, «Datos relevantes de los contratos» de 2025 y 2026 (215,121 contratos; 20,979 personas morales; 1,078 instituciones), con su diccionario de datos. Los archivos se bajan con el botón de la página (el servidor rechaza la descarga directa) y se procesan con `herramientas/actualizar_comprasmx.py` → `assets/auditor/data/comprasmx/` (613 archivos, 17 MB, cargados solo al preguntar). Chat: «contratos de Laboratorios Pisa», un RFC, «¿a quién le compra el IMSS?», «contratos del Tren Maya» y «¿qué contratistas están en la lista negra del SAT?» (10 aparecen: 1 presunto, 6 desvirtuados, 3 con sentencia favorable; ninguno definitivo). Página `contratos-publicos.html` (buscador, cruce con el 69-B y método). La columna del IMSS ya enlaza los contratos del IMSS; el pendiente de Olán sigue: ningún documento oficial liga a Olán con una empresa. **Pendiente:** los contratos de 2023 y 2024 (CompraNet histórico) y los de órganos autónomos que no usan ComprasMX, como el INE (Cajas Graf no aparece); ComprasMX no publica pagos.
- **Bloque 1 del plan v2 (pedido del autor, 26-10-2026: «adelante, empieza con el Bloque 1»; sellos 20261026e a j).** (1.1) `sello.py` rechaza un sello igual o anterior al publicado y acepta `--siguiente`. (1.2) Guaymas: la Orden DOE/FE 4629 (08-12-2020, expediente 20-31-LNG) entra a la columna como documento oficial: autoriza a Epcilon LNG exportar gas a México y reexportarlo como GNL, 395 mil millones de pies³ al año por 20 años, con inicio a más tardar el 08-12-2027; la prórroga a 2029 queda en «Sigue» (el DOE no la ha resuelto); alias `epcilon` en el bot. energy.gov no abre desde el entorno de la nube: la orden se cotejó con el buscador y falta guardarla en la bóveda (paso 2.2). (1.3) Taddei: la ASF anunció su investigación el 23-10-2026 según la prensa; su comunicado no se localizó en asf.gob.mx (las notas informativas de 2026 no están en la ruta `uploads/72_Boletines_de_prensa/NIASF_NN26.pdf`). Cajas Graf no está en ComprasMX 2025-2026, pero el INE tampoco: la ausencia no prueba nada. El chat no encuentra la columna con «investigación de la ASF al INE» (sí con «renuncia de Taddei»): va a las preguntas doradas (3.2). (1.4) **Sin hacer:** hrratings.com no abre desde la nube; el 4.6 % y la deuda a 2030 siguen pendientes hasta leer el reporte. (1.5) `aviso-de-privacidad.html` (`AVISO` de `apartados.py`), según el art. 15 de la LFPDPPP del 20-03-2025, con enlace en el pie de 185 páginas (las otras 28 son redirecciones); los enlaces del pie miden 44 px de alto. **Falta del autor:** nombre y domicilio del responsable; y el aviso debe cambiar antes de conectar Supabase. (1.6) **Sin hacer:** el nombre del dictamen es decisión del autor. (1.7) La lista 69-B del SAT se revisó: mismo archivo (misma huella, corte 31-12-2025). Plan completo: https://claude.ai/artifact/XBhVQAjy5TBGZ5yUHXpnAz (privado del autor).
- **Cuatro investigaciones nuevas en Auditoría en imágenes (pedido del autor, 26-10-2026: «integraras de una vez en auditoría de imágenes más investigaciones… lo que está pasando en el INE… de la gaceta… de los medicamentos… de que el Congreso aprobó más deuda»; sello 20261026k).** Auditoría en imágenes pasa de 9 a **13 investigaciones** (`herramientas/auditorias.py`, `assets/auditor/js/auditoria-imagen.js`, `assets/auditor/js/audit-database.js` → `auditorias_actuales`, generadas con `herramientas/integrar_auditorias_actuales.py`; ilustraciones 16:9 en `assets/auditor/img/showcase_*.jpg`; diapositivas 10 a 13 del carrusel de `index.html`). Cada una tiene su lectura breve y su lectura ampliada con tablas, chips de estado (`oficial`, `derivado`, `pendiente` con `data-pend`), fuentes oficiales verificables y enlace a su columna de `noticias-relevantes.html`: **(1) El INE, su presupuesto y los contratos en revisión** (`auditoria-ine-contratos.html`): Ramo 22 (ejercido 2025: $28,288.0 mdp; aprobado 2026: $21,837.2 mdp; pagado al 2T 2026: $9,648.4 mdp), Cuenta Pública 2024 de la ASF (4 auditorías, 3 pliegos, $66.6 mdp por aclarar), comunicados del INE del 24 y 25-10-2026 (investigación de oficio de la ASF, anuncio del micrositio de contrataciones y renuncia de la consejera presidenta), fallo público LP-INE-001/2025 (Cajas Graf en participación conjunta no cumplió especificaciones técnicas) y pendiente `red-taddei-renuncia-ine-contratos-4` (contratos señalados en prensa en el INE e IEE Sonora), sin nombrar a particulares conforme a `docs/VERIFICAMOS.md`. **(2) Guaymas, el predio costero y el proyecto de gas** (`auditoria-guaymas-gas.html`): exhorto en la Gaceta Parlamentaria No. 2104 del Congreso de Sonora (12-02-2026) sobre los proyectos Saguaro, AMIGO y Vista Pacífico; datos de la Secretaría de Energía (21-10-2026: 41.7 ha, diferencia derivada de 12.3 ha frente a las 54 ha señaladas en tribuna, 60 buques al año, 290 mil m³ de almacenamiento); Orden DOE/FE 4629 de EE. UU. (395 mil millones de pies³/año); presupuesto 2026 de las autoridades ambientales del Ramo 16 exhortadas (ASEA $353.5 mdp, PROFEPA $827.1 mdp, CONANP $1,502.3 mdp, INECC $159.3 mdp); y pendientes `red-guaymas-comodato-amigo-gnl-1` (contrato de comodato) y `-8` (resolutivo ambiental). **(3) Compras de medicamentos y contratos del sector salud** (`auditoria-medicamentos-imss.html`): Datos Abiertos de ComprasMX 2025-2026 en IMSS (`050GYR`, 31,666 contratos por $381,890.6 mdp; 53.1 % por adjudicación directa), IMSS-Bienestar (`056AYO`, 14,835 contratos por $227,202.8 mdp; 50.7 % por adjudicación directa) y Birmex (`012NEF`, 198 contratos por $35,853.1 mdp; 98.6 % por adjudicación directa), los 6 principales proveedores del IMSS en 2025-2026, la devolución sin pago de los 20 ventiladores en Hidalgo en 2020 e inhabilitación de Cyber Robotic Solutions (DOF circular 11/2020), y pendiente `red-salud-ventiladores-y-medicinas-4` (contratos 2023-2024 en CompraNet histórico). **(4) El Congreso aprobó más deuda — Ley de Ingresos 2027** (`auditoria-deuda-congreso-2027.html`): aprobación en Diputados (15-10-2026, 331 votos a favor y 118 en contra) y comisiones del Senado (21-10-2026, 18 a 11); ingresos totales ($10,636,488.0 mdp), presupuestarios ($9,156,528.9 mdp), techo de endeudamiento interno neto ($1,700,000.0 mdp), costo financiero 2027 ($1,636,247.1 mdp), RFSP ($1,555,655.8 mdp = 3.9 % del PIB), transitorio vigésimo primero sobre multas y recargos (sin tope de $300 mdp si se paga el adeudo principal), ajuste de HR Ratings de `BBB+` a `BBB` reconocido por Hacienda (Comunicado 82) y pendiente `red-hr-ratings-baja-mexico-bbb-3`. Integradas también en el capítulo 2 de Expedientes de la ASF (`herramienta-inspector-asf-imagenes.html`), el Índice general, el verificador de notas (`insp_nota.TEMAS`), el Registro de pendientes (`pendientes.py`) y el Auditor Virtual (`B.inv` y `TEMA_BOT`, incluyendo «investigación de la ASF al INE»).
- **Inversión en megaobras y rescates en Auditoría en imágenes y vinculación bidireccional (pedido del autor, 26-10-2026: «integrar lo que viene siendo las inversiones en megaobras como auditoría de imágenes, para que ya quede también todo eso vinculado»; sello 20261026l).** Investigación 14 de Auditoría en imágenes: **`auditoria-inversion-megaobras.html`** («Inversión en megaobras y rescates: 11 obras, 2 rescates y 6 sexenios», diapositiva 14 en `index.html`, ilustración `assets/auditor/img/showcase_inversion_megaobras.jpg`), armada sin una cifra nueva desde `mo_sector.obras_oficiales()`, `mo_base.balance()` y `mo_tabla._datos()` en `herramientas/integrar_auditorias_actuales.py`: las 11 obras ($529,936.6 mdp presupuestados frente a $1,176,646.8 mdp de costo real = +122.0 % de sobrecosto, $646,710.2 mdp por encima de lo aprobado), los 2 rescates aparte ($1,888,345.8 mdp en FOBAPROA-IPAB y FARAC carretero frente a $610,056.6 mdp iniciales; total con rescates: $3,064,992.6 mdp), la pérdida neta anual documentada ($77,881.1 mdp en los 6 proyectos con dato: 5 pierden $78,171.3 mdp y el AIFA gana $290.2 mdp), las 4 obras con operación anual pendiente (`reloj-megaobras`: Megafarmacia, Tren Interurbano, Agronitrogenados y Búnker) y el rastro de los 13 proyectos con enlace directo (`r.href` en `htmlRastro` de `auditoria-imagen.js`) a la ficha `#obra-<id>` de cada uno y a las 5 aplicaciones de `herramienta-megaobras.html` más `datos-ambiente-megaobras.html`. **Vinculación bidireccional:** (1) las 5 páginas individuales de megaobras en Auditoría en imágenes (`auditoria-tren-maya.html`, `auditoria-dos-bocas.html`, `auditoria-aifa.html`, `auditoria-tren-toluca.html`, `auditoria-megafarmacia.html`) enlazan ahora a su ficha y simulador (`#obra-<id>`), a su estado de resultados (`#cuenta-<id>`) y al panorama de las 13 (`auditoria-inversion-megaobras.html`); (2) cada una de las 13 fichas de obra en `herramienta-megaobras-sector.html` (`mo_sector.py`, `AUDITORIA_OBRA`) y la portada `herramienta-megaobras.html` (`apartados.megaobras_portada`) enlazan a su página de Auditoría en imágenes; (3) el Auditor Virtual, el verificador de notas y el Registro de pendientes (`MEGAOBRAS_PAGS`) enlazan `auditoria-inversion-megaobras.html`.
- **Las 13 megaobras y rescates individuales en Auditoría en imágenes (pedido del autor, 26-10-2026: «me refería a que cada auditoría en imagen fuera una de las obras. Mantenemos la que ya está, pero también hay que ponerlas como individuales»; sello 20261026m).** Auditoría en imágenes llega a **22 investigaciones**: se conserva la panorámica `auditoria-inversion-megaobras.html` y se integran como páginas propias las **8 obras y rescates de `simulador_megaobras`** que faltaban (`herramientas/integrar_auditorias_actuales.py`, `herramientas/auditorias.py`, `assets/auditor/js/auditoria-imagen.js` → `obraMega(id)` y ilustraciones 16:9 en `assets/auditor/img/showcase_*.jpg`; diapositivas 15 a 22 en `index.html`): **(1) Plantas de fertilizantes Agronitrogenados** (`auditoria-agronitrogenados.html`, `showcase_agronitrogenados.jpg`): $7,894.2 mdp autorizados en 2013 (`oficial`, Acuerdo CA-146/2013) frente a $13,698.3 mdp ejercidos (`derivado`, +73.5 %: $5,427.2 mdp en compra de activos y $8,271.1 mdp en rehabilitación 2014–2017), baja de tres plantas ociosas por $4,206.0 mdp (ASF CP 2015 aud. 498-DE y CP 2017 aud. 492-DE) y operación anual `pendiente` (`cuenta-agronitrogenados`). **(2) Compra de Grupo Fertinal** (`auditoria-fertinal.html`, `showcase_fertinal.jpg`): $12,532.0 mdp autorizados en 2015 (`oficial`, Acuerdo CA-209/2015) y $13,121.6 mdp financiados (+4.7 %, `derivado`), pérdida integral de $11,690.6 mdp en 2016, deterioro de crédito mercantil de $4,007.0 mdp en 2017 (ASF CP 2016 aud. 468-DE y CP 2017 aud. 492-DE) y pérdida neta de -$3,600.1 mdp en 2024 de PMX Fertilizantes Pacífico (CP 2024 Tomo VIII). **(3) Estela de Luz (Bicentenario)** (`auditoria-estela-luz.html`, `showcase_estela_luz.jpg`): de $393.5 mdp contratados en 2009 a $1,146.4 mdp tras 4 convenios (+192.0 %) y $1,304.9 mdp de costo final total (+231.6 %, `derivado`), con $399.2 mdp de pagos improcedentes observados por la ASF ($248.9 mdp en acero y $150.3 mdp en cuarzo y extraordinarios, Revisión de Situación Excepcional CP 2011) y mantenimiento anual `pendiente` (`cuenta-estela-luz`). **(4) El Búnker de Seguridad de García Luna (SSPC)** (`auditoria-bunker-garcia-luna.html`, `showcase_bunker.jpg`): contrato de obra civil de $347.4 mdp adjudicado sin licitación a TRADECO, costo real de obra civil en rango oficial entre $236.9 mdp y $289.1 mdp (punto medio $263.0 mdp, -24.3 %, `derivado`), $23.4 mdp observados en el edificio, presupuesto de Plataforma México en 2008 ($1,188.5 mdp) y 2011 ($1,898.1 mdp) (ASF CP 2008, 2009 aud. 1053 y 2011 aud. 16-GB) y equipamiento tecnológico reservado 12 años (`pendiente` en `obra-bunker-garcia-luna` y `cuenta-bunker-garcia-luna`). **(5) Refinería Bicentenario en Tula (Barda Perimetral)** (`auditoria-refineria-tula.html`, `showcase_refineria_tula.jpg`): $7,613.3 mdp de primer registro en cartera en 2009, $3,714.0 mdp autorizados en dos proyectos ($1,475.2 mdp en estudios y $2,238.8 mdp en terreno) y $1,127.6 mdp hundidos al cancelar en diciembre de 2014 ($659.3 mdp en 17 estudios y $468.3 mdp en terreno y barda perimetral, -69.6 %; ASF CP 2014 aud. 315-DE). **(6) Programa Enciclomedia** (`auditoria-enciclomedia.html`, `showcase_enciclomedia.jpg`): $21,398.3 mdp autorizados en el oficio OM-402 frente a $32,315.7 mdp ejercidos entre 2001 y 2011 (+51.0 %, `derivado`, en siete Cuentas Públicas de la ASF, CP 2005 a CP 2011), extinto en 2011. **(7) FOBAPROA / IPAB (Rescate Bancario de 1998)** (`auditoria-fobaproa.html`, `showcase_fobaproa.jpg`): $552,300.0 mdp presentados en febrero de 1998 (Informe Mackey, Gaceta Parlamentaria 23-09-1999), $710,923.3 mdp pagados por el Ramo 34 para apoyo a ahorradores (1999–2025), $1,023,571.0 mdp de pasivos netos vivos del IPAB al cierre de 2025 ($1,734,494.3 mdp comprometidos = +214.0 %, o $2,009,825.7 mdp con apoyo a deudores), $97,855.8 mdp de intereses devengados en 2025 y déficit 2025 sin Ramo 34 de -$59,971.8 mdp (`derivado`, Estados Financieros IPAB 2025 y PEF 2026). **(8) FARAC (Rescate Carretero de 1997)** (`auditoria-farac-carretero.html`, `showcase_farac.jpg`): $57,756.6 mdp en indemnizaciones por 23 autopistas y puentes en 1997, $96,094.9 mdp de pérdida acumulada 1997–2017, $153,851.5 mdp de costo documentado a 2017 (+166.4 %, `derivado`), $225,500.2 mdp de deuda bursátil neta en 2017 ($351,969.6 mdp por pagar 2018–2033 según la ASF), $153,035.5 mdp de pasivo vivo en el SHRFSP al cierre de 2025 y déficit anual 2017 de -$10,564.3 mdp (ASF CP 2015 aud. 99, CP 2017 aud. 91-GB y 96, y SHCP 4T 2025). **Vinculación completa:** las 13 obras enlazan a su propia `auditoria-<id>.html` desde `herramienta-megaobras-sector.html` (`mo_sector.py`), `herramienta-megaobras-tabla.html` (`mo_tabla.py`), `herramienta-megaobras-pulso-cuenta.html` (`mo_pulso.py`), `asistente_megaobras.py`, `insp_nota.py` y `pendientes.py`.
- **Inversión y Megaobras: una sola medida de pérdida y un solo filtro (pedido del autor, 21-10-2026).** Había tres medidas: la «pérdida anual» del pulso y de la mesa 2 (87,461.9 mdp: Tren Maya, AIFA en cero y el FOBAPROA de 2024 antes del Ramo 34), el «resultado del año» de La cuenta de cada obra (−25,429.2) y el «costo vivo» de Sector (PEF 2026 más intereses a la tasa implícita de la deuda, estimación propia). Ahora todas usan `mo_base.resultado()` / `balance()` / `medida_txt()`: lo que cada obra gana o pierde en su año más reciente publicado, **antes del apoyo del presupuesto** cuando se publica así (`resultado_sin_transferencias_anual_mdp` antes que `resultado_anual_mdp` del mismo año); si solo hay resultado del ejercicio (Dos Bocas, Fertinal, FARAC) entra ese y se dice; las ganancias restan (el AIFA ya no cuenta cero). Hoy: 6 de 13 obras con dato (2017, 2024, 2025), pierden 78,171.3, gana 290.2, **pérdida neta 77,881.1 mdp** (derivado); 4 no publican (pendiente, con su porqué) y 3 no operan (no aplica). La usan la portada y la tabla, las cuatro cifras, el ritmo, la composición, la cuenta, la mesa 2 y 3 de De cero, las fichas y el filtro de Sector, el reloj de la Calculadora Cívica (`cc_reloj.megaobras()`) y el contador de «Hoy» del Radar (`apartados.radar_hoy_vivo()`, antes 65,050.8). La ficha del FOBAPROA en Sector usa 2025 (déficit 7,519.9 + Ramo 34 52,451.9). El costo vivo de Sector se dejó de pintar (sus datos siguen en `costo_vivo_megaobras`). `operacion_oficial` y `totales_consolidados` de la base no se tocaron: los sigue usando el motor de `index.html`, que conserva la medida vieja. **Un solo filtro:** industria y presidente se eligen solo en «Obra por obra, por industria» (capítulo 5). Se quitaron el filtro de industria y mandato y «Solo lo documentado» de De cero (queda el orden de los renglones), los botones de industria de Los seis sexenios y «Todo lo registrado / Solo con documento» de Las cuatro cifras; cada página remite al filtro único. Se corrigió además que las partes del pulso habían quedado sin `mo-pulso.css` ni `mo-pulso.js` desde la reestructura en capítulos.
- **Auditor de entes públicos: el expediente se emite como ficha técnica de Auditavisión (pedido del autor, 21-10-2026, sello 20261021h).** El contenido no cambió; cambió el formato. Al abrir un ente (federal, estatal o municipal), `insp-entes.js` lo pinta con el encabezado y el sello del Estado de Cuenta y de la nota técnica del bot: arriba la banda `encabezado-estado-de-cuenta.jpg` (la detecta `insp_entes._banda()` y va en `data-cabecera` de `#ieExp`), el logo, «Ficha técnica · Expediente …», folio, fecha de expedición y de qué año son las cifras; abajo, después de las fuentes, el sello circular «AUDITAVISIÓN · FICHA TÉCNICA», folio `AV-FT-XXXXXXXX`, versión de la plataforma, huella SHA-256 y la leyenda de que no es documento oficial y de que los semáforos y el índice no son un dictamen. La huella firma el texto de la ficha (`cuerpoFicha()`, sin el enlace ni la versión): la misma ficha con las mismas cifras da el mismo folio, y se comprueba volviendo a abrir su enlace. Los botones salen de la hoja y se suma «Descargar en PDF» (`window.print()`; `@media print` deja solo la hoja). «Copiar ficha» agrega folio, huella y enlace. El verificador reconoce los folios `AV-FT-` desde el sello 20261021i (entrada siguiente).
- **Auditor de entes públicos: el directorio en su página y el verificador de fichas técnicas (pedido del autor, 21-10-2026, sello 20261021i).** El directorio (federal, estatal y municipal, con sus vistas, su orden y el buscador) pasó tal cual a `herramienta-inspector-entes-directorio.html` (`insp_entes.subpaginas()`; `_paginas()` arma las dos). La página del auditor se queda con el buscador, un botón amarillo «🗂️ Directorio» que la abre, las tres cifras (llevan al directorio con `?nivel=`), el método, las fuentes y «Para seguir el hilo». El expediente se abre en la página donde se pide (las dos tienen `#ieExp` y aceptan `#ente=`); Enter en el buscador del auditor manda al directorio con `?q=`. `insp-entes.js` sirve a las dos (`ES_DIR`). **Verificador:** `herramienta-inspector-verifica.html` manda los folios `AV-FT-…` a `herramienta-inspector-entes.html?verifica=`, que recalcula en el navegador la huella de la ficha de cada ente (federales y estados; si no aparece, carga los 2,479 municipios) y dice «Auténtica» con el enlace a la ficha, o «No coincide». Un enlace a una ficha pegado en el verificador se abre tal cual; una huella de 64 caracteres que no es de un estado de cuenta ofrece comprobarla como ficha técnica. El texto del verificador ya menciona las fichas técnicas.
- **Auditor de entes públicos: un solo navegador (pedido del autor, 21-10-2026, sello 20261021j; reemplaza la página aparte del directorio de la entrada anterior).** El buscador, los tres niveles, los filtros y el directorio se fusionaron en `herramienta-inspector-entes.html`, al estilo de «Contrasta una nota». El recuadro azul «Busca y verifica» lleva arriba los tres niveles como pestañas con su número grande (eran repetidos: las tres cifras y las pestañas del directorio se volvieron una sola fila), luego el buscador (filtra la lista al escribir y sugiere de los tres niveles), cuatro pasos y la salvaguarda. Debajo, el botón 📖 «Cómo se lee una ficha técnica y de dónde sale cada cifra» abre la ventana lateral con el método y las fuentes (`_cajon()`, plantilla `tplIeComo`; `#ie-metodo` en la dirección la abre, y los enlaces `#ie-metodo-fed`/`#ie-metodo-local` de la ficha la abren en su apartado). Siguen la ficha técnica (`#ieExp`, sin cambios), «El directorio» con sus vistas, su orden y sus tarjetas, y «Para seguir el hilo». Se quitaron el botón amarillo «Directorio», las tres cifras sueltas y `ES_DIR`/`DIRP` del guion. `herramienta-inspector-entes-directorio.html` redirige aquí conservando `?nivel=`, `?q=` y `#ente=` (`apartados.REDIRECCIONES`), así que los enlaces y folios ya emitidos siguen sirviendo.
- **El Radar por entidad, dentro del Auditor de entes públicos (pedido del autor, 21-10-2026, sello 20261021k).** La antigua aplicación 2 del Modo Inspector deja de ser aplicación: «Grandes investigaciones» queda con **siete** (ASF, Expedientes, Auditor de entes, Contrasta una nota, Lista negra del SAT, Verifica y Servicios; el Auditor pasa a ser la 3). En el directorio del Auditor, junto a «Todos», «Con incongruencias» y «Con señal fuerte», hay una vista más, «🚩 Radar por entidad 32 ›» (enlace `.ie-vista-ir`, en los tres niveles), que abre la página del radar. La página la genera ahora `insp_entes.subpaginas()` con `insp_radar.construir()`, con la misma dirección `herramienta-inspector-radar.html` (los enlaces viejos siguen sirviendo) y sus migas pasan por el Auditor («← Volver» lleva a él). Cada ficha de estado del radar trae «🏢 Su ficha técnica en el Auditor» (`#ente=estatal:<clave>`; el Estado de México es `MÉX`, `insp_radar.CLAVE_AUDITOR`), y «Sigue investigando» empieza por el Auditor. Se quitó `inspradar` de `HERRAMIENTAS` y de `INSP_NATIVAS`; el ancla vieja `herramienta-inspector.html#inspradar` lleva al radar. La portada heredada (`index.html`, bloque `eb-inspradar`) y la lista del motor no se tocaron.
- **El Radar por entidad, fusionado con la ficha técnica estatal (pedido del autor, 21-10-2026, sello 20261021l; reemplaza la entrada anterior).** El radar ya no tiene página: `herramienta-inspector-radar.html` redirige a `herramienta-inspector-entes.html?nivel=estatal&orden=radInt#ie-dir` (`apartados.REDIRECCIONES`), y se borraron `insp-radar.js` e `insp-radar.css`. `insp_radar.py` quedó como módulo de cálculo (`datos(C)`: promedio nacional, criterios, semáforo, PO/PRAS/SA y, por clave de estado del Auditor, totales de la Matriz, desglose, tres valores y lugar en cada criterio), que `insp_entes.datos()` mete en el JSON como `radar`. **En la ficha estatal**, después de «Las preguntas», va «🚩 Su radar de la Auditoría Superior» (`radarHtml()` en `insp-entes.js`): semáforo (bandera roja ≥ 1.5 × promedio, arriba, debajo), por aclarar, por cada $100 revisados, auditorías y acciones, la barra contra el promedio con su operación, su lugar entre los 32 en los tres criterios, «¿Quién tiene que aclararlo?» (gobierno, municipios/alcaldías, otros), «Más de la Matriz» y la fuente. **En el directorio estatal**: la vista «🚩 Bandera roja de la ASF» (con el promedio nacional en su descripción) y tres órdenes «ASF: …» (`radInt`, `radMonto`, `radMun`; las tarjetas muestran valor y lugar). La página acepta `?orden=` y `?vista=`. El método (ventana lateral 📖) suma el apartado `#ie-metodo-radar` con criterios, semáforo y glosario, y las fuentes, la Matriz pp. 19 a 23. Se quitó la cuarta vista-enlace del directorio; el bot y Qué encontró la ASF enlazan al Auditor.
- **Los tres niveles del Auditor, cerrados hasta que se pulsan (pedido del autor, 21-10-2026, sello 20261021m).** Federal, Estatal y Municipal ya no son pestañas con una abierta: son botones con `aria-expanded` y una flecha ▾. La página abre sin nivel (`st.nivel = null`) y con `#ie-dir` oculto; al pulsar un nivel se despliega su directorio y la página baja a él, y al pulsarlo otra vez se pliega. Escribir en el buscador no despliega nada (las sugerencias y los conteos «n de N» siguen); Enter sin sugerencia despliega el primer nivel con resultados. Abrir una ficha no despliega el directorio; `?nivel=` sí. Se quitaron las flechas de teclado entre pestañas. **El radar entra en la huella:** `cuerpoFicha()` suma el bloque «RADAR DE LA AUDITORÍA SUPERIOR» en las fichas estatales (también en «Copiar ficha»), así que las fichas estatales expedidas antes de este sello cambian de folio y el verificador ya no las reconoce; las federales y municipales no cambian.
- **Expedientes de casos de la ASF: las aplicaciones 1 y 2 fusionadas, todas las autoridades y un agente de seguimiento (pedido del autor, 21-10-2026, sello 20261021n).** «Qué encontró la ASF» y «Expedientes de casos» son una sola aplicación, «Expedientes de casos de la ASF» (`inspasf`, `herramienta-inspector-asf.html`); Grandes investigaciones queda con **seis** aplicaciones. Once capítulos (`insp_asf.capitulos()`): 1 Los casos por aclarar (`expedientes.html`, misma dirección y anclas `#exp-<id>`; `expedientes.py` ya no genera una página aparte: da `bloque()` y la arma `insp_asf.subpaginas()`), 2 Quién fiscaliza (`herramienta-inspector-asf-autoridades.html`), 3 El seguimiento 2024–2027 (el capítulo del calendario, misma dirección), y los ocho que ya había. **Quién fiscaliza** (`herramientas/fiscalizadores.py`, sin cifras): diez autoridades en cinco grupos (fiscalización superior: ASF, UEC, entidades estatales de fiscalización; control interno: Secretaría Anticorrupción y Buen Gobierno, órganos internos de control; sanción: TFJA, Fiscalía Anticorrupción; fiscal: SAT 69-B; coordinación y acceso: SNA, Plataforma Nacional de Transparencia), cada una con su fundamento (verificado el 21-10-2026 contra el texto vigente de CPEUM, LFRCF, LOAPF, LGRA y LOTFJA en diputados.gob.mx), qué hace, qué expediente oficial publica, su portal y qué tanto está integrado (sí, en parte, no; lo que falta se dice como falta de la plataforma). **El agente** (`python3 herramientas/agente_fiscalizacion.py`; `--ver` muestra el último reporte) recorre las direcciones donde la ASF publica cada entrega de las Cuentas Públicas 2024 a 2027 (`IR<año><a|b|c>/index.html`, con las fechas de CPEUM 74-VI y LFRCF 35), cuenta los informes individuales que enlaza cada índice y revisa los portales de las autoridades. Escribe `investigaciones/agente-fiscalizacion.json`, que la página pinta: integrada, publicada y por integrar (🆕), por venir, con retraso o portal sin respuesta. **No escribe cifras**: una entrega nueva entra a la base solo al extraerla de su documento (`extraer_mdb_asf.py`, `integrar_cuenta_publica.py`) y agregar su clave a `fiscalizadores.INTEGRADAS`. Primera vuelta (21-10-2026): CP2024 y 1.ª entrega 2025 integradas (sus índices enlazan 1,577 y 33 informes); la 2.ª entrega 2025 se espera el 30-10-2026; no respondieron los portales de la FGR, la Plataforma Digital Nacional ni la PNT (certificado o red), y la de Hacienda no se consulta por la misma razón. Las anclas viejas `herramienta-inspector.html#expedientes` llevan a `expedientes.html`.
  **Pendiente:** correr el agente después de cada fecha legal (la próxima, 30-10-2026) e integrar lo que marque 🆕; integrar las sentencias del TFJA, las auditorías y sanciones de la Secretaría Anticorrupción, la Plataforma Digital Nacional, las evaluaciones de la UEC y los informes de las 32 entidades estatales de fiscalización.
- **Pregúntale al Auditor, al día con la fusión (21-10-2026, sello 20261021o).** `asistente.py` suma dos tipos de ficha: `autoridad` (las diez de `fiscalizadores.AUTORIDADES`, con su fundamento, su expediente oficial y qué está integrado; llevan a «Quién fiscaliza») y `entrega` (una por Cuenta Pública 2024 a 2027 con el estado que vio el agente, y «La próxima entrega de la Auditoría Superior»). Las fichas de entidad añaden su radar (por cada $100 revisados, lugar entre los 32, chip derivado) y los expedientes llevan a «Expedientes de casos de la ASF». Ejemplos nuevos: «¿Quién sanciona la corrupción?» y «¿Cuándo sale la próxima entrega de la ASF?». **Tarea programada:** una sesión nueva corre `agente_fiscalizacion.py` los días 1 y 21 de cada mes (9:17, hora del centro de México), regenera, sube a la rama y avisa si hay entregas 🆕 por integrar; no integra cifras ni toca `main`.
- **Pregúntale al Auditor identifica cualquier dato de la plataforma (pedido del autor, 21-10-2026, sello 20261021p).** Además de lo anterior, el bot conoce: los **42 estados de cuenta** que expide `radar-estado-de-cuenta.html` (las 7 administraciones de Salinas a Sheinbaum, con ingresos, gasto, inversión y costo financiero en % del PIB, deuda al recibir y al entregar, y auditorías y montos de la ASF; y los 35 de cargos: diputación federal, Senado, 32 congresos locales y Suprema Corte), con el enlace que lo expide (`?adm=` o `?doc=`); las **48 fichas técnicas federales** del Auditor (aprobado, ejercido y pagado 2025); los **2,479 municipios** (ingresos 2024 del INEGI y enlace a su ficha), que viajan compactos en `AUDITOR_BASE.mun` y `asistente.js` arma al cargar, y las **248 cifras del catálogo** de Contrasta una nota. Todo sale de los datos ya generados (`asistente._estados_de_cuenta()` lee los JSON `#rdDatos` y `#exCargos` de la página; `_fichas_tecnicas()`, `insp_entes.datos()` y `municipios-efipem.js`): no hay cifra escrita a mano. Sinónimos nuevos: AMLO, EPN, Peña, Fox, Calderón, Zedillo. La base pesa 1.1 MB (antes, 0.77 MB).
  - **Lectura:** un sitio sin servidor no puede abrir páginas ajenas, así que la liga pasa por un lector externo gratuito, `r.jina.ai`, y de respaldo `api.allorigins.win` (decisión del autor). Las redes sociales suelen bloquearlo; entonces se pide pegar el texto. La nota viaja entre pasos en sessionStorage, y la liga en la dirección (`?liga=`), así que un veredicto se comparte.
  - **Empate:** cada renglón del catálogo lleva palabras clave (`claves()`: entidad y concepto, más alias de dependencias y estados). Una cifra solo se contrasta si la oración nombra ambos; el año y la cercanía del monto deciden entre candidatos. Lo que no empata queda «sin contrastar» y no cuenta. El lector puede corregir cada empate en el paso 2.
  - **Veredicto por cifra:** coincide (diferencia dentro del redondeo de la nota o ≤ 1 %, o respeta su «más de», «casi»), se acerca (≤ 10 %), error de unidades (×1000) o no coincide. **De conjunto** (`derivado`): coincide 1, se acerca ½, no coincide 0, promedio sobre 100; «se sostienen» (100), «en su mayoría» (≥ 70), «a medias» (≥ 40) o «no se sostienen». Califica las cifras, no al medio. Las cifras en dólares no se comparan.
  - **El catálogo y «Pruébala sin escribir» se mudaron** a la aplicación 1, Qué encontró la ASF: capítulo «Catálogo de cifras oficiales» y página `herramienta-inspector-asf-catalogo.html` (`insp_nota.catalogo_pagina()`, manejada por `insp-nota.js`), sin borrar ni depurar nada.
  - Nota: el «verificador de noticias» de la Enciclopedia que el autor recordaba no leía ligas: eran seis titulares fijos con ligas y puntajes inventados, retirados el 27-09-2026. Este es el primero que lee la nota de verdad. Sello 20261021b.
- **Emojis convertidos en íconos de trazo (decisión del autor, 20-10-2026; reemplaza la del 12-10-2026).** En toda la plataforma (no la Enciclopedia). Los textos siguen con emojis; `assets/auditor/js/iconos.js` (lo genera `herramientas/iconos.py` con los trazos de Lucide 1.49.0, licencia ISC, desde `npm pack lucide-static@1.49.0`) se carga en el `<head>` de cada página y, con un observador, cambia cada emoji por un `<svg class="ico">` que toma el color del texto, también en lo que arman el motor y los módulos. Tabla: 266 emojis → 215 íconos; los semáforos (🟢🟡🔴🟠⚪) y las alertas (⚠️ ⛔ ✅ ❌) conservan su color. En pestaña del navegador, opciones de listas y atributos (`title`, `aria-label`, `placeholder`, `alt`) el emoji solo se quita. Si un emoji era todo el contenido de un botón o enlace, el ícono le da su nombre al lector de pantalla. Se quedan como texto los signos tipográficos (↗ ➔ ← → ✓ ✕ ★ ▶ ©) y ▶ ↩ sin U+FE0F. Los dos emojis que venían del CSS (corona de `.versus-hero-box`, trofeo de `.au-bote-mayor`) ahora son máscaras SVG. Se corrigieron dos comparaciones que dependían del emoji pintado (`asistente.js`, copiar la nota; `agora.js`, aviso que se borra a los 5 s). Pendiente: las imágenes PNG que dibuja el lienzo (estado de cuenta cívico) no llevan emojis, así que no cambian.
