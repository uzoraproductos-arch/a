# La base de datos de Auditavisión

Pedido del autor, 24-10-2026: «se necesita construir la base de datos» para
el pendiente 3 del Auditor Virtual (portales externos y capa de inteligencia
artificial). Es la fase 3 de [LANZAMIENTO.md](LANZAMIENTO.md), ya construida y
probada. Falta solo lo que toca al autor: crear la cuenta y poner las llaves.

## Qué guarda y qué no

| Sí guarda | No guarda |
|---|---|
| Lo que escribe la gente: solicitudes, erratas, temas, reportes, el foro | **Ninguna cifra fiscal.** Las cifras siguen en los archivos que genera Python, con su fuente y su huella |
| «Lo que aún no sé»: las preguntas que el Auditor no supo contestar | Direcciones IP en claro: solo su huella con sal, para el límite por minuto |
| La copia de lo que se consulta en Banxico e INEGI, con dirección, fecha y huella SHA-256 | Llaves: viven en los secretos de Supabase, nunca en el repositorio ni en la página |
| La bitácora de la IA: fichas que recibió, lo que contestó, el modelo, los tokens y si pasó la verificación | |
| Perfiles, alertas, suscripciones y donaciones (fases 3 a 5) | |

## Cómo está hecha

```
   Página (navegador, llave pública)
        │  POST
        ▼
   Funciones de Supabase (llave de servicio, secreta)
   ├─ recibir-formulario ──▶ envios          (antispam + 5 envíos / 10 min)
   ├─ pregunta-bot ────────▶ preguntas_bot   («Lo que aún no sé»)
   ├─ portales ────────────▶ portales_cache  (Banxico SIE; INEGI por verificar)
   ├─ auditor-ia ──────────▶ consultas_ia    (Claude, con cuatro candados)
   └─ buscar-web ──────────▶ busquedas_web   (internet: solo enlaces)

   herramientas/boveda.py --subir (llave de servicio, desde la computadora del autor)
   └────────────────────────▶ evidencias + almacenamiento «boveda»
                               (la huella de cada documento oficial)
                                  │
                    lee las fichas del sitio publicado
                    (assets/auditor/js/asistente-base.js)
```

| Archivo | Qué es |
|---|---|
| `supabase/migrations/20261024000001_auditavision.sql` | Las 14 tablas y vistas, con seguridad por renglón en todas |
| `supabase/migrations/20261024000002_busquedas_web.sql` | La tabla de las búsquedas en internet (pública: solo enlaces) |
| `supabase/migrations/20261027000001_evidencias.sql` | La bóveda de evidencias: tabla pública de huellas SHA-256, inalterable (ni la llave de servicio corrige ni borra), y el almacenamiento «boveda» |
| `supabase/functions/*/index.ts` | Las cinco funciones (Deno) y lo que comparten (`_comun/`) |
| `supabase/pruebas/permisos.sql` | 30 pruebas de permisos: qué ve y qué escribe el público, una persona con cuenta y la administración |
| `supabase/pruebas/cotejo_test.ts` | Pruebas del candado de cifras de la IA |
| `supabase/pruebas/web_test.ts` | Pruebas de lo que puede devolver la búsqueda en internet |
| `herramientas/prueba_base_datos.py` | Corre la migración y las pruebas en un PostgreSQL local, sin cuenta ni red |

## Los cuatro candados de la IA (AGENTS.md §5 ter)

1. **No recibe texto ajeno.** La página manda la pregunta y los números de
   las fichas que encontró su buscador; la función lee esas fichas del sitio
   publicado. Nadie le puede colar una cifra.
2. **Solo ve esas fichas**, con la orden de no calcular, no redondear y no
   salir de ellas.
3. **Cada cifra se coteja.** Si la respuesta trae una cifra que no está en
   las fichas, se tira y el Auditor contesta como hoy, sin IA.
4. **Todo queda anotado** en `consultas_ia`, para auditar a la IA como a
   cualquier otra fuente.

