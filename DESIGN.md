# Auditavisión: sistema de marca

> Esta es la referencia única de la marca: logo, color, tipografía, forma y voz.
> Es para cualquier persona o asistente de IA que toque el sitio. Si una
> decisión de diseño no está aquí, se resuelve con el autor y se anota.

Hay tres fuentes de verdad, y cada una manda sobre lo suyo:

| Qué | Dónde |
|---|---|
| Valores de color y fuentes | `assets/auditor/css/auditavision.css` (en `:root` y `[data-theme="light"]`) |
| Reglas editoriales | `AGENTS.md` §2 y §6, y «Criterio editorial» en `CONTEXT.md` |
| Esta guía | `DESIGN.md` |
| Brand book interactivo | `brand/` (se abre en `/brand/`; su contenido sale de esta guía) |

La Enciclopedia (`enciclopedia.html` y `assets/css`) está congelada y **no se
migra** a esta guía.

**Cómo leer las etiquetas de este documento.** Lo marcado **vigente** es lo
que el CSS del auditor ya hace hoy. Lo marcado **propuesta** es una regla nueva
que todavía no está en el código. Aplicarla es un trabajo aparte (ver §9).

---

## 1. Esencia

| | |
|---|---|
| **Nombre** | Auditavisión, con acento en la o. Nunca «AuditaVision», «Auditavision» ni «AUDITAVISION» en texto corrido. |
| **Lema** | *El gasto público, a la vista.* |
| **Descriptor** | Sistema cívico de fiscalización y geopolítica del gasto público en México |
| **Qué hace** | Sigue el dinero público federal, estatal y municipal con documentos oficiales, y lo explica para que cualquier persona lo pueda revisar. |
| **Para quién** | Ciudadanía general: personas sin formación técnica que quieren saber a dónde va su dinero. |
| **Qué no es** | No es un sitio oficial. No es del gobierno ni habla en nombre de ninguna institución, aunque cite sus documentos. |
| **Tono** | Riguroso, cívico, sobrio, didáctico. |

### Personalidad

| Rasgo | Qué significa en la práctica |
|---|---|
| Riguroso | Toda cifra se rastrea a su documento y lleva su estado (`oficial`, `derivado`, `pendiente`). Lo que no se puede sostener se dice. |
| Cívico | Le habla a una persona que tiene derecho a saber, no a un especialista ni a un cliente. |
| Sobrio | Ni alarma ni celebración: el dato serio basta. Nada de cifras infladas para llamar la atención. |
| Didáctico | Se explica, no se simplifica. Cada término técnico lleva su glosario o su referencia. |

### La idea de la marca

La moneda de oro con alas es **el peso público que sale a vigilar a dónde va**.
Lleva bombín y lupa porque es un inspector, y alas porque el dinero público
vuela: se va a obras, a sueldos y a deudas que nadie ve. El lema lo resume:
*el gasto público, a la vista*.

---

## 2. Logo

El logo es un sistema de dos piezas: una ilustración con carácter para lo
grande y un símbolo plano para lo pequeño.

### 2.1 La ilustración: la moneda inspectora (vigente)

`assets/auditor/img/logo-auditavision.svg` (la copia en `assets/img/` es la
de la Enciclopedia y no se toca). Es una moneda de oro con canto acuñado,
bombín, lupa, cejas, bigote estilo Zapata, sello de lacre con palomita y alas de dos hileras
de plumas. Tiene proporción 128 × 100 y usa degradados.

- **Úsala** en el encabezado (hoy a 72 × 56 px), en «Quiénes somos», en
  portadas, presentaciones y todo lo que se vea en grande.
- **Tamaño mínimo:** 56 px de alto. Por debajo de eso los detalles se
  empastan: usa el símbolo plano.
- **Fondo:** funciona sobre los dos temas. No la pongas sobre fotografía sin
  una superficie detrás.
- No se redibuja ni se recolorea: es la cara de la marca tal como está.
- **El bigote es estilo Zapata** (decisión del autor, 01-10-2026): lleno, con
  las puntas caídas a los lados de la boca. Va así en la ilustración y en
  todas las versiones del símbolo plano.

### 2.2 El símbolo plano: la moneda con rostro (nuevo)

