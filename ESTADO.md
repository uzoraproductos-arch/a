# ESTADO.md: dónde va Auditavisión

La hoja corta para arrancar. Las reglas están en [AGENTS.md](AGENTS.md) y la
historia completa de cada decisión en [CONTEXT.md](CONTEXT.md), que pasa de
7,000 renglones: aquí va solo lo que necesitas para no repetir trabajo ni
pisar el de otro. **Se actualiza en el mismo commit que cambia lo que dice.**

Última actualización: 28-10-2026 · sello `20261028q` · rama `claude/funny-turing-imtm54`.

## Antes de empezar y antes de empujar

```bash
git pull origin claude/funny-turing-imtm54
python3 herramientas/revision.py --base origin/claude/funny-turing-imtm54   # al terminar
```

`revision.py` corre lo que pide AGENTS.md §5: `node --check`, los CR sueltos,
que el sello haya subido si tocaste `assets/`, el inventario (enlaces rotos y
cotejos sin evidencia), las **223 preguntas de prueba del Auditor**, la guardia
de legibilidad y, si tocaste `supabase/`, la base de datos. GitHub la corre sola
en cada envío (`.github/workflows/revision.yml`). Con `--rapida` se salta lo
que necesita navegador.

- **Las preguntas de prueba** viven en `herramientas/preguntas_auditor.json`.
  Si un cambio mueve una respuesta a propósito, se corrige su renglón en el
  mismo commit; si la mueve sin querer, el error está en el cambio. Cada dato
  nuevo que entre al bot (§5 ter) merece su pregunta ahí.
- **El sello** se sube con `python3 herramientas/sello.py --siguiente`, que
  además regenera todas las páginas. Para regenerar sin volver a subirlo:
  `git checkout index.html` y otra vez `--siguiente`.

## El plan v2, por bloques

| Bloque | Estado |
|---|---|
| 1 · Cambios pequeños (candado del sello, Guaymas, ASF-INE, HR Ratings, aviso de privacidad, dictamen, lista 69-B) | Hecho |
| 2 · Base de datos y bóveda de evidencias | Construido; falta lo del autor (abajo) |
| 3 · Operación | Hecho: revisión automática, preguntas de prueba, este ESTADO.md y revisión semanal. Falta una decisión: los PDF pesados (abajo) |
| 4 · Regla de prensa, personas privadas y réplica; mapa ambiental con gasto público aparte | Hecho (AGENTS.md §2 bis). Falta lo del autor: el responsable de las réplicas (abajo) |
| 5 · Legibilidad en celular (`docs/ux/PLAN.md`), lanzamiento (`docs/LANZAMIENTO.md`) y fusión a `main` | Por empezar; `main` solo avanza con permiso del autor |

## Lo último que entró

- **29-10-2026.** **Códigos de acceso para la versión de prueba**, como los del Nintendo Switch: ocho casillas (XXXX-XXXX) en `canjea-tu-codigo.html` y el panel del autor en `administracion-codigos.html` (genera códigos con su duración, de 1 día a 1 año o en días, sus usos y su fecha límite; los revoca y los baja en CSV). El tiempo corre desde el canje y se suma si se canjea otro. Base: `20261030000001_codigos.sql` y la función `codigo`; páginas: `herramientas/acceso.py`. **El candado está encendido desde el 30-10-2026** (`CANDADO = True` de `acceso.py`, pedido del autor: «enciende el código»); en localhost no pide código. Es un candado del navegador: para cerrar de verdad hace falta Vercel.
  Ese mismo día, la entrada se rehízo a pedido del autor: `canjea-tu-codigo.html` tiene su molde propio (`entrada_html()` de `acceso.py`), con la foto realista de la ciudad bajo la lluvia (`cabecera-lluvia.webp`) a un lado y, al otro, «¿Quieres saber en qué se gasta el dinero de todos?», «Descubre el gasto público», las tres notas «Al momento» más nuevas, las ocho casillas («Ingresa con tu código promocional») y **«¿No tienes código? Obtén uno»**, que deja el correo en `solicitudes_codigo` (migración `20261030000002`) para que el autor asigne un código desde su panel y lo mande desde su propio correo. Al canjear se abre **«¡Felicidades! Cuentas con…»** (1 día, 3 días, 1 año o **ilimitado**: 100 años exactos). Cuando se acaba el tiempo, la entrada dice que terminó y abre «Obtén uno». El administrador entra con su correo al panel y «Abrir la plataforma como administrador» le da a su navegador un pase ilimitado. Adentro, la cabecera sigue con la acuarela.
