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

## Los pasos, con cada nota que llegue

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

## Dónde buscar (fuentes oficiales)

| Qué | Dónde |
|---|---|
| Leyes, decretos, circulares de inhabilitación | Diario Oficial de la Federación (dof.gob.mx) |
| Auditorías y denuncias | Auditoría Superior de la Federación (asf.gob.mx) |
| Contratos del gobierno federal | ComprasMX (comprasmx.buengobierno.gob.mx) y CompraNet histórico |
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
