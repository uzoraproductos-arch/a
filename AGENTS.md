# AGENTS.md — Auditavisión

Instrucciones permanentes para cualquier agente de código que trabaje en este
repositorio: Antigravity, Astra/Codex, Cursor, Claude Code o quien venga.

Aquí están **las reglas**. El estado del proyecto, lo que está hecho, lo que
falta y por qué se decidió cada cosa está en [CONTEXT.md](CONTEXT.md): léelo
antes de tocar código.

---

## 0. El objetivo: la plataforma tiene dos partes

**Decisión del autor, 24-10-2026.** Todo cambio se mide contra esta estructura:

| Parte | Pestaña | Qué es |
|---|---|---|
| **La de consulta** (dogmática, teórica, de aprendizaje) | **Enciclopedia** (`enciclopedia-auditavision.html`: Números, Datos y Aprende) | La fuente de información de todo: cifras, leyes, glosario, Poderes, ambiente. |
| **La de uso** | **Auditor Virtual** (abre `herramienta-inspector-pregunta.html`) | El producto estrella. **Le resuelve al usuario todo lo que se le ofrezca**: cualquier dato, municipio, salud financiera, investigación o auditoría en imágenes. Encuentra, explica y lleva a la página de la Enciclopedia o de la herramienta donde está el detalle. |

- Las cuatro herramientas cuelgan del Auditor Virtual (botón «Herramientas»).
  **El Modo Inspector es las Grandes investigaciones** («realizar grandes
  investigaciones a través de seis aplicaciones»): una sola página,
  `herramienta-inspector.html`, con las seis aplicaciones. Ya no presenta al
  chat como su «otra división», y `herramienta-inspector-investigaciones.html`
  solo redirige ahí. Su imagen es `herr-inspector-camaras.jpg` (elegida por el
  autor); el chat conserva el foróptero (`foto_clase: 'foto-auditor'`).
- El Auditor Virtual tiene que funcionar y verse como lo mejor de la
  plataforma: un dato que la plataforma tiene y el chat no encuentra es un
  error (ver §5 ter).
- Comunidad queda aparte, como la tercera pestaña.

---

## 1. Se trabaja en la rama, `main` es la versión entregada

**Todo el trabajo se hace en la rama `claude/funny-turing-imtm54`.**
`main` es la versión que el autor aprueba: el 29-09-2026 se puso al día con la
rama y quedaron idénticas. Desde entonces, `main` solo avanza cuando el autor
lo pide, así que la rama puede volver a ir adelante. Para ver cuánto le falta
a `main`: `git rev-list --count origin/main..origin/claude/funny-turing-imtm54`
(0 = están iguales).

```bash
git clone --branch claude/funny-turing-imtm54 \
  https://github.com/uzoraproductos-arch/a.git
cd a
```

El ciclo, sin excepciones:

```bash
git pull origin claude/funny-turing-imtm54   # ANTES de empezar
# ...cambios...
git add -A && git commit -m "Describe el cambio"
git push origin claude/funny-turing-imtm54   # AL TERMINAR, aunque quede a medias
```

Un commit imperfecto vale más que un avance perdido: si se cae la sesión o se
acaban los créditos, lo único que se pierde es lo que no se empujó.

**Nunca empujes a `main` sin permiso expreso del autor.**

**La Enciclopedia (`enciclopedia.html`) está congelada** por decisión del autor:
no se modifica, ni siquiera su sello, ni se abre en las pruebas. Es un
proyecto aparte que sirve solo de fuente de consulta; todo el trabajo va a
`index.html`, la plataforma del auditor. **Desde el 27-09-2026 ya no
comparten archivos:** el auditor carga sus copias de `assets/auditor/` y la
Enciclopedia se quedó con `assets/css`, `assets/js` y `assets/data`, que
**no se tocan** salvo que el autor lo pida. Solo `assets/img/` (fotografías)
sigue compartida.

Para saber si una copia está al día:

```bash
git fetch origin && git status
# "up to date with 'origin/claude/funny-turing-imtm54'" = esta copia es la buena
```

**Excepción: rediseño de legibilidad (`docs/ux/PLAN.md`).** Las fases con
cambio visible se trabajan en ramas cortas (`ux/fase-1a`, `ux/fase-1b`…).
Se rebasan cada día sobre `claude/funny-turing-imtm54`, se revisan en una
vista previa y se integran solo con visto bueno del autor. GitHub Pages
publica desde `claude/funny-turing-imtm54`: lo que llega ahí es público.

---

## 2. Regla editorial, por encima de cualquier otra

Esto es una plataforma de fiscalización del gasto público:
**un dato inventado la desacredita entera.**

- Toda cifra debe poder rastrearse a una fuente oficial: DOF, SHCP,
  Transparencia Presupuestaria, ASF, Banxico, INEGI, CONASAMI, INE, SCJN,
  Gaceta Parlamentaria.
- Si un dato no se puede verificar, **se etiqueta como pendiente**, con el
  chip `pendiente`. Nunca se estima, nunca se rellena, nunca se redondea a
  ojo de buen cubero La única aproximación permitida es el rango
  derivado de cotas oficiales (ver más abajo).
- Los estados de un dato son tres: `oficial` (tomado de su documento),
  `derivado` (calculado a partir de datos oficiales, con la operación dicha)
  y `pendiente`. La función `chipEstado(estado)` los pinta.
- Las estructuras derogadas se marcan con su vigencia en lugar de borrarse.
- **Un `pendiente` dice por qué y señala a quién** (decisión del autor,
  09-10-2026). No basta con «no hay documento oficial»: casi siempre falta
  porque la dependencia obligada no lo ha transparentado, y eso se dice con
  su nombre. Ejemplo: «Ni el SAT ni Hacienda han publicado cuánto se evade:
  falta de transparencia de esas dependencias». Solo se nombra a la
  dependencia que de verdad debía publicarlo. Si la falta es de la
  plataforma (el documento existe y aún no lo integramos) o el dato es
  histórico sin dependencia que responda, se dice así, sin culpar a nadie:
  atribuir una omisión que no se puede sostener también es un dato
  inventado.

- **Todo pendiente da la cara** (decisión del autor, 10-10-2026). Además de
  su chip y su porqué, lleva el **enlace oficial donde debería estar** el
  dato y queda en el **Registro de pendientes** (`pendientes.html`, lo
  genera `herramientas/pendientes.py`). Ahí se anota qué falta, por qué
  falta, a quién le toca publicarlo y en qué páginas aparece. Toda
  etiqueta «pendiente» de la plataforma lleva a ese registro al hacerle
  clic, y con `data-pend="<id>"` lleva directo a su ficha. Un registro de
  la base con estado `pendiente` necesita `motivo` y `url`. Si no los
  trae, `pendientes.py` detiene la generación, y `inventario.py` reporta
  como roto cualquier `data-pend` que no tenga ficha.

- **Cuando solo hay aproximación, se da un rango: mínimo, máximo y punto
  medio** (decisión del autor, 10-10-2026). Si la cifra exacta no está
  publicada pero sí se puede acotar, no se escribe «~$380» con chip
  `pendiente`: se escribe «entre X y Y; punto medio Z» con chip
  `derivado`. Condiciones, sin excepción:
  - **El mínimo y el máximo salen cada uno de un documento oficial** (o se
    calculan a partir de cifras oficiales), y cada cota lleva su fuente.
    Una cota que no se puede sostener no es cota: si falta una, el dato
    sigue `pendiente`.
  - **El punto medio es la media aritmética:** Z = (X + Y) ÷ 2. Se dice la
    operación, como todo `derivado`.
  - **Se dice de qué está hecho el rango**, por ejemplo «mínimo con el
    subsidio PEF 2024 ÷ pasajeros AFAC 2024; máximo con el subsidio PEF
    2025 ÷ pasajeros AFAC 2024».
  - **La cifra exacta sigue debiéndose:** el rango no la sustituye, así que
    su ficha del Registro de pendientes se queda, con la nota de que ya
    hay un rango derivado y de quién debe la cifra exacta.