Es la misma moneda reducida a lo esencial: bombín, un ojo, el otro tras la
lupa, el bigote estilo Zapata y cinco plumas por ala. Todo está hecho con rellenos planos. Los
grabados y la separación entre las alas y la moneda son recortes
transparentes, así que el símbolo funciona a una sola tinta y sobre cualquier
fondo.

- **Úsalo** en la pestaña del navegador, en el ícono de la app, en sellos, en
  marcas de agua, en impresión a una tinta y en todo lo menor de 56 px.
- **Tamaño mínimo:** 16 px (favicon). A 16 px el rostro se reduce a dos
  puntos y el bigote, pero la silueta alada se sigue leyendo.

### 2.3 Composición combinada y nombre

- **Combinado:** el símbolo plano a la izquierda y el nombre a la derecha. El
  símbolo mide el doble de la altura de las mayúsculas del nombre, y los
  separa un espacio igual al 18 % del símbolo.
- **Nombre:** «Auditavisión» en Playfair Display Black (900), la misma letra
  del título del encabezado, convertida a contornos.
- **Ancho mínimo del combinado:** 140 px. Por debajo, usa el símbolo solo.
- **Espacio libre:** deja alrededor de cualquier versión un margen igual al
  radio de la moneda. Nada entra en ese margen: ni texto, ni bordes, ni el
  canto de la pantalla.

### 2.4 Color del logo

| Variante | Moneda | Alas | Nombre | Fondo |
|---|---|---|---|---|
| `primary-dark` ★ | `#c9a84c` oro | `#f0ede6` marfil | `#f0ede6` | Oscuro |
| `primary-light` ★ | `#967420` oro | `#575d6e` grafito | `#14171f` | Claro |
| `white-dark` | `#f0ede6` | `#f0ede6` | `#f0ede6` | Oscuro, una tinta |
| `dark-light` | `#14171f` | `#14171f` | `#14171f` | Claro, una tinta |
| `gold-dark` | `#c9a84c` | `#c9a84c` | `#c9a84c` | Oscuro, una tinta oro |
| `gold-light` | `#967420` | `#967420` | `#967420` | Claro, una tinta oro |

Los valores son los mismos `--gold`, `--text-main` y `--text-secondary` de
cada tema: el logo no introduce colores nuevos.

### 2.5 Archivos

Todos están en `assets/brand/logos/`. Son SVG limpios, solo con `fill` en
hexadecimal y sin texto: el nombre va en contornos.

| Archivo | Tipo | Color | Fondo |
|---|---|---|---|
| `combined/auditavision-combined-primary-dark.svg` | Combinado | Principal | Oscuro |
| `combined/auditavision-combined-primary-light.svg` | Combinado | Principal | Claro |
| `combined/auditavision-combined-white-dark.svg` | Combinado | Marfil | Oscuro |
| `combined/auditavision-combined-dark-light.svg` | Combinado | Tinta | Claro |
| `combined/auditavision-combined-gold-dark.svg` | Combinado | Oro | Oscuro |
| `combined/auditavision-combined-gold-light.svg` | Combinado | Oro | Claro |
| `symbol/auditavision-symbol-primary-dark.svg` | Símbolo | Principal | Oscuro |
| `symbol/auditavision-symbol-primary-light.svg` | Símbolo | Principal | Claro |
| `symbol/auditavision-symbol-white-dark.svg` | Símbolo | Marfil | Oscuro |
| `symbol/auditavision-symbol-dark-light.svg` | Símbolo | Tinta | Claro |
| `symbol/auditavision-symbol-gold-dark.svg` | Símbolo | Oro | Oscuro |
| `symbol/auditavision-symbol-gold-light.svg` | Símbolo | Oro | Claro |
| `symbol/auditavision-favicon.svg` | Favicon | Principal | Cuadro `#0c0e15` con radio 12 |
| `wordmark/auditavision-wordmark-primary-dark.svg` | Nombre | Marfil | Oscuro |
| `wordmark/auditavision-wordmark-primary-light.svg` | Nombre | Tinta | Claro |
| `wordmark/auditavision-wordmark-white-dark.svg` | Nombre | Marfil | Oscuro |
| `wordmark/auditavision-wordmark-dark-light.svg` | Nombre | Tinta | Claro |
| `wordmark/auditavision-wordmark-gold-dark.svg` | Nombre | Oro | Oscuro |
| `wordmark/auditavision-wordmark-gold-light.svg` | Nombre | Oro | Claro |

