# AGENTS.md — Auditavisión

Instrucciones permanentes para cualquier agente de código que trabaje en este
repositorio: Antigravity, Astra/Codex, Cursor, Claude Code o quien venga.

Aquí están **las reglas**. Dónde va el proyecto, en corto, está en
[ESTADO.md](ESTADO.md): empieza por ahí. Lo que está hecho, lo que falta y por
qué se decidió cada cosa está completo en [CONTEXT.md](CONTEXT.md).

---

## 0. El objetivo: la plataforma tiene dos partes

**Decisión del autor, 24-10-2026.** Todo cambio se mide contra esta estructura:

| Parte | Pestaña | Qué es |
|---|---|---|
| **La de consulta** (dogmática, teórica, de aprendizaje) | **Enciclopedia** (`enciclopedia-auditavision.html`: Números, Datos y Aprende) | La fuente de información de todo: cifras, leyes, glosario, Poderes, ambiente. |
| **La de uso** | **Auditor Virtual** (abre `herramienta-inspector-pregunta.html`) | El producto estrella. **Le resuelve al usuario todo lo que se le ofrezca**: cualquier dato, municipio, salud financiera, investigación o auditoría en imágenes. Encuentra, explica y lleva a la página de la Enciclopedia o de la herramienta donde está el detalle. |

- **El Auditor trabaja en cuatro modos** (decisión del autor, 29-10-2026:
  «las herramientas… se van a convertir como en estos modelos que contienen
  las inteligencias artificiales»): **Inspector** (la investigación más
  completa: expedientes, entes, estados de cuenta, RFC, nepotismo, contratos
  y megaobras), **Periodista** (un tema contado como nota, con las Noticias;
  se llamó «Reportero» hasta que el autor lo renombró el 29-10-2026, y
  `?modo=reportero` sigue sirviendo),
  **Ciudadano** (en corto, como un amigo, con la Calculadora Cívica; es el
  modo con el que abre) y **Ambientalista** (costo y daño ambiental). Viven
  en `MODOS` de `herramientas/asistente.py`: cada uno con su saludo, sus
  aplicaciones y sus preguntas de ejemplo (`modo_de()`); se eligen en el
  botón de la cabecera del chat, se recuerdan en el navegador (`av-modo`) y
  se piden por la dirección (`?modo=periodista`). **Periodista** (29-10-2026) suma bajo la respuesta
  «📰 La nota del Periodista» (`periodista()` de `asistente.js`): lo que casi nadie
  cuenta, sacado de la base (ASF, pendientes con quién los debe, cotejos de lo
  que circula, lo que sigue); **lo «privilegiado» es lo enterrado en documentos
  públicos, nunca un rumor**. El banco de pruebas acepta `modo`. **El modo cambia la forma de
  investigar y de contestar, nunca los datos** (§2). Por entregas: (a) el
  selector, hecho; (b) la forma de responder de cada modo, hecha (Periodista el
  29-10-2026; los otros tres el 04-11-2026: `inspectorCapa()`, «🔍 La revisión del
  Inspector»: de qué está hecha la respuesta por chip, sus documentos, lo que falta y
  por dónde seguir; `ciudadanoCapa()`, «🙋 En corto»: la respuesta en una oración, sus
  palabras difíciles con el glosario y su estado de cuenta cívico; `ambientalistaCapa()`,
  «🌎 La mirada ambiental»: los proyectos con alerta ambiental del tema o del estado
  y quién los paga, o, si no hay, el puente del tema a su lado ambiental (`AMB_PUENTE`, solo a páginas que existen);
  sin nota, el Periodista enseña los puntos ciegos que toca la respuesta y calla en las herramientas. **Ninguna capa agrega cifras**. Cada modo ofrece pasarse al que le
  toca, con `MODO_PAL` de `asistente.js`, y el banco de pruebas lee la capa de
  cualquier modo con `capaModo()`); (c) el dictamen de cada modo, hecho (04-11-2026): el
  enlace lleva `&modo=` y el dictamen suma la capa del modo como capítulo, «La lectura del
  modo X», sin botones; la página vuelve a contestar con la base y **el modo no entra a la
  huella**.
- **Las cuatro herramientas se mudaron a la Enciclopedia** (29-10-2026): su
  índice es la quinta tarjeta de Números, «Herramientas del Auditor»
  (`numeros-herramientas-del-auditor.html`, `HERR_INDICE` y `HERR_SITIO` de
  `apartados.py`), y sus páginas cuelgan de ahí en las migas.
  `herramientas.html` solo redirige.
  **El Modo Inspector es las Grandes investigaciones** («realizar grandes
  investigaciones a través de seis aplicaciones»): una sola página,
  `herramienta-inspector.html`, con sus aplicaciones (siete desde el
  28-10-2026: la sexta es Nepotismo y parentesco). Ya no presenta al
  chat como su «otra división», y `herramienta-inspector-investigaciones.html`
  solo redirige ahí. Su imagen son las cámaras con ojos (elegida por el
  autor, dibujada desde el 27-10-2026: `herr-inspector-ilustracion.svg`); el
  chat lleva el foróptero, en la ilustración del autor desde el 29-10-2026
  (`herr-auditor-foroptero.webp`, `foto_clase: 'foto-auditor'`).
- El Auditor Virtual tiene que funcionar y verse como lo mejor de la
  plataforma: un dato que la plataforma tiene y el chat no encuentra es un
  error (ver §5 ter).
- Comunidad queda aparte, como la tercera pestaña, y **Noticias** es la
  cuarta desde el 28-10-2026 (ver §5 bis).

### 0 quater. El menú de cinco pestañas y el Planisferio

**Decisión del autor, 02-11-2026.** El menú (`MENU` de `apartados.py` y su
copia a mano en `index.html`) queda: **Auditor** (antes «Auditor Virtual»),
**Servicios** (segunda desde el 21-11-2026, pedido del autor), **Planisferio**, **Comunidad** (con la Enciclopedia como cuarta tarjeta, tras
Ágora, Garantías y Donaciones) y **Noticiero** (antes «Noticias»); **Servicios** es `servicios.html`, que fue módulo del Modo Inspector. **Desde el 21-11-2026 su portada va como una página de producto** (rediseño del autor con getfinos.com de referencia: «muy esquematizado, muy concreto»): una idea por sección y en este orden: portada, **la base al día** (sube antes de «Cómo funciona» desde el 21-11-2026, pedido del autor; la imagen del autor va de fondo del recuadro de la portada, del lado donde estaba el ejemplo de la empresa y sus hallazgos, `sv-hero-foto`, desde el 21-11-2026), cómo funciona (tres pasos: elige tu servicio, la revisión y tu dictamen, y pedir más solo si hace falta; **sin caja de preguntas ni botón «Elige tu servicio» desde el 22-11-2026**), **los servicios: qué necesitas, lo nuevo y cómo operan** (fusionadas el 21-11-2026, pedido del autor: una pestaña por familia y cada servicio con su cobro y sus novedades, `sv_servicios_y_nuevo()`; **sin botones**: el nombre del servicio y cada novedad son ligas a la respuesta completa del Inspector, `resp_liga()` de `servicios_fichas.py`; **el Inspector de cada servicio vive en su propia página** (pedido del autor, 22-11-2026: «cada vínculo nos va a dirigir… a una página autónoma independiente dentro de la plataforma donde va a estar nuestro inspector»): `servicios-revisa.html?s=<id>` (`revisa_liga()` de `servicios_fichas.py`; **nunca `?servicio=`, que es de la cotización**), con el recuadro de `sv_mostrador()` y `sv-mostrador.js`; el nombre de cada servicio, su «Revísalo con el Inspector», cada novedad (`&q=&abre=`) y cada consecuencia de «Lo que arriesgas» llevan ahí, con el servicio ya elegido y que se puede cambiar; `#revisa-<id>` de `servicios.html` se manda solo allá; **el documento que se descarga es el dictamen**; pide lo que cada servicio recibe (`SV_ENTRADA`: **un servicio nuevo necesita ahí su renglón**, con ejemplos que el chat contesta y sin personas físicas, o la generación se detiene), abre la aplicación del servicio para los archivos (se leen en el navegador, nada se sube) y contesta ahí mismo con la respuesta completa en vista «De un vistazo» (`servicios-respuesta.html?vista=1`, `vistazoHtml()` de `asistente.js`: la respuesta en corto, lo que encontró cada capítulo de «La revisión completa», el dictamen a un toque y lo demás desplegable; mismos datos, nada nuevo a la huella); **«Cómo operan» y «Compara los servicios de…» se quitaron el 22-11-2026** (el autor: «ya quedó superado»): las páginas de `SV_PAGINAS` siguen vivas, sin tablero en la portada), **lo que arriesgas si no revisas** (`SV_CONSECUENCIAS`: cada consecuencia con su artículo, su cita textual y la huella de su ley; **nunca un monto de multa** y nunca se dice que revisar libra de nada) y **las preguntas frecuentes, completas** (`PREGUNTAS`, las mismas de `servicios-preguntas.html`; desde el 21-11-2026 «¿Cuánto cuesta?» y «¿Es seguro?» dejaron de ser secciones y son preguntas: **una duda nueva va como pregunta, no como sección**). **No se repite una sección**: el catálogo completo vive en su página. Desde el 11-11-2026 va en cuatro familias (`LINEAS` de `apartados.py`), cada servicio con su forma de cobro en `COBRO` (**nunca un monto sin pilotos**), y sus argumentos y cuentas viven en `servicios-por-que.html`: **un servicio nuevo necesita su renglón en `COBRO`**, o la generación se detiene. **Cada servicio tiene su página** (`servicio-<id>.html`, 18-11-2026) **y su ficha en `FICHAS` de `herramientas/servicios_fichas.py`**: lo que la plataforma ya hace gratis, sus preguntas al Auditor, su fundamento en la Biblioteca del Erario (términos del Diccionario y fichas de Referencias, tal como están en la base) y en la Enciclopedia, y sus palabras para el chat (`srv_<id>`). **Un servicio nuevo sin ficha, o una ficha con una liga, un término o una referencia que no existan, detienen la generación**; **una herramienta nueva de la plataforma entra a la ficha del servicio que la aprovecha** (etiqueta «Nuevo»), y así llega al tablero y al chat; desde el 21-11-2026 «Lo nuevo» de `servicios.html` va dentro de «¿Qué necesitas?», por familia y por servicio (`sv_servicios_y_nuevo()`), y cada página de servicio la trae en su sección `#nuevo`. **Los Servicios operan para quien tiene un código de acceso vigente** (decisión del autor, 19-11-2026): lo manda `SERVICIOS_OPERAN` de `apartados.py`, que cambia todos los avisos a la vez, y `servicios.js` no envía la solicitud sin pase vigente; **el servidor lo revisa también** (`SERVICIOS_CON_CODIGO` de `supabase/functions/recibir-formulario`, con `pase_hasta`): si los dos no dicen lo mismo, la generación se detiene. En el chat, la respuesta de cada servicio dice quién puede pedirlo y cada modo le suma su capa (`svCapa()` de `asistente.js`, con lo que agrega `herramientas/asistente_servicios.py`): **ninguna capa da montos ni dice que un servicio mide lo que no mide**. Las familias y los perfiles se ven por pestañas (`data-sv-tabs` de `servicios.js`; **un perfil nuevo necesita su nombre corto en `PERFILES_CORTO`**), y el argumento de fraude y lavado vive en `RIESGOS` (`#riesgo`): **nunca dice que la plataforma evita el fraude ni que cumple por el cliente**. Desde el 12-11-2026 `servicios.html` es un **tablero de tarjetas**: cada sección vive en su página (`SV_PAGINAS` de `apartados.py`) y las ligas viejas a sus anclas se mandan solas allá (`SV_ANCLAS`); **una sección nueva de Servicios es una tarjeta con su página, no un desglose en el tablero**. **Toda tarjeta de Servicios sale de `sv_card()`** (19-11-2026: una sola tarjeta, `.sv-card`), y la de un servicio lleva sus cuatro puertas (`sv_acciones()`: el servicio, el Auditor, su dictamen con «servicio de <nombre>» y su cotización) y sus aplicaciones (`sv_apps()`); el dictamen cierra con el servicio que toca (`svDicHtml()`), y la cotización monta la pregunta en el chat con la aplicación principal del servicio (`sv_monta()`): **nunca un monto, y nada de eso entra a la huella**. **Los simuladores son servicios** (20-11-2026, familia `simuladores`: `simulacion` y `escenarios`; el simulador laboral, `cc_laboral.py`, cita la LFT renglón por renglón y **nunca se dice como asesoría ni como convenio**; los salarios vencidos y el reparto de utilidades van aparte del total, como escenario, y en el apartado B solo sale lo que la LFTSE ya da: lo demás lo fija el laudo; el contrato eventual y la plataforma digital siguen su fracción del art. 50, y lo que la ley no dice claro va «en espera», sin sumarse): la cuenta la hace el simulador, con su artículo; **un simulador nuevo entra a la ficha del servicio que lo aprovecha**, y el encargo nunca se dice como declaración ni un escenario como pronóstico. **La cotización se llena con opciones a un toque** (pedido del autor, 16-11-2026): el servicio, el ámbito, el periodo, el plazo y el uso son botones (`.sv-ops` de `servicios.js`), y cada servicio trae ejemplos de tema y pregunta que se tocan y se cambian (`SV_EJEMPLOS` de `apartados.py`: **un servicio nuevo necesita ahí sus ejemplos**, sin cifras ni nombres, o la generación se detiene); todo campo sigue siendo libre. Ningún
archivo cambió de nombre. Las páginas de Números, Datos y Aprende marcan
Comunidad (`ENCICLO_MARCAN`) y sus migas empiezan «Comunidad › Enciclopedia».
Donde §0 y §5 bis dicen «pestaña Enciclopedia» o «Noticias», léase así.

- **El Planisferio es la segunda herramienta en funcionalidad**, después del
  Auditor: un mapa grande de México por **dimensiones** (`DIMENSIONES` de
  `herramientas/planisferio.py`): financiera, deuda, inversión, ambiental,
  legislativa y judicial. Toca una entidad y lleva a su **portal**
  (`planisferio-<clave>.html`, clave sin acentos: `mex`), con sus municipios.
  **El portal va por tarjetas** (decisión del autor, 04-11-2026): arriba solo el mapa de sus
  municipios y sus municipios uno por uno; cada tema vive en su página,
  `planisferio-<clave>-<tema>.html` (`TEMAS` y `subpagina()` de `planisferio.py`, con su copia en
  `planisferio.js`). **Un tema nuevo del portal necesita su renglón en `TEMAS`**, o la generación se
  detiene; una liga a un tema apunta a su página, nunca a `#tema` del portal.