- **29-10-2026, sello 20261029l.** **El modo Reportero ahora se llama Periodista.** Pedido del autor: «cambiaremos el modo a modo periodista en vez de reportero». Cambian el nombre, la clave del modo (`periodista` en `MODOS` de `asistente.py`, `modos.py`, `asistente.js` y el banco de pruebas), «📰 La nota del Periodista» y `AuditorBot.periodista`. Las ligas viejas `?modo=reportero` y el `av-modo` guardado en el navegador se traducen solos. Las citas textuales del autor («el reportero se convierte…») se quedan como las dijo; las clases CSS `pa-reportero` no cambian.
- **29-10-2026, sello 20261029k.** **Bandeja 2: Jalisco y el gasto federal.** El autor pasó la publicación de @radioformulajalisco (análisis del PRI Jalisco). Nota «Al momento» `jalisco-gasto-federal-pef-2027`: Jalisco aporta el 7.5 % del PIB (INEGI, PIBE 2024, p. 1, consta) y recibe el 6.1 % de los Ramos 28 + 33 de 2026 con el 6.7 % de la población: $16,408 por habitante, lugar 30 de 32 (derivado de `estados`, más abajo que el «24» que circula, matiz). El punto ciego: en participaciones queda en el lugar 12 y en aportaciones, que se reparten por necesidad, en el 29. El agua: la Presidenta anunció el 21-10 que la Federación pone «todo», 12 a 13 mil millones (anuncio, no presupuesto). Pendientes, por falta de la plataforma: el lugar 24 (PPEF 2027 por entidad), el 83 % de caída de la inversión (Cuenta Pública por entidad) y los recortes en carreteras. Personaje nuevo: Laura Haro. «millones», «pesos», «dinero» y «mucho» ya no cuentan para mandar un cotejo a una columna. 245 preguntas.
- **29-10-2026, sello 20261029j.** **Primera pieza de la bandeja: el Senado y la Ley de Ingresos 2027.** El autor pasó la publicación de @elfinanciero_mx. Nota «Al momento» `senado-ley-de-ingresos-2027` (`integrar_al_momento.py`): el pleno la aprobó 75 a 34, en sus términos (Canal del Congreso, 28-10-2026); de los $10,636,488.1 millones, $9,156,528.9 son ingresos presupuestarios y $1,479,959.2 son financiamiento (derivado, leído de `paquete_2027`), así que no es «recaudación»; impuestos $6,263,886.8 millones; la cuota del turista sube 17.8 % a $1,158 (Diputados, 14-10-2026; los 983 de hoy, derivados). Pendientes, por falta de la plataforma: el voto del Senado sobre la Ley de Derechos y la excepción del ISR para automotrices y gasolineras (el portal del Senado no abre desde la sesión). La columna de Diputados ya dice que el Senado votó. 242 preguntas.
- **29-10-2026, sello 20261029i.** **Noticias en tres tarjetas.** La pestaña `noticias-relevantes.html` es ahora un índice con tres tarjetas, cada una con su página: **Auditavisión Noticias** (`noticias-auditavision.html`: portada, noticias, opinión y réplica; las columnas viven aquí), **Verifica una noticia** (`noticias-verifica.html`: verificador, mesa de redacción y método, con «Propón una nota») y **Seguimiento: el caso no se olvida** (`noticias-seguimiento.html`: casos abiertos, tus seguimientos y la agenda del erario). Cada página trae el cabezal del diario y una barra con sus secciones y las otras dos. Los enlaces viejos (`#col-<id>`, `#verifica`, `#seguir`…) se mandan solos a la página nueva; los de la plataforma, el chat y el banco de pruebas ya apuntan directo. Las tres están en el modo Reportero. 172 páginas de la Enciclopedia vinculadas.
- **29-10-2026, sello 20261029h.** **«¿Sabías esto?» entre las preguntas de ejemplo.** Pedido del autor («para dejar como libre un poquito el chat»): el saludo del Reportero ya no lleva los dos bloques; las tres columnas verificadas más nuevas («🆕 ¿Sabías esto?») y los tres casos para retomar («🗂️ Para retomar») se reparten en «Prueba con:», dos por tanda, con su seña, y quitan la pregunta de ejemplo que ya llevaba a la misma columna (`_ejemplos()` de `asistente.py`). El título de una columna, tal cual, abre esa columna (`tituloColumna()` de `asistente.js`). 239 preguntas.
- **29-10-2026, sello 20261029f.** **El Reportero, reportero virtual.** Saludo con «🆕 ¿Sabías esto?» (las tres columnas verificadas más nuevas) y «🗂️ Casos para retomar» (los de Personajes y Hechos que llevan más tiempo sin moverse; vuelven al frente al cambiar su `actualizado`). Nueva página **Periodismo en riesgo** (`periodismo-en-riesgo.html`, cuelga de Noticias, `herramientas/periodistas.py`) con el informe del Mecanismo de Protección al 31-05-2026: 690 periodistas protegidos, 759 agresiones registradas y 40.7 % de los probables agresores son servidores públicos (derivado); homicidios y sentencias de la FEADLE, pendientes (su archivo no abre desde esta sesión). Cuatro aplicaciones nuevas en la franja: Contratos públicos, Empresas contratistas, obras sin cifras publicadas y Periodismo en riesgo. Nepotismo: la nota trae los puntos ciegos y la regla del apellido. La nota pone primero lo que falta en la página misma de la respuesta, y una columna entra solo si habla del tema. La bandeja del autor, en `docs/VERIFICAMOS.md`. 233 preguntas.
- **29-10-2026, sello 20261029e.** **El modo Reportero tiene su objetivo y su forma de contestar** (entrega b, primer modo). Objetivo del autor: «el reportero se convierte como en un chismoso… aquel que te transmite información privilegiada»; aquí, privilegiada quiere decir **enterrada en documentos públicos que casi nadie lee**, nunca un rumor. Bajo la misma respuesta, «📰 La nota del Reportero» (`reportero()` de `asistente.js`): 🕵️ lo que casi nadie te cuenta (la investigación de Auditoría en imágenes, lo que la ASF dejó por aclarar, lo que falta publicar y a quién le toca, o «Aún no lo integramos» si la falta es nuestra, y los «matiz» y «no consta» de lo que circula), 📢 el ruido con su cotejo, 🗓️ lo que sigue y las búsquedas en internet «sin verificar». Nuevo saludo y lema; tres preguntas de ejemplo; el banco de pruebas acepta `modo` (229 preguntas).
- **29-10-2026, sello 20261029d.** **La Enciclopedia es la base de datos física del Auditor, en sus cuatro modos.** Cada una de sus 168 páginas tiene modo (`herramientas/modos.py`: Inspector 121, Ciudadano 23, Ambientalista 21, Reportero 3), lleva en su cabecera «Pregúntale al Auditor · Modo X» (abre el chat en ese modo con la pregunta hecha) y el chat la ofrece al pie de cada respuesta en «📚 En la Enciclopedia», primero las del modo elegido. `herramientas/cobertura_auditor.py` lo comprueba en cada revisión y escribe `docs/COBERTURA-AUDITOR.md`: antes, 39 páginas no salían al preguntar por su nombre; ahora, 168 de 168.
- **29-10-2026, sello 20261029c.** **El Auditor trabaja en cuatro modos** (entrega a): Inspector, Reportero, Ciudadano (con el que abre) y Ambientalista, en el botón de la cabecera del chat, cada uno con su saludo, sus aplicaciones y sus preguntas de ejemplo (`MODOS` de `asistente.py`, `?modo=`). **Las herramientas se mudaron a la Enciclopedia**: quinta tarjeta de Números, «Herramientas del Auditor» (`numeros-herramientas-del-auditor.html`); sus páginas cuelgan de ahí y `herramientas.html` redirige. Faltan (b) la forma de responder de cada modo y (c) su dictamen.
- **28-10-2026, sello 20261028p.** **Noticias se rehízo como periódico** («Auditavisión Noticias»): nueve secciones con barra, la noticia separada de la opinión (la Columna del Erario), Seguimiento de casos, Mesa de redacción (titulares sin verificar; `recolectar_noticias.py` y el flujo «Mesa de redacción», que corre sola cada día desde que el autor lo activó el 28-10-2026), Agenda del erario (plazos de la LFPRH, la LFRCF y la Constitución) y el método de siete pasos. El verificador dice quién aparece en la nota y lleva a su ficha del Auditor de entes. Ver AGENTS.md §5 bis.
- **28-10-2026, sello 20261028o.** **Nepotismo y parentesco es la séptima aplicación del Modo Inspector** (`herramienta-inspector-nepotismo.html`, la arma `nepotismo.construir()`); la página de Aprende redirige ahí y la tarjeta de Aprende lleva a la aplicación. **En pausa, por decisión del autor:** las leyes de responsabilidades de los 32 estados y lo que obligan a los municipios (nepotismo, declaraciones, gastos, obligaciones y adjudicaciones), hasta tener acceso a todos los portales; lo ya cotejado está en CONTEXT.md.
- **28-10-2026, sello 20261028n.** **Noticias reúne todo lo de noticias**: la aplicación Contrasta una nota dentro de la pestaña (`#verifica`, la misma de Herramientas y del chat), «Propón una nota» (`#propon`) y «Réplica y postura» (`#replica`, con el campo nuevo `postura` de `columnas.js`). **Nepotismo y cargos públicos** (`nepotismo-y-cargos-publicos.html`, tarjeta de Aprende, `herramientas/nepotismo.py`): calculadora de parentesco, árbol de grados, las tres leyes (LGRA 63 Bis, CPF 220 y nepotismo electoral desde 2030), cómo se investiga un cargo y los puntos ciegos; el chat contesta «¿mi cuñado puede trabajar en mi oficina?». Cinco términos al glosario. 218 preguntas de prueba.
- **28-10-2026, sello 20261028m.** **Noticias es la cuarta pestaña** del menú (`MENU` de `apartados.py` e `index.html`), y estrena **«Al momento»**: notas breves verificadas con fecha, la nota de prensa de origen, el cotejo, la cuenta con números redondos, nuestros datos, el glosario y las búsquedas armadas en la red («sin verificar»). Las escribe `herramientas/integrar_al_momento.py`. Primera: el IMSS acota la Modalidad 40 (DOF 21-10-2026), con tres pendientes en el Registro. Glosario: «Continuación Voluntaria (Modalidad 40)». Personaje: Zoé Robledo. 207 preguntas de prueba.
- **28-10-2026, sello 20261028l.** Preguntas de ejemplo del chat (`EJEMPLOS` de `asistente.py`): 9 nuevas sobre lo verificado y las auditorías de gestión (Seguro Popular, acceso a la salud, ISSSTESON, consejerías del INE, consultas del IMSS, asuntos del Poder Judicial, denuncias de la PROFEPA). La del Seguro Popular entra en la primera tanda; las demás, una por tanda. 201 preguntas de prueba.
- **28-10-2026, sello 20261028k.** Auditoría en imágenes llega a 23 investigaciones: **Seguro Popular** (`auditoria-seguro-popular.html`, diapositiva 23), a pedido del autor («resaltar el éxito que fue»). El logro con sus números (5.3 → 53.5 millones de afiliados, ASF CP 2018), la línea del tiempo de la gente sin acceso a la salud 2016–2024 (INEGI, escena nueva `serie` de `auditoria-imagen.js`) y, como contrapeso, los $928.7 mdp que la ASF le observó en 2018 por tipo de irregularidad. Lo escribe `herramientas/integrar_seguro_popular.py`; el chat la abre con «la auditoría del Seguro Popular» o «qué le observó la ASF».
- **28-10-2026, sello 20261028j.** Verificamos: «Con el Seguro Popular se atendieron más de 51 millones; ahorita nada» (columna `seguro-popular-51-millones`, audio de un reel). Matiz: el padrón llegó a 53.5 millones de afiliados (ASF, Cuenta Pública 2018), pero afiliado no es atendido. Consta el retroceso: sin acceso a servicios de salud, 20.1 millones en 2018, 50.4 en 2022 y 44.5 en 2024 (INEGI, comunicado 118/25). Pendiente: cuántos afiliados se atendieron de verdad (informes de resultados del SPSS, falta de la plataforma).
- **28-10-2026, sello 20261028i.** La columna del ISSSTESON se corrige: lo que circula es el audio de un reel de Instagram, no una nota de prensa. VERIFICAMOS.md suma el paso 0: se coteja el texto de lo que circula, llegue con liga, captura, video o audio.
- **28-10-2026, sello 20261028h.** Verificamos: «ISSSTESON: oxígeno pagado a un paciente fallecido y pensiones a personas muertas» (columna `isssteson-oxigeno-pensiones-fallecidos`). La nota no viene de la ASF sino del ISAF de Sonora (informe 2025AE0109010005, segundo trimestre de 2025). Consta: $158,400 de oxígeno sin vale, un paciente cobrado siete meses después de morir y que es recurrente (2024: $358,643 y tres pacientes). Matiz: de los $2,990,499 en pensiones, $2,458,447 eran cheques cancelados sin cobrarse y $158,619 ya se recuperaron; faltan $373,438. Empresa nueva: Biosistemas y Seguridad Privada.
- **28-10-2026, sello 20261028e.** Verificamos: «¿Auditarán también las oficinas de los consejeros del INE?» (columna `ine-oic-auditorias-consejerias`), con la pregunta de la prensa en la conferencia de las consejerías del 27-10-2026. La ley sí permite auditar sus oficinas (LGIPE 478, 490 y 492); el Órgano Interno de Control depende en lo administrativo de la presidencia del Consejo (Constitución, art. 41); lo de sueldos, plazas y cuentas no consta; la confianza en los institutos electorales bajó a 48.1 % (ENCIG 2025). Personaje nuevo: el titular del Órgano.
- **28-10-2026, sello 20261028c.** Auditoría de gestión ambiental: tarjeta «Justicia ambiental» en Datos (`herramientas/gestion_ambiental.py`), con los Informes de Actividades 2022 a 2024 de la PROFEPA y la LGEEPA. Denuncias que recibe contra las que resuelve (de las que investigó en 2024 concluyó 19.9 % en el año, derivado), la ley sin plazo para concluirlas, el rezago de procedimientos (11,179 de 2019 a 2023), multas impuestas sin dato de cobro, denuncias ante la FGR y el cotejo del informe contra sus tablas. Cinco pendientes nuevos; el anuario del ISSSTE sigue sin responder.
- **27-10-2026, sello 20261027t.** Auditoría de gestión de salud: tarjeta «Salud pública» en Datos (`herramientas/gestion_salud.py`). El IMSS con su Memoria Estadística 2025: lo que gasta el seguro de enfermedad, consultas, cirugías, médicos y camas, y el cotejo de su boletín de resultados (las cirugías no cuadran). Seguro Popular → INSABI → IMSS-Bienestar cotejado con la Ley General de Salud. ISSSTE (servicios) e IMSS-Bienestar quedan pendientes. Sigue ambiente cuando el autor lo pida.
- **27-10-2026, sello 20261027r.** Auditoría de gestión, piloto del Poder Judicial: página `datos-judicial-gestion.html` («Lo que cuesta y lo que resuelve») y su chat, con el censo del INEGI CNIJF-E 2025 (`herramientas/gestion_judicial.py`): asuntos que entran y salen, dinero por asunto resuelto, rezago penal por estado y cuánto tardan la Corte y el Tribunal Electoral. Cuánto tarda un juzgado o una audiencia y el rezago civil quedan pendientes. Salud y ambiente siguen con el mismo molde cuando el autor lo pida.
- **27-10-2026, sello 20261027o.** Verificamos: «¿Investigarán a Lorenzo Córdova?»
  (publicación de politicomx), columna `ine-contratos-desde-cordova`. Consta el pedido
  de auditoría (versión estenográfica del 26-10); lo de Córdova y «desde cuándo» queda
  pendiente hasta que Presidencia publique la del 27-10; lo de la UIF es de un solo
  proveedor, en 2023, y el amparo no tiene documento. Córdova entra al chat, y un
  «¿es cierto que…?» se coteja antes de buscar en ComprasMX.