El favicon actual de `index.html` (la balanza a trazo) y el emoji ⚖️ de la
Enciclopedia quedan retirados de la marca. Cambiar el favicon del auditor por
`auditavision-favicon.svg` es parte de la aplicación (§9).

### 2.6 Qué no hacer con el logo

- No lo rotes, estires, inclines ni recortes.
- No le pongas sombras, brillos, contornos ni degradados. La ilustración ya
  trae los suyos; el símbolo plano no lleva ninguno.
- No cambies sus colores fuera de las seis variantes de §2.4.
- No lo pongas sobre la fotografía de la ciudad sin una superficie detrás.
- No uses la ilustración a menos de 56 px ni el combinado a menos de 140 px.
- No reescribas el nombre con otra letra, en mayúsculas o sin acento.
- No lo acompañes de escudos, banderas ni emblemas oficiales. La marca no es
  un sitio de gobierno y no debe parecerlo.

---

## 3. Color

La paleta tiene dos temas, oscuro (predeterminado, `<html data-theme="dark">`)
y claro (`[data-theme="light"]`). Cada color tiene **un solo papel**. Los siete
acentos se conservan (decisión del autor, 29-09-2026); lo que esta guía fija es
para qué sirve cada uno.

### 3.1 Marca: oro (vigente)

| Variable | Oscuro | Claro | Uso |
|---|---|---|---|
| `--gold` ★ | `#c9a84c` | `#967420` | Color de marca: logo, títulos de sección, controles activos, bordes de marca |
| `--gold-bright` | `#f3cf65` | `#7c5c16` | Énfasis y anillo de foco (`:focus-visible`) |
| `--text-gold` | `#e8c86a` | `#7c5c16` | Texto dorado sobre superficie |
| `--gold-glow` | `rgba(201,168,76,.18)` | `rgba(160,120,30,.15)` | Halos y fondos de estado activo |
| `--border-gold` | `rgba(201,168,76,.40)` | `rgba(160,120,30,.38)` | Borde de elementos de marca |
| `--gold-gradient` | `#e8c86a → #c9a84c → #9a7828` | `#967420 → #7c5c16 → #5d440c` | Solo el título «Auditavisión» del encabezado (135°) |

### 3.2 Los seis acentos y su único papel (vigente; papeles fijados aquí)

| Variable | Oscuro | Claro | Papel | Ejemplo |
|---|---|---|---|---|
| `--crimson` / `--crimson-bright` | `#8b1a1a` / `#e74c3c` | `#942020` / `#ba2828` | **Alerta**: irregularidad, monto observado, sobrecosto, cifra en contra | Banderas rojas de la ASF |
| `--emerald` / `--emerald-bright` | `#1e824c` / `#2ecc71` | `#196f3d` / `#1e824c` | **Oficial y verificado**: dato tomado de su documento | Chip `oficial` |
| `--amber` | `#f39c12` | `#b7791f` | **Derivado**: cálculo propio a partir de datos oficiales | Chip `derivado` |
| `--orange` | `#e67e22` | `#b95c0c` | **Advertencia**: riesgo medio, algo que revisar sin ser irregularidad | Avisos de cautela |
| `--cyan` | `#4ecdc4` | `#167a73` | **Referencia y contexto**: `[Ref. N]`, glosario, chip `contexto` | Enlaces a fuentes |
| `--blue` | `#3498db` | `#1f618d` | **Información** neutra: notas y datos de apoyo | Notas informativas |

Solo en el tema claro existe también `--navy: #0b3a6e`, el azul
institucional que usan los títulos, botones y enlaces del tema claro.

### 3.3 Neutros y superficies (vigente)

Las superficies son **translúcidas**: se ven sobre la fotografía de la ciudad
(`city_night.jpg` en oscuro, `city_day.jpg` en claro) y sobre un ruido de
papel al 2.5 %.