Modelo: `claude-opus-5-5` (se cambia con el secreto `MODELO_IA`), esfuerzo
bajo, salida en JSON con esquema, y si el modelo se niega, la API reintenta
con otro (`fallbacks: "default"`). Tope: 10 preguntas por minuto y 100 por
día por persona.

## La búsqueda en internet (`buscar-web`, 24-10-2026)

Cuando el lector pregunta por un personaje, el chat ya ofrece búsquedas
armadas (no necesitan la base). Con la llave puesta, `buscar-web` las hace por
él con la búsqueda web de Claude:

1. **Solo en sitios de una lista cerrada** (`_comun/web.ts`): los oficiales
   (gob.mx y sus subdominios, INE, SCJN, Congreso, ASF, DOF, INEGI, Banxico,
   TEPJF y la justicia de EE.UU.) y una **lista editorial de prensa**, que
   decide el autor. Nada de redes, foros ni blogs.
2. **Solo enlaces**: título, dirección, sitio, si es oficial o prensa, y la
   fecha de la página. Lo que el modelo escriba se tira; la plataforma no
   publica un texto redactado por IA sobre una persona.
3. **Todo queda en `busquedas_web`**, pública, con modelo y tokens; la misma
   búsqueda se reusa un día. Tope: 5 por minuto y 30 por día por persona.

Usa la misma `ANTHROPIC_API_KEY` que `auditor-ia`.

## La bóveda de evidencias (27-10-2026)

Cada documento oficial que respalda un dato tiene su ficha en
`docs/boveda/evidencias.json`: huella SHA-256, tamaño, tipo y fecha. La
escribe `herramientas/boveda.py`, y `inventario.py` falla si un cotejo
«consta» o «matiz» de Verificamos no tiene evidencia (o un motivo escrito de
por qué no se pudo copiar). Si un documento cambia, la huella vieja se queda
en el historial: así se sabe que lo modificaron después del cotejo.

Muchos portales no abren desde la nube donde trabajan los agentes (DOF, INE,
Cuenta Pública, Transparencia Presupuestaria, energy.gov, archive.org). Desde
tu computadora sí abren, así que la copia completa se hace ahí:

```bash
python herramientas/boveda.py --descargas C:\boveda-auditavision --archivo
# y, cuando exista el proyecto de Supabase:
set SUPABASE_URL=https://TU-PROYECTO.supabase.co
set SUPABASE_SERVICE_ROLE_KEY=...      (en la terminal, nunca en un archivo)
python herramientas/boveda.py --subir C:\boveda-auditavision
```

La carpeta de descargas queda **fuera** del repositorio: los archivos pesan
cientos de megas y van al almacenamiento, no a Git.

## Lo que le toca al autor (decisiones 0.1 a 0.5 de LANZAMIENTO.md)

| Paso | Qué | Costo |
|---|---|---|
| 1 | Crear el proyecto en supabase.com (región más cercana a México) | Gratis para probar; Pro, US$25 al mes, para producción |
| 2 | Pasarle al agente la dirección del proyecto. **Nunca la llave de servicio por chat**: va directo en Supabase → Edge Functions → Secrets | — |
| 3 | Secretos: `SITIO`, `SAL_IP` (cualquier frase larga), `TURNSTILE_SECRET` (antispam de Cloudflare, gratis) | — |
| 4 | `BANXICO_TOKEN`: gratis, desde la página del API del SIE (banxico.org.mx/SieAPIRest/service/v1/, opción del token; llega por correo, 64 caracteres). Va en **GitHub → Settings → Secrets → Actions**; el flujo «Sube la base de datos» lo pasa a Supabase y sube `portales` | Gratis |
| 5 | `INEGI_TOKEN`: gratis en la página de desarrolladores del API de indicadores del INEGI. Igual: secreto de GitHub, y el flujo lo pasa a Supabase | Gratis |
| 6 | `ANTHROPIC_API_KEY`, solo si quieres la capa de IA | Por pregunta, según el modelo |

