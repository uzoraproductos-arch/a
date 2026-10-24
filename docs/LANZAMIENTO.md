# Plan de lanzamiento y crecimiento de Auditavisión

Pedido del autor, 24-10-2026 (dos partes): todos los pendientes para salir en
línea, paso a paso, con **Vercel** (publicación) y **Supabase** (base de
datos), y la lectura de la plataforma con las notas del curso «Contexto
millonario» del autor. Se mantiene al día junto con CONTEXT.md.

> **Lo que no cambia al lanzar:** las cifras siguen saliendo de archivos
> estáticos que genera Python y que cualquiera puede revisar. Supabase guarda
> solo lo que escriben las personas (formularios, foro, preguntas del bot,
> cuentas, alertas y pagos). Ninguna cifra fiscal vive en la base de datos: así
> no se puede alterar sin que se note, y la huella SHA-256 de cada documento
> sigue valiendo. Es la regla de AGENTS.md §2 llevada a la infraestructura.

---

## 1. Verificación de la lista (segunda revisión, 24-10-2026)

Se volvió a cotejar cada pendiente contra el repositorio. Cambios frente a la
primera versión:

| Pendiente | Primera versión | Verificado |
|---|---|---|
| Pase de $79 | «Se ve y no se puede pagar» | **Ya dice «Disponible en el lanzamiento»** (`pase-del-auditor.html`): no engaña. El problema real es otro (siguiente renglón) |
| Lo que promete el Pase | — | **Punto ciego nuevo:** promete el expediente del estado y del municipio en PDF y el ticket cívico, que **ya son gratis** (ficha técnica con «Descargar en PDF» y estado de cuenta cívico). Y promete un radar de alertas que **no existe**: necesita cuentas y correo. Hoy el Pase cobra por lo gratuito y por lo que aún no hay |
| Donaciones | Canal vacío | Confirmado: `CANAL_DONACION = ''` y la alcancía en $0, que solo muestra dinero que de verdad entró |
| Servicios | Canal vacío | Confirmado: `CANAL_SOLICITUD = ''`, el formulario arma el texto y no envía |
| Comunidad | Canal vacío | Confirmado: `CANAL_COMUNIDAD = ''`; foro en `localStorage` |
| Aviso de privacidad | No hay | Confirmado: ninguna página del auditor lo tiene |
| Dirección del sitio | Fija en el código | Confirmado: una sola constante, `SITIO` en `herramientas/apartados.py` (y el agente de `agente_fiscalizacion.py`) |
| Tamaño | ~340 MB | Confirmado: 717 archivos; los PDF de `investigaciones/` llegan a 17 MB cada uno |
| Guardia | 1 error de consola | Confirmado en la vista «portal» de `index.html`, más letra menor a 12 px (24 %; meta ≤ 10 %) |
| Registro de pendientes | 57 | Confirmado: 57, todos con porqué, responsable y enlace |
| Datos con fecha | ASF 30-10-2026 | Confirmado en CONTEXT.md; es en seis días |

## 2. Por qué Vercel + Supabase, y sus dos letras chiquitas

```
                 ┌─────────────────────────────────────────────┐
   Lector ──────▶│ VERCEL  ·  auditavision.mx                  │
                 │ 210 páginas estáticas, tal como hoy          │
                 │ Vista previa por cada rama (la de trabajo)   │
                 │ Producción = main (lo que aprueba el autor)  │
                 └───────┬─────────────────────────────────────┘
                         │ formularios · preguntas · pagos · cuenta
                         ▼
                 ┌─────────────────────────────────────────────┐
                 │ SUPABASE                                     │
                 │ · Base de datos (PostgreSQL) con permisos    │
                 │   por renglón: nadie lee lo de otro          │
                 │ · Cuentas (correo sin contraseña)            │
                 │ · Funciones (Edge Functions): reciben        │
                 │   formularios, cobran, mandan alertas        │
                 │ · Almacén de archivos (PDF de respaldo)      │
                 └───────┬───────────────────────┬─────────────┘
                         ▼                       ▼
                    Stripe / Mercado Pago    Correo (Resend u otro)

   GitHub Actions (cada semana) ─▶ datos abiertos SHCP · INEGI · Banxico
       ─▶ herramientas/*.py ─▶ guardia ─▶ PR ─▶ el autor aprueba ─▶ main ─▶ Vercel
```