| Variable | Oscuro | Claro | Uso |
|---|---|---|---|
| `--bg-surface` | `rgba(12,14,21,.72)` | `rgba(255,255,255,.78)` | Barras y paneles |
| `--bg-card` | `rgba(18,21,32,.62)` | `rgba(255,255,255,.65)` | Tarjetas |
| `--bg-card-alt` | `rgba(23,27,41,.52)` | `rgba(246,244,238,.55)` | Tarjeta alterna |
| `--bg-card-hover` | `rgba(28,33,51,.80)` | `rgba(255,255,255,.90)` | Tarjeta al pasar el cursor |
| `--border-subtle` | `rgba(255,255,255,.10)` | `rgba(0,0,0,.10)` | Borde discreto |
| `--border-accent` | `rgba(255,255,255,.18)` | `rgba(0,0,0,.16)` | Borde marcado |
| `--text-main` | `#f0ede6` | `#14171f` | Texto |
| `--text-secondary` | `#a8a59e` | `#575d6e` | Texto secundario, bajadas, pies |
| `--text-dim` | `#6d6b66` | `#8b92a2` | Texto atenuado; nunca para cifras |

Colores sólidos de referencia (logo, favicon, piezas fuera del sitio):
fondo oscuro `#0c0e15`, fondo claro `#f6f4ee`.

### 3.4 Los tres estados de un dato (vigente)

Es la pieza más propia del sistema. `chipEstado(estado)` en
`audit-engine.js` los pinta con la clase `.est-chip`:

| Estado | Clase | Color | Borde | Significa |
|---|---|---|---|---|
| `oficial` | `.est-oficial` | esmeralda | sólido | Tomado de su documento oficial |
| `derivado` | `.est-derivado` | ámbar | sólido | Calculado por Auditavisión a partir de datos oficiales, con la operación dicha |
| `pendiente` | `.est-pendiente` | gris (`--text-secondary`) | **punteado** | La fuente no lo publica o no se ha podido verificar |

El chip `contexto` (cian) acompaña a lo que no es cifra. `.est-analisis`
(morado) es heredado de la Enciclopedia: **no se usa en contenido nuevo**.

### 3.5 Proporción

Aproximada, en una pantalla típica del auditor: 70 % superficies y
fotografía, 20 % texto, 7 % oro y 3 % acentos de estado. Si un bloque se ve
«de colores», sobran acentos.

### 3.6 Reglas de color

1. Un acento, un papel. Un color no se usa para decorar ni para un significado
   que no sea el suyo: el carmesí nunca marca algo positivo ni el esmeralda
   algo sin documento.
2. El color nunca va solo: todo estado lleva también texto (el chip dice
   `oficial`) o forma (el borde punteado de `pendiente`).
3. En componentes, usa siempre la variable, nunca el hexadecimal. Así el tema
   claro funciona solo.
4. Texto de cifras en `--text-main` o `--text-secondary`, nunca en
   `--text-dim`.
5. El degradado dorado se reserva al título del encabezado.
6. No agregues colores nuevos. Si hace falta uno, se decide con el autor y se
   anota aquí.

---

## 4. Tipografía (vigente)

Todas vienen de Google Fonts.

| Variable | Familia | Pesos | Papel |
|---|---|---|---|
| `--font-serif` | Playfair Display | 400, 700, 900, itálica 400 | Títulos y nombre de la marca |
| `--font-body` | Source Serif 4 | 400, 600, 700, itálica 400 | Texto corrido (`body`) |
| `--font-sans` | Inter | 400, 500, 600, 700 | Interfaz: botones, pestañas, controles |
| `--font-mono` | JetBrains Mono | 400, 500, 700, 800 | Cifras, chips de estado, `[Ref. N]`, eyebrows |

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Source+Serif+4:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

### 4.1 Escala

El CSS actual usa más de veinte tamaños distintos (los más frecuentes: 11, 12,
13, 12.5 y 11.5 px). **Propuesta**: reducirlos a esta escala al migrar.

| Tamaño | Nombre | Familia | Peso | Uso |
|---|---|---|---|---|
| `clamp(28px, 3.2vw, 36px)` | Marca | Playfair | 900 | Título del encabezado (vigente) |
| 28 px | Título 1 | Playfair | 700 | Título de pestaña |
| 22 px | Título 2 | Playfair | 700 | Título de subpestaña o módulo |
| 18 px | Título 3 | Playfair | 700 | Título de tarjeta |
| 15 px | Texto | Source Serif 4 | 400 | Texto corrido, interlineado 1.65 |
| 13 px | Texto chico | Source Serif 4 / Inter | 400–500 | Bajadas, pies de gráfica, controles |
| 11 px | Etiqueta | JetBrains Mono | 600 | Eyebrows y rótulos en mayúsculas, espaciado 0.12em |
| 9.5 px | Chip | JetBrains Mono | 500 | Chips de estado, espaciado 0.07em |

