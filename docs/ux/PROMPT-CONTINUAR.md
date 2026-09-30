# Prompt para revisar la fase 1 y seguir con el plan

Copia el bloque de abajo tal cual en Claude Code (o en otro asistente) abierto
en la raíz del repositorio.

```text
Vamos a revisar la fase 1 del rediseño de legibilidad de Auditavisión y a
seguir con el plan. Trabaja paso por paso y pregúntame antes de publicar.

CONTEXTO
- Condición del dueño: la plataforma tiene que ser fácil de leer y de
  entender, empezando por el celular.
- Lee antes de tocar nada: AGENTS.md, CONTEXT.md, docs/ux/PLAN.md y
  docs/ux/fase-0-propuestas.md.
- La fase 1 vive en la rama ux/fase-1. NO está publicada. GitHub Pages publica
  la rama claude/funny-turing-imtm54: lo que llegue ahí es público.

PASO 1 · Traer la rama del preview
  git fetch origin
  git checkout ux/fase-1
  git pull origin ux/fase-1

PASO 2 · Verla funcionando
- Levanta el sitio: python3 -m http.server 8000 y ábrelo en
  http://127.0.0.1:8000 (no uses localhost).
- Revísalo en modo celular (DevTools, 390 px de ancho) y en escritorio:
  1. la portada: lema, tres puertas (Lee, Explora, Consulta), la cifra de la
     ASF y la guía «Cómo se usa»;
  2. el botón «Menú» en celular y las cuatro secciones en escritorio;
  3. un módulo abierto (por ejemplo «Busca tu municipio») con su ruta de
     migas y el botón «‹ Inicio»;
  4. el buscador (prueba «Zapopan») y el tema claro.
- Hazme una lista corta de lo que se ve mal o no se entiende.

PASO 3 · Correr la guardia de legibilidad
  pip install playwright
  python3 -m playwright install chromium
  python3 herramientas/guardia_legibilidad.py --fase 1
Debe decir «Fase 1: cumple». Si no, dime qué vista falla y por qué.

PASO 4 · Decisiones del autor
Recorre conmigo docs/ux/fase-0-propuestas.md, punto por punto, y pregúntame qué
apruebo:
  1. reglas de lectura para AGENTS.md;
  2. escala de letra y fondo para DESIGN.md;
  3. nombres de las secciones y rutas;
  4. el dominio propio.
Aplica solo lo que yo apruebe y márcalo en ese archivo.

PASO 5 · Integrar la fase 1 (solo con mi visto bueno explícito)
- Trae lo último de la rama publicada y mézclalo en ux/fase-1:
    git fetch origin
    git merge origin/claude/funny-turing-imtm54
- Si hay choques en los sellos ?v= de index.html, quédate con una sola versión
  y sube un sello nuevo con: python3 herramientas/sello.py AAAAMMDDx
- Conserva los CRLF (AGENTS.md §4): index.html debe seguir con 56 CR sueltos.
- Vuelve a correr la guardia (--fase 1) y node --check sobre
  assets/auditor/js/audit-engine.js y assets/auditor/js/legibilidad.js.
- Antes de empujar, pregúntame. Luego:
    git checkout claude/funny-turing-imtm54
    git merge ux/fase-1
    git push origin claude/funny-turing-imtm54

PASO 6 · Seguir con la fase 2 (docs/ux/PLAN.md §5)
- Un módulo por entrega, cada uno en su propia rama creada desde la rama
  publicada ya al día. Orden: calculadora → megaobras → asf-2024 →
  municipios → panorama-2026, y después el resto.
- Empieza con la calculadora, en la rama ux/fase-2-calculadora:
  a. Pásala a la plantilla «herramienta» (PLAN §3): un paso visible a la vez,
     el resultado justo después del paso y «¿Cómo se calcula?» desplegable.
  b. Quita los emojis EN EL ARCHIVO (index.html, audit-engine.js y
     audit-database.js) solo de ese módulo. Hoy los retira al mostrarse
     assets/auditor/js/legibilidad.js; eso es una capa de transición.
  c. Cambia «Reiniciar a ceros» y «Contabilizar» por textos sencillos
     («Volver a cero», «Ver la cuenta»). Ajusta también la lógica que
     reconoce esos textos: BOTON_UNICO_REINICIO en audit-engine.js, cerca de
     la línea 28172.
  d. Deja la guardia en verde con --fase 2 para esa vista:
       python3 herramientas/guardia_legibilidad.py --fase 2 --vistas calculadora
  e. Muéstrame cómo quedó y espera mi visto bueno antes de integrarla.
- Si tienes gstack, antes de la fase 2 corre /plan-design-review sobre las
  tres plantillas.

REGLAS (de AGENTS.md y del plan)
- Ninguna cifra inventada. Si no se puede sostener, se marca «pendiente».
- No toques la Enciclopedia (enciclopedia.html, assets/css, assets/js ni
  assets/img).
- Los cambios de lectura van en assets/auditor/css/legibilidad.css, no en la
  hoja principal.
- Nada de emojis en títulos, botones o menús. Nada de font-size en línea.
  Al lector se le habla de tú, con palabras sencillas.
- Si tocas assets/, sube el sello de versión.
- Al terminar cada paso, actualiza «Estado» en docs/ux/PLAN.md y la sección
  «Siguiente tarea» de CONTEXT.md, y dime qué quedó pendiente.
```