- **La página del mapa va por pestañas y cajones** (decisión del autor, 03-11-2026:
  «hay mucho contenido de narración»). Las dimensiones son una tira de pestañas;
  lo que cada una pinta («📏 Cómo leer esta dimensión») y sus puntos ciegos («👁️ Lo
  que este mapa no dice») abren en la ventana lateral (`button[data-cajon]` de
  `apartados.js`), y en la página solo queda una línea. **Una dimensión nueva que se
  pinte necesita su texto en `leer` de `pagina_mapa()`**, o la generación se detiene.
  Cada contador trae «Ver su desglose» y abajo va «La cuenta completa», que es
  `numeros_tres()` de la Enciclopedia (la misma función, nunca una copia). Junto a
  ella van «💰 Cuánto dinero es» (`presupuesto_modulos.cuanto()`) y «🧾 Los 16
  orígenes del ingreso» (`numeros_renglones(..., lleno=True)`: ya contabilizados,
  porque en el Planisferio no corre `numeros.js`).
  **El mapa es lo principal** (rediseño del autor, 03-11-2026): la página es una sola
  sección, sin «En esta página»; tras la entrada vienen las dimensiones y su mapa.
  Los contadores, «Cuánto dinero es» y «Los 16 orígenes» fueron integrados debajo del
  mapa en la dimensión financiera hasta el 16-11-2026; **desde ese día viven en su página**,
  `planisferio-dinero.html` (`DINERO` de `planisferio.py`; pedido del autor: «que quede como una
  tarjeta… que nos dirija a una nueva página»), y en el Planisferio queda su tarjeta (`.pl-dinero`),
  arriba de «Juega con el mapa». **Lo financiero nuevo va a esa página, no bajo el mapa.** Las 32
  entidades abren en la ventana lateral con el botón «📍 Las 32 entidades».
  **El mapa es el protagonista** (reestructura del autor, 04-11-2026: «lo que le llama al
  usuario a jugar con él»): encabezado con la foto del paisaje y la persona en sombra
  (`planisferio-paisaje.webp`, en su sentido original, con su versión `-movil`), «cómo se juega» en
  tres pasos, las nueve dimensiones como mosaico de color (`--dim` de `planisferio.css`)
  y el mapa en su tablero (`#plTablero`), que toma el color, el nombre y la descripción de
  la dimensión; «Para leerla bien» (los cajones) va al pie del tablero y lo financiero en
  tres pestañas (`.pl-hoja-b`). **Una dimensión nueva necesita su color en `planisferio.css`**,
  o su mosaico sale azul. Se reordenó; no se quitó contenido.
- **El tablero ordena y recuerda** (11-11-2026): cada lente trae su orden (`rank()` de `planisferio.js`: las cinco
  cifras más altas y las cinco más bajas, y el lugar de la entidad en su ficha), **que nunca se dice como
  calificación** y se esconde si hay empate en el corte; la dirección guarda la vista (`?d=&l=&e=`); hay buscador de
  estado, y el pie lleva a Servicios (`#plPuente`: una franja de venta con su botón, y el servicio también en la ficha
  de la entidad elegida, `.pl-ficha-serv`; **nunca un monto**). El encabezado es bajo para que el mapa suba. Nada de eso agrega cifras.
- **La ficha va esquematizada y las lentes, por tema** (reestructura del autor, 16-11-2026: «muestra mucha información
  que no es tan fácil de comprender»). Al tocar una entidad, la ficha abre con la cifra de la lente y su lugar entre las 32
  (`esquema()` y `tira()` de `planisferio.js`), sigue con cada tema en un acordeón (abre solo el de la lente) y cierra con sus
  puertas; **una fila que es lente (`dt[data-l]`) se toca y el mapa cambia a ella**. Las dimensiones con muchas lentes las
  ordenan por tema (`TEMAS_LENTES` de `planisferio.py`): **una lente nueva de esas dimensiones necesita ahí su tema**, o la
  generación se detiene. La advertencia general de una dimensión lleva `pl-ficha-gen` para quedar siempre a la vista. Nada de eso agrega cifras.
- **El Planisferio es la matriz de los mapas** (pedido del autor, 04-11-2026: «las cuestiones que
  tienen que ver con los mapas quedan vinculadas con el planisferio… va a ser nuestra matriz, que se
  vincula y se alimenta al mismo tiempo con la información de la Enciclopedia»). Cada lente del mapa de
  la Enciclopedia (`numeros-mapa-del-gasto-federalizado.html`) que ya se pinta en el Planisferio dice en
  `PLANISFERIO` de `territorio_modulos.py` en qué dimensión y lente vive allá; ese mapa lleva ahí con
  «Ábrelo en el Planisferio» (y cada ficha, a su portal), y `matriz()` de `planisferio.py` detiene la
  generación si una apunta a una dimensión o lente que no existe. **En el chat, los mapas que viven en el
  Planisferio salen en un solo renglón** («Ver en el Planisferio», con las otras dimensiones al lado:
  `lineaPl()` de `asistente.js`, con el `pl` que escribe `asistente_recursos.py`), nunca como tarjetas
  sueltas que repiten el mismo mapa, y «el mapa de…» se abre allá. **Una lente nueva del mapa de la
  Enciclopedia con par en el Planisferio necesita su renglón en `PLANISFERIO`.**
  «No cuadra» y «Obras con alerta ambiental» viven además en el Planisferio como lentes `cua`
  (financiera) y `obr` (ambiental), con la misma cuenta y el mismo texto (`cuadre_obras()`,
  `QUE_CUADRE`, `QUE_OBRAS` de `territorio_modulos.py`), y el mapa ambiental de megaobras tiene su
  par en `OTROS_MAPAS`. El chat reconoce por su archivo y su `?l=` cualquier tarjeta que lleve a un
  mapa con par (`conPl()`), aunque la haya armado otra respuesta.
  La página de presupuestos de cada portal trae «No cuadra» como cuarto piso, con la misma cuenta.
  La administración pública va en **gris pizarra** (`#4a5a6a`, elegido por el autor el 04-11-2026).
- **No trae datos propios:** ordena en el territorio lo que la Enciclopedia
  ya cotejó (`AUDIT_DB`, `municipios-efipem.js`). Una cifra nueva entra
  primero a su módulo de la Enciclopedia y de ahí la lee el Planisferio.
- **Por entregas.** Primera (02-11-2026): la dimensión financiera, los tres
  presupuestos de cada entidad (lo que baja de la Federación, lo que cobra el
  estado, lo que ingresan sus municipios) y los contadores de la Enciclopedia
  (ritmo por segundo = cifra anual ÷ 31,536,000 s, `derivado`). Las demás
  dimensiones salen «Próximamente» y llevan a donde ya viven; un enlace roto
  detiene la generación.
- **El mapa de los municipios de las 32 entidades** (03-11-2026: Jalisco
  primero y, el mismo día, las otras 31; 2,478 municipios y alcaldías). Sus
  límites salen del **Marco Geoestadístico 2024 del INEGI**: `herramientas/integrar_mg_municipios.py <ent>_<nombre>.zip` (se
  corre a mano con `pyshp`) escribe `docs/geo/mg2024-mun-<cve>.json`, con la
  huella SHA-256 del archivo de origen, y `planisferio.py` lo pinta en el
  portal (`#mapa-municipios`) si existe. **Si sus claves no coinciden con las
  del padrón municipal, la generación se detiene** (salvo las claves 990 y
  más, «No especificado», que no son territorio). La simplificación baja de
  400 m a 80 m en las entidades chicas. Las alcaldías de la Ciudad de México
  van en gris, porque no rinden cuenta municipal. La página repite el aviso
  del INEGI: esos límites son geoestadísticos, no la fuente oficial de la
  división político-administrativa. El chat lleva ahí con
  `planisferio.html?e=JAL&m=1` (renglón `mapa-mun` de `RECURSOS`).
- **La deuda, segunda dimensión pintada** (03-11-2026). Cada dimensión de
  `DIMENSIONES` dice si se pinta, y sus lentes viven en `LENTES` con su
  `dim` y su formato. La deuda lee del Sistema de Alertas (`deuda`,
  `deudaIld`, `deudaSd`, `deudaOcp`, `ildMdp` de `DB.estados`, que escribe
  `integrar_expedientes.py`); **el mapa colorea por cifra, no por semáforo**,
  porque el semáforo junta en verde a estados muy distintos, y lo dice. Lo
  que no se mide por ley va en gris como «no se mide», no como pendiente. Se
  abre con `planisferio.html?d=deuda` y cada portal la trae en `#deuda`.
  **La de los municipios** (03-11-2026) sale de su propia cuenta al INEGI
  (`municipios-deuda.js`, que escribe `herramientas/anclar_deuda_municipios.py`):
  **lo que pagaron y pidieron prestado en el año, nunca lo que deben** (el saldo es
  del Sistema de Alertas y sigue pendiente), los ADEFAS no se dicen como crédito y
  el capítulo «Financiamiento» del INEGI no se dice como deuda nueva: casi todo es
  «Déficit», su renglón de cuadre.
  **A quién le debe** (17-11-2026, pedido del autor: «las deudas»): el Registro Público Único de Hacienda, crédito por
  crédito (`herramientas/anclar_rpu.py <registro_deuda.xlsx>` → `assets/auditor/data/deuda-rpu.js`, con huella; el servidor pide el
  intermedio YR1 en `--cacert`). Va en la página de deuda de cada portal (cuarto piso) y en el chat (`deudaRpu()` de `asistente.js`:
  «¿a quién le debe Nuevo León?», «¿cuánto le deben a Banobras?»). **Cada crédito es oficial y las sumas, derivado; su saldo (corte
  trimestral) no se suma ni se compara con el del Sistema de Alertas; en una emisión bursátil el acreedor anotado es el fiduciario, una APP
  no es préstamo de banco y «refinanciamiento sin autorización» no quiere decir ilegal (LDF, art. 23).** Un acreedor que no sea
  institución ni empresa detiene el script (§2 bis).
- **La inversión, tercera dimensión pintada** (03-11-2026). Lee `invPub`,
  `invInfra` y `egr2024` de `DB.estados` (los escribe
  `herramientas/anclar_egresos_entidades.py` desde la estadística estatal del
  INEGI, con su tabla dentro del script y `--csv` para cotejarla contra el
  archivo) y lo que dejó la ASF. **La obra directa y lo que pasa a los
  organismos de obra nunca se suman**: con eso también se paga nómina. Se
  abre con `planisferio.html?d=inversion` y cada portal la trae en
  `#inversion`; en la Enciclopedia son las lentes `inv` e `invt` del mapa del
  gasto federalizado. **La de cada municipio vive en su propio archivo**
  (`municipios-inversion.js`, que escribe
  `herramientas/anclar_inversion_municipios.py <zip municipal del INEGI>`),
  nunca como columna nueva del padrón, que se lee por posición; si no trae a
  los mismos municipios con cuenta que el padrón, la generación se detiene.
  El «egreso total» del INEGI incluye lo que quedó en caja: se dice «de cada
  $100 de su egreso», no «de lo que gastó».
- **La legislativa, cuarta dimensión pintada** (03-11-2026). Los 32 congresos
  locales: lo que gastó cada uno en 2024 (CNPLE 2025), cuántos lo integran, el
  gasto por curul y el gasto frente al egreso del estado. Todo sale de
  `congresos_estados()` de `asistente_legislativo.py`, que leen el Planisferio,
  la Enciclopedia y el chat. **El tope del 0.70 % (art. 116, fr. II) se dice como
  referencia, nunca como incumplimiento** mientras se compare gasto de 2024 contra
  el egreso del INEGI: la prueba es el presupuesto aprobado del congreso contra el
  presupuesto de egresos del estado. El gasto por curul no es lo que gana nadie.
  Se abre con `planisferio.html?d=legislativa` y cada portal la trae en
  `#legislativa`; en el chat, `congLocal()` va antes que las Cámaras federales.
- **La judicial, quinta dimensión pintada** (03-11-2026). Los 32 poderes judiciales
  de los estados: lo que ejerció cada uno en 2024 junto a lo que le entró y lo que
  concluyó en primera instancia, el dinero por asunto concluido, las causas penales
  pendientes y sus personas juzgadoras (CNIJF-E 2025). Todo sale de
  `judiciales_estados()` de `gestion_judicial.py`, que leen el Planisferio y el chat.
  **«Concluyó de cada 100» no es el rezago y el dinero por asunto no es lo que cuesta
  un juicio**: se dice junto a la cifra. Se abre con `planisferio.html?d=judicial` y
  cada portal la trae en `#judicial`; en el chat, `judLocal()` va antes que la ficha
  del estado.
- **La ambiental, sexta dimensión pintada** (03-11-2026). Empieza por los recursos
  no renovables: las siete refinerías de PEMEX, el crudo que procesa cada una
  (Segundo Informe) y el valor que ganó o perdió en los libros de PEMEX. Todo sale
  de `herramientas/recursos_naturales.py`, que es además la metodología del
  capítulo 6 del libro del autor (`docs/libro/derecho-economico/`): **el libro es
  guía de temas, no fuente**, y cada regla se coteja contra la ley vigente, porque
  describe el marco de 1993-1994. **Una entidad sin refinería va en gris como «sin
  refinería», nunca como «sin problema»**, y el deterioro se dice como estimación
  contable, no como dinero que salió de la caja. Se abre con
  `planisferio.html?d=ambiental` y cada portal la trae en `#ambiental`; en el chat,
  los temas `rn_*` van en `mapaResp()`, antes que las megaobras. **Las concesiones
  mineras** (03-11-2026) salen del cuadro por entidad de la Dirección General de Minas
  (`MINAS`, con su total: si no cuadra, se detiene) y **una concesión no se dice como mina
  trabajando ni como irregularidad**; la capacidad de cada refinería, del Anuario
  Estadístico de PEMEX. `&l=` abre el mapa en una lente.
  **El agua del subsuelo** (03-11-2026) sale del Acuerdo de disponibilidad de los 653
  acuíferos de la CONAGUA (DOF 09-11-2023), copiado a un CSV con huella: `acuiferos()` recalcula
  las sumas de cada entidad y se detiene si no cuadran. **La disponibilidad se dice como el agua
  que aún se puede concesionar, nunca como el agua que queda, y «sin disponibilidad» no se dice
  «sobreexplotado»**: son dos mediciones distintas de la CONAGUA.
  **Los incendios forestales** (03-11-2026) salen del cierre estadístico anual de la CONAFOR
  (`INC25`, `INC24`, con huella; si las filas no suman el cierre, se detiene). **La superficie afectada
  no se dice como bosque perdido**: casi toda es pasto y matorral. **La superficie forestal** (03-11-2026) sale del
  «Estado que guarda el sector forestal en México 2023» de la CONAFOR (`SF`, con huella; si una fila o una columna
  no cuadran, se detiene): **«forestal» no se dice como «bosque»** (incluye el matorral), y lo que el fuego tocó
  frente a ella es una proporción con años distintos, nunca la parte que se perdió.
  **La pesca y la acuacultura** (03-11-2026) salen de las series del Anuario Estadístico de Acuacultura y Pesca de la
  CONAPESCA (`PESCA`, con huella; si una fila o una columna no cuadran, se detiene): **lo registrado se dice como lo declarado
  en los avisos de arribo y de cosecha, nunca como todo lo pescado ni como salud de la especie**, y una entidad sin registro va
  en gris como «no registró», no como «sin pesca». Si el Anuario se contradice entre cuadros, se dice y se toman sus series.
