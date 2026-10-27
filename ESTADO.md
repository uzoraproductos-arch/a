# ESTADO.md: dónde va Auditavisión

La hoja corta para arrancar. Las reglas están en [AGENTS.md](AGENTS.md) y la
historia completa de cada decisión en [CONTEXT.md](CONTEXT.md), que pasa de
7,000 renglones: aquí va solo lo que necesitas para no repetir trabajo ni
pisar el de otro. **Se actualiza en el mismo commit que cambia lo que dice.**

Última actualización: 27-10-2026 · sello `20261027l` · rama `claude/funny-turing-imtm54`.

## Antes de empezar y antes de empujar

```bash
git pull origin claude/funny-turing-imtm54
python3 herramientas/revision.py --base origin/claude/funny-turing-imtm54   # al terminar
```

`revision.py` corre lo que pide AGENTS.md §5: `node --check`, los CR sueltos,
que el sello haya subido si tocaste `assets/`, el inventario (enlaces rotos y
cotejos sin evidencia), las **157 preguntas de prueba del Auditor**, la guardia
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
