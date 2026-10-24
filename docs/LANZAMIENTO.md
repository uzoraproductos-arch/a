# Plan de lanzamiento de Auditavisión

Pedido del autor, 24-10-2026: «muchos detalles se resuelven sacando la
plataforma en línea». Aquí está todo lo que falta para lanzarla, en orden, con
lo que decide el autor y lo que hace el agente. Se mantiene al día junto con
CONTEXT.md.

> **Lo que no cambia al lanzar:** las cifras siguen saliendo de archivos
> estáticos que genera Python y que cualquiera puede revisar. La base de datos
> es solo para lo que escriben las personas (formularios, foro, preguntas del
> bot, cuentas y pagos). Ninguna cifra fiscal vive en la base de datos: así no
> se puede alterar sin que se note, y la huella SHA-256 de cada documento sigue
> valiendo.

---

## 1. Dónde estamos

```
HOY                                          AL LANZAR
GitHub Pages (uzoraproductos-arch.github.io/a)    auditavision.mx (dominio propio)
Solo archivos estáticos                      Archivos estáticos + funciones + base de datos
Formularios que no envían (canales vacíos)   Formularios que llegan a un correo y a la base
Foro y «Lo que aún no sé» en localStorage    Guardados en la base, con moderación
Cifras que se actualizan a mano              Tarea programada que descarga y regenera
Sin aviso de privacidad                      Aviso de privacidad y términos de uso
```

## 2. «Bessel» es Vercel, y no es la única opción

Lo que te mencionaron casi seguro es **Vercel**, un servicio que publica sitios
web desde GitHub. Sirve, pero tiene un punto ciego para este proyecto:

| Servicio | Para qué sirve | Punto ciego |
|---|---|---|
| **GitHub Pages** (el de hoy) | Publica los archivos estáticos gratis | No corre funciones ni guarda datos; el sitio vive en `/a/` |
| **Vercel** | Publica el sitio y corre funciones | **El plan gratuito (Hobby) es solo para uso no comercial**; con Servicios, Pase y donaciones hay que pagar el plan Pro, que se cobra por persona del equipo |
| **Cloudflare Pages + Workers** | Publica el sitio, corre funciones, trae base de datos (D1), antispam (Turnstile), analítica sin cookies y reenvío de correo | No vende dominios `.mx`: el dominio se compra en otro lado y solo se apunta a Cloudflare |
| **Netlify** | Parecido a Vercel | Mismo tipo de límites en su plan gratuito |

**Recomendación:** **Cloudflare Pages** para el sitio, **Supabase** para la base
de datos (PostgreSQL con cuentas de usuario y permisos por renglón) y el dominio
`.mx` comprado en un registrador acreditado ante NIC México. Si prefieres Vercel,
el plan funciona igual cambiando la primera pieza; solo hay que contratar Pro
antes de cobrar el primer peso.

Verifica los precios vigentes en la página de cada servicio al contratar: aquí
no se anotan porque cambian y no se inventan.

## 3. La arquitectura

```
                    ┌──────────────────────────────┐
  Lector ──────────▶│  auditavision.mx (Cloudflare) │
                    │  · 210 páginas estáticas       │  ← las genera Python
                    │  · cifras con su fuente        │    (herramientas/)
                    └──────┬───────────────┬────────┘
                           │ formularios   │ preguntas del bot
                           ▼               ▼
                    ┌──────────────────────────────┐
                    │  Funciones (Workers / API)    │  ← antispam Turnstile
                    └──────┬───────────────┬────────┘
                           ▼               ▼
                    ┌────────────┐   ┌─────────────┐
                    │  Supabase  │   │ Correo del  │
                    │ (personas) │   │  dominio    │
                    └────────────┘   └─────────────┘

  GitHub Actions (cada día o semana) ─▶ descarga datos abiertos de Hacienda,
  INEGI, Banxico ─▶ corre herramientas/ ─▶ abre un PR ─▶ el autor aprueba ─▶ se publica
```

## 4. Todos los pendientes, por tipo

### A. Bloquean el lanzamiento (decide el autor)