- **La salud pública, séptima dimensión pintada** (03-11-2026, pedido del autor: «sería
  IMSS e ISSSTE»). Del **IMSS**, su Memoria Estadística 2025 por OOAD; del **ISSSTE**, el
  registro «Recursos en Salud Sectorial» de la DGIS (Secretaría de Salud), porque su anuario
  no responde. `herramientas/anclar_salud_estados.py <Excel de la Memoria> <ZIP de la DGIS>`
  escribe `docs/salud/imss-issste-estados-2025.json` con las huellas; si las OOAD no suman el
  total de su cuadro o la DGIS no trae los establecimientos de su nota de cierre, se detiene.
  `salud_estados()` de `gestion_salud.py` lo leen el Planisferio, la Enciclopedia (tema
  `estados`) y el chat (`salEdo()`, antes que las columnas). **Las dos fuentes no se mezclan**
  (desde 2025 el IMSS de la DGIS incluye el antiguo IMSS-Bienestar programa), **los hospitales
  de alta especialidad se cuentan donde están** y lo que el ISSSTE no publica por estado
  (derechohabientes, consultas, cirugías) sigue con su ficha. Se abre con
  `planisferio.html?d=salud` y cada portal la trae en `#salud`.
- **La administración pública, octava dimensión pintada** (03-11-2026, pedido del autor: «qué funciones tiene… sus auditorías… en los tres niveles»). El gobierno que ejecuta: la federal, las 32 estatales y las municipales. Todo sale de `herramientas/administracion_publica.py`, con los censos de gobierno del INEGI (CNGF-E 2025 y CNGMD 2025, con huella; si una tabla no suma el total que el reporte dice en su texto, se detiene) y la Matriz de la ASF que ya está en la base. Lo leen la Enciclopedia (Datos › Administración pública), el Planisferio (`?d=administracion`, `#administracion` en cada portal) y el chat (`D.apu`, `apuEdo()` antes que las columnas). **Lo del censo se dice como lo que cada gobierno reportó, nunca como auditoría**, y el personal de dos estados no se compara sin decir que el censo no dice qué organismos incluyó cada uno; **la adjudicación directa cuenta contratos, no pesos, y no se dice como irregularidad**; y lo que dejó la ASF es solo del dinero federal.
- **La social, novena dimensión pintada** (04-11-2026). La pobreza de cada estado, de las
  infografías del INEGI, Pobreza multidimensional 2024 (`anclar_pobreza_estados.py` →
  `docs/social/pobreza-entidades-2024.json`, con huellas; si moderada + extrema no da la pobreza
  publicada o los 32 no suman el país, se detiene), y las aportaciones 2026 por persona en pobreza.
  Todo sale de `herramientas/dimension_social.py`, que leen el Planisferio (`?d=social`, `#social`) y
  el chat (`socEdo()`). **La pobreza no se dice como calificación de un gobierno, y las aportaciones
  por persona en pobreza no son lo que le llega a cada persona.**
- **La penal, décima dimensión pintada** (07-11-2026, pedido del autor: «una dimensión de penal»).
  La ENVIPE 2026 del INEGI por entidad (datos de 2025): la tasa de fraude por cada 100 mil habitantes
  y la cifra oculta, del texto de cada ficha estatal (`anclar_envipe_estados.py` →
  `docs/seguridad/envipe-2026-entidades.json`, con huellas; se corre a mano con `pdftotext`). Todo sale
  de `herramientas/dimension_penal.py` (`?d=penal`, `#penal` y su página en cada portal). **Más fraude
  registrado no se dice como peor gobierno** (lo cometen particulares y es una encuesta en los hogares),
  y **la cifra oculta no se dice como la eficacia de la fiscalía**. Las cinco entidades cuya ficha da
  la tasa de fraude solo en gráfica (Chiapas, Guerrero, Estado de México, Oaxaca y Puebla) **nunca se leen
  a ojo**: desde el 07-11-2026 su tasa sale del tabulado básico del INEGI, cuadro 1.13 (con su huella), y el
  script se detiene si el cuadro no da lo mismo que las otras 27 fichas y que el país (8,290). Cada entidad
  dice de dónde salió su tasa (`fraude_de`); si una ENVIPE nueva deja alguna sin ella, vuelve a gris con
  su pendiente (`penal-fraude-graficas`). **Las carpetas por fraude del SESNSP** (07-11-2026, pedido del autor)
  salen de sus datos abiertos estatales (`anclar_sesnsp_fraude.py <ZIP>` → `docs/seguridad/sesnsp-fraude-estatal.json`,
  con huella; el ZIP se baja de su SharePoint, `sspcgob-my.sharepoint.com`), y van como lentes `pnN` (oficial) y
  `pnC` (por cada 100 mil, derivado, con la población del CONAPO a mitad de 2026) y en «El fraude en números».
  **Una carpeta no se dice como una víctima ni como un fraude, más carpetas no se dice como más fraude, y las
  carpetas no se restan de la ENVIPE**: la proporción del país (carpetas por cada 100 fraudes estimados, cuadro
  1.20 del tabulado) es derivada y no es «la cifra oculta del fraude». Cuando el SESNSP publique otro corte, se
  vuelve a correr el script con el ZIP nuevo.
- **Cada dimensión va vinculada al Contexto dimensional y al estado de resultados** (04-11-2026,
  pedido del autor). `CONTEXTO` de `dimension_social.py` dice qué página del Contexto dimensional mira
  cada dimensión a nivel federal: **una dimensión nueva necesita ahí su renglón**, o la generación se
  detiene. El mapa, cada portal y cada ficha llevan además el estado de resultados del Gobierno y el
  estado de cuenta del estado; el Contexto dimensional y el estado de resultados llevan de vuelta.
- **Las leyes del dinero en los tres niveles** (03-11-2026,
  `herramientas/leyes_niveles.py`, página `marco-legal-tres-niveles.html`):
  cuál ley rige, quién la aprueba y dónde se publica, federal, estatal y
  municipal. **No copia leyes ni pone una liga que no respondió al cotejo**:
  una dirección sin verificar va con su nombre y «liga por cotejar». Las
  fechas federales salen del índice de la Cámara de Diputados; si una ley se
  reforma, se cambia su renglón en `FEDERALES`. Cada portal del Planisferio
  la lee en `#leyes` y en «Las reglas de su deuda». El chat la abre con
  `leyNivel()` de `asistente.js` antes que la ficha del estado.
- **Vive en el Auditor:** «Ver en el Planisferio» es un renglón de
  `RECURSOS` (`asistente_recursos.py`, con `?e=` para abrir el mapa con la
  entidad elegida) y «planisferio» cuenta como pedir un mapa (`TIPOS_REC` de
  `asistente.js`). Una dimensión nueva que se pinte necesita su pregunta en
  `preguntas_auditor.json`.

### 0 quinquies. Todo pasa por el Auditor

**Dos chats, reflejo uno del otro** (decisión del autor, 21-11-2026: «crear dos chats… ambos se
alimentan de lo mismo… aquí únicamente va a ser todo el modo Inspector»). El chat del Auditor
(`herramienta-inspector-pregunta.html`) trabaja en **tres modos**: Periodista, Ciudadano y
Ambientalista. **El modo Inspector, con todas sus aplicaciones, vive en Servicios**: `servicios-inspector.html`
(`asistente.pagina(..., solo='inspector')`, `data-solo` en la página). Los dos cargan el mismo
`asistente.js` y la misma base: **el modo cambia la forma, nunca los datos**. El de Servicios **contesta en
corto** (`corto()` y `accionesSv()`), y la respuesta completa abre en su propia página,
`servicios-respuesta.html?q=…` (`armaRespuesta()`): la respuesta, la revisión del Inspector, su aplicación,
el expediente, el servicio que toca, las demás partes de la plataforma (Planisferio, Enciclopedia…) y, al
final, **«Generar dictamen»**. Como el dictamen, esa página vuelve a contestar con la base: nada viaja en el
enlace. Toda liga de Servicios a un chat va al Inspector de Servicios (`chat_liga()`, `por_auditor(...,
origen='Servicios')`), y una liga vieja al Auditor con `?modo=inspector` se muda sola allá. Entre los dos
chats, la remisión de modo es una liga al otro, con la misma pregunta (`remiteHtml()`). Cada chat guarda su
plática aparte (`av-chat` y `av-chat-sv`).

**Decisión del autor, 19-11-2026, y es el pilar de la plataforma:** «el chat se alimenta y
vincula de todas las pestañas y tarjetas y subtarjetas dentro de ellas, pero entre pestañas no se
vinculan: todo es a través del Auditor», y «las aplicaciones del chat se convierten en servicios».
La Enciclopedia es el respaldo de la base de datos, ordenada en tarjetas; **la puerta es el chat**:
respuesta rápida, «Generar dictamen», «Saber más» (la página a fondo) y el servicio que toca.

- **La plataforma es una estrella.** El Auditor (`herramienta-inspector-pregunta.html` y el
  dictamen) es el centro; Planisferio, Comunidad (con la Enciclopedia), Noticiero y Servicios son
  puntas. Dentro de una pestaña las páginas se ligan entre sí; **una liga a otra pestaña pasa por el
  chat**: `herramienta-inspector-pregunta.html?q=<pregunta>&modo=<modo>&abre=<página>`
  (`servicios_fichas.por_auditor()`). El chat contesta con esa página o abre la aplicación en su
  marco (`abre()` de `asistente.js`), y el dictamen lleva el mismo `&abre=`.
- **Las aplicaciones del chat son servicios, y lo que revisan ya va en la respuesta** (el autor,
  22-11-2026: «en el mismo dictamen le resolvemos todo lo que tiene nuestra base de datos… ya ni
  siquiera tiene que cotizar»). Si una respuesta lleva a una página que un servicio aprovecha (su
  `hace` en `FICHAS` de `servicios_fichas.py`), abajo sale «✅ Ya revisamos esto por ti» (`resueltoHtml()`
  de `asistente.js`, que lee `srv` de la base: `mapa_chat()`), y el encargo queda solo para lo que la base
  no hace sola, con la solicitud ya llena (`pideLiga()`: servicio, tema y pregunta). **Con un RFC de
  persona moral, una empresa o un grupo, la respuesta completa y el dictamen traen «La revisión completa»**
  (`integral()`): las listas del SAT, Sancionados, la OFAC y la ONU, sus contratos de ComprasMX y su grupo,
  aunque se haya preguntado solo una parte; son las mismas respuestas del chat, y en el dictamen sus cifras
  y fuentes **entran a la huella**. **Nunca un monto de servicio, y nunca una persona física.**
- **Las cuatro pestañas ya están mudadas** (19-11-2026: Servicios, y el mismo día, a pedido del
  autor, «todas las demás pestañas al chat»). `pagina()` de `apartados.py` pasa cada página de
  Planisferio, Comunidad, Noticiero y Servicios por `por_auditor_html()`: una liga nueva a otra
  pestaña se muda sola, con el modo del servicio o el de la página a la que va (`modos.py`). Las
  ligas que arma el navegador (la ficha del Planisferio) las muda al tocarlas `volver-auditor.js`,
  con la misma regla. La pestaña de cada página sale de su nombre (`pestana_de()`); si una página
  marca otra, va en `EXCEPCIONES` (y en `EXC` de `volver-auditor.js`) o la revisión se detiene.
- **Ni una liga directa entre pestañas.** `herramientas/vinculos_auditor.py` (corre en `revision.py`)
  las cuenta, sin la cabecera, el menú, las migas, el cajón «Cuéntanos lo que viste» ni el pie: **si
  aparece una, la revisión se detiene**. La portada (`index.html`) no es pestaña y liga a todas.
- **Cada liga `abre=` del sitio se prueba** en `prueba_auditor.py` (587 al 19-11-2026): la página debe
  existir y el chat debe abrirla. Una página sin ficha propia (un mapa, un tablero) se abre igual, sin cifras.
- **La Enciclopedia es el espejo de la base de datos** (el autor, 19-11-2026): de ahí toma el
  Auditor y lo desarrolla. **Lo que el Planisferio enseña abre en páginas del propio Planisferio**
  («que se abran en su propia página automatizada… no dentro de la enciclopedia»): sus portales y
  sus temas (`TEMAS` de `planisferio.py`) y, para lo que antes mandaba a la Enciclopedia (las fuentes,
  el estado de cuenta y de resultados de cada estado, el Contexto dimensional, las leyes en sus tres
  niveles, los Datos de cada dimensión), **sus páginas propias** `planisferio-ficha-<página>.html`
  (`herramientas/planisferio_espejo.py`). `a_espejo()` cambia cada liga del Planisferio a la Comunidad
  por la de su página propia y `generar()` la escribe al final, desde la página ya generada de la
  Enciclopedia: **la misma página, nunca una copia a mano ni una cifra distinta**, marcada Planisferio,
  con sus migas, el aviso «Lo ves desde el Planisferio» y su canónica en la original (`sitemap.py` no la
  lista y el chat no la indexa: contesta con la original). Dentro, a otra página propia va directo y a
  otra pestaña, por el Auditor. **Nadie la edita**: una nueva sale sola cuando el Planisferio liga a otra
  página de la Enciclopedia, y la que ya no se pide se borra. `planisferio.js` liga a ellas por su nombre
  (si liga a una que ninguna página pide, la generación se detiene), y `volver-auditor.js` deja en su
  página propia la liga que una aplicación reflejada arma a sí misma.