### 4.2 Reglas

1. Playfair solo en títulos. Nunca en párrafos, botones ni cifras de tabla.
2. Toda cifra que se compare va en JetBrains Mono con
   `font-variant-numeric: tabular-nums`.
3. Renglones de 80 caracteres o menos (`max-width: 76ch` en bajadas).
4. Mayúsculas solo en etiquetas mono, siempre con espaciado de letra.
5. Interlineado del cuerpo: 1.65; títulos, 1.05 a 1.2.

---

## 5. Forma y componentes

### 5.1 Radios

Hoy conviven ocho radios distintos (8, 10, 6, 4, 12, 14, 3 y 9 px, de más a
menos usado). **Propuesta**: tres más la píldora.

| Variable propuesta | Valor | Uso |
|---|---|---|
| `--radius-sm` | 4 px | Chips, etiquetas, anillo de foco |
| `--radius-md` | 8 px | Botones, campos, tarjetas pequeñas |
| `--radius-lg` | 12 px | Tarjetas, paneles, ventanas |
| `--radius-pill` | 999 px | Pastillas de filtro |

Al migrar, 3 → 4, 6 → 8, 9 y 10 → 8, 14 → 12.

### 5.2 Foco (vigente)

Todo lo que se opera con teclado muestra
`outline: 2px solid var(--gold-bright)` con `outline-offset: 2px`, o `-2px`
dentro de barras de pestañas. No se quita nunca.

### 5.3 Tarjetas (vigente)

Fondo `--bg-card`, borde `1px solid var(--border-subtle)` y radio grande. El
borde `--border-gold` se reserva a la tarjeta que es la protagonista de su
bloque, no a todas.

### 5.4 Movimiento (vigente)

Las cifras nacen en cero y cuentan con `requestAnimationFrame` y suavizado
cúbico. Con `prefers-reduced-motion: reduce`, el dato aparece completo de
inmediato.

---

## 6. Voz y tono

### 6.1 Principios

| Rasgo | Sí | No |
|---|---|---|
| Cercano | «Tu dinero», «revisa», «pídele a la SSPC» | «El usuario», «se recomienda al ciudadano» |
| Riguroso | «$357,887.3 mdp, ASF, Cuenta Pública 2024, auditoría 247, p. 8» | «Cientos de miles de millones», «según fuentes» |
| Honesto | «Este dato no se publica; lo marcamos pendiente» | Rellenar, redondear a ojo o estimar sin decirlo |
| Sobrio | «La ASF observó $14.1 mdp por recuperar» | «¡Escándalo!», «saqueo», adjetivos de indignación |
| Didáctico | Explicar qué es el Ramo 33 la primera vez que aparece | Dar por sabido el vocabulario técnico |

### 6.2 Reglas de redacción

1. **Al lector se le habla de tú** (decisión del autor, 27-09-2026). Las citas
   textuales de leyes y documentos se dejan como están.
2. Español con acentos, siempre: es contenido público.
3. Toda cifra lleva fuente y chip de estado. Lo que es interpretación se
   rotula como «estimación propia».
4. Las referencias van en el texto como `[Ref. N]`, no como notas al pie
   debajo de las gráficas.
5. Lo derogado se marca con su vigencia; no se borra.
6. Unidades: 1 mdp es un millón de pesos, 1,000 mdp son mil millones y
   1,000,000 mdp es un billón. No se usa «mil mdp».
7. Solo se nombran limitaciones demostrables.
8. Nombres de pestañas y módulos: no se cambian sin decisión del autor.

### 6.3 Glosario de marca

| Se dice | No se dice |
|---|---|
| Auditavisión | AuditaVisión, Audita Visión |
| Pendiente (dato sin documento) | Sin datos, N/D, «próximamente» |
| Derivado (cálculo propio) | Estimado, aproximado (salvo «estimación propia» para interpretaciones) |
| Mdp (millones de pesos) | MDP, mmdp, mil mdp |

---

## 7. Sí y no

**Sí**