**Por qué encaja con las reglas de la casa:**
- Vercel publica `main` como sitio oficial y **cada empuje a la rama de
  trabajo como vista previa**: es exactamente el ciclo de AGENTS.md §1
  (la rama va adelante, `main` es lo aprobado).
- Las funciones van en **Supabase Edge Functions**, no en Vercel: así el sitio
  sigue sin `npm install` ni compilación (AGENTS.md §3) y las llaves secretas
  viven en un solo lugar.

**Las letras chiquitas (verificar al contratar; no se anotan precios porque cambian):**
1. **Vercel Hobby (gratis) es solo para uso no comercial.** Mientras no se
   cobre nada sirve para probar; antes del primer peso (Pase, Servicios,
   donaciones) hay que pasar al plan **Pro**.
2. **Supabase gratis pausa el proyecto tras días sin actividad** y tiene topes
   de base y de correos. Para producción: plan **Pro** y un servidor de correo
   propio (SMTP), porque el de Supabase es solo para pruebas.

## 3. Los pendientes, paso a paso

Cada paso dice quién lo hace y cuándo está listo. **Nada de la fase 1 empieza
sin las decisiones de la fase 0.**

### Fase 0. Decisiones del autor (semana 1)

| # | Decisión | Opciones | Listo cuando |
|---|---|---|---|
| 0.1 | Dominio | `auditavision.mx`, `.org.mx` o `.com.mx`; se compra en un registrador acreditado ante NIC México (Vercel no vende `.mx`) | Comprado a tu nombre o al de la asociación |
| 0.2 | Forma jurídica | Asociación civil (permite donaciones y, si quieres, ser donataria autorizada) o persona física con actividad empresarial | Con RFC: lo pide la pasarela de pago |
| 0.3 | Qué se publica de `investigaciones/` | (a) nada, solo ligas a la fuente oficial; (b) todo, en el almacén de Supabase; (c) solo lo que ya no está en línea en su fuente | Elegido |
| 0.4 | Imagen del Modo Inspector | Confirmar autor y licencia de las cámaras, o reemplazar por una propia | Resuelto |
| 0.5 | **Qué da el Pase** (ver §4.4) | Rehacer su oferta antes de cobrar | Aprobada la nueva oferta |
| 0.6 | Enciclopedia congelada | Publicarla tal cual o dejarla fuera | Elegido |

### Fase 1. La casa nueva en Vercel (semana 1-2)

| Paso | Qué | Quién |
|---|---|---|
| 1.1 | Cuenta de Vercel con tu correo; conectar el repositorio `uzoraproductos-arch/a` | Tú (dos clics) |
| 1.2 | Proyecto: *Framework Preset* «Other», sin comando de compilación, carpeta de salida la raíz; **rama de producción `main`** | Agente te guía |
| 1.3 | `.vercelignore` para no publicar `herramientas/`, `docs/`, `tests` ni lo que decidas en 0.3 | Agente |
| 1.4 | `vercel.json`: encabezados de seguridad, caché de `assets/` con el sello, y las 26 redirecciones como redirecciones reales (hoy son páginas con `meta refresh`) | Agente |
| 1.5 | Apuntar el dominio a Vercel (registros DNS que Vercel indica) y HTTPS automático | Tú en el registrador, agente te dice qué poner |
| 1.6 | `SITIO = 'https://auditavision.mx/'`, `sello.py`: se actualizan `canonical`, Open Graph y `sitemap.xml`; agregar `robots.txt` | Agente |
| 1.7 | La dirección vieja (`uzoraproductos-arch.github.io/a/`) manda a la nueva página por página | Agente |
| 1.8 | Corregir el error de consola y la letra chica de la vista «portal» (guardia) | Agente |

**Listo cuando:** `auditavision.mx` abre igual que hoy, la vista previa de la
rama funciona y la guardia no marca errores.

### Fase 2. Correo y legal (semana 2)