- **El índice general cuelga del Auditor** (el autor, 19-11-2026: «se va a integrar nuestro índice
  general… y todo esto queda vinculado con nuestro auditor»). `indice.html` marca la pestaña Auditor
  (con el Registro de pendientes y la base al día, que cuelgan de él: `EXCEPCIONES`), lleva a todas
  las pestañas, Planisferio y Servicios incluidos, y el chat lo abre con «el índice», «¿qué tiene la
  plataforma?» o «mapa del sitio» (`INDICE_RE` de `asistente.js`) y con su botón «🗂️ Índice general».
- **La página automatizada de tus respuestas** (el autor, 19-11-2026: «la página… automatizada de las respuestas o de los servicios a los
  problemas, peticiones, solicitudes de lo que hayan hecho los usuarios»). `mis-respuestas.html` (pestaña Auditor; `herramientas/mis_respuestas.py`
  y `mis-respuestas.js`). El chat anota cada pregunta que contesta **solo en el navegador** (`av-caso`, hasta 60; `caso()` de `asistente.js`):
  la pregunta, la fecha, el modo, la respuesta en corto (el texto que ya dio), «Saber más», el enlace de su dictamen y los servicios de `srv`
  para su página; lo que no supo contestar queda como solicitud y se pide como investigación (servicio `expediente`). La página lo junta con
  los dictámenes (`av-dics`) y Mi Auditavisión (`av-mia`), ordena los servicios de más a menos preguntas que los piden y llena la cotización
  con esas preguntas (`?servicio=&tema=&pregunta=`). **Nada sale del navegador, nunca un monto, no es un documento oficial**; se imprime, se
  descarga en texto y se borra ahí. El chat la abre con «mis respuestas» o «mi caso» (`MIS_RE`) y con su botón «📋 Tus respuestas». **Un
  dato nuevo que el chat guarde en el navegador necesita su renglón en `_AV_NAVEGADOR` del aviso de privacidad.**

### 0 bis. Una sola plataforma: la Enciclopedia antigua se retiró

**Decisión del autor, 24-10-2026.** Antes había dos «Enciclopedias». La
**plataforma antigua** (`enciclopedia.html`, de 9 pestañas, con su propio
`assets/css`, `assets/js` y `assets/data`) se fusionó con Auditavisión: lo que
servía ya vivía aquí con su fuente, y lo demás se depuró. Se retiró del sitio
y del repositorio; su dirección redirige a la pestaña, y el código queda en el
historial (último commit que la trae: `490233d`) por si un día se retoma.

| Ahora | Archivo |
|---|---|
| **La Enciclopedia** = la pestaña de Auditavisión (Números, Datos y Aprende) | `enciclopedia-auditavision.html` y las páginas de sus tres tarjetas |
| `enciclopedia.html` | Solo redirige a la pestaña (`REDIRECCIONES` de `apartados.py`) |

Si se rescata algo de la antigua, se trata como dato nuevo: se coteja contra
el documento oficial (§2) y entra a su página de Auditavisión y al bot
(§5 ter). La antigua nunca es fuente de cifras.

### 0 ter. Los pilares: el periodista virtual del gasto público

**Decisión del autor, 26-10-2026.** Auditavisión es el periodista virtual que
sigue el gasto público. Sus doce pilares están dichos al lector en
`pilares.html` (`PILARES_LISTA` de `herramientas/apartados.py`) y valen para
todo cambio: que la verdad sea incómoda no la vuelve falsa; evidencia con
folio; contrapeso, no propaganda (las mismas reglas para todos los gobiernos);
se reconoce a quienes hacen periodismo, pero su nota es punto de partida, no
fuente de cifras; lo que falta se señala con nombre; que se entienda de un
vistazo; el ambiente también es gasto público; y el caso no se olvida (cada
columna de Verificamos trae «Lo que sigue» y se puede seguir: al cambiar su
`actualizado`, quien la sigue ve el aviso). Un pilar nuevo se agrega ahí.

**La base de datos es el pilar de transparencia** (decisión del autor,
03-11-2026: «la construcción de nuestra base de datos debe convertirse en ese
pilar de transparencia», tras «no podemos contar o confiar con la plataforma de
transparencia»). Es el duodécimo pilar, y la página lo explica en seis pasos
(`BASE_PASOS` de `apartados.py`, sección `#base` de `pilares.html`). **Ninguna
cifra se apoya en una respuesta a una solicitud de acceso** (la Plataforma
Nacional de Transparencia, sin órgano autónomo desde la Ley General de
Transparencia, DOF 20-03-2025): solo entra lo que la dependencia publica para
todos, con la huella SHA-256 del archivo, su cuadre (si no cuadra, se detiene),
su chip y su enlace. **Un pendiente no se resuelve proponiendo una solicitud**:
su enlace es el portal donde la dependencia debía publicarlo, y si no lo
publica, se queda con su nombre. Lo que diga una solicitud ajena, si alguna vez
llega, es punto de partida, como una nota de prensa.

**Competimos siendo el mejor auditor, no el más rápido** (decisión del autor,
01-11-2026: «podríamos ser considerados competidores de todos estos medios
informativos, pero debemos ser los mejores, y eso consiste en armar una buena
base de datos»). Es el segundo pilar. Los medios dan la noticia; Auditavisión
la coteja, la cruza con su base y no la olvida. Lo «privilegiado» es lo que ya
es público pero está enterrado en documentos que casi nadie cruza: **nunca una
filtración, un dato personal ni un rumor**. Se construye en entregas:

1. **El detector de puntos ciegos** (hecho, 01-11-2026): lo que las notas
   suelen esconder, en reglas (`REGLAS` de `herramientas/puntos_ciegos.py`)
   que el verificador de notas y el chat («¿es cierto que…?») aplican solos
   (`ciegos()` de `verificador.js`). Se explican al lector en
   `noticias-verifica.html#puntos-ciegos`. **Un punto ciego no califica la
   nota ni entra al veredicto**: es una pregunta que conviene hacer, y se
   encuentra por las palabras. Cada regla nace de una nota «Al momento» y la
   cita en `de`; **cuando una nota nueva enseñe un punto ciego nuevo, se
   agrega su regla y su caso en `prueba_puntos_ciegos.py`** (corre en
   `revision.py`). Las expresiones valen igual en Python y en JavaScript: sin
   lookbehind ni grupos con nombre.
2. **La memoria de promesas** (hecha, 01-11-2026): cada cifra que anuncia un
   gobierno, con su fecha, seguida por promesa → Presupuesto → Cuenta Pública
   → ASF, para ver cuándo cambia o nunca llega (`PROMESAS` de
   `herramientas/promesas.py`; se lee en `noticias-seguimiento.html#promesas` y
   el chat la contesta con `D.prom`). **Ninguna cifra se escribe ahí**: se lee
   del módulo que ya la coteja, y si cambia allá la generación se detiene. Una
   promesa es «oficial» porque consta que se dijo, no porque se gastó; una
   etapa sin documento es «pendiente» con su ficha (`pendientes()`), y la que
   todavía no toca dice su fecha legal. **Una nota «Al momento» que anuncie
   una cifra de gasto agrega su promesa ahí**, con su pregunta de prueba.
3. **Abrir la red** (del autor): los portales de `docs/RED-PENDIENTE.md`.

---

## 1. Se trabaja en la rama, `main` es la versión entregada

**Todo el trabajo se hace en la rama `claude/funny-turing-imtm54`.**
**`main` es su espejo y se actualiza sola** (decisión del autor, 19-11-2026: «solo quiero
modificar uno y que se actualice [el otro]»): el flujo «Espejo de main»
(`.github/workflows/espejo-main.yml`) la adelanta a la rama en cada envío, al terminar cada flujo
programado, cada día y a mano, solo por avance directo. **Nunca se escribe directo en `main`**: si
alguien lo hace, el flujo se detiene sin pisar nada, y se arregla integrando `main` en la rama. Para
ver si están iguales: `git rev-list --count origin/main..origin/claude/funny-turing-imtm54` (0 = iguales).

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

**Nunca empujes a `main` a mano**: la iguala el flujo «Espejo de main».

**Hay una sola plataforma** (§0 bis). La Enciclopedia antigua
(`enciclopedia.html` con `assets/css`, `assets/js` y `assets/data`) se retiró
el 24-10-2026; `enciclopedia.html` solo redirige a la pestaña Enciclopedia.
Todo el código vive en `assets/auditor/`, y las fotografías en `assets/img/`.

Para saber si una copia está al día:

```bash
git fetch origin && git status
# "up to date with 'origin/claude/funny-turing-imtm54'" = esta copia es la buena
```

**Excepción: rediseño de legibilidad (`docs/ux/PLAN.md`).** Las fases con
cambio visible se trabajan en ramas cortas (`ux/fase-1a`, `ux/fase-1b`…).
Se rebasan cada día sobre `claude/funny-turing-imtm54`, se revisan en una
vista previa y se integran solo con visto bueno del autor. GitHub Pages
publica desde `claude/funny-turing-imtm54`: lo que llega ahí es público.

---

## 2. Regla editorial, por encima de cualquier otra

Esto es una plataforma de fiscalización del gasto público:
**un dato inventado la desacredita entera.**

- Toda cifra debe poder rastrearse a una fuente oficial: DOF, SHCP,
  Transparencia Presupuestaria, ASF, Banxico, INEGI, CONASAMI, INE, SCJN,
  Gaceta Parlamentaria.
- Si un dato no se puede verificar, **se etiqueta como pendiente**, con el
  chip `pendiente`. Nunca se estima, nunca se rellena, nunca se redondea a
  ojo de buen cubero La única aproximación permitida es el rango
  derivado de cotas oficiales (ver más abajo).
- Los estados de un dato son tres: `oficial` (tomado de su documento),
  `derivado` (calculado a partir de datos oficiales, con la operación dicha)
  y `pendiente`. La función `chipEstado(estado)` los pinta. El recuadro de
  `derivado` se lee **«auditada»** (decisión del autor, 09-11-2026,
  confirmada el 11-11-2026: ese día dijo «calculada» por unas horas y el
  autor pidió regresarla): la clave interna y la clase `.est-derivado` no
  cambian.
- Las estructuras derogadas se marcan con su vigencia en lugar de borrarse.
- **Un `pendiente` dice por qué y señala a quién** (decisión del autor,
  09-10-2026). No basta con «no hay documento oficial»: casi siempre falta
  porque la dependencia obligada no lo ha transparentado, y eso se dice con
  su nombre. Ejemplo: «Ni el SAT ni Hacienda han publicado cuánto se evade:
  falta de transparencia de esas dependencias». Solo se nombra a la
  dependencia que de verdad debía publicarlo. Si la falta es de la
  plataforma (el documento existe y aún no lo integramos) o el dato es
  histórico sin dependencia que responda, se dice así, sin culpar a nadie:
  atribuir una omisión que no se puede sostener también es un dato
  inventado.

- **Todo pendiente da la cara** (decisión del autor, 10-10-2026). Además de
  su chip y su porqué, lleva el **enlace oficial donde debería estar** el
  dato y queda en el **Registro de pendientes** (`pendientes.html`, lo
  genera `herramientas/pendientes.py`). Ahí se anota qué falta, por qué
  falta, a quién le toca publicarlo y en qué páginas aparece. Toda
  etiqueta «pendiente» de la plataforma lleva a ese registro al hacerle
  clic, y con `data-pend="<id>"` lleva directo a su ficha. Un registro de
  la base con estado `pendiente` necesita `motivo` y `url`. Si no los
  trae, `pendientes.py` detiene la generación, y `inventario.py` reporta
  como roto cualquier `data-pend` que no tenga ficha.

- **Cuando solo hay aproximación, se da un rango: mínimo, máximo y punto
  medio** (decisión del autor, 10-10-2026). Si la cifra exacta no está
  publicada pero sí se puede acotar, no se escribe «~$380» con chip
  `pendiente`: se escribe «entre X y Y; punto medio Z» con chip
  `derivado`. Condiciones, sin excepción:
  - **El mínimo y el máximo salen cada uno de un documento oficial** (o se
    calculan a partir de cifras oficiales), y cada cota lleva su fuente.
    Una cota que no se puede sostener no es cota: si falta una, el dato
    sigue `pendiente`.
  - **El punto medio es la media aritmética:** Z = (X + Y) ÷ 2. Se dice la
    operación, como todo `derivado`.
  - **Se dice de qué está hecho el rango**, por ejemplo «mínimo con el
    subsidio PEF 2024 ÷ pasajeros AFAC 2024; máximo con el subsidio PEF
    2025 ÷ pasajeros AFAC 2024».
  - **La cifra exacta sigue debiéndose:** el rango no la sustituye, así que
    su ficha del Registro de pendientes se queda, con la nota de que ya
    hay un rango derivado y de quién debe la cifra exacta.

Si te piden una cifra que no puedes sostener, dilo y déjala pendiente. Es la
respuesta correcta en este proyecto.

### 2 bis. Prensa, personas privadas y derecho de réplica

**Bloque 4 del plan v2, 27-10-2026.** Cotejado contra la Ley Reglamentaria del
artículo 6o. constitucional en materia del Derecho de Réplica (DOF 04-11-2015,
última reforma DOF 14-11-2025). Lo explica al lector `derecho-de-replica.html`
(`REPLICA` de `herramientas/apartados.py`), y es el undécimo pilar.

- **La nota de prensa es punto de partida, no fuente.** Se cita a la persona
  que la firma y a su medio, con enlace; cada afirmación se coteja contra el
  documento oficial (`docs/VERIFICAMOS.md`). No se copian notas enteras.
- **A las personas privadas no se les nombra**: familiares, apoderados,
  empleados, testigos. Solo servidores públicos, quienes buscan un cargo,
  quienes una autoridad ya hizo públicos en un documento oficial y las
  empresas que un documento oficial nombra. Las personas físicas con
  contratos no se publican.
- **Una acusación no es una condena** (Constitución, art. 20, B, fr. I): se
  dice junto a cada acusación.
- **La réplica se publica** en la misma columna, en su campo `replica`
  (`columnas.js`), íntegra y sin comentarios (art. 6), y se cambia su
  `actualizado` para que quien sigue el caso reciba el aviso. Plazos: 3 días
  hábiles para resolver y 3 para notificar (arts. 11 y 12); si se niega, por
  escrito y con una causa del art. 19. Si la réplica prueba un error nuestro,
  además va a la fe de erratas.
