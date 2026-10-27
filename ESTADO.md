# ESTADO.md: dónde va Auditavisión

La hoja corta para arrancar. Las reglas están en [AGENTS.md](AGENTS.md) y la
historia completa de cada decisión en [CONTEXT.md](CONTEXT.md), que pasa de
7,000 renglones: aquí va solo lo que necesitas para no repetir trabajo ni
pisar el de otro. **Se actualiza en el mismo commit que cambia lo que dice.**

Última actualización: 27-10-2026 · sello `20261027g` · rama `claude/funny-turing-imtm54`.

## Antes de empezar y antes de empujar

```bash
git pull origin claude/funny-turing-imtm54
python3 herramientas/revision.py --base origin/claude/funny-turing-imtm54   # al terminar
```

`revision.py` corre lo que pide AGENTS.md §5: `node --check`, los CR sueltos,
que el sello haya subido si tocaste `assets/`, el inventario (enlaces rotos y
cotejos sin evidencia), las **149 preguntas de prueba del Auditor**, la guardia
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
| 4 · Regla de prensa, personas privadas y réplica; mapa ambiental con gasto público aparte | Por empezar |
| 5 · Legibilidad en celular (`docs/ux/PLAN.md`), lanzamiento (`docs/LANZAMIENTO.md`) y fusión a `main` | Por empezar; `main` solo avanza con permiso del autor |

## Lo último que entró

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
- Sacar los tokens de Banxico y del INEGI.
- Correr `python3 herramientas/boveda.py` desde su computadora: varios
  portales de gobierno no abren desde las sesiones en la nube.
- **Decidir qué hacer con los PDF pesados.** Hay 90 PDF en el repositorio
  (183 MB, casi todos en `investigaciones/`; el historial pesa 355 MB). Ninguna
  página los enlaza: son los documentos que se cotejaron. Sacarlos del todo
  exige reescribir el historial, y eso rompe las copias de quien ya clonó.
  Alternativas: dejarlos, moverlos a Git LFS de aquí en adelante o guardarlos
  fuera (la bóveda ya guarda la huella SHA-256 de cada documento cotejado).