| Paso | Qué | Quién |
|---|---|---|
| 2.1 | Buzones `contacto@`, `investigaciones@`, `privacidad@` (Google Workspace, Zoho o reenvío) y un servicio de envío para avisos automáticos | Tú contratas, agente configura DNS (SPF, DKIM, DMARC) |
| 2.2 | **Aviso de privacidad** (Ley Federal de Protección de Datos Personales en Posesión de los Particulares): qué se pide, para qué, cuánto tiempo, derechos ARCO y a qué correo | Agente redacta, **tú haces la revisión legal** |
| 2.3 | **Términos de uso**: la plataforma no es documento oficial, «por aclarar no es robado», cómo se corrige | Igual |
| 2.4 | Ligas al pie de todas las páginas y casilla de aceptación en cada formulario | Agente |

### Fase 3. La base de datos en Supabase (semana 3-4)

| Paso | Qué | Quién |
|---|---|---|
| 3.1 | Proyecto Supabase en la región más cercana a México; llaves guardadas en sus *secrets* (la llave pública puede ir en la página; la de servicio **nunca**) | Tú creas la cuenta, agente configura |
| 3.2 | Tablas (abajo), con **seguridad por renglón** activada en todas | Agente, con migraciones en `supabase/migrations/` dentro del repositorio |
| 3.3 | Funciones: `recibir-formulario` (solicitudes, erratas, temas, reportes), `pregunta-bot`, con antispam (Cloudflare Turnstile o hCaptcha) y límite por minuto | Agente |
| 3.4 | Llenar `CANAL_SOLICITUD` y `CANAL_COMUNIDAD` con la función; los formularios ya arman el texto, solo cambia el botón «Enviar» | Agente |
| 3.5 | Foro de Comunidad y «Lo que aún no sé» pasan de `localStorage` a la base | Agente |
| 3.6 | Panel de moderación (página privada con cuenta de administrador): aprobar, responder, mandar a erratas | Agente |
| 3.7 | Respaldo: copia diaria de la base (incluida en Pro) y exportación mensual a un lugar tuyo | Tú lo activas |

**Las tablas:**

| Tabla | Qué guarda | Quién escribe | Quién lee |
|---|---|---|---|
| `solicitudes` | Pedidos de investigación (Servicios) | Cualquiera, por la función | Solo administración |
| `erratas` | «¿Viste un error?» | Cualquiera | Administración; lo aprobado se publica en la fe de erratas |
| `temas`, `reportes` | Propuestas y reportes ciudadanos | Cualquiera | Administración; lo aprobado, público |
| `foro_hilos`, `foro_mensajes` | El foro de Comunidad | Personas con cuenta | Público lo aprobado |
| `preguntas_bot` | Lo que el Auditor no supo (sin datos personales) | Cualquiera | Administración: decide qué fichas faltan |
| `perfiles` | Seudónimo, estado y municipio que sigue | La propia persona | Solo ella |
| `alertas` | Qué entes sigue cada persona | La propia persona | Ella y la función de avisos |
| `suscripciones` | Plan, estado y vencimiento (lo escribe el webhook de pago) | Solo la función de pagos | La persona ve la suya |
| `donaciones` | Monto, fecha y comprobante | Solo la función de pagos | **Público** (la alcancía de cuentas claras) |

### Fase 4. Datos que se actualizan solos (semana 4-5)

| Paso | Qué |
|---|---|
| 4.1 | GitHub Actions semanal: descarga datos abiertos de Transparencia Presupuestaria, Banxico (SIE) e INEGI; corre `herramientas/`; corre la guardia y el inventario |
| 4.2 | **Abre un PR, no publica**: tú lo apruebas y `main` lo lleva a Vercel. Si un archivo cambió de formato, la generación se detiene (como ya hace `asistente_recursos.py`) |
| 4.3 | Contadores en vivo con el calendario oficial de pagos del DOF (opción B) |
| 4.4 | Primer uso real: la segunda entrega de la Cuenta Pública 2025 de la ASF (30-10-2026) y el avance del 3.er trimestre |

### Fase 5. Comprar y entregar (semana 5-7)

