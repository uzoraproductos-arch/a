# Verificamos: cómo entra a la plataforma lo que circula en redes

Protocolo para el autor y para cualquier agente o programador que dé
seguimiento a notas, videos y casos (decisión del autor, 26-10-2026). La
regla editorial manda (AGENTS.md §2): **un video, una nota o una publicación
nunca es fuente**. Es lo que se coteja.

## El objetivo

Que el Auditor Virtual pueda **seguir el dinero**: cuando el lector pregunte
por un caso, un personaje o una empresa contratista, el chat le dice qué
consta en documentos oficiales, qué tiene matices, qué solo dice la prensa y
qué falta, con cada fuente, y el dictamen lo respalda.

## La bandeja del Periodista

**Decisión del autor, 29-10-2026:** el modo Periodista del Auditor se llena con
lo que el autor va pasando («videos o noticias para nosotros verificarlo,
integrarlo… para que cuando el usuario lo responda, pues nosotros ya lo
tenemos resuelto»). Cada pieza sigue los pasos de abajo y se vuelve una
columna de Verificado; desde ahí el Periodista la cuenta sola: en «¿Sabías
esto?» del saludo (las tres más nuevas), en «📢 El ruido» de cada respuesta
y en «🗓️ Lo que sigue». Los casos viejos de Personajes y Hechos que llevan
más tiempo sin moverse salen en «Casos para retomar»: **al cambiar su
`actualizado` con un documento nuevo, el caso vuelve al frente.**

Para cada pieza, el autor pasa lo que tenga:

1. La liga (o el archivo, la captura o la transcripción, si no hay liga).
2. Quién lo dice y dónde: el medio, la cuenta o el programa, y la fecha.
3. Qué le llamó la atención (una cifra, un contrato, una obra, un nombre).

Lo que no cambia: un video o una nota nunca es fuente; a las personas
privadas no se les nombra; un apellido igual nunca es prueba de parentesco;
una acusación no es una condena; y lo que no tiene documento queda
`pendiente`, con quién lo debe. Los contratos y las empresas se cotejan en
ComprasMX y en las listas oficiales (ver «Dónde buscar»); las agresiones a
la prensa, en el Mecanismo de Protección y en la FEADLE
(`herramientas/periodistas.py`).

## Los pasos, con cada nota que llegue

0. **Fijar lo que circula, venga como venga.** Una liga, una captura, un
   video o el audio de un reel sin liga valen igual: lo que se coteja es su
   **texto**. Si llega como audio o video, se transcribe palabra por palabra
   en `circula.texto`, y `circula.red` dice el formato («Instagram (audio de
   un reel)»). Sin liga no se cita a la cuenta que lo publicó ni se le
   atribuye nombre; con liga, se cita como en cualquier nota de prensa.
   Que la plataforma no pueda abrir la liga no detiene el cotejo: lo que
   decide es el documento oficial.
1. **Separar las afirmaciones.** Cifras, nombres, contratos, fechas y
   frases atribuidas. Las opiniones de quien habla («me da la sensación…»)
   se cotejan solo si afirman un hecho.
2. **Buscar el documento oficial de cada una** (lista de abajo). Si el
   documento existe pero no abre desde el entorno, la falta es de la
   plataforma y así se dice.
3. **Darle su resultado:**

   | Resultado | Cuándo |
   |---|---|
   | `consta` | El documento oficial lo dice. |
   | `matiz` | El documento lo sostiene en parte, o dice algo distinto en un punto importante. |
   | `no consta` | Solo lo dicen la prensa o las redes; no hay documento. No se afirma ni se niega. |
   | `pendiente` | El documento debería existir y no lo tenemos: lleva `quien` (a quién le toca o «Falta de la plataforma…») y `donde` (enlace oficial). Entra solo al Registro de pendientes. |

4. **Escribir la columna** en `assets/auditor/js/columnas.js`, sección
   `Verificado`, con `circula`, `cotejo`, `sigue`, `cifras` (solo las que
   sostiene un documento), `fuentes` y `actualizado`. Se respeta el CRLF del
   archivo.
5. **Si nombra a alguien de la vida pública**, su renglón en `PERSONAJES`
   de `herramientas/asistente_personajes.py`. **Si nombra a una empresa
   contratista** que aparece en un documento oficial, su renglón en
   `EMPRESAS`. A los particulares (familiares, apoderados, empleados) no se
   les nombra ni se les agrega.
