# Plan: Auditavisión legible en celular (UX, marca y URLs)

Generado por /plan-ceo-review el 29-09-2026, en modo de expansión selectiva.
Lo revisaron dos voces externas: Codex y un subagente de Claude.

- Repositorio: `uzoraproductos-arch/a`
- Rama publicada: `claude/funny-turing-imtm54` (GitHub Pages la sirve)
- Commit de partida: `ef9de85`

## 1. Problema

Condición del dueño: **la plataforma debe ser fácil de leer y de entender,
empezando por el celular.** Hoy no lo es.

Se midió en Chromium, en un celular de 390 × 844 px con el tema oscuro. Las 11
vistas medidas son la portada y los módulos `presupuesto`, `megaobras`,
`proyeccion2027`, `ambiente`, `territorio`, `municipios`, `calculadora`,
`poderes`, `verificador` y `portal`. Cada módulo se abrió con
`AuditEngine.seleccionarModuloExplorer(id)`.

| Medida | Hoy | Meta |
|---|---|---|
| Texto visible menor de 14 px | 78–86 % | 10 % o menos (solo chips, rótulos y pies) |
| Texto visible menor de 12 px | 16–42 % | 2 % o menos |
| Tamaños de letra distintos por vista | 19–27 | 8 o menos (nueva escala móvil de DESIGN.md §4.1) |
| Emojis visibles por vista | 50–198 | 0 en títulos, botones, menús y rótulos |
| Botones y enlaces de menos de 32 px por vista | 20–80 | 0; todo lo que se toca mide al menos 44 × 44 px |
| Primera pantalla de un módulo | empieza entre 3,767 y 4,585 px más abajo | título y primer párrafo visibles al abrir, sin desplazarse |
| Tiempo hasta poder usar la página, en un Android de gama media simulado (CPU 4× más lenta, 4G lento) | por medir en fase 0 | la línea base menos 40 % en fase 1 |
| Texto legible sin JavaScript (SEO/GEO) | ~8,700 de ~38,000 palabras | un resumen curado con cifras, chips y fuentes en cada URL |
| Errores de consola y desborde horizontal | 0 y 0 | se mantienen en 0 |

**El problema vive sobre todo en el JavaScript, no en el HTML.** Conteos
verificados en el repo:

| Archivo | Emojis | `font-size` en línea |
|---|---|---|
| `index.html` | 286 | 78 |
| `audit-engine.js` | 854 | 414 |
| `audit-database.js` | 609 | — |

- El CSS tiene 111 `!important`.
- Unas 44 frases del motor siguen tratando de usted.
- Como los estilos en línea mandan sobre la hoja de estilos, cambiar solo el CSS
  no alcanza las metas.

Otros problemas medidos:

- El botón flotante «Ayúdanos a fiscalizar» tapa contenido en todas las vistas.
- Cada módulo repite su índice dos veces.
- La foto de la ciudad aparece detrás de todo el texto.
- En celular, la primera pantalla es solo cabecera: 5 menús, 4 botones,
  buscador, una cinta que corre y contadores que cambian cada segundo.

**Premisa verificada:** el problema de lectura es real y se puede medir.
**Riesgo:** subir la letra sin reorganizar el contenido alarga todo. Proyección
2027 pasaría de 42 a unas 60 pantallas. Por eso el plan cambia la estructura y
ordena el contenido en capas, no solo la tipografía.

## 2. Decisiones