- Usa la ilustración en grande y el símbolo plano en pequeño.
- Toma colores y fuentes siempre de sus variables.
- Pon chip de estado a toda cifra.
- Deja que el oro marque lo importante, y solo eso.
- Revisa cada pantalla en los dos temas y a 390 px de ancho.

**No**

- No inventes una cifra, ni para una maqueta.
- No uses un acento fuera de su papel.
- No imites la imagen de una dependencia de gobierno.
- No uses emojis como marca ni como íconos de sección nuevos.
- No quites el anillo de foco.
- No toques la Enciclopedia para aplicar esta guía.

---

## 8. Referencia rápida

Así están hoy en `assets/auditor/css/auditavision.css`. Los radios son la
propuesta de §5.1 y todavía no existen en el archivo.

```css
:root {
  /* Marca */
  --gold: #c9a84c;
  --gold-bright: #f3cf65;
  --gold-glow: rgba(201, 168, 76, 0.18);
  --gold-gradient: linear-gradient(135deg, #e8c86a 0%, #c9a84c 50%, #9a7828 100%);
  --text-gold: #e8c86a;
  --border-gold: rgba(201, 168, 76, 0.40);
  /* Acentos: un papel cada uno */
  --crimson: #8b1a1a;         --crimson-bright: #e74c3c;  /* alerta */
  --emerald: #1e824c;         --emerald-bright: #2ecc71;  /* oficial */
  --amber: #f39c12;                                        /* derivado */
  --orange: #e67e22;                                       /* advertencia */
  --cyan: #4ecdc4;                                         /* referencia */
  --blue: #3498db;                                         /* información */
  /* Superficies y texto */
  --bg-surface: rgba(12, 14, 21, 0.72);
  --bg-card: rgba(18, 21, 32, 0.62);
  --bg-card-alt: rgba(23, 27, 41, 0.52);
  --bg-card-hover: rgba(28, 33, 51, 0.80);
  --border-subtle: rgba(255, 255, 255, 0.10);
  --border-accent: rgba(255, 255, 255, 0.18);
  --text-main: #f0ede6;
  --text-secondary: #a8a59e;
  --text-dim: #6d6b66;
  /* Tipografía */
  --font-serif: 'Playfair Display', Georgia, 'Times New Roman', serif;
  --font-body: 'Source Serif 4', Georgia, serif;
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', Consolas, monospace;
  /* Propuesta: radios */
  --radius-sm: 4px; --radius-md: 8px; --radius-lg: 12px; --radius-pill: 999px;
}

[data-theme="light"] {
  --navy: #0b3a6e;
  --gold: #967420;
  --gold-bright: #7c5c16;
  --gold-glow: rgba(160, 120, 30, 0.15);
  --gold-gradient: linear-gradient(135deg, #967420 0%, #7c5c16 50%, #5d440c 100%);
  --text-gold: #7c5c16;
  --border-gold: rgba(160, 120, 30, 0.38);
  --crimson: #942020;         --crimson-bright: #ba2828;
  --emerald: #196f3d;         --emerald-bright: #1e824c;
  --amber: #b7791f;
  --orange: #b95c0c;
  --cyan: #167a73;
  --blue: #1f618d;
  --bg-surface: rgba(255, 255, 255, 0.78);
  --bg-card: rgba(255, 255, 255, 0.65);
  --bg-card-alt: rgba(246, 244, 238, 0.55);
  --bg-card-hover: rgba(255, 255, 255, 0.90);
  --border-subtle: rgba(0, 0, 0, 0.10);
  --border-accent: rgba(0, 0, 0, 0.16);
  --text-main: #14171f;
  --text-secondary: #575d6e;
  --text-dim: #8b92a2;
}
```

---

## 9. Aplicar esta guía (trabajo aparte)

Documentar la marca no cambió el sitio. Queda pendiente, en este orden y con
el visto bueno del autor:

1. Cambiar el favicon del auditor por `symbol/auditavision-favicon.svg`.
2. Declarar `--radius-*` en el CSS del auditor y migrar los radios sueltos.
3. Migrar los estilos en línea de `index.html` a clases con estas variables.
4. Reducir los tamaños de letra a la escala de §4.1.

Todo eso toca solo `index.html` y `assets/auditor/`. La Enciclopedia no se
migra.

---

*Sistema de marca v1.1 · 01-10-2026 (bigote estilo Zapata)*