6. **Regenerar y probar:** `python3 herramientas/sello.py <sello>`, una
   pregunta en el chat por el caso, por la persona y por la empresa, y el
   dictamen. Luego los criterios de terminado de AGENTS.md §5.

## Prensa, personas privadas y derecho de réplica

Reglas completas en AGENTS.md §2 bis y, para el lector, en
`derecho-de-replica.html`. En corto:

- **La nota de prensa se cita con nombre** (quién la firma, qué medio, enlace)
  y nunca es fuente de una cifra. Lo que solo dice la prensa es `no consta`.
- **No se nombra a particulares**, aunque la nota lo haga. Si hace falta
  aludirlos, se dice su relación («un familiar», «un apoderado»).
- **Si alguien pide réplica** y procede (Ley de réplica, arts. 10 a 14):
  su texto va íntegro en el campo `replica` de la columna
  (`[{quien, fecha, texto}]`), sin comentarios ni apostillas (art. 6); se
  cambia `actualizado`, y si demuestra un error nuestro, se corrige la
  columna y se anota en la fe de erratas. Si no procede, se le responde por
  escrito con la causa del art. 19 que aplica.

## Dónde buscar (fuentes oficiales)

| Qué | Dónde |
|---|---|
| Leyes, decretos, circulares de inhabilitación | Diario Oficial de la Federación (dof.gob.mx) |
| Auditorías y denuncias | Auditoría Superior de la Federación (asf.gob.mx) |
| Contratos del gobierno federal | **Ya integrados (2025 y 2026):** `contratos-publicos.html` y el chat («contratos de…», «¿a quién le compra…?»). Se actualizan con `herramientas/actualizar_comprasmx.py`. Los de 2023 y 2024 están en el CompraNet histórico, aún sin integrar |
| Empresas sancionadas o inhabilitadas | Directorio de proveedores y contratistas sancionados (directoriosancionados.buengobierno.gob.mx) |
| Empresas que facturan operaciones simuladas | Listado del artículo 69-B del SAT (ya está en la plataforma: Modo Inspector y el chat) |
| Lavado de dinero y redes financieras | Comunicados de la UIF (en gob.mx/shcp/prensa). La Lista de Personas Bloqueadas de la UIF **no es pública**: no se puede integrar. |
| Sanciones de Estados Unidos | Lista OFAC del Tesoro (sanctionssearch.ofac.treas.gov) |
| Congreso | Gaceta Parlamentaria, Canal del Congreso, Senado |
| Elecciones | INE (Central Electoral, repositorio documental) |
| Presidencia | Versiones estenográficas en gob.mx/presidencia |
| Transparencia de estados y órganos autónomos | Plataforma Nacional de Transparencia |

## Lo que sigue

Cada columna de Verificamos trae `sigue`: lo que falta revisar para seguir el
dinero (un voto, una publicación en el DOF, un informe de la ASF, unos
contratos por integrar). **Quien retome el proyecto empieza por ahí:** abre
`noticias-relevantes.html`, sección Verificamos, revisa cada «🗓️ Lo que
sigue», actualiza la columna (`actualizado`, `cotejo`, `cifras`) y quita lo
que ya se cumplió. Los `pendiente` del cotejo están además en
`pendientes.html` (ids `red-<columna>-<n>`).

**Al actualizar una columna, cambia su `actualizado`.** Es lo que dispara el
aviso «🆕 Novedades» a quien sigue el caso («🔔 Seguir este caso», panel «Tus
seguimientos» de `noticias-relevantes.html#seguimientos`). Si cambias el texto
y no la fecha, nadie se entera. Y no reordenes el `cotejo`: el número de cada
afirmación es el id de su ficha de pendientes, y otras páginas lo citan (la
ficha de Guaymas en Crisis ambientales usa `red-guaymas-comodato-amigo-gnl-1`
y `-8`).

**Si el caso tiene costo ambiental**, además de la columna va una ficha en
Crisis ambientales (`herramientas/crisis_ambientales.py`, función `casos`),
con enlace a la dependencia que lo vigila en el Auditor ambiental
(`herramienta-ambiente-auditor.html#aa-<clave>`; la ASEA es `G00`).

## Los pilares

Este protocolo es la forma práctica de los pilares de la plataforma
(`pilares.html`, AGENTS.md §0 ter): que la verdad sea incómoda no la vuelve
falsa, evidencia con folio, contrapeso y no propaganda, y reconocimiento a
quienes hacen periodismo, cuya nota es el punto de partida del cotejo.