Si te piden una cifra que no puedes sostener, dilo y déjala pendiente. Es la
respuesta correcta en este proyecto.

---

## 3. Cómo está construido

Sitio estático. **Sin framework, sin compilación, sin `npm install`.** Se abre
y funciona.

```
index.html                       Estructura, 9 pestañas, contenido editorial
assets/auditor/css/auditavision.css      Diseño: temas claro y oscuro
assets/auditor/js/mexico-states-geo.js   Geometría de las 32 entidades
assets/auditor/js/audit-database.js      Datos fiscales           → window.AUDIT_DB
assets/auditor/js/municipios-efipem.js   Padrón municipal INEGI
assets/auditor/js/audit-engine.js        Motor y controlador      → window.AuditEngine
herramientas/sello.py            Sube el sello de versión (ver §4)
```

**El orden de carga importa:** geometría y datos **antes** que el motor. El
motor lee `window.AUDIT_DB` y `window.MEXICO_GEOJSON` al arrancar y aborta si
no los encuentra.

Dependencias externas por CDN: Leaflet 1.9.4 y Google Fonts.

Para ejecutarlo hace falta un servidor HTTP. Abrirlo con doble clic (`file://`)
deja la página en blanco: el navegador bloquea los scripts locales.

```bash
python3 -m http.server 8000    # y abrir http://localhost:8000
```

---

## 4. Convenciones que rompen el archivo si se ignoran

- **Saltos de línea CRLF** en `index.html`, los cuatro `.js` y el `.css`.
  Al editar con scripts, ábrelos en binario y preserva los CRLF, o el diff se
  llena de ruido y se pierde la trazabilidad del cambio.
  Cuentas de CR sueltos que deben conservarse (copias de `assets/auditor/`):
  `index.html` 56, `audit-engine.js` 2, `audit-database.js` 2,
  `auditavision.css` 1.
  El `.gitattributes` fija `* -text` para que Git no los convierta al clonar
  ni al commitear, en Windows tampoco. **No lo quites.**
- **El texto va con acentos.** Es contenido de cara al público mexicano.
  Ojo: `audit-engine.js` mezcla acentos reales y secuencias `á`. Al
  anclar un reemplazo, usa fragmentos cortos y sin acentos.
- **La base de datos se llama `window.AUDIT_DB`**, no `AuditDB`.
- `audit-engine.js` es un IIFE que expone su API en `window.AuditEngine` al
  final del archivo. **Todo método invocado desde un `onclick` del HTML tiene
  que estar exportado ahí**, o el botón no hace nada y la consola calla.
- **El sello de versión se sube a mano en todo cambio que toque `assets/`.**
  GitHub Pages sirve con `cache-control: max-age=600` y sin sello el lector
  sigue viendo la copia vieja. Formato `AAAAMMDD` más letra:

  ```bash
  python3 herramientas/sello.py 20260923a
  ```

  Cambia las referencias `?v=` y el sello visible al pie de `index.html` (solo ahí). Si no tocaste
  `assets/`, no lo subas.
- La navegación usa `data-tab` en las pestañas y `data-sub` en las
  subpestañas; los paneles, `data-subpanel`.
- **Reglas de lectura** (condición del dueño: fácil de leer en celular):
  - Sin `font-size` en línea (`style="font-size:…"` ni en cadenas del
    motor). El tamaño se da solo con clases de la escala de DESIGN.md §4.1.
  - El texto corrido nunca baja de 16 px en celular.
  - Todo lo que se toca mide al menos 44 × 44 px.
  - Al lector se le habla de tú, también en los textos del motor.
  - **Los emojis se ven como íconos de trazo** (decisión del autor,
    20-10-2026, que reemplaza la del 12-10-2026). Los textos se siguen
    escribiendo con emojis; `assets/auditor/js/iconos.js`, que se carga en el
    `<head>` de todas las páginas, los cambia al pintar por íconos Lucide de
    un solo color. Un emoji nuevo necesita su renglón en
    `herramientas/iconos.py` (ícono y nombre en español), y luego se corre
    el script; si no, se queda como emoji. No compares textos de la página
    que lleven emoji (`textContent === '🔒 …'`): al pintarse ya no lo traen.