- **27-10-2026, sello 20261027m.** Imágenes, paso 5: las fotos de la Calculadora
  Cívica, Costo Ambiental, el Modo Inspector y el foróptero del Auditor Virtual se
  cambiaron por ilustraciones propias (SVG), con la misma idea de cada foto. Quedan
  el encabezado de la portada.
- **27-10-2026.** Las 22 ilustraciones de las investigaciones (`showcase_*.jpg`,
  generadas con IA en Antigravity) se quedan como están: decisión del autor.
- **27-10-2026.** Se borraron las 26 capturas de revisión que estaban sueltas en la
  raíz (6.3 MB, públicas en Pages y ya desactualizadas); quedan en el historial, y
  `.gitignore` ignora desde ahora los `*.png` de la raíz.
- **27-10-2026.** Pie de la portada: «Informes Individuales ASF», «Banxico: SIE» y
  «SHCP: Registro Público Único» ya llevan a su página de la Enciclopedia
  (`informes-cuenta-publica.html`, `radar-peso-maquina.html`, `numeros-las-32-entidades.html`).
- **27-10-2026, sello 20261027l.** Imágenes, paso 4: se retiraron las dos fotos de
  la ciudad y el modo de noche del Estado de cuenta cívico; su encabezado y la
  imagen para compartir llevan la franja azul marino.