| Paso | Qué |
|---|---|
| 5.1 | Cuenta en Stripe (acepta tarjeta y OXXO en México) o Mercado Pago, con el RFC de 0.2 |
| 5.2 | Función `crear-pago` (abre el cobro seguro de la pasarela) y `webhook-pago` (escribe `suscripciones` o `donaciones`) |
| 5.3 | Cuentas sin contraseña: la persona escribe su correo y recibe una liga |
| 5.4 | **Página de entrega** «Mi Auditavisión»: sus alertas, los entes que sigue, sus expedientes y su recibo (§4.4) |
| 5.5 | Función programada de alertas: cuando entra un dato nuevo de un ente que alguien sigue, le llega un correo |
| 5.6 | `CANAL_DONACION` con la liga de pago; la alcancía lee `donaciones` |

### Fase 6. Red, difusión y lanzamiento (semana 7-8)

| Paso | Qué | Quién |
|---|---|---|
| 6.1 | Google Search Console y Bing Webmaster con el `sitemap.xml` | Tú das acceso, agente registra |
| 6.2 | Vercel Web Analytics (sin cookies) y un monitor de caída | Agente |
| 6.3 | Cuentas con el mismo nombre en YouTube, Facebook, X, TikTok e Instagram | Tú |
| 6.4 | Barrido final: guardia, inventario, consola sin errores, prueba de cada formulario y de un pago de prueba | Agente |
| 6.5 | `main` al día y anuncio | **Tú das la orden** |

### Fase 7. Después del lanzamiento

Capa de inteligencia artificial que redacte solo con las fichas (la llave
del modelo en una función, nunca en el navegador), consulta de portales
externos, licencias para universidades y medios, informe anual de
transparencia de ingresos (compromiso de la política de independencia).

## 4. La plataforma leída con «Contexto millonario»

Las notas del autor, agrupadas por idea. Para cada una: **dónde ya se
refleja**, **qué falta** y **qué se hace**. Columna «Estado»: ✅ se refleja,
🟡 a medias, ❌ falta.

### 4.1 Mentalidad y propósito

| Frase del curso | Dónde se refleja en Auditavisión | Estado | Qué se hace |
|---|---|---|---|
| «Conectar con mi propósito de vida» · «Decidir mi propio camino de grandeza» | El propósito está escrito: fiscalizar el gasto público con datos oficiales, «exigimos transparencia y empezamos por casa» | ✅ | Ponerlo en una frase de una línea en la portada y en «Quiénes somos» |
| «Visión a largo plazo» | AGENTS.md, CONTEXT.md, el Registro de pendientes y este plan: todo queda escrito para que cualquier agente o persona continúe | ✅ | Un mapa de ruta público de 12 meses (página nueva) |
| «Trabaja más en ti que en tu negocio» · «Invertir en mí para poder dar más» · «Desarrollo personal» | Es del autor, no de la plataforma | — | Reservar en el plan horas fijas para que el autor aprenda lo que el producto necesita (lectura de Cuenta Pública, ventas, liderazgo) |
| «Que los pretextos mueran» · «El reto es psicológico» | Muchos pendientes están listos «para el lanzamiento» desde octubre | 🟡 | **Fecha de lanzamiento** fija y pública; la fase 0 cabe en una semana |
| «Todos hacemos lo mejor que podemos con lo que tenemos» · «No existen personas incapaces, sino estados de conciencia» | Es la filosofía de la plataforma con el lector: «se le explica, no se le simplifica» (AGENTS.md §6); el Auditor contesta en lenguaje de calle | ✅ | Mantenerlo: cero tecnicismo sin explicar |
| «La gente que te quiere te limita…» | No es del producto | — | — |

### 4.2 Valor, proximidad y transformación