| # | Pendiente | Por qué bloquea |
|---|---|---|
| A1 | Comprar el dominio (`.mx` o `.org.mx`) | Sin dominio no hay correo, ni canales, ni `robots.txt` |
| A2 | Elegir dónde se publica (§2) | Define el resto de la instalación |
| A3 | **Aviso de privacidad** y **términos de uso** | Los formularios piden seudónimo y correo: son datos personales (Ley Federal de Protección de Datos Personales en Posesión de los Particulares). Hoy el auditor no tiene aviso |
| A4 | Origen y licencia de las imágenes (cámaras con ojos del Modo Inspector, sin autor a la vista) | Una imagen de origen dudoso desacredita como un dato inventado |
| A5 | El Pase Cívico de $79 se ve, pero no hay forma de pagarlo | Al publicarse, o se conecta la pasarela o se marca «próximamente» |
| A6 | Qué se publica de `investigaciones/` (PDFs de trabajo, cerca de 340 MB) | Son documentos oficiales descargados; publicar el respaldo da transparencia, pero pesa y algunos pasan de 15 MB |
| A7 | Visto bueno para llevar la rama a `main` | `main` es la versión aprobada |
| A8 | Forma jurídica (por ejemplo, asociación civil) | La necesitan las donaciones, la pasarela y, si se quiere, ser donataria autorizada ante el SAT |

### B. Se resuelven solos al tener dominio y servidor (hace el agente)

| # | Pendiente | Qué se hace |
|---|---|---|
| B1 | `SITIO` en `herramientas/apartados.py` apunta a GitHub Pages | Cambiar a `https://auditavision.mx/` y correr `sello.py`: se actualizan `canonical`, Open Graph y `sitemap.xml` |
| B2 | `CANAL_SOLICITUD` vacío (Servicios) | Llenarlo con el correo o la función que guarda la solicitud |
| B3 | `CANAL_COMUNIDAD` vacío (erratas, «¿Viste un error?», temas) | Igual |
| B4 | `CANAL_DONACION` vacío | La liga de la pasarela, cuando exista (A8) |
| B5 | El foro de Comunidad guarda en el navegador | Guardar en la base, con moderación |
| B6 | «Lo que aún no sé» del bot vive en cada navegador | Registro central: así se sabe qué fichas faltan |
| B7 | `robots.txt` y Google Search Console | Ya se puede: el sitio vive en la raíz |
| B8 | El «Volver al Auditor» y la plática usan `sessionStorage` | Siguen igual; no necesitan servidor |

### C. Esperan una publicación oficial (no se estiman)

| Dato | Quién lo debe | Cuándo |
|---|---|---|
| 2.ª entrega de la Cuenta Pública 2025 | ASF | 30-10-2026 |
| Avance del gasto, 3.er trimestre 2026 | SHCP | Fin de octubre de 2026 |
| Cuentas Ecológicas 2025 | INEGI | Diciembre de 2026 |
| Finanzas municipales 2025 definitivas (EFIPEM) | INEGI | Por publicar |
| Ajuste del Ramo 28 por entidad | SHCP | Con los coeficientes de junio o la Cuenta Pública 2026 |
| Estudio de evasión (huachicol fiscal) | SAT | Principios de 2028 |
| 57 pendientes con porqué, responsable y enlace | Cada dependencia | `pendientes.html` |

### D. Bloqueados desde el entorno de trabajo (revisar a mano)

FGR, SAT, IECM, SEMARNAT (dgiraDocs) e IPAB no abren desde el contenedor del
agente. Ya en línea, la tarea programada (§5, fase 4) lo vuelve a intentar desde
otra red; si tampoco abre, el autor los revisa desde su navegador.

### E. Calidad antes de anunciar

- La guardia de legibilidad aún marca, en la vista «portal» de `index.html`,
  letra menor a 12 px (24 %; meta ≤ 10 %) y **un error en la consola**:
  corregirlo antes de anunciar.
- La propuesta 2 de `docs/ux/PLAN.md` (escala de letra y fondo) sigue sin
  aprobar.

## 5. El plan, paso a paso