- **27-10-2026, sello 20261027k.** Imágenes, paso 3: la foto de Inversión y
  Megaobras se cambió por una ilustración propia (SVG, sin derechos de terceros).
- **27-10-2026, sello 20261027j.** Imágenes, paso 2: los estados de cuenta y las
  fichas técnicas ya no llevan foto en el encabezado; va una franja azul marino.
- **27-10-2026, sello 20261027i.** Imágenes, paso 1: el pie de la portada ya
  no lleva foto; son tres franjas horizontales en escala de azul marino.
- **27-10-2026, sello 20261027h.** Bloque 4: `derecho-de-replica.html` (Ley de
  réplica cotejada, décimo pilar, recuadro «✉️ Réplica» en las columnas) y el
  mapa ambiental separa 🏛️ gasto público de 🏢 inversión privada. Al revisarlo
  salieron cifras sin documento en el mapa (Guaymas $3,977.5 mdp; montos de la
  ASF que no cuadraban con los expedientes): ya salen de los expedientes.
- **27-10-2026, sello 20261027g.** Bloque 3: `revision.py`, `prueba_auditor.py`
  con 149 preguntas, `semanal.py` y los dos flujos de GitHub. Las preguntas
  destaparon siete respuestas mal dirigidas, ya corregidas (detalle en
  CONTEXT.md, «Preguntas de prueba del Auditor»).