| # | Decisión | Elegido |
|---|---|---|
| D1 | Enfoque | Base nueva y después los módulos uno a uno |
| D2 | Postura del review | Expansión selectiva |
| D3.1 | Analítica sin cookies | Pospuesta |
| D3.2 | URL propia por módulo | **Aceptada** (SEO y GEO) |
| D3.3 | Bloque «Lo esencial» | Pospuesto; las plantillas le reservan lugar |
| D3.4 | Guardia de legibilidad | **Aceptada**, con metas absolutas escalonadas (X3) |
| D4 + X2 | Páginas por URL | **Una copia de `index.html` por ruta**, con sus propios metadatos y un **resumen estático curado**: cifras oficiales con chip y fuente, aprobado por el autor. Sin capturas del motor con Playwright |
| D5 | Publicación | Ramas cortas por fase, rebasadas cada día, con vista previa. Se integran a la rama publicada con el visto bueno del autor. Requiere enmendar AGENTS.md §1 |
| D6 | Reparto de módulos en secciones | Aceptado (§3). Los nombres finales los aprueba el autor |
| D7 | Radar y cinta | El radar pasa a Explora. La cinta se elimina |
| D8 | Fondo | Se cambia la foto por un fondo vectorial SVG discreto, con contraste AA en los dos temas |
| D9 | Quién genera las rutas | GitHub Actions. Publica **todo el repo** más las rutas y lo verifica con un manifiesto |
| D10 | Que cada página cargue solo sus datos | En una fase propia. Excepción: municipios y Leaflet se adelantan a la fase 1 (X4) |
| D11 | Tamaño de texto | 17 px en Lee (18 px en escritorio) y 16 px en el resto. Ningún texto corrido baja de 16 px. Se actualiza DESIGN.md §4.1 |
| D12 | Navegación entre módulos | Páginas de verdad, mediante la función `irA()` |
| D13 | Dominio | Por ahora se queda en github.io. **Comprar el dominio es acción obligatoria antes de la fase de URLs** |
| D14 | Contenido de cada página | Estructura completa. El resumen curado va solo en su módulo |
| X1 | Orden | **Primero la lectura**, luego los módulos en capas, luego el dominio y al final las URLs |
| X3 | Alcance de la fase 1 | Incluye barrer el motor y la base de datos, y sumar reglas de lectura a AGENTS.md |
| X4 | Velocidad | Carga diferida de municipios y Leaflet en la fase 1. La métrica es el tiempo hasta poder usar la página |
| X5 | Validación | Sin prueba con usuarios. «Terminado» = guardia en verde en los 5 módulos principales |
| X6 | Arreglos menores | Los cinco se incorporan (ver fases) |

## 3. Arquitectura de información

```
                           PORTADA (tres puertas)
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
   LEE /lee/…               EXPLORA /explora/…       CONSULTA /consulta/…
   plantilla artículo       plantilla herramienta    plantilla consulta
         PARTICIPA /participa/… en el menú y en el pie; no es puerta principal
```

### Tabla de rutas

Los nombres son propuesta. Se fijan con el autor en la fase 0, porque una URL
publicada es una puerta de un solo sentido. El origen de cada ruta se confirma
con `TAB_METADATA` (`audit-engine.js:5447`) y con los `data-subpanel`.

| Ruta | Plantilla | Origen |
|---|---|---|
| `/lee/panorama-2026/` | artículo | `presupuesto` |
| `/lee/megaobras/` | artículo | `megaobras` (las simulaciones en vivo se quedan dentro) |
| `/lee/paquete-2027/` | artículo | `proyeccion2027` |
| `/lee/costo-ambiental/` | artículo | `ambiente` |
| `/lee/congreso-y-judicatura/` | artículo | `poderes` |
| `/explora/calculadora/` | herramienta | `calculadora` |
| `/explora/auditoria-en-imagenes/` | herramienta | `.civic-showcase-section` |
| `/explora/contrasta-una-nota/` | herramienta | el Inspector «Contrasta una nota», dentro de `verificador` |
| `/explora/reloj-del-dinero/` | herramienta | el radar hacendario de la cabecera (D7) |
| `/consulta/asf-2024/` | consulta | `verificador`: «Qué encontró la ASF» y el radar de banderas rojas por entidad (es otro radar, no el de D7) |
| `/consulta/expedientes/` | consulta | `#expedientesCasos` |
| `/consulta/lista-69b/` | consulta | `#efosVerificador` |
| `/consulta/entidades/` | consulta | `territorio` |
| `/consulta/municipios/` | consulta | `municipios` |
| `/consulta/datos/` | consulta | Descargar datos |
| `/consulta/glosario/`, `/consulta/marco-legal/`, `/consulta/fuentes/` | consulta | secciones de referencia |
| `/participa/` | consulta | `portal`, denuncia y decálogo |

**Regla:** una ruta sale de un fragmento (`verificador` o la portada) **solo
cuando su módulo ya fue migrado y separado** en la fase 2. No se publican rutas
que apunten a pedazos de un módulo sin separar.

### Las tres plantillas

**Artículo (Lee)**

- Una sola columna: 68ch como máximo en escritorio; en celular, todo el ancho
  menos 16 px por lado.
- Source Serif 4 a 17/18 px, con interlineado de 1.6.
- Cifras en letra monoespaciada tabular, con su chip.
- Tablas: se prueban con contenido real a 390 px y con la letra ampliada. Solo
  se convierten en tarjetas si la comparación no se pierde; si no, se deja
  desplazamiento horizontal dentro de la tabla con encabezado fijo.