- **El responsable** que pide el art. 7 (nombre, domicilio, código postal,
  entidad, correo y teléfono, siempre a la vista) lo designó el autor el
  02-11-2026. Vive en `RESPONSABLE` de `herramientas/apartados.py`, que leen
  el aviso de privacidad y `derecho-de-replica.html`: si cambia, cambia ahí.

---

## 3. Cómo está construido

Sitio estático. **Sin framework, sin compilación, sin `npm install`.** Se abre
y funciona.

```
index.html                       Estructura, 9 pestañas, contenido editorial
assets/auditor/css/auditavision.css      Diseño: temas claro y oscuro
assets/auditor/js/mexico-states-geo.js   Geometría de las 32 entidades
assets/auditor/js/audit-database.js      Datos fiscales           → window.AUDIT_DB
assets/auditor/js/municipios-efipem.js   Padrón municipal INEGI
assets/auditor/js/audit-engine.js        Motor y controlador      → window.AuditEngine
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
  Cuentas de CR sueltos que deben conservarse (copias de `assets/auditor/`):
  `index.html` 56, `audit-engine.js` 2, `audit-database.js` 2,
  `auditavision.css` 1.
  El `.gitattributes` fija `* -text` para que Git no los convierta al clonar
  ni al commitear, en Windows tampoco. **No lo quites.**
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
  python3 herramientas/sello.py --siguiente   # el que sigue al publicado
  ```

  Rechaza un sello igual o anterior al publicado (26-10-2026: un plan de otro
  agente propuso uno ya rebasado). Si falla, `git pull` y `--siguiente`.

  Cambia las referencias `?v=` y el sello visible al pie de `index.html` (solo ahí). Si no tocaste
  `assets/`, no lo subas.
- **Cada página lleva la política de seguridad de contenido (CSP)** de
  `herramientas/seguridad.py` (19-11-2026, LFPDPPP art. 18): la ponen los
  generadores y la portada a mano, y `revision.py` se detiene si una página no
  la trae igual. **Un servicio externo nuevo (API, CDN, antispam) necesita ahí su
  anfitrión**, o el navegador lo bloquea en silencio. **El panel de la
  administración pide dos factores**: `es_admin()` solo responde con la sesión
  aal2 (migración `20261119000001_doble_factor.sql`).
- La navegación usa `data-tab` en las pestañas y `data-sub` en las
  subpestañas; los paneles, `data-subpanel`.
- **Reglas de lectura** (condición del dueño: fácil de leer en celular):
  - Sin `font-size` en línea (`style="font-size:…"` ni en cadenas del
    motor). El tamaño se da solo con clases de la escala de DESIGN.md §4.1.
  - El texto corrido nunca baja de 16 px en celular.
  - Todo lo que se toca mide al menos 44 × 44 px.
  - Al lector se le habla de tú, también en los textos del motor.
  - **Los emojis se ven como íconos de trazo** (decisión del autor,
    20-10-2026, que reemplaza la del 12-10-2026). Los textos se siguen
    escribiendo con emojis; `assets/auditor/js/iconos.js`, que se carga en el
    `<head>` de todas las páginas, los cambia al pintar por íconos Lucide de
    un solo color. Un emoji nuevo necesita su renglón en
    `herramientas/iconos.py` (ícono y nombre en español), y luego se corre
    el script; si no, se queda como emoji. No compares textos de la página
    que lleven emoji (`textContent === '🔒 …'`): al pintarse ya no lo traen.

---

## 5. Criterios de terminado

Un cambio **no está hecho** hasta que las siete líneas se cumplen:

1. `node --check assets/auditor/js/audit-engine.js` pasa sin error.
2. La página levanta en `http://localhost:8000` y **la consola del navegador
   no arroja ni un error**.
3. La pestaña tocada renderiza, y las demás siguen renderizando: cambiar de
   pestaña y volver no debe romper nada.
4. Toda cifra nueva lleva su fuente y su chip de estado (§2).
5. Está commiteado y **empujado a `claude/funny-turing-imtm54`** (§1). Si
   tocaste `assets/`, con el sello subido (§4).
6. `python3 herramientas/guardia_legibilidad.py --fase N` pasa, con N la
   fase vigente de `docs/ux/PLAN.md`. Para corregir una cifra con urgencia:
   `GUARDIA_OMITIR="motivo"`, y el motivo se anota en el commit.
7. `python3 herramientas/prueba_auditor.py` pasa: las preguntas de prueba
   del Auditor (`herramientas/preguntas_auditor.json`) siguen llevando a
   donde deben. Un dato nuevo del bot lleva su pregunta ahí, y si un cambio
   mueve una respuesta a propósito, su renglón se corrige en el mismo commit.

El detector de puntos ciegos tiene su prueba (`prueba_puntos_ciegos.py`, sin
navegador), que `revision.py` corre junto con el inventario.

Las siete se corren de una vez con
`python3 herramientas/revision.py --base origin/claude/funny-turing-imtm54`,
y GitHub las corre solas en cada envío (`.github/workflows/revision.yml`). El
estado corto del proyecto vive en [ESTADO.md](ESTADO.md): se actualiza en el
mismo commit que cambia lo que dice.

Al terminar, di explícitamente qué quedó pendiente y por qué. La lista de
pendientes vive en CONTEXT.md y se mantiene al día: es parte del entregable.

---

## 5 bis. La portada ya no despliega nada: cada clic abre una página

**Decisión del autor, 09-10-2026.** La página principal (`index.html`) queda
como está. **Ningún contenido nuevo se desglosa debajo de ella**, ni en
cuadros que se abren encima: todo clic lleva a una página propia de la
plataforma, bien estructurada (como los apartados `*.html` y las páginas
`auditoria-*.html`). Lo que todavía se despliega en la portada se irá
mudando a su página; no se agregan desgloses nuevos.

- Las páginas se generan con Python desde `herramientas/` (no se editan a
  mano) y comparten cabecera, sello y estilos: `apartados.py` para los
  apartados, `auditorias.py` para Auditoría en imágenes y `expedientes.py`
  para los Expedientes de casos. `sello.py` las
  regenera.
- Si una página necesita abrir un módulo que sigue en la portada, enlaza a
  `index.html?ir=destino&ancla=...` (ver `IR_MODULOS` e `IR_DESTINOS` en el
  motor).
- Hecho así: Auditoría en imágenes (`auditoria-*.html`) y el radar
  hacendario, que dejó de ser menú de la portada y vive en
  `descarga-los-datos.html#radar` (menú «Datos»),
  y los Expedientes de casos por aclarar, que eran el bloque 3 del Modo
  Inspector y viven en `expedientes.html#exp-<id>`
  (`herramientas/expedientes.py` + `assets/auditor/js/expedientes.js`).
- Lo único que se agregó a la portada después (entrega 2 de la propuesta de
  Astra, 10-10-2026, a pedido del autor) son **enlaces**: las tres acciones
  bajo el carrusel. Sus datos los escribe `herramientas/auditorias.py`; no
  se editan a mano. El bloque «Por dónde empezar» se quitó el mismo día por
  decisión del autor («la plataforma queda intacta»): sus temas y su nota de
  verificación viven al pie de cada investigación, y sus accesos, en el
  índice general.
- El menú «Busca y verifica» se fusionó con el Modo Inspector (09-10-2026):
  es su parte B, y `busca-y-verifica.html` solo redirige ahí.
- **El menú tiene cuatro pestañas** (decisión del autor, 28-10-2026: «darle
  más protagonismo a las noticias relevantes… como una cuarta pestaña», que
  amplía la de tres del 23-10-2026, que a su vez reemplazó la de cinco del
  09-10-2026): **Auditor
  Virtual** (abre `herramienta-inspector-pregunta.html`, «Pregúntale al
  Auditor»; desde el 29-10-2026 su botón de la cabecera elige uno de los
  cuatro modos, §0, y las herramientas viven en la Enciclopedia, en Números
  › Herramientas del Auditor; `herramientas.html` redirige ahí), **Enciclopedia**
  (`enciclopedia-auditavision.html`, con tres tarjetas: Números, Datos y
  Aprende, que conservan sus páginas) y **Comunidad** (`participa.html`, la
  antigua Participa, con tres tarjetas desde el 24-10-2026: Ágora cívica,
  Garantías cívicas y Donaciones. `comunidad.html`, que antes se llamó
  «Comunidad» y luego «Participa», ya no es tarjeta: se fundió con el botón
  «Cuéntanos lo que viste» de la cabecera, su única puerta: ese botón abre
  el cajón con las cinco rutas (algo raro con el dinero público, un dato mal,
  un tema para investigar, compartir el Estado de Cuenta y fe de erratas); el Pase del Auditor Cívico se retiró y
  `pase-del-auditor.html` redirige a Donaciones) y **Noticias**
  (`noticias-relevantes.html`, que antes colgaba de Aprende; Aprende conserva
  su tarjeta hacia ahí). Ningún archivo cambió de nombre, para no romper
  enlaces. Las pestañas viven en `MENU` de `herramientas/apartados.py`, y
  la portada (`index.html`) tiene su copia a mano. Lo que cuelga de
  Números, Datos o Aprende muestra «Enciclopedia» en sus migas.
  **Ojo:** la página de la pestaña Enciclopedia es
  `enciclopedia-auditavision.html`; `enciclopedia.html` solo redirige ahí (§0 bis).
  «Números» es la antigua «Sigue el dinero»; su archivo sigue siendo
  `sigue-el-dinero.html`.
- **«Al momento»: las noticias del día, verificadas** (pedido del autor,
  28-10-2026: «notas más pequeñas… fechado con nuestros datos, verificado,
  nuestra salud financiera, estado de resultados… y el glosario»). Es la
  sección `Al momento` de `columnas.js` y la franja al inicio del diario.
  Cada nota la escribe `herramientas/integrar_al_momento.py` (no se edita a
  mano) con el molde de Verificamos (la nota de prensa es lo que se coteja,
  con su medio y su liga) y además `fecha`, `nota`, `ejemplo` (la cuenta con
  números redondos, siempre `derivado`), `datos` (lo que dice la plataforma:
  estado de resultados, salud financiera, herramientas), `glosario` (cada
  concepto con su ficha: si falta, se agrega al glosario en el mismo cambio)
  y `red`: las búsquedas armadas en noticias, YouTube, X, Facebook y el DOF,
  **rotuladas «sin verificar»; nunca se copia ni se resume lo que dice la
  red**. Las cifras que la plataforma ya tiene se leen de su módulo, no se
  copian. El chat la encuentra sola, y «noticias de hoy» lista las más nuevas.
  **Hemeroteca y buscadores** (pedido del autor, 31-10-2026): una nota puede
  traer `medios` (cómo lo contaron otros medios: medio, titular, fecha y liga,
  sin verificar, nunca el texto); se juntan en `noticias-verifica.html#hemeroteca`
  y el chat reconoce esas ligas. Cada nota tiene su página
  `noticias-al-momento-<id>.html`, escrita en el HTML con su NewsArticle, para
  que Google la encuentre (`paginas_al_momento()` de `herramientas/noticias.py`).
  Si la pregunta natural de una nota nombra un municipio o un estado («¿cuánto
  costó el Carnaval de Ensenada?»), la nota lleva `temas` (sus palabras propias)
  para que el chat la abra antes que la ficha del lugar (`temaColumna()`).
- **Noticias reúne todo lo de noticias** (pedido del autor, 28-10-2026: «que
  todo quede debidamente vinculado»). Además de «Al momento» y la Columna del
  Erario, `noticias-relevantes.html` trae dentro la aplicación **Contrasta una
  nota** (sección `#verifica`: es `insp_nota.construir()`, la misma de
  Herramientas y del chat, nunca una copia), **Propón una nota** (`#propon`,
  que abre la ruta «tema» del cajón) y **Réplica y postura** (`#replica`, que
  `columnas.js` llena con las columnas que traen `replica` o `postura`). La
  **postura** (`postura[{quien, fecha, texto, url}]`) es lo que la parte
  aludida dijo en su propio documento: se publica en sus palabras, con su liga,
  y no se califica. La página es la función `noticias(base, ref)` de
  `apartados.py`.
- **El Noticiero es un tablero y sus páginas van por pestañas** (reestructura del autor, 16-11-2026: «teniendo en
  cuenta las novedades de los servicios… y el objetivo… del modo Periodista»). `noticias-relevantes.html` trae una
  tarjeta por sección, en tres grupos (Lee, Verifica, Sigue; `TARJETA` y `tablero()` de `noticias.py`: **una sección
  nueva necesita ahí su línea de tarjeta**, o la generación se detiene), «Lo último, verificado» (`ultimas()`) y el
  puente. En las tres páginas **la barra son pestañas: se ve una sección a la vez** (`irA()` de `noticias.js`); las
  direcciones no cambian, y un ancla de adentro (`#col-<id>`, `#propon`, `#ciego-<id>`, `#promesa-<id>`) abre su
  sección. Los puntos ciegos y lo que falta de cada caso abierto van plegados. **El puente** (`PUENTE` y `puente()`)
  cierra cada página con el modo Periodista (preguntas que el chat ya contesta) y los servicios que vienen al caso,
  leídos de `SERVICIOS` y `COBRO`: **nunca un monto**. Cada nota trae «📰 Pregúntale al Periodista». El cabezal del
  periódico va solo en el diario. Se reordenó; no se quitó contenido.