- **27-10-2026, sello 20261027f.** Informe semestral de la ASF
  (`informes-semestral-asf.html`, `herramientas/informe_semestral.py`).
- **27-10-2026.** Informe especial «Documentar para sancionar»
  (`informes-documentar-para-sancionar.html`).

## Lo que espera fecha

- **Informe semestral de la ASF, corte al 30-09-2026:** la ley le da hasta el
  1 de noviembre de 2026. En su dirección ya hay un PDF de una página que dice
  «Próximamente» (155 KB): no es el informe. La revisión semanal avisa cuando
  aparezca el de verdad; entonces se cambian `DOC` y `ANT` de
  `informe_semestral.py`.

## Lo que solo puede hacer el autor

- Crear el proyecto de Supabase y poner las llaves **solo en su panel**
  (Edge Functions → Secrets), nunca en el repositorio ni en el chat.
- Llenar `FUNCIONES`, `TURNSTILE_SITIO` y `AVISO_CONSERVACION` en
  `herramientas/apartados.py`, y dar el nombre y el domicilio del responsable
  para el aviso de privacidad.
- **Designar al responsable de las réplicas** (Ley de réplica, art. 7: nombre
  completo, domicilio, código postal, entidad, correo y teléfono, siempre a la
  vista). Puede ser la misma persona del aviso de privacidad. Mientras no esté,
  la plataforma no puede recibir un escrito de réplica (`replica-responsable`).