Con eso, el agente corre `supabase db push` y `supabase functions deploy`, y
conecta los botones «Enviar», «Lo que aún no sé» y «Búscalo en internet» de la página.

## Pendiente, y por qué

- **INEGI**: la dirección sigue la sintaxis de su página de desarrolladores,
  cotejada por el autor el 30-10-2026 (`…/INDICATOR/[id]/es/00/…/BISE/2.0/[token]?type=json`;
  con `BIE:` adelante de la clave usa el BIE, área `0700`). Falta probarla con la llave.
- **Transparencia Presupuestaria y el DOF** no están en `portales`: publican
  archivos de datos abiertos, no una API de consulta. Entran por la fase 4
  (GitHub Actions semanal que descarga, regenera y abre un PR).
- **Encendido el 30-10-2026** (autor: «ambos sí»): `FUNCIONES` apunta al proyecto, el aviso de privacidad dice que los envíos se guardan 12 meses y la migración `20261030000005_conservacion_envios.sql` lo cumple (cada envío nuevo borra los de más de un año; una errata publicada se queda sin correo). `recibir-formulario` y `pregunta-bot` se suben con el flujo. Falta el antispam (`TURNSTILE_SITIO` y `TURNSTILE_SECRET`, gratis en Cloudflare): sin él, solo frena el límite por conexión.
- *(Nota anterior, 27-10-2026)* **La página ya sabe llamar a las funciones (27-10-2026), pero está apagada**:
  no hay proyecto. Al crearlo se llenan tres renglones de
  `herramientas/apartados.py`: `FUNCIONES` (la dirección de las funciones),
  `TURNSTILE_SITIO` (la llave **pública** del antispam) y
  `AVISO_CONSERVACION` (cuánto tiempo se guardan los envíos; sin él la
  generación se detiene, porque el aviso de privacidad debe cambiar antes del
  primer dato). Entonces los formularios de «Cuéntanos lo que viste» mandan su
  texto y devuelven folio, «Lo que aún no sé» llega a `preguntas_bot`, y si el
  servidor falla, el texto se queda en pantalla para copiarlo. Falta el
  formulario de Servicios (`servicios.js`), que tiene su propio envío.
- **La IA no se probó contra la API real**: falta la llave. El candado de
  cifras y el filtro de enlaces de `buscar-web` sí están probados sin red.
- **La lista de prensa es editorial**: la escogió el agente como punto de
  partida (diarios nacionales con hemeroteca en línea); el autor la confirma
  o la cambia en `_comun/web.ts`.

## Los códigos de acceso (29-10-2026)

Mientras la plataforma se perfecciona, la versión de prueba se abre con un código de invitación, como los del Nintendo Switch: ocho casillas, `XXXX-XXXX`.

| Pieza | Qué hace |
|---|---|
| `codigos` | El código, su duración (1 hora a 5 años), sus usos, la fecha límite para canjearlo, la nota y si está revocado |
| `pases` | Un número al azar que guarda el navegador de quien canjeó (`av-pase`). Sin nombre ni correo |
| `canjes` | Qué pase canjeó qué código y cuándo |
| `generar_codigos`, `crear_codigo`, `revocar_codigo`, `codigos_lista` | Las usa el panel (`administracion-codigos.html`); revisan `es_admin()`. `crear_codigo` da de alta un código escrito por la administración (30-10-2026). Desde el mismo día los códigos son de 8 números, del 0 al 9 (migración `20261030000004`); los de letras que existieran se siguen canjeando. Ojo: en Supabase, `pgcrypto` vive en el esquema `extensions`, así que una función que use `gen_random_bytes` necesita `search_path = public, extensions` (la prueba local lo simula) |
| `fijar_codigo_admin`, `codigo_admin_info`, `revisar_codigo_admin` | El código maestro de la administración (30-10-2026, migración `20261030000009`): 8 números que la administración pone y cambia en su panel; solo se guarda su huella bcrypt. Escrito en la entrada, la función `codigo` (con límite de 10 intentos cada 10 minutos y 40 al día por IP) lo revisa con `revisar_codigo_admin` (solo llave de servicio), anota la entrada en `admin_entradas` (fecha y hora, sin IP; 12 meses) y devuelve un enlace de un solo uso (`token_hash`) que el navegador cambia por la sesión en `/auth/v1/verify`. Nunca va en el repositorio ni en el chat |
| `canjear_codigo`, `pase_hasta` | Solo la llave de servicio: las llama la función `codigo`, que pone el límite de 10 intentos cada 10 minutos por IP |
| `solicitudes_codigo` | «¿No tienes código? Obtén uno»: el correo (y, si quiere, nombre y a qué se dedica), solo con el aviso aceptado. Se borra a los 12 meses de atendida |
| `solicitar_codigo` | Solo la llave de servicio (función `codigo`, 3 por hora por IP). No duplica una solicitud nueva del mismo correo |
| `atender_solicitud`, `descartar_solicitud`, `solicitudes_lista` | El panel: asigna un código de un uso con la duración elegida y arma el correo para que el autor lo mande desde el suyo |