| Frase | Dónde se refleja | Estado | Qué se hace |
|---|---|---|---|
| «¿Qué tengo que dar?» · «Aprender a ganar es el juego del valor» | Todo lo que publica es gratis y con fuente: 210 páginas, 2,479 municipios, 32 estados, el Auditor Virtual | ✅ | — |
| «Generar proximidad es poder» | El lector ve **su** estado, **su** municipio y **su** estado de cuenta cívico; el Auditor le habla de tú | 🟡 | Falta que la plataforma **lo recuerde**: cuenta, «mi municipio», alertas cuando cambia un dato (fase 5). Hoy cada visita empieza de cero |
| «Construye tu gallina de los huevos de oro a partir del valor de tu transformación» | La transformación que vende Auditavisión: **de ciudadano que no entiende el presupuesto a auditor ciudadano que verifica una cifra en un minuto** | 🟡 | Decirla así, en una frase, en la portada y en el Pase; hoy está implícita |
| «Crear soluciones estratégicas» | El Auditor, los estados de cuenta, el contraste de notas, el dictamen sellado | ✅ | — |

### 4.3 El negocio digital

| Pieza del curso | En Auditavisión hoy | Estado |
|---|---|---|
| **Producto** | La plataforma y el Auditor Virtual, gratis | ✅ |
| **Servicio** | Servicios de investigación (cinco, con política de independencia) | ✅ escrito, ❌ sin canal |
| **Modelo de negocio** | Gratis para todos; ingresos por Pase, Servicios, licencias y donaciones | ✅ |
| **Modelo de monetización** | Pase $79/mes o $699/año; Servicios por cotización; licencias; donaciones | 🟡 sin pasarela ni tarifas de Servicios (salen de los pilotos) |
| **Clientes** | Ciudadanía, periodistas, organizaciones, universidades, despachos, gobiernos (la política los admite a todos con las mismas reglas) | 🟡 no hay un cliente prioritario elegido |

**Qué se hace:** elegir **un** cliente para los primeros 90 días. Recomendación:
**periodistas y organizaciones civiles**, porque ya buscan exactamente lo que
la plataforma da (cifra + documento + folio verificable) y pagan por ahorrar
horas. La ciudadanía llega por ellos.

### 4.4 La oferta irresistible (el punto ciego más importante)

«Aprender a crear una oferta irresistible, rentable, escalable» · «Construir
ofertas, elegir por inteligencia».

**Hoy el Pase no es irresistible:** dos de sus tres promesas ya son gratis y la
tercera no existe. Propuesta para que el autor decida (0.5):

| Lo gratis (se queda gratis) | Lo que da el Pase (nuevo) |
|---|---|
| Consultar todo, el Auditor, las fichas, el PDF de cada ficha, el estado de cuenta cívico | **Alertas**: un correo cuando la ASF, Hacienda o el INEGI publican algo de los entes que sigues |
| | **Mi expediente**: guardar y comparar fichas en el tiempo (antes y después de cada entrega) |
| | **Resumen mensual** de tu estado y tu municipio, con lo que cambió |
| | **Prioridad** en las preguntas que el Auditor aún no sabe |
| | Insignia de auditor cívico y el informe anual de en qué se gastó cada peso |

Regla que no cambia: **el Pase nunca compra contenido ni oculta una cifra**.
Lo que se paga es comodidad, memoria y aviso; la información pública sigue
pública.

Para organizaciones y medios, un **Pase institucional** (varias cuentas,
alertas por tema, descargas en CSV con su folio) es lo escalable.

### 4.5 Las cuatro páginas del embudo

«Desarrollar una página de aprendizaje, página de ventas, página de compra y
página de entrega».

```
 APRENDIZAJE ────────▶ VENTAS ────────▶ COMPRA ────────▶ ENTREGA
 Enciclopedia,         pase-del-         (no existe)      (no existe)
 Aprende, Auditor      auditor.html,     Fase 5.1-5.2     Fase 5.4
 Virtual               servicios.html                     «Mi Auditavisión»
      ✅                   🟡                 ❌               ❌
```

| Página | Qué tiene | Qué le falta |
|---|---|---|
| Aprendizaje | Lo mejor de la plataforma | Una invitación suave al Pase al final de cada respuesta útil, sin interrumpir (por ejemplo: «¿Quieres que te avise cuando cambie?») |
| Ventas | Precio, promesas y política | La transformación en una frase, la oferta nueva (§4.4), pruebas (cifras de uso cuando las haya, testimonios reales, nunca inventados) y preguntas frecuentes |
| Compra | — | Cobro seguro con tarjeta y OXXO, recibo, aviso de privacidad |
| Entrega | — | Bienvenida, «sigue tu municipio» en un clic, primera alerta de prueba |