---

## 5. Criterios de terminado

Un cambio **no está hecho** hasta que las seis líneas se cumplen:

1. `node --check assets/auditor/js/audit-engine.js` pasa sin error.
2. La página levanta en `http://localhost:8000` y **la consola del navegador
   no arroja ni un error**.
3. La pestaña tocada renderiza, y las demás siguen renderizando: cambiar de
   pestaña y volver no debe romper nada.
4. Toda cifra nueva lleva su fuente y su chip de estado (§2).
5. Está commiteado y **empujado a `claude/funny-turing-imtm54`** (§1). Si
   tocaste `assets/`, con el sello subido (§4).
6. `python3 herramientas/guardia_legibilidad.py --fase N` pasa, con N la
   fase vigente de `docs/ux/PLAN.md`. Para corregir una cifra con urgencia:
   `GUARDIA_OMITIR="motivo"`, y el motivo se anota en el commit.

Al terminar, di explícitamente qué quedó pendiente y por qué. La lista de
pendientes vive en CONTEXT.md y se mantiene al día: es parte del entregable.

---

## 5 bis. La portada ya no despliega nada: cada clic abre una página

**Decisión del autor, 09-10-2026.** La página principal (`index.html`) queda
como está. **Ningún contenido nuevo se desglosa debajo de ella**, ni en
cuadros que se abren encima: todo clic lleva a una página propia de la
plataforma, bien estructurada (como los apartados `*.html` y las páginas
`auditoria-*.html`). Lo que todavía se despliega en la portada se irá
mudando a su página; no se agregan desgloses nuevos.

- Las páginas se generan con Python desde `herramientas/` (no se editan a
  mano) y comparten cabecera, sello y estilos: `apartados.py` para los
  apartados, `auditorias.py` para Auditoría en imágenes y `expedientes.py`
  para los Expedientes de casos. `sello.py` las
  regenera.
- Si una página necesita abrir un módulo que sigue en la portada, enlaza a
  `index.html?ir=destino&ancla=...` (ver `IR_MODULOS` e `IR_DESTINOS` en el
  motor).
- Hecho así: Auditoría en imágenes (`auditoria-*.html`) y el radar
  hacendario, que dejó de ser menú de la portada y vive en
  `descarga-los-datos.html#radar` (menú «Datos»),
  y los Expedientes de casos por aclarar, que eran el bloque 3 del Modo
  Inspector y viven en `expedientes.html#exp-<id>`
  (`herramientas/expedientes.py` + `assets/auditor/js/expedientes.js`).
- Lo único que se agregó a la portada después (entrega 2 de la propuesta de
  Astra, 10-10-2026, a pedido del autor) son **enlaces**: las tres acciones
  bajo el carrusel. Sus datos los escribe `herramientas/auditorias.py`; no
  se editan a mano. El bloque «Por dónde empezar» se quitó el mismo día por
  decisión del autor («la plataforma queda intacta»): sus temas y su nota de
  verificación viven al pie de cada investigación, y sus accesos, en el
  índice general.
- El menú «Busca y verifica» se fusionó con el Modo Inspector (09-10-2026):
  es su parte B, y `busca-y-verifica.html` solo redirige ahí.
