# Rediseño del Portal de Acceso (`canjea-tu-codigo.html`) — Especificación aprobada por el autor

**Fecha:** 23-11-2026 · **Aprobado por el Director Creativo** (Opción 2 de imagen editorial + Tarjeta de 2 pestañas + Reestructura en 2 planos).

## 1. Nueva imagen editorial

- **Origen en este paquete:** `docs/ux/portada-acceso-editorial.webp` (`1376 × 768`, `107,230 bytes`, `sha256: 07e1cc48e6e85e2ec9ae7a7bdc5febfeddf024f739da31d957ed76220df6d9f7`).
- **Destino al implementar (Ronda 12):** copiar a `assets/auditor/img/portada/portada-acceso-editorial.webp` (reemplazando `cabecera-lluvia.webp` en `canjea-tu-codigo.html` y en su `og:image`).
- **Descripción / `alt`:** arquitectura cívica mexicana al amanecer con un muro azul marino a la izquierda (contraste natural para el titular y las preguntas) y un paseo arbolado con jacarandas, cantera clara y luz cálida de mañana a la derecha.
- **Crédito discreto:** `Ilustración editorial generada con IA`.

## 2. Reestructura visual en dos planos

Se abandona la columna dividida 50/50 estirada (que apretaba todo el contenido en `560 px` y alargaba la foto izquierda más de `2,500 px`).

### Plano 1 — Hero de acceso (`min-height: 100dvh`)
- Imagen de fondo a ancho completo (`object-fit: cover; object-position: 62% 50%`) con velo direccional azul marino sutil desde la izquierda (`linear-gradient(100deg, rgba(7, 25, 62, 0.84) 0%, rgba(11, 42, 99, 0.56) 46%, rgba(11, 42, 99, 0.14) 100%)`) para garantizar contraste alto en el texto izquierdo y dejar lucir la luz cálida y las jacarandas detrás de la tarjeta derecha.
- Contenedor centrado `max-width: 1200px`, grid `minmax(0, 1.15fr) minmax(360px, 468px)` (en `<= 960px` pasa a una sola columna).
- **Columna izquierda (identidad editorial):**
  - Marca (`logo-auditavision.svg` + `Auditavisión` + `El gasto público, a la vista`).
  - Titular `<h1>` en `Playfair Display` 900 (`clamp(34px, 4.1vw, 54px)`, `line-height: 1.08`, `letter-spacing: -0.02em`, `text-wrap: balance`): `Las cuentas del gobierno,` + `<span>con sus documentos</span>` en dorado claro `#ebd07f`.
  - Párrafo conciso de quiénes somos (`max-width: 52ch`, `17px`, alto contraste).
  - Pregunta detonadora sobre barra lateral dorada (`border-left: 3px solid #c8a032`), conservando las **8 preguntas en el HTML** y respetando `prefers-reduced-motion`.
  - Tira discreta con **3 cifras contadas automáticamente de la base** (`RFC en lista 69-B`, `contratos ComprasMX`, `municipios y alcaldías`, en `JetBrains Mono` tabular, sin números inventados).
- **Columna derecha (tarjeta protagonista de acceso, `.ac-card`):**
  - Tarjeta blanca elevada (`border-radius: 20px`, sombra tintada en azul marino `rgba(7, 29, 71, 0.34)`).
  - **Dos pestañas accesibles (`role="tablist"`):**
    1. **`Tengo código`** (`#tabTengo`, activa por defecto) → muestra `#acCanje` con las **8 casillas `XXXX – XXXX`** en grid proporcional `repeat(4, minmax(0, 1fr)) auto repeat(4, minmax(0, 1fr))` (`min-height: 54px` en escritorio, `>= 48px` en móvil, `JetBrains Mono` 700, estado visual al llenarse, pegado inteligente y flechas), texto de ayuda, botón ancho completo `Ingresar` y `#acEstado` + `#acTuyo`.
    2. **`Solicitar código`** (`#tabPedir`) → muestra `#acPedir` con sus campos exactos (`#acPCorreo`, `#acPNombre`, `#acPMotivo`, checkbox `acepta` con aviso de privacidad, botón `Pedir mi código` y `#acPEstado`).
  - Pie discreto dentro de la tarjeta: liga a `servicios.html` (*«Conoce los Servicios»*).
  - **Sin botones duplicados** en el primer pantallazo.

### Plano 2 — Cuerpo editorial a ancho completo (`max-width: 1200px`)
- **Sección 1 — Los 4 ejes (`#acEjesTit`):** rejilla **2×2** equilibrada (1 columna en móvil), tarjetas blancas limpias con borde superior `#0b2a63`, conteos reales en `JetBrains Mono` (`font-variant-numeric: tabular-nums`), nota metodológica y botón único `[data-pide-codigo]` que hace scroll suave a la tarjeta y activa automáticamente la pestaña **`Solicitar código`**.
- **Sección 2 — Banda editorial en 2 columnas (`1fr 1fr`):** izquierda *«Lo último, verificado»* (las 3 notas con fecha monoespaciada); derecha *«Preguntas frecuentes»* (acordeón limpio con `+` / `−`).
- **Pie sobrio** a ancho completo con versión de prueba, aviso de privacidad y sello.

## 3. Contratos técnicos a preservar (cero regresiones)
- **IDs y selectores intactos** para `acceso.js` y `acceso-paginas.js`: `#acCanje`, `#acCasilla0` (`data-i="0..7"`), `#acEstado`, `#acTuyo`, `#acPedir`, `#acPCorreo`, `#acPNombre`, `#acPMotivo`, `#acPEstado`, `[data-pide-codigo]` y `<dialog id="acFelicidades">`.
- **SEO intacto:** conservar `<title>`, `<meta description>`, `canonical`, Open Graph (actualizando `og:image` a `portada-acceso-editorial.webp`) y JSON-LD (`WebSite`, `Organization`, `FAQPage`).
- **Legibilidad móvil (`AGENTS.md §4`):** cero desborde horizontal a `390 px`, texto corrido mínimo `16 px` en celular, casillas y botones `>= 44 px`.
- **Panel de administración (`administracion-codigos.html`):** no romper ninguno de sus estilos compartidos en `acceso.css` (`.ac-panel`, `.ac-tabla`, `.ac-pestanas`, `.ac-kpis`, `.ac-graficas`).
