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
- Correr `python3 herramientas/boveda.py` desde su computadora: varios
  portales de gobierno no abren desde las sesiones en la nube.
- **Decidir qué hacer con los PDF pesados.** Hay 90 PDF en el repositorio
  (183 MB, casi todos en `investigaciones/`; el historial pesa 355 MB). Ninguna
  página los enlaza: son los documentos que se cotejaron. Sacarlos del todo
  exige reescribir el historial, y eso rompe las copias de quien ya clonó.
  Alternativas: dejarlos, moverlos a Git LFS de aquí en adelante o guardarlos
  fuera (la bóveda ya guarda la huella SHA-256 de cada documento cotejado).