- **El menú tiene tres pestañas, ni una más** (decisión del autor,
  23-10-2026, que reemplaza la de cinco del 09-10-2026): **Auditor
  Virtual** (abre `herramienta-inspector-pregunta.html`, «Pregúntale al
  Auditor»; desde el 23-10-2026 las cuatro herramientas cuelgan de su botón
  «Herramientas», junto a «Cómo platicar conmigo», y `herramientas.html`
  sigue como su índice; el Modo Inspector de ese menú lleva directo a las
  Grandes investigaciones), **Enciclopedia**
  (`enciclopedia-auditavision.html`, con tres tarjetas: Números, Datos y
  Aprende, que conservan sus páginas) y **Comunidad** (`participa.html`, la
  antigua Participa, con tres tarjetas desde el 24-10-2026: Ágora cívica,
  Garantías cívicas y Donaciones. `comunidad.html`, que antes se llamó
  «Comunidad» y luego «Participa», ya no es tarjeta: se fundió con el botón
  «Cuéntanos lo que viste» de la cabecera, su única puerta: ese botón abre
  el cajón con las cinco rutas (algo raro con el dinero público, un dato mal,
  un tema para investigar, compartir el Estado de Cuenta y fe de erratas); el Pase del Auditor Cívico se retiró y
  `pase-del-auditor.html` redirige a Donaciones). Ningún archivo cambió de nombre, para no romper
  enlaces. Las pestañas viven en `MENU` de `herramientas/apartados.py`, y
  la portada (`index.html`) tiene su copia a mano. Lo que cuelga de
  Números, Datos o Aprende muestra «Enciclopedia» en sus migas.
  **Ojo:** la página de la pestaña Enciclopedia no es `enciclopedia.html`,
  que sigue congelada (§1).
  «Números» es la antigua «Sigue el dinero»; su archivo sigue siendo
  `sigue-el-dinero.html`.

---

## 5 ter. El bot es el auditor de la plataforma

**Decisión del autor, 23-10-2026.** «Pregúntale al Auditor»
(`herramienta-inspector-pregunta.html`) no es una herramienta más: es **el
auditor** de Auditavisión. Su encargo es **localizar, interpretar, verificar
y mostrar** al lector, en sencillo, todo lo que la plataforma sabe: datos,
estadísticas, estados de cuenta, sueldos, márgenes, porcentajes,
presupuestos, impuestos, glosario, leyes, referencias y las herramientas
mismas. La plataforma es extensa; el bot es la puerta corta a todo.

- **Todo lo nuevo entra al bot.** Una cifra, página o herramienta que se
  agrega a la plataforma no está terminada hasta que el bot la encuentra:
  las páginas y secciones se indexan solas al regenerar; las cifras
  estructuradas entran al bloque `dat` de `herramientas/asistente.py`
  (`_charla()`) o al catálogo de cifras (`insp_nota.catalogo()`), y se prueba
  con una pregunta en el chat. Las cifras de la pestaña Números entran por
  `herramientas/asistente_numeros.py`: un renglón por cifra, con su estado,
  su documento y la página donde se lee (y debe leerse igual ahí). Las de la
  pestaña Datos, por `herramientas/asistente_datos.py`, igual; las que no
  son millones de pesos llevan su unidad (`un`) y su frase (`fr`). El Poder Legislativo
  y las elecciones, por `herramientas/asistente_legislativo.py`, cotejado
  contra la Constitución, la LGIPE, el INE y el INEGI (nunca contra la
  Enciclopedia, que solo sirve de guía de temas). El Poder Judicial, por
  `herramientas/asistente_judicial.py`, cotejado contra la Constitución, los
  acuerdos del INE (INE/CG563/2025 e INE/CG564/2025), el Manual de
  remuneraciones del PJF y el PEF 2026. Los dos Poderes viven además en la
  pestaña Datos (`datos-poder-legislativo.html`, `datos-poder-judicial.html`),
  una página por grupo de temas, armadas con el mismo texto del bot
  (`PAGINAS` de cada módulo).
- **Responde como chat:** claro, corto y contundente, con la cifra, qué
  quiere decir y su fuente a la vista. Cada respuesta con datos lleva
  **«Saber más»**, que abre la página de la plataforma donde está la
  información (el campo `ir` de la respuesta: una respuesta nueva sin `ir`
  no está terminada), y **«Generar dictamen»**, que abre en otra pestaña el
  dictamen pericial sellado (`herramienta-inspector-dictamen.html`). El
  enlace del dictamen solo lleva la pregunta (`?q=`, y las previas en `&c=`):
  la página vuelve a contestarla con la misma base, así que no se puede
  fabricar un dictamen con cifras ajenas. El dictamen dice que no es un
  documento oficial ni un peritaje con validez ante autoridad.