**Herramienta (Explora)**

- Un paso a la vez, con controles de 44 px como mínimo.
- El resultado va justo después del paso, sin fijarlo a la pantalla (evita
  tapar el teclado).
- Un desplegable «¿Cómo se calcula?».
- Si no hay JavaScript, se muestran el resumen curado y el aviso de que la
  herramienta lo necesita.

**Consulta (Consulta)**

- El buscador va primero.
- En celular, los filtros abren en una hoja inferior.
- Resultados en tarjetas con su chip.
- Si no hay resultados, se explica qué se buscó y qué intentar.
- Mientras llegan los datos (municipios y 69-B), se muestra un aviso de
  «cargando», y otro si la carga falla.
- Descarga en CSV.

**Las tres comparten:**

- la cabecera móvil;
- la ruta de migas;
- **un solo índice por módulo**;
- el glosario en línea;
- el pie de fuentes;
- el lugar reservado para «Lo esencial».

## 4. Arquitectura técnica (fase de URLs)

```
  push a la rama publicada
        │
        ▼
  GitHub Actions ─▶ herramientas/rutas.py  (Python, sin navegador)
        │             1. copia TODO el repo a la carpeta de salida (Enciclopedia incluida)
        │             2. por ruta: copia index.html → <ruta>/index.html
        │                · reescribe assets/… a ../../assets/…
        │                · <title>, description, canonical, OG, JSON-LD (Article / WebPage)
        │                · <meta name="ruta" content="lee/megaobras">
        │                · inserta el resumen curado de herramientas/resumenes/<ruta>.html
        │             3. 404.html, sitemap.xml, robots.txt, llms.txt (ya con dominio)
        │             4. manifiesto: ningún archivo público del repo desaparece
        ▼
  guardia de legibilidad sobre la salida ─▶ si falla, no se publica y se avisa
        ▼
  GitHub Pages (artefacto de Actions)
```

`herramientas/rutas.py --local` genera la misma salida en la máquina de
cualquiera, para verla con `python3 -m http.server`.

**Cambios en el motor**

1. `RAIZ` se calcula **al inicio del IIFE** a partir de
   `document.currentScript.src`. Dentro de funciones vale `null`. Se usa en las
   rutas dinámicas de `:2389`, `:3402`, `:3685`, `:3703` y `:8941`.
2. `SITIO`: una sola constante con el dominio y la ruta base.
3. Tabla `RUTAS` (ruta → pestaña y subpestaña). El motor la lee **antes** que el
   `#` al arrancar (`:25040`), y `popstate` la respeta.
4. `irA(módulo, sub)` reemplaza en un solo commit las 78 llamadas a
   `seleccionarModuloExplorer` y `switchTab`, tanto en `index.html` como en el
   motor. Si el módulo vive en otra URL, navega hasta ella. Si está en la misma
   página, hace lo de hoy.
5. El resumen curado **no se borra hasta que el módulo termina de pintarse
   bien**. Si el arranque falla, el resumen sigue visible. Esto se prueba
   provocando una falla a propósito.
6. En el `<head>` de la raíz, un script redirige las ligas viejas con `#` a su
   ruta nueva (`location.replace`) antes de que arranque el motor.

## 5. Fases

### Fase 0: preparación (sin cambio visible)

1. **AGENTS.md**, antes de empezar a trabajar:
   - enmendar §1: ramas cortas por fase (D5);
   - en §4, sumar «Reglas de lectura» que se puedan verificar:
     - nada de emojis en títulos, botones, menús ni rótulos;
     - nada de `font-size` en línea;
     - el texto se da formato solo con clases;
     - se le habla al lector de tú;
   - en §5, sumar la guardia a los criterios de terminado;
   - corregir §5: `node --check assets/auditor/js/audit-engine.js`, no
     `assets/js`.
2. **DESIGN.md**: nueva escala móvil en §4.1 (D11) y el fondo vectorial en §3.3
   (D8). Los aprueba el autor.
3. **Con el autor**: los nombres de las secciones y las rutas. Además, agendar la
   compra del dominio (D13).