- **Noticias es un periódico: «Auditavisión Noticias»** (pedido del autor,
  28-10-2026: «una nueva reestructuración tanto de diseño como de la
  información… partiendo de una metodología u objetivo»). **Objetivo: que
  ninguna noticia sobre el dinero público se quede sin cotejar.** Nueve
  secciones con su barra: Portada, Verifica (`#verifica`), **Noticias**
  (`#al-momento`: «Al momento» y «Verificado»; aquí no se opina), **Opinión**
  (`#columnas`: la Columna del Erario, Personajes, Hechos e Historia: nuestro
  argumento, siempre parado en un documento y nunca sobre la vida privada),
  Réplica y postura (`#replica`), Seguimiento (`#seguir`: los casos con
  `sigue` y «Pedir un seguimiento»), Mesa de redacción (`#mesa`), Agenda del
  erario (`#agenda`) y Cómo trabajamos (`#metodo`, con `#propon`): el método
  de siete pasos, del rumor al documento. **Desde el 29-10-2026 la pestaña es
  un índice de tres tarjetas** (pedido del autor), y el diario se reparte en tres
  páginas (`PARTES` de `herramientas/noticias.py`): **Auditavisión Noticias**
  (`noticias-auditavision.html`: Portada, Noticias, Opinión y Réplica; ahí viven
  las columnas, `#col-<id>`), **Verifica una noticia** (`noticias-verifica.html`:
  el verificador, la Mesa de redacción y Cómo trabajamos, con `#propon`) y
  **Seguimiento: el caso no se olvida** (`noticias-seguimiento.html`: los casos
  abiertos, `#seguimientos` y la Agenda). Las anclas viejas de
  `noticias-relevantes.html` se mandan solas a su página (`ANCLAS`); un enlace
  nuevo apunta directo a la página donde vive la sección. **La noticia y la opinión no se
  mezclan:** `columnas.js` reparte por `seccion` (`NOTICIA`), y una columna
  nueva va en la que le toca. El armazón, el método, la agenda y las búsquedas
  de la mesa viven en `herramientas/noticias.py`; la página la pinta
  `noticias.js`. **La mesa de redacción** trae titulares de Bing Noticias y
  Google Noticias al pedirlos (en el navegador) y los junta
  `herramientas/recolectar_noticias.py` en `docs/noticias/bandeja.json`
  (flujo «Mesa de redacción», cada día a las 8:23 de la Ciudad de México y a mano): **solo titular, medio, fecha y liga,
  rotulados «sin verificar»; nunca el texto de la nota**. Un titular entra a
  la plataforma solo después de pasar por el método. **La agenda** son plazos
  de la ley, cada uno con su artículo; las fechas que la ley da como «30 días
  después del trimestre» o «último día hábil» se dicen como cuenta nuestra
  (`derivado`). El verificador dice además **quién aparece en la nota**
  (`insp_nota.ENTE_PAL` y `ESTADO_PAL`) y lleva a su ficha del Auditor de
  entes, con su estado de cuenta y su salud financiera.

---

## 5 ter. El bot es el auditor de la plataforma

**Decisión del autor, 23-10-2026.** «Pregúntale al Auditor»
(`herramienta-inspector-pregunta.html`) no es una herramienta más: es **el
auditor** de Auditavisión. Su encargo es **localizar, interpretar, verificar
y mostrar** al lector, en sencillo, todo lo que la plataforma sabe: datos,
estadísticas, estados de cuenta, sueldos, márgenes, porcentajes,
presupuestos, impuestos, glosario, leyes, referencias y las herramientas
mismas. La plataforma es extensa; el bot es la puerta corta a todo.

- **La Enciclopedia es la base de datos física del Auditor** (decisión del autor,
  29-10-2026). Cada página de la Enciclopedia tiene su modo (`herramientas/modos.py`),
  lleva «Pregúntale al Auditor · Modo X» en su cabecera y sale en el chat, en
  «Saber más» o en «📚 En la Enciclopedia». **Una página nueva de la Enciclopedia
  no está terminada hasta que `python3 herramientas/cobertura_auditor.py` pasa**
  (corre en `revision.py`); si su título solo no basta para encontrarla, su
  pregunta va en `PREGUNTA` de `modos.py`. La bodega de Supabase es el respaldo
  y la navegación en internet solo da búsquedas «sin verificar».
- **Todo lo nuevo entra al bot.** Una cifra, página o herramienta que se
  agrega a la plataforma no está terminada hasta que el bot la encuentra:
  las páginas y secciones se indexan solas al regenerar; las cifras
  estructuradas entran al bloque `dat` de `herramientas/asistente.py`
  (`_charla()`) o al catálogo de cifras (`insp_nota.catalogo()`), y se prueba
  con una pregunta en el chat. Las cifras de la pestaña Números entran por
  `herramientas/asistente_numeros.py`: un renglón por cifra, con su estado,
  su documento y la página donde se lee (y debe leerse igual ahí). Las de la
  pestaña Datos, por `herramientas/asistente_datos.py`, igual; las que no
  son millones de pesos llevan su unidad (`un`) y su frase (`fr`). El Poder Legislativo
  y las elecciones, por `herramientas/asistente_legislativo.py`, cotejado
  contra la Constitución, la LGIPE, el INE y el INEGI (nunca contra la
  Enciclopedia, que solo sirve de guía de temas). El Poder Judicial, por
  `herramientas/asistente_judicial.py`, cotejado contra la Constitución, los
  acuerdos del INE (INE/CG563/2025 e INE/CG564/2025), el Manual de
  remuneraciones del PJF y el PEF 2026. Lo que resuelve con su dinero (la auditoría
  de gestión: asuntos, rezago y tiempos), por `herramientas/gestion_judicial.py`,
  con el censo del INEGI; **el dinero va siempre junto a lo que se resolvió con
  él, y el «dinero por asunto» se dice como derivado, nunca como costo de un juicio**. La salud pública
  (IMSS, ISSSTE, IMSS-Bienestar), con el mismo molde, por `herramientas/gestion_salud.py`
  (tarjeta «Salud pública» de Datos y `D.sal` del chat); **lo que una institución anuncia se
  coteja contra lo que registra su propio documento estadístico**. La justicia ambiental (PROFEPA:
  denuncias, rezago, multas y la Fiscalía), igual, por `herramientas/gestion_ambiental.py` (tarjeta
  «Justicia ambiental» de Datos y `D.amg` del chat), cotejada con sus Informes de Actividades y la LGEEPA. Los dos Poderes viven además en la
  pestaña Datos (`datos-poder-legislativo.html`, `datos-poder-judicial.html`),
  una página por grupo de temas, armadas con el mismo texto del bot
  (`PAGINAS` de cada módulo).
  El nepotismo y el parentesco en los cargos públicos, por
  `herramientas/nepotismo.py` (28-10-2026; aplicación del Modo Inspector,
  `herramienta-inspector-nepotismo.html`, con su tarjeta en Aprende, y
  `D.nep` del chat; la página que tuvo en Aprende redirige ahí), cotejado con la
  LGRA (art. 63 Bis), el Código Penal Federal (art. 220), el Código Civil
  Federal (arts. 292 a 300) y la Constitución (nepotismo electoral, desde
  2030): **qué ley alcanza a cada parentesco vive en una sola tabla
  (`ALCANCE`/`alcance()`), que leen la calculadora, la página y el chat**, y
  cómo se dice cada parentesco en la calle va en `ALIAS`. **Un apellido igual
  nunca es prueba de parentesco**: un vínculo entra a la plataforma solo si lo
  dice un documento oficial, y a los familiares que no son servidores públicos
  no se les nombra.
  **Los deudores alimentarios y las candidaturas** (17-11-2026, pedido del autor «por el momento electoral»): tema `deudores` de
  `asistente_legislativo.py`, cotejado con el art. 38, fr. VII de la Constitución y los arts. 135 Bis a 135 Septies de la LGDNNA.
  **El Registro Nacional de Obligaciones Alimentarias no se copia ni se publica un solo nombre** (son particulares y sus acreedores,
  menores; decisión del autor, que además descartó cobrar por consultarlo): se explica, se da su liga y se cita solo lo que una
  autoridad electoral haga público en un documento. El **RUG** (garantías mobiliarias, Código de Comercio) va en el glosario: **no es
  una lista de fianzas ni de sancionados**, y su consulta pide cuenta de usuario.
  El cruce de contratos × lista 69-B × ASF, por `herramientas/cruce_contratos.py`
  (04-11-2026, integrado el 22-11-2026 desde el PR #137; aplicación del Modo Inspector,
  `herramienta-inspector-cruce.html`, y `D.cru` del chat): **lo que declaró la autoridad va
  `oficial` y la señal es nuestra (`derivado`, «señal para revisar»)**; una empresa desvirtuada
  o con sentencia favorable nunca es señal. El chat solo menciona el hallazgo, o el antecedente
  si no hay, y lleva a su sección. Contratos de CompraNet por `actualizar_compranet.py`; serie de
  la ASF por `extraer_estadisticas_asf.py`. Mientras `actualizar_69b.py` y `actualizar_comprasmx.py`
  no guarden la fecha de presunto y la de firma, el cruce usa la de publicación y lo dice.
  Las agresiones a la prensa, por `herramientas/periodistas.py` (29-10-2026;
  `periodismo-en-riesgo.html`, del modo Periodista), con el informe mensual del
  Mecanismo de Protección (Gobernación); **los homicidios y las sentencias son de
  la FEADLE y, mientras no se coteje su documento, siguen pendientes: no se
  rellenan con cifras de organizaciones civiles**, y no se nombra a las personas.
  Los informes especiales de la ASF, por `herramientas/informe_sancion.py`
  (27-10-2026: «Documentar para sancionar», cotejado contra la LGRA y la
  LFRCF vigentes): su página es la tarjeta «Informe especial» de Informes
  oficiales (`informes-documentar-para-sancionar.html`) y el chat lo lee como
  `D.san`. Sus 20 matrices viven en `docs/informes/documentar-para-sancionar.json`;
  **un tipo de irregularidad que la gente diga de otro modo necesita su frase
  en `FAMILIAS`**. El informe semestral de la ASF (art. 38 de la LFRCF), por
  `herramientas/informe_semestral.py`: cuarta tarjeta de Informes oficiales
  (`informes-semestral-asf.html`), y el chat lo lee dentro de `D.san` (claves
  `sem_*`). **Cada semestre (1 de mayo y 1 de noviembre) se cambian sus cifras
  y su `DOC` por las del informe nuevo**, con el anterior en `ANT` para el
  cambio del semestre. Un documento de doctrina o una guía oficial es metodología:
  se explica en sencillo con su página, no se copia entero. La metodología de auditoría (control interno, riesgos, fraude, prueba y lavado) vive en `aprende-auditoria.html`, por
  `herramientas/metodologia_auditoria.py`, cotejada contra el Marco Integrado de Control Interno de la ASF, la LFPIORPI y el
  CNPP: **un temario o un folleto de curso nunca es fuente**, solo guía de temas.
- **Responde como chat:** claro, corto y contundente, con la cifra, qué
  quiere decir y su fuente a la vista. Cada respuesta con datos lleva
  **«Saber más»**, que abre la página de la plataforma donde está la
  información (el campo `ir` de la respuesta: una respuesta nueva sin `ir`
  no está terminada), y **«Generar dictamen»**, que abre en otra pestaña el
  «Dictamen cívico independiente» sellado (`herramienta-inspector-dictamen.html`). El
  enlace del dictamen solo lleva la pregunta (`?q=`, las previas en `&c=` y el modo en `&modo=`):
  la página vuelve a contestarla con la misma base, así que no se puede
  fabricar un dictamen con cifras ajenas. El dictamen dice que no es un
  documento oficial ni un peritaje con validez ante autoridad.
- **Los Expedientes de investigación** (pedido del autor, 16-11-2026: «grandes investigaciones que se irán dando seguimiento de forma
  autónoma, automatizada e independiente, alimentándose de nuestra base de datos y al día», y «que el usuario también nos puede solicitar»).
  Son la quinta tarjeta de la Biblioteca del Erario Público, **con el nombre «Expedientes de control interno»** (decisión del autor, 17-11-2026; los archivos no cambian de nombre): `expedientes-investigacion.html` y un `expediente-<id>.html` por cada
  investigación de Auditoría en imágenes. Los arma `herramientas/expedientes_inv.py` y **nadie los escribe a mano ni traen cifras propias**:
  cruzan por las frases de `TEMA_BOT` la lectura breve, las notas del Noticiero y la memoria de promesas (la bitácora), los «Lo que sigue» y
  el Registro de pendientes. «En el radar» lee en el navegador la bandeja de la Mesa de redacción: **solo titular, medio, fecha y liga,
  «sin verificar»; un titular nunca entra como dato**. **Una investigación nueva tiene su expediente sola**; «abierto» quiere decir que hay
  pendientes o un «lo que sigue», nunca una acusación. Se piden con el servicio `expediente` (se cotiza, **nunca un monto**) o proponiendo un
  caso. `expedientes.html` sigue siendo los casos de la ASF: «expediente de Segalmex» abre esa aplicación; «expediente del Tren Maya», el de
  la Biblioteca (`expInvResp()` de `asistente.js`).
  **Son el archivero digital** (17-11-2026): las investigaciones propias y las pedidas pasan por las mismas etapas (`ETAPAS`); un pedido aceptado va en
  `SOLICITADOS`, **sin decir quién lo pidió y sin cifras** (las cifras entran por su módulo), y la lista no se rellena con solicitudes inventadas.
  **El expediente es una gran investigación hecha de dictámenes**: lista los dictámenes de su caso y lleva su sello, con folio y huella SHA-256 de su
  contenido (`_huella()`), que cambia cuando cambia una cifra, un documento, la bitácora o un pendiente. No es un documento oficial, y lo dice.
  **El registro por modo vive en Supabase** (`preguntas_bot.modo` y `modo_toca`, vista `preguntas_por_modo`): solo de las preguntas sin respuesta.
  **Todo queda vinculado al expediente** (17-11-2026): cada investigación de Auditoría en imágenes lleva a su expediente (`expediente_puerta()` de
  `auditorias.py`); una nota o columna entra a la bitácora si nombra el caso (título, `temas` o su clave), si ella misma cita la investigación con su
  liga (`auditoria-<id>.html`) o si está en `VINCULOS` (`_cita()`): **el cuerpo no se lee por palabras, porque mencionar de paso no es pertenecer al caso**.
  Los dictámenes que el lector genera en el chat y tocan una investigación se listan en su expediente, «Tus dictámenes de este caso», **guardados solo en su
  navegador** (`av-dics`, `guardaDic()` de `asistente.js`): nunca van a un servidor ni entran a la huella.
  **Se arman cada día** (17-11-2026, flujo «Expedientes al día», `.github/workflows/expedientes.yml`, 8:53 de la Ciudad de México y a mano): vuelve a correr
  `apartados.py` y publica solo si algo cambió; su reporte (`resumen()`) cuenta los titulares por cotejar de cada caso, que **nunca entran solos**. Por eso
  **la generación debe dar lo mismo dos veces seguidas**: un orden que salga de un `set` se desempata (`key=lambda x: (-len(x), x)`), o el flujo publicaría ruido.
