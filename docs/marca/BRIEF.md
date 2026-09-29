# Brief de marca — Auditavisión

Punto de partida para generar `DESIGN.md` con el skill
`.claude/skills/brand-book-generator`. Todo lo de la sección «Lo que ya existe»
se extrajo del sitio tal como está en `main`; no hay que volver a preguntarlo,
sólo confirmarlo. Lo de «Pendiente de decidir» sí requiere respuesta de quien
es dueño de la marca.

## Para qué sirve `DESIGN.md`

Que cualquier persona o asistente que toque el sitio use los mismos colores,
tipografías, radios, espaciados y tono sin tener que adivinarlos del CSS. Hoy
eso no es posible: el HTML tiene más de 1,300 atributos `style=` en línea con
valores sueltos (ver «Estilos en línea» en `CONTEXT.md`). `DESIGN.md` es la
referencia contra la cual se migran.

## Cómo generarlo

1. En Claude Code, abierto en la raíz del repositorio, ejecuta
   `/brand-book-generator` (el skill vive en `.claude/skills/` y se detecta
   solo). Con otra herramienta, dale a leer `SKILL.md`, `md-template.md` y este
   brief.
2. Responde las preguntas de «Pendiente de decidir».
3. Aprueba el logo antes de que genere las variantes.
4. Revisa `DESIGN.md`, haz commit y push a `main`.

## Lo que ya existe

### Identidad

- **Nombre:** Auditavisión (con acento en la o).
- **Descriptor en `<title>`:** «Sistema Cívico de Fiscalización y Geopolítica
  del Gasto Público en México».
- **Eyebrow del encabezado:** «Enciclopedia Electrónica de Fiscalización ·
  Geopolítica del Gasto Público en México».
- **Qué hace:** plataforma de fiscalización ciudadana del gasto público federal
  y federalizado. Dirigida a un público no especializado, sin renunciar al
  rigor técnico.
- **Firma:** «Creado por Inspector Meteoro · Enciclopedias Interactivas». El
  sello menciona una plataforma hermana, **Fortuvisión**.
- **Comentario del CSS:** «Estilo Editorial Formal de Alta Densidad
  Informativa».

### Logo actual

- En el encabezado el emblema es el emoji ⚖️ (`.brand-emblem`); el sello del
  autor usa 🪐.
- El favicon ya es un dibujo propio: una **balanza a trazo**, embebida como
  data URI en `index.html`. Decodificado:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#0c0e15"/>
  <g stroke="#c9a84c" stroke-width="3.2" stroke-linecap="round" fill="none">
    <path d="M32 12v38"/>
    <path d="M20 50h24"/>
    <path d="M14 22h36"/>
    <path d="M14 22l-6 13a7 7 0 0 0 12 0z"/>
    <path d="M50 22l-6 13a7 7 0 0 0 12 0z"/>
  </g>
  <circle cx="32" cy="12" r="3.4" fill="#f3cf65"/>