### 4.6 Prospectos y contenido

| Frase | Qué se hace |
|---|---|
| «Aprende a crear el contenido correcto para conseguir clientes» · «Línea editorial» | La línea editorial ya existe y es la ventaja: **cada cifra con su documento**. El contenido para redes sale de la propia plataforma: el dato de la semana con su folio, «¿es cierto que…?» resuelto por el Auditor, el contador en vivo de un estado. Un formato por red, siempre con liga a la página |
| «Prospectos, por qué compran las personas, circunstancias emocionales» | Las personas compran por **coraje** (¿en qué se va mi dinero?), **orgullo** (entender lo que otros no) y **seguridad** (votar informado, que no les vean la cara). **Límite ético:** la emoción se despierta con datos verdaderos, nunca con miedo inventado, urgencias falsas ni acusaciones: «por aclarar no es robado» también rige la publicidad |
| «Liderazgo» | Publicar el informe anual de ingresos y la fe de erratas: liderar con el ejemplo («si el gobierno falla, nosotros ponemos el ejemplo») |

### 4.7 Optimización, multiplicación, automatización

| Etapa | En Auditavisión |
|---|---|
| **Optimización** | Medir: qué preguntan al Auditor, dónde se van las personas, qué formulario no se termina (analítica sin cookies, `preguntas_bot`) |
| **Multiplicación** | Los municipios son 2,479 páginas posibles: una ficha por municipio que Google encuentre; licencias a universidades y medios; contenido que se comparte con folio |
| **Automatización** | La tarea programada de datos (fase 4), las alertas (fase 5.5) y la respuesta automática a cada formulario |

## 5. Calendario resumido

```
Semana  1  2  3  4  5  6  7  8
Fase 0  ██
Fase 1  ██ ██
Fase 2     ██
Fase 3        ██ ██
Fase 4           ██ ██
Fase 5              ██ ██ ██
Fase 6                    ██ ██ ← lanzamiento
Datos oficiales: ASF 30-10-2026 · avance 3T fin de octubre · Cuentas Ecológicas diciembre
```

Se puede **lanzar antes** (al terminar la fase 2) con todo gratis y los
formularios funcionando por correo, y sumar cuentas y cobros después. Es la
recomendación: lo que se publica hoy empieza a posicionarse en Google hoy.

## 5 bis. Costos y mantenimiento

Precios de referencia consultados el 24-10-2026 en guías de terceros y en las
páginas de cada servicio; **se confirman en la página oficial al contratar**.
Los servicios en dólares se pagan al tipo de cambio del día: aquí no se
convierten para no inventar una cifra.

### Etapa 1 · Lanzar gratis (sin cobrar nada)

| Concepto | Servicio | Costo | Periodicidad |
|---|---|---|---|
| Publicación | Vercel Hobby | $0 | — (solo uso no comercial) |
| Base de datos | Supabase Free | $0 | — (se pausa tras días sin uso) |
| Dominio `.mx` | Registrador acreditado | Entre $185 y $445 MXN; promedio $295 (GoDaddy) | Anual |
| Correo | Reenvío gratuito, o Google Workspace Business Starter | $0, o $140 MXN por usuario al mes con contrato anual ($168 flexible) | Mensual |
| Avisos por correo | Resend Free | $0 hasta 3,000 al mes y 100 al día | — |
| Antispam | Cloudflare Turnstile | $0 | — |
| Datos automáticos | GitHub Actions | $0 en repositorio público | — |

**Total: el dominio, más el correo si lo eliges de pago.**

### Etapa 2 · Cobrar (Pase, Servicios, donaciones)