- **La respuesta va esquematizada y los modos remiten** (pedido del autor, 16-11-2026). Cada respuesta abre con su cabecera (`cabResp()`: tipo de
  ficha, modo al que pertenece y chips), pliega el detalle largo (`esquema()`), trae la tarjeta de su expediente (`expInvHtml()`) y guarda
  «Explóralo a fondo» y «En la Enciclopedia» en paneles (`panel()`). **Si la pregunta le toca a otro modo, la respuesta lo dice arriba y ofrece
  pasar** (`modoToca()` y `remiteHtml()`: por las palabras de `MODO_PAL` o por el modo con que `modos.py` clasificó la página); la contesta igual,
  con los mismos datos. El dictamen abre con «De un vistazo», trae las cifras en tabla y el capítulo «Expediente relacionado». **Nada de esto
  agrega cifras ni entra a la huella.**
- **Se ve y se usa como el mejor producto** (rediseño del 24-10-2026): un
  solo logo (el de la cabecera del chat; las burbujas no llevan avatar), cada
  respuesta en cuatro capas (texto, panel de fuente, acciones, «Sigue
  preguntando»), preguntas de ejemplo quietas que solo cambian con «Otras
  preguntas», y «↩️ Regresar» y «🗑️ Limpiar» bajo la caja. La plática se
  guarda en la pestaña (`sessionStorage`, clave `av-chat`); un enlace de una
  respuesta deja la seña `av-volver`, y la página a la que llega muestra
  «Volver al Auditor» (`assets/auditor/js/volver-auditor.js`, cargado en
  todas las páginas junto a `iconos.js`; su estilo vive en `civico.css`).
- **Abre los estados de cuenta y los recursos de la Enciclopedia**
  (24-10-2026). «Estado de cuenta de…» lleva directo al documento (cívico,
  ambiental, cada presidente, diputación federal y local, senaduría, Corte,
  estado, municipio), y al pie de cada respuesta van, en «Explóralo a fondo»,
  los mapas, relojes, tableros, simuladores y páginas de fiscalización que
  vienen al caso («Ver mapa», «Ver fiscalización»…), con el estado ya
  elegido. Los dos catálogos viven en `herramientas/asistente_recursos.py`:
  **un mapa, reloj, contador o simulador nuevo no está terminado hasta que
  tiene ahí su renglón**, y si un enlace o un ancla deja de existir, la
  generación se detiene. Así la Enciclopedia alimenta al Auditor.
- **Cada estado y cada municipio tiene sus cuatro documentos** (24-10-2026):
  estado de cuenta, salud financiera, dictamen y ritmo en vivo, en su ficha
  del Auditor de entes. El contador «en vivo» es la cifra anual oficial
  repartida entre los 31,536,000 segundos del año: va como `derivado`, con
  su operación y con lo que no dice; nunca se presenta como dinero que se
  mueve en tiempo real.
- **El Modo Inspector vive también en el chat** (24-10-2026): sus seis
  aplicaciones se usan desde la plática. La lista negra del SAT la contesta
  el chat (RFC o nombre); un folio, una liga, un ente federal, un expediente
  o «quiero pedir una investigación» abren la aplicación en un marco de la
  respuesta (`iframe` `av-en-chat`, que `volver-auditor.js` muestra sin
  cabecera ni pie). Las aplicaciones no se copian: **una aplicación nueva
  del Modo Inspector entra sola** al catálogo (`_inspector()` de
  `asistente.py`), pero su página debe aceptar lo que el lector trae por la
  dirección (`?q=`, `?liga=`, `?verifica=`, `#ente=`) y su intención se
  agrega en `inspector()` de `asistente.js`.
- **El mapa ambiental separa quién paga** (Bloque 4, 27-10-2026):
  cada proyecto de `OBRAS_MAPA` (`herramientas/am_basura.py`) lleva `paga`
  (`publico` o `privado`) y su porqué en `pagaTxt`; **solo el gasto público
  se suma** en los contadores del mapa y del chat, y la inversión privada se
  dice con su nombre, sin monto si no hay documento. Los montos «por aclarar»
  ante la ASF **no se escriben a mano**: salen de los expedientes
  (`EXPEDIENTE` del mismo módulo) como suma derivada. Un proyecto privado que
  la gente nombra de otro modo lleva sus frases en `al`.
- **Inversión y Megaobras vive también en el chat** (24-10-2026): cada obra,
  cada presidente, los rankings y las cuatro cifras los contesta
  `megaobras()` de `asistente.js` con lo que escribe
  `herramientas/asistente_megaobras.py` (las mismas funciones que pintan la
  herramienta). **Una obra nueva necesita su renglón en `ALIAS`** (cómo se
  dice en la calle) y, si tiene dependencia a cargo en el Auditor de entes,
  en `ENTE`; sus cinco aplicaciones se abren en el marco del chat como las
  del Modo Inspector. Su salud financiera es su **estado de resultados**
  básico (verde suma, rojo resta), en pesos de su año y de hoy con el INPC
  de la máquina del tiempo del peso; y donde la plataforma no tiene mapa,
  el chat lleva al **simulador** de la herramienta, ya filtrado.
- **Las cuatro herramientas viven en el chat** (24-10-2026): además del Modo
  Inspector y de Inversión y Megaobras, las seis aplicaciones de **Costo
  Ambiental** y las cinco de la **Calculadora Cívica** se reconocen por su
  nombre o por cómo se dicen en la calle (`ALIAS_APPS` de
  `herramientas/asistente.py`) y se abren en el marco del chat
  (`herramienta()` de `asistente.js`). «Gano 15 mil al mes, ¿cuánto me
  retienen?» abre la Calculadora con el ingreso ya puesto (`?m=&p=&n=`): la
  cuenta la hace la calculadora, nunca el chat. **Una aplicación nueva de
  esas dos herramientas entra sola** al catálogo, y si la gente la llama de
  otro modo, su frase va en `ALIAS_APPS`.
  El régimen también se lee («manejo Uber», «rento mi depa», RESICO: `&r=&pl=`).
  Toda aplicación abierta en el chat trae **«Generar dictamen»** (`conApp()`):
  respalda qué hace y de qué documentos salen sus datos (`_fuentes_app()`
  los toma de su página), con el enlace que repite la cuenta; nunca copia el
  resultado.
- **Las investigaciones de Auditoría en imágenes salen al frente**
  (24-10-2026): cuando la plática toca su tema (Tren Maya, Dos Bocas,
  huachicol, Ramo 33…), «Explóralo a fondo» abre con «📖 Ver la
  investigación». **Una investigación nueva necesita sus frases en
  `TEMA_BOT`** de `herramientas/auditorias.py`, o la generación se detiene.
  **Las imágenes de la portada abren el modo Periodista** (decisión del autor,
  21-11-2026): cada diapositiva lleva `&modo=periodista` (`MODO_PORTADA` y
  `chat_url()` de `auditorias.py`) y dice «📰 Pregúntale al Periodista».
- **Noticias relevantes vive también en el chat** (24-10-2026): el nombre
  de un personaje abre sus columnas (con sus cifras y documentos) y lo que
  circula sin pruebas, con el motivo (`DESCARTADO` de `columnas.js`). Lo
  escribe `herramientas/asistente_personajes.py`: **una columna nueva entra
  sola**; **un personaje nuevo necesita su renglón en `PERSONAJES`**, y si su
  nombre no aparece en ninguna columna ni en lo descartado, la generación se
  detiene. De internet el chat **solo ofrece búsquedas armadas** en portales
  oficiales y noticias, rotuladas «sin verificar», y lleva a Contrasta una
  nota; la función `buscar-web` devuelve solo enlaces, nunca un texto
  redactado por la IA sobre una persona.
- **Verificamos: lo que circula en redes entra a la Enciclopedia**
  (decisión del autor, 26-10-2026: «que el auditor tenga ese contenido en la
  enciclopedia y que al momento de preguntar cuente con esa información y sus
  fuentes para interpretarla y plasmarla en nuestro dictamen»). Cuando el
  autor pasa un video, una publicación o una nota de redes, se vuelve una
  columna de la sección **Verificado** de `columnas.js`, con `circula` (qué
  dice, quién, dónde y cuándo) y `cotejo`: cada afirmación con su resultado
  (`consta`, `matiz`, `no consta`, `pendiente`), su explicación y su
  documento. **Un video o una nota nunca es fuente**: es lo que se coteja.
  Un `pendiente` del cotejo lleva `quien` y `donde`, y entra solo al
  Registro de pendientes (`red-<columna>-<n>`). El chat lo contesta, el
  dictamen lo trae en su capítulo «Cotejo de lo que circula», y si nombra a
  una persona de la vida pública se le agrega su renglón en `PERSONAJES`. A
  los particulares (familiares, empleados de una empresa) no se les nombra.
  Cada columna trae además `sigue`: lo que falta revisar para **seguir el
  dinero** (un voto, el DOF, un informe de la ASF, contratos por integrar).
  **Las empresas contratistas** que nombra un documento oficial van en
  `EMPRESAS` (mismo módulo): el chat las contesta por su nombre, con
  búsquedas armadas en ComprasMX, el directorio de sancionados, el DOF, la
  ASF, la UIF y la OFAC, y la lista negra del SAT avisa si la plataforma ya
  las tiene. El protocolo completo, con dónde buscar cada cosa, está en
  [docs/VERIFICAMOS.md](docs/VERIFICAMOS.md): **quien retome el proyecto
  empieza por los «Lo que sigue»**.