4. **Guardia**: `herramientas/guardia_legibilidad.py`, en Python con
   Playwright, solo como herramienta. Cualquier agente la corre con
   `python3 herramientas/guardia_legibilidad.py`.
   - Qué mide:
     - las 11 vistas;
     - los emojis, con `\p{Extended_Pictographic}` sobre el texto visible;
     - la posición del título y del primer párrafo en coordenadas de la
       pantalla, después de abrir el módulo;
     - el tiempo hasta poder usar la página en el Android simulado.
   - Metas **absolutas y escalonadas**:
     - en la fase 1: texto menor de 12 px ≤ 10 % y 0 emojis en rótulos;
     - en la fase 2: las metas completas de §1.
   - Correcciones urgentes de cifras: pueden saltarse la guardia con
     `GUARDIA_OMITIR=motivo`, que queda registrado en el commit.

### Fase 1: lectura en todo el sitio

Son entregas chicas y ordenadas para chocar lo menos posible con el otro
desarrollador.

- **1a · CSS** (`auditavision.css`):
  - la escala móvil;
  - las variables `--radius-*`;
  - superficies sólidas;
  - el fondo vectorial;
  - el foco visible;
  - el botón flotante deja de tapar contenido.
- **1b · Cabecera móvil**: marca, botón «Menú» y buscador. El menú lleva Lee,
  Explora, Consulta y Participa.
- **1c · Portada**:
  - el lema;
  - las tres puertas;
  - un ejemplo por puerta;
  - como máximo una cifra fija, con su fuente y su chip;
  - sin cinta, y el radar pasa a Explora.
- **1d · Barrido del motor, la base de datos y el HTML**, un commit por módulo
  (X3):
  - los emojis salen de los rótulos, donde el dato se genera;
  - los `font-size` en línea pasan a clases de la escala;
  - las frases de usted pasan a tú;
  - un solo índice por módulo;
  - el favicon de la marca.
- **1e · Imágenes del carrusel**: archivos nuevos en `assets/auditor/img/`, en
  WebP de 150 KB como máximo, con JPG de respaldo. `assets/img/` no se toca,
  porque es de la Enciclopedia. También se anota que las imágenes para compartir
  (`:3685`) dependen de `assets/img/city_*.jpg`.
- **1f · Velocidad** (X4): carga diferida de `municipios-efipem.js`,
  `municipios-rendicion.js` y Leaflet, con los avisos de «cargando» y de falla.
  Reusa el patrón de `sat-69b.js` (`:3402`).
- **Sello de versión** en cada entrega (AGENTS.md §4).

### Fase 2: módulos en capas

Un módulo por entrega. Cada uno:

- pasa a la plantilla de su sección;
- ordena su contenido en capas, con lo principal arriba y el detalle desplegable;
- deja la guardia en verde;
- recibe el visto bueno del autor.

Orden: calculadora → megaobras → asf-2024 → municipios → panorama-2026, y
después el resto.

**Terminado (X5):** la guardia está en verde, con las metas completas, en
calculadora, megaobras, asf-2024, municipios y panorama-2026.

### Fase 3: dominio (acción del autor)

1. Comprar el dominio.
2. Conectarlo a GitHub Pages.
3. Cambiar `SITIO`.

### Fase 4: URLs (SEO/GEO)

- Todo lo de §4.
- Los resúmenes curados de cada ruta, que aprueba el autor.
- El sitemap se envía a Google Search Console.
- robots.txt permite la entrada a los rastreadores de buscadores y de IA.

### Fase 5: datos (D10)

- Partir `audit-database.js` por módulo.
- El motor deja de exigir todos los datos al arrancar.

## 6. Revisión por secciones

| Sección | Hallazgos | Estado |
|---|---|---|
| 1 · Arquitectura | Rutas relativas, arranque por `#`, composición de las páginas, dominio y ruta base, rutas que salen de fragmentos | Resueltos en §3, §4, D13, D14 y X2 |
| 2 · Errores | Ver §7 | Sin huecos críticos abiertos |
| 3 · Seguridad | Sitio estático, sin datos nuevos del usuario. La acción de CI solo tiene permisos `pages: write` y `contents: read` | Sin hallazgos altos |
| 4 · Casos límite | Sin JS, ligas viejas, rutas inexistentes, tema claro, teclado sobre un resultado fijo, tablas en celular, carga de municipios | Cubiertos en §3, §4 y §7 |
| 5 · Calidad | 1,313 estilos en línea en el HTML y 414 en el motor, 111 `!important` | Se barren en la fase 1d |
| 6 · Pruebas | La guardia sobre las 11 vistas y cada ruta: responde 200, `<title>` único, canonical correcto, 0 errores, resumen presente sin JS, falla provocada del arranque | En el plan |
| 7 · Rendimiento | El JS pesa ~2.9 MB y se procesa en cada página | Fase 1f y fase 5 |
| 8 · Observabilidad | Sin analítica (pospuesta). La guardia deja un reporte y avisa si CI falla | Aceptado |
| 9 · Despliegue | Ramas cortas, vista previa, Actions con manifiesto | En el plan |
| 10 · Trayectoria | Reversibilidad 3/5: las URLs son de un solo sentido. Se mitiga creándolas ya en el dominio | Resuelto con X1 |
| 11 · Diseño | Organización en tres puertas, tres plantillas, contraste en los dos temas, tablas probadas con contenido real | Se recomienda `/plan-design-review` |