</svg>
```

  Está hecho con `stroke`; el skill pide SVG sólo con `fill`, así que habría que
  convertir los trazos a contornos.

### Color

Definidos en `assets/css/auditavision.css`: tema oscuro en `:root` (el
predeterminado, `<html data-theme="dark">`) y tema claro en
`[data-theme="light"]`.

| Variable | Oscuro | Claro | Papel |
|---|---|---|---|
| `--bg-void` | `#06070a` | `#f6f4ee` | Fondo de página |
| `--bg-surface` | `#0c0e15` | `#ece8dc` | Superficies, `theme-color` |
| `--bg-card` | `#121520` | `#ffffff` | Tarjetas |
| `--bg-card-alt` | `#171b29` | `#f1ede1` | Tarjeta alterna |
| `--bg-card-hover` | `#1c2133` | `#e6e0ce` | Hover de tarjeta |
| `--border-subtle` | `#1e2333` | `#ded7c6` | Borde discreto |
| `--border-accent` | `#2d344d` | `#c7beab` | Borde marcado |
| `--border-gold` | `rgba(201,168,76,.45)` | `rgba(160,120,30,.45)` | Borde de marca |
| `--gold` | `#c9a84c` | `#967420` | **Color de marca** |
| `--gold-bright` | `#f3cf65` | `#7c5c16` | Énfasis dorado |
| `--gold-gradient` | `#e8c86a → #c9a84c → #9a7828` | `#967420 → #7c5c16 → #5d440c` | Degradado 135° |
| `--crimson` | `#8b1a1a` | `#942020` | Alerta, irregularidad |
| `--crimson-bright` | `#e74c3c` | `#ba2828` | Alerta intensa |
| `--emerald` | `#1e824c` | `#196f3d` | Positivo, verificado |
| `--emerald-bright` | `#2ecc71` | `#1e824c` | Positivo intenso |
| `--cyan` | `#4ecdc4` | `#167a73` | Referencias `[27]` |
| `--blue` | `#3498db` | `#1f618d` | Información |
| `--orange` | `#e67e22` | `#b95c0c` | Advertencia |
| `--amber` | `#f39c12` | `#b7791f` | Advertencia suave |
| `--text-main` | `#f0ede6` | `#14171f` | Texto |
| `--text-secondary` | `#a8a59e` | `#575d6e` | Texto secundario |
| `--text-dim` | `#6d6b66` | `#8b92a2` | Texto atenuado |
| `--text-gold` | `#e8c86a` | `#7c5c16` | Texto dorado |

Los `--*-glow` son el mismo color al 15–18 % de opacidad. El `body` lleva tres
halos radiales muy tenues: dorado, carmesí y cian.

### Tipografía

Todas por Google Fonts.

| Variable | Familia | Pesos cargados | Uso actual |
|---|---|---|---|
| `--font-serif` | Playfair Display | 400, 700, 900, itálica 400 | Títulos |
| `--font-body` | Source Serif 4 | 400, 600, 700, itálica 400 | Texto corrido (`body`) |
| `--font-sans` | Inter | 400, 500, 600, 700 | Interfaz, controles |
| `--font-mono` | JetBrains Mono | 400, 500, 700, 800 | Cifras, referencias `[Ref. N]` |

Interlineado del `body`: 1.65. Medida de lectura: 80 caracteres por renglón o
menos (ver `CONTEXT.md`).

### Forma

No hay variables de radio ni de espaciado. Los radios más usados en el CSS son
8 px (61 veces), 6 px (56), 10 px (51), 4 px (37), 12 px (33) y 14 px (25).
`DESIGN.md` debería reducirlos a una escala corta.

### Voz

- Español con acentos: es contenido de cara al público.
- Rigor editorial: «un dato inventado la desacredita entera». Cada cifra se
  rastrea a una fuente oficial y se marca como `oficial`, `derivado` o
  `análisis`.
- Las referencias van en el texto como `[Ref. N]`, nunca como notas al pie
  debajo de las gráficas.
- Lo derogado se marca con su vigencia en vez de borrarse.

Detalle completo en «Criterio editorial» de `CONTEXT.md`.

## Pendiente de decidir

1. **Alcance de la marca:** ¿sólo Auditavisión, o también el sello Inspector
   Meteoro y la relación con Fortuvisión?
2. **Lema:** no hay uno corto. ¿Existe o se propone?
3. **Público prioritario:** ciudadanía general, periodistas, estudiantes,
   activistas…
4. **Qué no es:** partidista, medio de opinión, sitio oficial de gobierno…
5. **Tono en 3–5 adjetivos.** Propuesta a partir del sitio: riguroso, cívico,
   sobrio, didáctico.
6. **Logo:** ¿refinar la balanza del favicon hasta un logo completo (símbolo +
   nombre), o conceptos nuevos? ¿Se retira el emoji ⚖️ del encabezado?
7. **Paleta y tipografía:** ¿se conservan tal cual, o se aprovecha para
   ajustarlas? En particular, ¿cuántos acentos se quedan? Hoy conviven
   dorado, carmesí, esmeralda, cian, azul, naranja y ámbar.