- **Contratos públicos de ComprasMX** (decisión del autor, 26-10-2026: «integra
  los contratos de ComprasMX»). `herramientas/actualizar_comprasmx.py` lee los
  archivos de Datos Abiertos de ComprasMX (se bajan con su botón en
  `comprasmx.buengobierno.gob.mx/datos-abiertos`; el servidor no los sirve a
  una descarga directa) y escribe `assets/auditor/data/comprasmx/`: índice de
  proveedores, una ficha por proveedor (por las dos primeras letras del RFC),
  las instituciones y el cruce con la lista 69-B del SAT. El chat lo contesta
  (`contratosCmx()` y `cruceSat()` de `asistente.js`, que cargan los
  catálogos solo al preguntar) y `contratos-publicos.html` es su buscador. El
  importe de cada contrato es `oficial` (antes de impuestos, como lo reportó la
  institución); las sumas, `derivado`; no se convierten monedas, y en un
  contrato abierto el importe suele ser el máximo, no lo pagado. **Las personas
  físicas no se publican** (su RFC es un dato personal), y tener contratos no
  es una irregularidad: así se dice en cada respuesta.
  **El padrón de contrapartes** (18-11-2026, pedido del autor: «que nuestra base de datos quede muy bien integrada… para el compliance de prevención de
  lavado de dinero»). Una sola ficha por RFC (`assets/auditor/js/padron.js`, que leen la aplicación «Revisa a tu contraparte»,
  `herramienta-inspector-padron.html` de `herramientas/insp_padron.py`, y el chat, `padronResp()` de `asistente.js`) con las listas del SAT del art. 69,
  17-H Bis y 69-B Bis (`herramientas/anclar_listas.py` → `assets/auditor/data/padron/`, con huella y cuadre; flujo semanal «Base al día»), la 69-B,
  el Directorio de Sancionados, la OFAC y la ONU (`sanciones-int.js`) y ComprasMX. **No trae datos propios**: lee los archivos que ya escriben esos
  scripts. **Las personas físicas no se publican** (decisión del autor, 18-11-2026): las listas del SAT las guardan por la huella SHA-256 de su RFC
  (sal `av-padron:`), y de ellas solo se dice si el RFC coincide, nunca el nombre. **Una coincidencia es una señal para revisar, nunca una acusación
  ni una calificación**; coincidir en un nombre no es ser la misma persona, y lo que no es público (la Lista de Personas Bloqueadas de la UIF) se dice
  con su nombre. **Una lista nueva entra en `anclar_listas.py`, con sus columnas fijas y su cuadre**, o no entra. **El lote, la cadena de terceros y la matriz** (18-11-2026, `insp-padron-lote.js`, sección `#lote`): hasta 2,000 RFC de un CSV, un TXT o lo pegado de Excel, o las facturas XML (emisor, receptor y los RFC «a cuenta de terceros» del CFDI 4.0, con el papel de cada uno), en una matriz de una fila por RFC y una columna por lista que se descarga en CSV, **todo en el navegador**; **la columna «Revisar» ordena por la señal más seria, nunca suma ni califica**.
  **La nómina** (18-11-2026, pedido del autor: «calcular la nómina… y tener las distinciones entre trabajadores del gobierno, ISSSTE, y trabajadores para empresas, IMSS»). La Calculadora Cívica (`cc_ticket.py`, `cc-ticket.js`) pregunta quién paga (`&pt=issste`) y suma «Tu nómina completa»: lo que pone el patrón y el costo de la plaza; las tasas viven en `calculadora_civica.imss_patronal` e `issste` de la base, cada una con su artículo y la huella de la ley. **La cesantía y vejez patronal sube cada 1 de enero hasta 2030**: en enero se cambia `cesantia_2026` por el renglón del año (decreto DOF 16-12-2020, Segundo transitorio). El Lector de facturas revisa recibos de nómina (`revisar_nomina()` de `lector_cfdi.py` y `revisarNomina()` de `insp-factura.js`, gemelos); **el ISR del recibo es una cuenta aproximada nuestra**, y una diferencia chica es solo nota. **Nunca se muestra el nombre, la CURP ni el número de seguridad social de quien trabaja**, y la señal del art. 127 es una comparación de cifras, no una acusación. **Revisamos la nómina; no la calculamos ni la timbramos por nadie.**
  **Los grupos y sus filiales** (17-11-2026, `herramientas/empresas_grupos.py`, sección `#grupos` y `grupoEmp()` del chat; pedido del
  autor: «le pregunté al chat por Grupo Prodi y no salió información»). Muchos grupos no contratan con su nombre: `GRUPOS` dice con qué
  empresas (por RFC) aparece cada uno en ComprasMX. **Ninguna cifra se escribe ahí**; **el vínculo entre el grupo y la filial es `pendiente`
  mientras solo lo diga la prensa**; lo que falta cotejar va sin montos y con el portal donde debe estar; **contrato, concesión y permiso
  no se confunden** (`FIGURAS`: ComprasMX trae contratos, una concesión se acredita con su título), y **nunca se dice el partido de un
  gobierno**. Una empresa por su nombre, sin la palabra «contratos», se busca en ComprasMX (`empresaNombre()` y `quizaEmpresa()`); si no
  está, se dice, y no se contesta con lo que se le parece. **Un grupo nuevo necesita su renglón en `GRUPOS`** y su pregunta de prueba.
  **El padrón del SAT y las donatarias** (19-11-2026, `herramientas/padron_sat.py`, tarjeta «Padrón del SAT» de Datos, `D.pad` del chat y las lentes `sat`, `satH` y `don` del Planisferio). **Ninguna cifra se escribe en el módulo**: el padrón sale de `docs/sat/padron-sat.json` (`anclar_padron_sat.py`, los datos abiertos del SAT, con su cuadre; semanal en «Base al día») y las donatarias de `docs/sat/donatarias.json` (`anclar_donatarias.py`, a mano cada enero). **Los regímenes no se suman** (una persona puede estar en varios), **el estado es el del domicilio fiscal** (por habitante puede pasar de 100 y no califica a nadie) y **un RFC activo no es un pago**. Las asociaciones religiosas son de Gobernación y siguen pendientes: **no se toman de la prensa**. **El simulador de venta de un inmueble** (`cc_inmueble.py`, sexta aplicación de la Calculadora Cívica) cita su artículo en cada paso; su tarifa es la de 2026, y **su año sale de la tarifa de la base** (`RMF AAAA` de `tarifa_mensual.ley`): cuando entre la del año nuevo, cambia solo; su UDI la pone al día `anclar_udi.py`. **«Inviertes en la bolsa»** (`cc_bolsa.py`, séptima aplicación) saca el 10 % de los arts. 129 y 140 y **dice lo que no calcula** (10 % o más de la emisora, fuera de bolsa, antes de 2014). Los dos usan la lectura usual del factor del INPC (mes anterior a la venta ÷ mes de compra) y lo dicen junto a la del art. 17-A al pie de la letra.
  **El simulador del predial** (19-11-2026, `herramientas/cc_predial.py`, octava aplicación de la Calculadora Cívica): **cada municipio cobra con su propia Ley de Ingresos, así que cada uno es un renglón de `MUNICIPIOS`** con su ley, su huella y el artículo de cada cifra; `revisa()` detiene la generación si una tabla no está en orden o no es continua. **Un municipio nuevo solo entra cotejado con su ley**; los demás dicen su recaudación del INEGI y «pendiente» como falta de la plataforma. **El mercado de la vivienda va junto al valor fiscal, nunca en su lugar** (21-11-2026): la escala del Índice SHF (`shf()` y `cuartil()`, gemela de la de `cc-predial.js`) lee `docs/vivienda/shf-precios-vivienda.json`, que escribe `anclar_shf_vivienda.py` con huella y cuadre; **no se dice como avalúo, como el valor de un predio ni como error del catastro**, y las estimaciones de portales privados no son fuente. **El mismo índice vive en el Planisferio** (lentes `shfI`, `shfV` y `shfM` de la dimensión financiera) **y en el chat** (`vivEdo()` de `asistente-charla.js`, con `chat_shf()`): una cifra, tres puertas. **El informe del simulador** (21-11-2026, `docInforme()` de `cc-predial.js`) se pinta, se imprime y se descarga del mismo modelo, con folio y huella SHA-256 de los datos y las cifras (sin la fecha), y su liga repite la cuenta: **no agrega cifras, no es documento oficial ni avalúo y nada sale del navegador**. Las lecturas nuestras («sobre el primer $X», la sobretasa de baldíos, cuál beneficio se suma) van como `derivado` y la página las dice. **Nunca se publican los datos de la persona de un mandamiento**: el ejemplo de Zapopan va sin nombre, domicilio ni cuenta, y es la prueba de `--prueba`. Cada enero se cambian las tablas por las de la ley nueva. **Una ley ambigua no se interpreta para sacar una tasa**: se lee, se anota en `ESPERA` con su huella y su porqué (Acatlán de Juárez, Chapala y Tala escriben «%» bajo «tasa al millar»; Poncitlán da a sus gastos de ejecución un mínimo mayor que su tope) y la ficha del municipio lo dice. La cobranza de cada ley se describe con sus campos (`req`, `emb`, `pesos`, `min_pesos`, `max_pesos` y su `nota`), y la prueba compara la tarifa de cada tipo de predio en Python y en el navegador. En el chat, «predial» con «cuánto pago», «debo»… abre el simulador antes que la ficha del municipio y con `?mun=` si su ley está cotejada (`predialResp()` de `asistente.js`, con la lista `pred` que escribe `asistente.py` desde `MUNICIPIOS`); «¿cuánto recaudó X de predial?» sigue yendo a la ficha.
  **El calendario de conservación** (19-11-2026, `herramientas/insp_conservacion.py`, aplicación del Modo Inspector y entrega 1 del servicio `gobernanza`): cada plazo es un renglón de `REGLAS` con su ley (`LEYES`, con la huella del PDF), su artículo y su cita textual. **Las reglas son `oficial` y las fechas, `derivado`**; la cuenta del navegador (`insp-conservacion.js`) y `vence()` son gemelas y `--prueba` las compara: **una regla nueva se escribe en los dos**. **Manda el plazo más largo, y al vencer los datos personales se bloquean y se suprimen (LFPDPPP, art. 10): nunca se dice «guárdalo por si acaso»**. Si una ley cambia, se vuelve a bajar su PDF y se cambian su huella y su cita.
  **El autodiagnóstico de cumplimiento** (19-11-2026, `herramientas/insp_cumplimiento.py`, entrega 2 del mismo servicio): una pregunta por obligación en `PREGUNTAS`, con su ley de `LEYES` y su cita textual; **las preguntas son `oficial` y el resultado, `derivado`: cuenta las respuestas, nunca califica, certifica ni dice que alguien cumple ante una autoridad**, y nada sale del navegador. `resumen()` y el de `insp-cumplimiento.js` son gemelos (`--prueba`). **La matriz de riesgos** (19-11-2026, `herramientas/insp_riesgos.py`, entrega 3): lee esas mismas `PREGUNTAS` (una obligación nueva necesita su renglón en `RIESGOS`, o `--prueba` se detiene); la probabilidad sale de la respuesta y **la gravedad la pone el lector, nunca se rellena**; cada consecuencia cita su artículo y **nunca un monto de multa**. `matriz()` y la de `insp-riesgos.js` son gemelas.
  **Las señales de fraccionamiento** (04-11-2026, `herramientas/fraccionamiento.py`, sección
  `#fraccionamiento` y `fraccCmx()` del chat): adjudicaciones directas por monto de la misma unidad,
  empresa y partida que en 90 días rebasan el tope del Anexo 9 del PEF (LAASSP art. 55; Reglamento
  art. 111). **Se dicen siempre como señal para revisar, nunca como irregularidad**, sin nombrar a la
  empresa; los topes de cada año van en `ANEXO9` y se cotejan contra el DOF; lo que depende del escalón
  de cada dependencia queda pendiente (`fracc-escalon`).
- **El vigía legislativo y el lector de facturas** (05-11-2026,
  `docs/ENCARGO-VIGIA-Y-CFDI.md`). `herramientas/vigia_legislativo.py` lee el
  DOF y el índice de Diputados y deja en `docs/legislativo/bandeja.json` lo
  que hay **por cotejar** y los módulos que citan una reforma vieja: **detecta
  y propone, nunca escribe en la base**. Una ley nueva que la plataforma cite
  va en su `LEYES` (con cómo la nombramos), o su cita no se revisa. El
  **Lector de facturas CFDI** (`insp_factura.py`, `insp-factura.js`, y su
  gemelo `lector_cfdi.py`) lee el XML **en el navegador, sin subirlo**: lo que
  dice la 69-B es `oficial`; comparar fechas o rehacer la cuenta es `derivado`
  y se dice «señal para revisar», nunca «irregularidad». Con dos o más facturas
  (hasta 500) suma el resumen **por proveedor** (`proveedores()` de `insp-factura.js` y
  `por_proveedor()` de `lector_cfdi.py`, con las mismas reglas). **El Vigía 69-B** (`herramientas/vigia_69b.py`,
  flujo semanal) compara la lista del SAT contra `sat-69b.js` por RFC y deja en
  `docs/sat69b/bandeja.json` altas, cambios de situación, bajas y cambios de razón
  social, con las personas físicas con el RFC recortado y sin nombre. **Desde el 18-11-2026
  se actualiza sola** (decisión del autor): si el SAT publicó otro archivo, el flujo «Base al día» corre
  `actualizar_69b.py` con ese mismo archivo, sube el sello y publica; se detiene si cambian
  las columnas o si la lista se encoge más de 10 %. **`sat-69b.js` conserva los nombres
  tal como los publica el SAT** (decisión del autor, 18-11-2026: la 69-B es una lista que la
  ley manda publicar en el DOF), a diferencia de las otras listas del padrón. **Revisa tu estado de resultados** (05-11-2026,
  `insp_resultados.py`, `insp-resultados.js` y su gemelo `lector_resultados.py`, con
  la prueba en `revision.py`) lee un CSV o lo pegado de Excel **en el navegador**, sin
  subirlo, y lo revisa en seis dimensiones (cuadre, estructura, rentabilidad, tendencia
  a 3 y 5 años, impuestos y deuda): todo es `derivado` y «señal para revisar». **Los
  patrones de los renglones viven en `CONCEPTOS` de `lector_resultados.py`** y la página
  se los pasa al JavaScript: una regla nueva se escribe en los dos y se prueba allá.
  **Mi Auditavisión** (05-11-2026, `insp_mia.py`, `insp-mia.js`) es el tablero: «Mis
  proveedores» contra la 69-B y «Mis revisiones», **guardado solo en el navegador**
  (localStorage `av-mia`; los dos lectores escriben ahí con `miaGuardar()`, solo el
  resumen y nunca el archivo; las personas físicas no entran a la lista).
- **La base al día** (18-11-2026, pedido del autor: «que nuestra base de datos quede bien integrada… únicamente para
  alimentarla o actualizarla con las novedades»). **Cada fuente de la base tiene su renglón en `FUENTES` de
  `herramientas/fuentes.py`**: quién la publica, cada cuándo, cómo entra (🤖 sola, 🔔 avisa o ✋ a mano), su script, su
  archivo y, si es a mano, la fecha `revisar` en que conviene ir a buscar la siguiente; se lee en `base-al-dia.html` y
  `revision.py` lo prueba. **Una fuente nueva no está terminada hasta que tiene ahí su renglón.** Lo que se actualiza solo
  corre en un flujo semanal, «Base al día» (`.github/workflows/base-al-dia.yml`, miércoles 9:41: la 69-B, las listas del
  padrón y el Directorio de sancionados): cada fuente por su lado, y la que no contesta o no cuadra se deshace sin tocar a las
  demás; al final escribe la agenda (`docs/base/agenda.json`) con las fuentes a mano que ya toca revisar. **Al integrar una
  fuente a mano se cambian su `corte` y su `revisar`.** La página no depende del día (la regenera cada mañana «Expedientes al
  día»): el «ya toca» solo vive en la agenda. **GitHub programa los flujos desde `main`**: un flujo nuevo o cambiado solo corre
  solo cuando su archivo llega ahí, con permiso del autor.
- **Verifica:** ante «¿es cierto que…?», «dicen que…» o la liga de una nota,
  compara contra el documento oficial con el mismo criterio de «Contrasta
  una nota» (`assets/auditor/js/verificador.js`, compartido por los dos).
  Un redondeo solo coincide si no se aleja más de 10 % del documento.
- **La regla editorial (§2) también lo manda.** No escribe cifras propias;
  todo cálculo va como `derivado` con su operación; lo que no tiene lo dice
  y lo anota en «Lo que aún no sé».
- **Hacia dónde va:** consultar portales externos y tener una capa de
  inteligencia artificial que aprenda de las preguntas. **La base de datos y
  sus funciones ya están construidas** (24-10-2026, `supabase/`, explicadas en
  `docs/BASE-DE-DATOS.md`). **La IA está encendida desde el 02-11-2026**, a
  pedido del lector y con botón: «📝 Redáctalo con las fichas» cuando la base
  no contesta o el lector pulsa «No era lo que buscaba» (`pideIa()` de `asistente.js`, que le pasa las fichas más
  cercanas) y «🔎 Buscar ahora» en «Búscalo en internet» (`pideWeb()`). El
  flujo «Sube la base de datos» sube las dos funciones y prueba la IA con una
  pregunta real; el aviso de privacidad dice qué se manda a Anthropic. La IA (`auditor-ia`) solo redacta con lo que le entregan las
  fichas, y cada cifra de su respuesta se coteja contra ellas: si una no
  aparece, se tira; `buscar-web` solo devuelve enlaces de sitios oficiales y
  de una lista editorial de prensa. **Ninguna cifra fiscal vive en la base.**
  **Los códigos de acceso** (29-10-2026) abren la versión de prueba: `herramientas/acceso.py` arma el canje
  y el panel, y su candado (`acceso.js`, en el `<head>` de todas las páginas) solo se enciende con
  `CANDADO = True`; una página que deba abrir sin código va en `LIBRES`.
  **El control interno** (18-11-2026): el panel (`administracion-codigos.html`) va en pestañas (`HOJAS` de `acceso.py`): tablero de uso con
  gráficas, códigos (con Renovar), solicitudes, bitácora y mi acceso. La bitácora la escriben disparadores de la base: **una acción nueva de la
  administración sobre los códigos queda anotada sola; una tabla nueva de la administración necesita su disparador**. La medición de uso
  (`acceso.js`, `uso_eventos`) **nunca guarda la IP, lo que se escribe ni las preguntas al chat**, respeta «No rastrear» y GPC, no mide a la
  administración y se apaga en el aviso de privacidad (`#uso`): **si algún día mide algo más, el aviso cambia antes**. Todo cambio a
  `supabase/` pasa `python3 herramientas/prueba_base_datos.py` y, si toca
  las funciones, `deno check` y `deno test supabase/pruebas/`.

---

## 6. Tono al escribir de cara al lector

Formal, cálido y llano, sin renunciar al rigor técnico. El lector no es
especialista pero no es tonto: se le explica, no se le simplifica. Cada
afirmación fuerte va acompañada del artículo, el ramo o el documento que la
sostiene.

**Al lector se le habla de tú** (decisión del autor, 27-09-2026): la
plataforma le habla a una persona, no a un trámite. Las citas textuales de
leyes y documentos se dejan como están. En el motor, que comparte la
Enciclopedia, los textos van en `tuUd('versión usted', 'versión tú')`: el
auditor muestra la de tú. (Heredado de cuando compartía motor con la
Enciclopedia antigua, ya retirada.)