| Fase | Qué | Quién | Listo cuando |
|---|---|---|---|
| **0. Decisiones** | A1, A2, A4, A5, A6, A8 | Autor | Dominio comprado y servicio elegido |
| **1. Casa nueva** | Cuenta en Cloudflare (o Vercel) conectada al repositorio; dominio apuntado (DNS); HTTPS; `SITIO` cambiado (B1); `robots.txt`; redirección de `github.io/a/` al dominio | Agente, con el autor para los pagos y las cuentas | `auditavision.mx` abre igual que hoy |
| **2. Correo y legal** | Correos `contacto@`, `investigaciones@`, `privacidad@` (reenvío gratuito de Cloudflare o un buzón de pago); aviso de privacidad y términos en páginas propias, enlazados al pie y en cada formulario | Agente redacta; **el autor hace la revisión legal** | Los avisos están publicados y aprobados |
| **3. Base de datos** | Proyecto Supabase con tablas `solicitudes`, `erratas`, `temas`, `mensajes_foro`, `preguntas_bot`, `donaciones`; permisos por renglón (nadie lee lo de otro); funciones que reciben los formularios con antispam; llenar B2 a B6; panel de moderación | Agente | Un formulario de prueba llega a la base y al correo |
| **4. Datos que se actualizan solos** | Tarea programada de GitHub Actions: descarga datos abiertos (Transparencia Presupuestaria, Banxico SIE, INEGI), corre `herramientas/` y la guardia, y **abre un PR**; nada se publica sin que el autor lo apruebe. Calendario oficial de pagos en los contadores en vivo (opción B) | Agente | El primer PR automático llega con el avance del 3.er trimestre |
| **5. Red y difusión** | Google Search Console y Bing con el `sitemap.xml`; analítica sin cookies; monitor de caída; cuentas en YouTube, Facebook, X, TikTok e Instagram con el mismo nombre; tarjetas para compartir (ya existen) | Autor abre las cuentas; agente conecta | El sitio aparece en Google |
| **6. Lanzamiento** | Barrido final (guardia, inventario, consola sin errores); `main` al día; anuncio | Autor da la orden | Público |
| **7. Después** | Cuentas y Pase con pasarela (Stripe, Mercado Pago o Conekta, con RFC); capa de IA que redacte solo con las fichas (necesita llave de API en una función, nunca en el navegador); consulta de portales externos | Autor decide el orden | — |

## 6. Lo que se vincula con la red

| Vínculo | Para qué | Fase |
|---|---|---|
| DNS del dominio → Cloudflare | Que el dominio abra el sitio | 1 |
| GitHub → Cloudflare | Cada cambio aprobado se publica solo | 1 |
| Correo del dominio | Recibir solicitudes, erratas y avisos | 2 |
| Supabase (llaves en variables de entorno, nunca en el código) | Guardar lo que escriben las personas | 3 |
| Turnstile | Frenar spam sin captchas molestos | 3 |
| Datos abiertos de SHCP, INEGI, Banxico | Actualizar cifras | 4 |
| Search Console, Bing Webmaster | Que te encuentren | 5 |
| Redes sociales | Difundir con tarjetas de vista previa | 5 |
| Pasarela de pago | Pase y donaciones | 7 |
| API de un modelo de lenguaje | Capa de IA del Auditor | 7 |

## 7. Puntos ciegos

1. **Publicar no resuelve los datos que faltan.** Los pendientes de la sección C
   dependen de las dependencias, no del servidor.
2. **Con datos de personas llegan obligaciones:** aviso de privacidad, derechos
   ARCO, resguardo y a quién se responde si hay una fuga. Conviene guardar lo
   mínimo: seudónimo y correo opcional, como ya está.
3. **La actualización automática puede romper una cifra** si Hacienda cambia
   el formato de un archivo. Por eso abre un PR que revisa el autor en vez de
   publicar directo, y la generación se detiene si algo no cuadra.
4. **El costo crece con el éxito:** los planes gratuitos tienen topes de
   funciones y de base de datos. Hay que revisar el consumo el primer mes.
5. **La Enciclopedia congelada** (`enciclopedia.html`) se publica tal cual o se
   deja fuera: decisión del autor.