| Concepto | Servicio | Costo | Periodicidad |
|---|---|---|---|
| Publicación | Vercel Pro | US$20 por miembro al mes (1 miembro), con uso incluido | Mensual |
| Base de datos | Supabase Pro | US$25 al mes; incluye 8 GB de base, 100,000 usuarios activos y US$10 de cómputo | Mensual |
| Avisos por correo | Resend Pro (al pasar de 3,000 al mes) | US$20 al mes por 50,000 correos | Mensual |
| Correo del dominio | Google Workspace (1 buzón con alias `contacto@`, `investigaciones@`, `privacidad@`) | $140 MXN al mes (anual) | Mensual |
| Dominio | — | Entre $185 y $445 MXN | Anual |
| Cobro con tarjeta | Stripe México | 3.6 % + $3 MXN por cobro (OXXO y meses sin intereses cuestan más) | Por cobro |

**Fijo:** US$45 al mes (US$65 con Resend Pro) + $140 MXN al mes + el dominio al
año. **Al año:** US$540 (US$780 con Resend Pro) + $1,680 MXN + el dominio.

**Lo que deja cada Pase** (derivado; comisión de Stripe antes de IVA):

| Plan | Precio | Comisión: precio × 3.6 % + $3 | Queda |
|---|---|---|---|
| Mensual | $79 | $5.84 | $73.16 |
| Anual | $699 | $28.16 | $670.84 |

**Cuántos Pases mensuales cubren el fijo:**
(US$45 × tipo de cambio del día + $140) ÷ $73.16.

### Costos que no son de servicios en línea (se cotizan, no se estiman)

- Constitución de la asociación civil ante notario y alta en el SAT.
- Contador para la contabilidad y las declaraciones mensuales.
- Revisión legal del aviso de privacidad y los términos.
- La capa de inteligencia artificial (fase 7): se cobra por uso del modelo.

### Calendario de mantenimiento

| Cada | Qué | Quién |
|---|---|---|
| Semana | Aprobar el PR automático de datos; moderar formularios y foro | Autor |
| Mes | Revisar el consumo de Vercel, Supabase y Resend; exportar un respaldo de la base; revisar «Lo que aún no sé» y sumar fichas | Autor y agente |
| Trimestre | Informes trimestrales de Hacienda (avance del gasto y deuda); revisar los 57 pendientes del Registro | Agente |
| Entregas de la ASF | Junio, octubre y febrero (Ley de Fiscalización y Rendición de Cuentas, art. 35): integrar sus resultados | Agente |
| Año | Renovar el dominio; Paquete Económico (septiembre) y PEF aprobado (noviembre); Cuenta Pública (abril); informe anual de transparencia de ingresos; revisar el aviso de privacidad | Autor y agente |

## 6. Los pendientes que no dependen del servidor

Siguen en su lugar y no se mueven con el lanzamiento:

- **Esperan una publicación oficial:** ASF, segunda entrega de la Cuenta
  Pública 2025 (30-10-2026); SHCP, avance del 3.er trimestre; INEGI, Cuentas
  Ecológicas 2025 (diciembre) y EFIPEM 2025 definitiva; SHCP, ajuste del
  Ramo 28 por entidad; SAT, estudio de evasión (2028). Los 57 del Registro
  (`pendientes.html`).
- **Revisar a mano** (no abren desde el entorno del agente): FGR, SAT, IECM,
  SEMARNAT e IPAB.
- **Legibilidad:** la propuesta 2 de `docs/ux/PLAN.md` sigue sin aprobar.

## 7. Puntos ciegos

1. **Publicar no hace aparecer los datos que faltan:** dependen de cada
   dependencia.
2. **Con datos de personas llegan obligaciones:** aviso de privacidad,
   derechos ARCO y qué hacer ante una fuga. Pedir lo mínimo, como ya está.
3. **El Pase no puede cobrar por lo gratuito** (§4.4): sería el primer
   reclamo público, y en una plataforma de cuentas claras pesa doble.
4. **Marketing contra regla editorial:** las técnicas del curso funcionan,
   pero aquí la credibilidad es el producto. Ningún mensaje de venta puede
   llevar una cifra sin fuente ni una acusación.
5. **Vercel Hobby y Supabase gratis no sirven para cobrar ni para
   producción**: el costo mensual empieza con el primer cobro.
6. **La actualización automática puede romper una cifra** si una dependencia
   cambia el formato: por eso abre un PR que revisa el autor.