## 7. Registro de fallas

| Punto | Qué puede fallar | Qué pasa | Qué ve el lector | ¿Se detecta? |
|---|---|---|---|---|
| `rutas.py` en CI | Falta un resumen o una ruta | La acción falla, **no publica** y avisa por correo de GitHub | La versión anterior, intacta | Sí |
| Despliegue | El artefacto omite archivos (la Enciclopedia) | El manifiesto detiene la publicación | Nada roto | Sí |
| Arranque del motor en una ruta | Falla JS o CDN | El resumen curado sigue visible | El resumen, con aviso | Prueba de falla provocada |
| `RAIZ` mal calculada | Recursos 404 | La guardia en CI lo detecta | No se publica | Sí |
| Carga de municipios | Falla la red | Aviso con botón «Reintentar» | El aviso, no un hueco | Guardia simulando la falla |
| Liga vieja con `#` | `#` sin ruta equivalente | Queda en la portada y deja registro en la consola | La portada | Sí |
| Ruta inexistente | Error de dedo | `404.html` | Las tres puertas y el buscador | — |
| Cifra en un resumen curado | El dato cambia en la base y el resumen no | La guardia compara las cifras del resumen con `AUDIT_DB` | La cifra correcta o CI detenido | Sí |
| Enciclopedia | Se tocan archivos compartidos | Regla: `assets/img` y `assets/css` no se tocan | Sin cambios | Revisión |

## 8. Lo que ya existe y se reusa

- El ruteo por `#` y `pushState` del motor (`:5710` y `:25012` a `:25066`): se
  extiende con `RUTAS` e `irA()`.
- La carga diferida de `sat-69b.js` (`:3402`), para municipios y Leaflet.
- Las variables de marca, `DESIGN.md` y `/brand/`.
- El patrón `erario-indice` (índice único), `chipEstado()` y `.est-chip`.
- `herramientas/sello.py`: `rutas.py` lee el sello y no lo duplica.
- El script de medición de esta auditoría, que se convierte en la guardia.

## 9. Pospuesto y fuera de alcance

**Pospuesto.** Va a «Pendiente» de CONTEXT.md:

- la analítica sin cookies (D3.1);
- «Lo esencial» (D3.3);
- la prueba con usuarios (X5);
- la fase de datos (D10).

**Acción obligatoria:** el dominio, antes de la fase 4.

**Fuera de alcance:**

- la Enciclopedia;
- cifras o contenido editorial nuevos;
- un framework o `npm install` para el sitio;
- la persistencia del portal ciudadano.

## 10. Dónde nos deja respecto al ideal a 12 meses

```
  HOY                           ESTE PLAN                          IDEAL A 12 MESES
  1 página, texto chico,  ──▶   legible en celular, 3 secciones, ──▶ + «Lo esencial», analítica,
  1,749 emojis en JS,           módulos en capas, guardia,          ≤1.5 MB por página,
  sin URLs                      URLs en dominio propio              módulos en su plantilla
```

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 1 | CLEAR | 4 propuestas, 2 aceptadas, 2 pospuestas; 20 decisiones tomadas |
| Codex Review | `/codex review` | Independent 2nd opinion | 1 | issues_found → resueltas | 10 hallazgos; los 6 de fondo decididos (X1–X6) |
| Eng Review | `/plan-eng-review` | Architecture & tests (required) | 0 | — | — |
| Design Review | `/plan-design-review` | UI/UX gaps | 0 | — | — |
| DX Review | `/plan-devex-review` | Developer experience gaps | 0 | — | — |

- **CROSS-MODEL:** Codex y el subagente de Claude coincidieron en adelantar la
  lectura, en no capturar el motor con Playwright y en que las metas necesitan
  umbrales absolutos. Las tres cosas se aceptaron.
- **VERDICT:** CEO CLEARED; eng review required

NO UNRESOLVED DECISIONS
