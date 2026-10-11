# Fase 0: lo que el autor tiene que aprobar

Estas propuestas salen de `docs/ux/PLAN.md`. **No se aplica ninguna hasta que
el autor la apruebe.** La fase 1 no empieza sin las propuestas 1 a 3. Para
contestar, marca cada casilla o escribe tus cambios debajo de cada punto.

La línea base ya está medida con `herramientas/guardia_legibilidad.py` y
guardada en `herramientas/guardia_linea_base.json`. En un celular de 390 px:

| | Hoy |
|---|---|
| Texto menor de 12 px | 16–42 % por vista |
| Texto menor de 14 px | 78–86 % |
| Emojis en rótulos | 37–175 |
| Tocables de menos de 44 px | 44–108 |
| Tiempo hasta usar la portada en un Android simulado (CPU 4× más lenta, 4G lento) | **50 segundos** |

---

## 1. Cambios a AGENTS.md

- [ ] **§1, ramas por fase.** Agregar al final de §1:

  > **Excepción: rediseño de legibilidad (`docs/ux/PLAN.md`).** Las fases con
  > cambio visible se trabajan en ramas cortas (`ux/fase-1a`, `ux/fase-1b`…).
  > Se rebasan cada día sobre `claude/funny-turing-imtm54`, se revisan en una
  > vista previa y se integran solo con visto bueno del autor. GitHub Pages
  > publica desde `claude/funny-turing-imtm54`: lo que llega ahí es público.

- [ ] **§4, reglas de lectura.** Agregar como viñeta nueva de §4:

  > **Reglas de lectura** (condición del dueño: fácil de leer en celular):
  > - Sin emojis en títulos, botones, enlaces, pestañas, menús ni rótulos, ni
  >   en el HTML ni en los textos que genera el motor o la base de datos.
  > - Sin `font-size` en línea (`style="font-size:…"` ni en cadenas del
  >   motor). El tamaño se da solo con clases de la escala de DESIGN.md §4.1.
  > - El texto corrido nunca baja de 16 px en celular.
  > - Todo lo que se toca mide al menos 44 × 44 px.
  > - Al lector se le habla de tú, también en los textos del motor.

- [ ] **§5, criterios de terminado.** Hacer dos cambios:
  - Corregir la línea 1. Hoy revisa la copia de la Enciclopedia:

    ```diff
    - 1. `node --check assets/js/audit-engine.js` pasa sin error.
    + 1. `node --check assets/auditor/js/audit-engine.js` pasa sin error.
    ```

  - Agregar una línea 6:

    > 6. `python3 herramientas/guardia_legibilidad.py --fase N` pasa, con N la
    > fase vigente de `docs/ux/PLAN.md`. Para corregir una cifra con urgencia:
    > `GUARDIA_OMITIR="motivo"`, y el motivo se anota en el commit.

## 2. Cambios a DESIGN.md

- [ ] **§4.1, escala para celular.** Sustituir la escala propuesta por esta.
  Llena la regla de «ningún texto corrido debajo de 16 px»:

  | Nombre | Celular | Escritorio | Familia | Uso |
  |---|---|---|---|---|
  | Marca | 28 px | 36 px | Playfair 900 | Título del encabezado |
  | Título 1 | 26 px | 32 px | Playfair 700 | Título de módulo |
  | Título 2 | 22 px | 24 px | Playfair 700 | Bloque dentro del módulo |
  | Título 3 | 19 px | 20 px | Playfair 700 | Título de tarjeta |
  | Lectura | **17 px** | 18 px | Source Serif 4 | Texto corrido en Lee, interlineado 1.6 |
  | Texto | **16 px** | 16 px | Source Serif 4 / Inter | Texto corrido en Explora y Consulta, controles |
  | Apoyo | 14 px | 14 px | Inter | Pies de gráfica, notas de fuente, bajadas cortas |
  | Etiqueta | 12 px | 12 px | JetBrains Mono 600 | Rótulos en mayúsculas, **dos o tres palabras como máximo** |
  | Chip | 11 px | 11 px | JetBrains Mono 500 | Chips de estado |

  Son 9 tamaños. La guardia exige 8 o menos por vista, porque ninguna vista
  usa a la vez Lectura y Texto.

- [ ] **§3.3, fondo.** Sustituir «las superficies son translúcidas sobre la
  fotografía de la ciudad» por:

  > El fondo es un **dibujo vectorial discreto** (SVG de pocos KB): líneas finas
  > de la ciudad o del territorio, a menos de 6 % de contraste, en los dos
  > temas. Donde hay texto, las superficies son sólidas. La fotografía se
  > retira del fondo. `city_*.jpg` se conserva en `assets/img/` porque la usan
  > la Enciclopedia y las imágenes para compartir.

## 3. Nombres de secciones y rutas

- [ ] **Las tres puertas y Participa:**
  - **Lee:** reportajes para leer.
  - **Explora:** herramientas que se usan.
  - **Consulta:** datos que se buscan.
  - **Participa:** el portal ciudadano.

  ¿Te sirven estos nombres o prefieres otros? Candidatos: «Entiende /
  Calcula / Busca», «Reportajes / Herramientas / Datos».

- [ ] **Rutas.** Son las de la tabla de `docs/ux/PLAN.md` §3. No se publican
  hasta la fase 4, pero conviene fijarlas ya, porque la fase 1 construye el
  menú con estos nombres. Si hay que renombrar alguna, anótalo aquí.

## 4. Acción pendiente: dominio propio

- [ ] Comprar el dominio (por ejemplo `auditavision.mx`) y conectarlo a GitHub
  Pages antes de la fase 4 (URLs). Mientras tanto, el sitio sigue en
  `uzoraproductos-arch.github.io/a/` y no se envía ningún sitemap.