Las duraciones van de 1 hora a 5 años, o **ilimitado** (`interval '100 years'`). El tiempo corre desde el canje; si el mismo pase canjea otro código, se suma. El administrador entra a su panel y «Abrir la plataforma como administrador» le da a su navegador un pase ilimitado, marcado como de la administración. Revocar un código le quita su tiempo a quien lo canjeó. Los códigos no llevan 0, O, 1, I ni L (31 caracteres, unos 850 mil millones de combinaciones).

**Para encenderlo:** (1) crear el proyecto; (2) darte de alta en `administradores` con tu `user_id` (Authentication → Users → invita tu correo, y luego en el editor SQL: `insert into administradores values ('<tu user_id>', 'Tu nombre');`); (3) en Authentication → URL Configuration, agregar la dirección del panel a las *Redirect URLs*; (4) llenar `SUPABASE_URL` y `SUPABASE_ANON` (`acceso.py`, la llave **pública**; hecho el 29-10-2026, proyecto `nuqiyzcilbrrlezmesnf`), que van aparte de `FUNCIONES` para no encender los formularios; (5) desplegar: el flujo «Sube la base de datos» (`.github/workflows/base-de-datos.yml`) corre `supabase db push` y `supabase functions deploy codigo --no-verify-jwt` con los secretos del repositorio `SUPABASE_ACCESS_TOKEN` y `SUPABASE_DB_PASSWORD` (y `SAL_IP`, opcional); sin ellos avisa y no hace nada. A mano: `supabase functions deploy codigo --no-verify-jwt` si el proyecto usa las llaves nuevas (`sb_publishable_…`), que no son JWT; (6) cuando quieras cerrar la versión de prueba, `CANDADO = True` y regenerar.

**El límite, dicho claro:** en un sitio estático el candado vive en el navegador. Detiene a quien entra por la puerta, no a quien lee el código de las páginas o desactiva JavaScript. Para cerrar de verdad, el sitio necesita un servidor que revise el pase antes de entregar la página (Vercel, fase 1 de LANZAMIENTO.md).

## Respaldos (27-10-2026)

```bash
python herramientas/respaldo_base.py C:\respaldos-auditavision            # completo, llave de servicio
python herramientas/respaldo_base.py C:\respaldos-auditavision --publico  # solo lo público
```

Baja cada tabla a CSV con un manifiesto de huellas SHA-256. El completo trae
correos: va fuera del repositorio (el script se niega a guardarlo dentro) y
se guarda cifrado. Si una migración agrega una tabla y no se suma a `TABLAS`,
el respaldo se detiene. Conviene correrlo cada semana.

Para comprobar la base en cualquier momento:

```bash
python3 herramientas/prueba_base_datos.py
deno test supabase/pruebas/
```
- **La bóveda corre sola cada miércoles** (`.github/workflows/boveda.yml`, 30-10-2026):
  desde la red de GitHub revisa las direcciones oficiales que respaldan los datos y guarda
  su huella en `docs/boveda/evidencias.json`. No cambia ninguna cifra.