- Sacar los tokens de Banxico y del INEGI.
- **Códigos de acceso:** la base y la función `codigo` están en su proyecto (flujo «Sube la base de datos», 29-10-2026) y el autor ya está en `administradores` y entra al panel (30-10-2026). El candado se encendió el 30-10-2026, con la plataforma ya en `auditavision.com.mx`. El mismo día: `main` se igualó con la rama (permiso del autor), Banxico quedó conectado en vivo (función `portales`, probada en el flujo), la bóveda corre cada miércoles y los formularios guardan lo enviado 12 meses (`FUNCIONES` encendido). Falta: la llave del INEGI probada, el antispam Turnstile y que el chat use `portales`.
- Correr `python3 herramientas/boveda.py` desde su computadora: varios
  portales de gobierno no abren desde las sesiones en la nube.
- **Decidir qué hacer con los PDF pesados.** Hay 90 PDF en el repositorio
  (183 MB, casi todos en `investigaciones/`; el historial pesa 355 MB). Ninguna
  página los enlaza: son los documentos que se cotejaron. Sacarlos del todo
  exige reescribir el historial, y eso rompe las copias de quien ya clonó.
  Alternativas: dejarlos, moverlos a Git LFS de aquí en adelante o guardarlos
  fuera (la bóveda ya guarda la huella SHA-256 de cada documento cotejado).