- **Se ve y se usa como el mejor producto** (rediseño del 24-10-2026): un
  solo logo (el de la cabecera del chat; las burbujas no llevan avatar), cada
  respuesta en cuatro capas (texto, panel de fuente, acciones, «Sigue
  preguntando»), preguntas de ejemplo quietas que solo cambian con «Otras
  preguntas», y «↩️ Regresar» y «🗑️ Limpiar» bajo la caja. La plática se
  guarda en la pestaña (`sessionStorage`, clave `av-chat`); un enlace de una
  respuesta deja la seña `av-volver`, y la página a la que llega muestra
  «Volver al Auditor» (`assets/auditor/js/volver-auditor.js`, cargado en
  todas las páginas junto a `iconos.js`; su estilo vive en `civico.css`).
- **Abre los estados de cuenta y los recursos de la Enciclopedia**
  (24-10-2026). «Estado de cuenta de…» lleva directo al documento (cívico,
  ambiental, cada presidente, diputación federal y local, senaduría, Corte,
  estado, municipio), y al pie de cada respuesta van, en «Explóralo a fondo»,
  los mapas, relojes, tableros, simuladores y páginas de fiscalización que
  vienen al caso («Ver mapa», «Ver fiscalización»…), con el estado ya
  elegido. Los dos catálogos viven en `herramientas/asistente_recursos.py`:
  **un mapa, reloj, contador o simulador nuevo no está terminado hasta que
  tiene ahí su renglón**, y si un enlace o un ancla deja de existir, la
  generación se detiene. Así la Enciclopedia alimenta al Auditor.
- **Cada estado y cada municipio tiene sus cuatro documentos** (24-10-2026):
  estado de cuenta, salud financiera, dictamen y ritmo en vivo, en su ficha
  del Auditor de entes. El contador «en vivo» es la cifra anual oficial
  repartida entre los 31,536,000 segundos del año: va como `derivado`, con
  su operación y con lo que no dice; nunca se presenta como dinero que se
  mueve en tiempo real.
- **Verifica:** ante «¿es cierto que…?», «dicen que…» o la liga de una nota,
  compara contra el documento oficial con el mismo criterio de «Contrasta
  una nota» (`assets/auditor/js/verificador.js`, compartido por los dos).
  Un redondeo solo coincide si no se aleja más de 10 % del documento.
- **La regla editorial (§2) también lo manda.** No escribe cifras propias;
  todo cálculo va como `derivado` con su operación; lo que no tiene lo dice
  y lo anota en «Lo que aún no sé».
- **Hacia dónde va:** consultar portales externos y tener una capa de
  inteligencia artificial que aprenda de las preguntas. Las dos necesitan
  servidor y llaves que GitHub Pages no tiene: son decisión del autor (plan
  en CONTEXT.md). Cuando llegue la IA, solo redacta con lo que le entregan
  las fichas; nunca pone una cifra que no venga de un documento.

---

## 6. Tono al escribir de cara al lector

Formal, cálido y llano, sin renunciar al rigor técnico. El lector no es
especialista pero no es tonto: se le explica, no se le simplifica. Cada
afirmación fuerte va acompañada del artículo, el ramo o el documento que la
sostiene.

**Al lector se le habla de tú** (decisión del autor, 27-09-2026): la
plataforma le habla a una persona, no a un trámite. Las citas textuales de
leyes y documentos se dejan como están. En el motor, que comparte la
Enciclopedia, los textos van en `tuUd('versión usted', 'versión tú')`: el
auditor muestra la de tú. (Heredado de cuando compartían motor; la copia
congelada de la Enciclopedia conserva el usted.)
