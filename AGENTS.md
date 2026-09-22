# AGENTS.md — Auditavisión

Instrucciones permanentes para cualquier agente de código que trabaje en este
repositorio: Antigravity, Astra/Codex, Cursor, Claude Code o quien venga.

Aquí están **las reglas**. El estado del proyecto, lo que está hecho, lo que
falta y por qué se decidió cada cosa está en [CONTEXT.md](CONTEXT.md): léelo
antes de tocar código.

---

## 1. La rama de trabajo no es `main`

**Todo el proyecto vive en la rama `claude/funny-turing-imtm54`.**
`main` se quedó 37 commits atrás: no tiene la calculadora cívica, ni el padrón
municipal, ni las 32 entidades, ni el Paquete Económico. **No sirve como punto
de partida y clonarla es perder el trabajo.**

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

Para saber si una copia está al día:

```bash
git fetch origin && git status
# "up to date with 'origin/claude/funny-turing-imtm54'" = esta copia es la buena
```

---

## 2. Regla editorial, por encima de cualquier otra

Esto es una plataforma de fiscalización del gasto público:
**un dato inventado la desacredita entera.**

- Toda cifra debe poder rastrearse a una fuente oficial: DOF, SHCP,
  Transparencia Presupuestaria, ASF, Banxico, INEGI, CONASAMI, INE, SCJN,
  Gaceta Parlamentaria.
- Si un dato no se puede verificar, **se etiqueta como pendiente**, con el
  chip `pendiente`. Nunca se estima, nunca se rellena, nunca se redondea a
  ojo de buen cubero.
- Los estados de un dato son tres: `oficial` (tomado de su documento),
  `derivado` (calculado a partir de datos oficiales, con la operación dicha)
  y `pendiente`. La función `chipEstado(estado)` los pinta.
- Las estructuras derogadas se marcan con su vigencia en lugar de borrarse.

Si te piden una cifra que no puedes sostener, dilo y déjala pendiente. Es la
respuesta correcta en este proyecto.

---

## 3. Cómo está construido

Sitio estático. **Sin framework, sin compilación, sin `npm install`.** Se abre
y funciona.

```
index.html                       Estructura, 9 pestañas, contenido editorial
assets/css/auditavision.css      Diseño: temas claro y oscuro
assets/js/mexico-states-geo.js   Geometría de las 32 entidades
assets/js/audit-database.js      Datos fiscales           → window.AUDIT_DB
assets/js/municipios-efipem.js   Padrón municipal INEGI
assets/js/audit-engine.js        Motor y controlador      → window.AuditEngine
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
  Cuentas de CR sueltos que deben conservarse: `index.html` 56,
  `audit-engine.js` 2, `audit-database.js` 2, `auditavision.css` 1.
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

  Cambia las cinco referencias `?v=` y el sello visible al pie. Si no tocaste
  `assets/`, no lo subas.
- La navegación usa `data-tab` en las pestañas y `data-sub` en las
  subpestañas; los paneles, `data-subpanel`.

---

## 5. Criterios de terminado

Un cambio **no está hecho** hasta que las cinco líneas se cumplen:

1. `node --check assets/js/audit-engine.js` pasa sin error.
2. La página levanta en `http://localhost:8000` y **la consola del navegador
   no arroja ni un error**.
3. La pestaña tocada renderiza, y las demás siguen renderizando: cambiar de
   pestaña y volver no debe romper nada.
4. Toda cifra nueva lleva su fuente y su chip de estado (§2).
5. Está commiteado y **empujado a `claude/funny-turing-imtm54`** (§1). Si
   tocaste `assets/`, con el sello subido (§4).

Al terminar, di explícitamente qué quedó pendiente y por qué. La lista de
pendientes vive en CONTEXT.md y se mantiene al día: es parte del entregable.

---

## 6. Tono al escribir de cara al lector

Formal, cálido y llano, sin renunciar al rigor técnico. El lector no es
especialista pero no es tonto: se le explica, no se le simplifica. Cada
afirmación fuerte va acompañada del artículo, el ramo o el documento que la
sostiene.
