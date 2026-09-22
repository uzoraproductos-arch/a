# Auditavisión

Sistema cívico de fiscalización y geopolítica del gasto público en México.

**Versión:** 3.3 — Golden Master (estado aprobado)

| | |
|---|---|
| **En vivo** | https://uzoraproductos-arch.github.io/a/ |
| **Rama de trabajo** | `claude/funny-turing-imtm54` — **no `main`** |
| **Antes de tocar código** | [AGENTS.md](AGENTS.md) (reglas) · [CONTEXT.md](CONTEXT.md) (estado) |

```bash
git clone --branch claude/funny-turing-imtm54 https://github.com/uzoraproductos-arch/a.git
```

`main` se quedó atrás y no tiene el trabajo de los últimos meses: clonarla es
empezar sin lo hecho.

## Qué es

Plataforma web de consulta ciudadana sobre el ejercicio del gasto público
federal y federalizado, organizada en nueve módulos:

| Módulo | Contenido |
|---|---|
| Presupuesto | Desglose del PEF y gasto federalizado por entidad |
| Políticos | Fichas de servidores públicos |
| Judicial | Resoluciones SCJN y marco constitucional |
| Legislativo | Iniciativas y Gaceta Parlamentaria |
| Acción financiera | Simuladores y comparativos de ahorro |
| Verificador | Validación de cifras contra fuente oficial |
| Comunidad | Participación ciudadana |
| Referencias | Fuentes: ASF, SHCP, Banxico, DOF, INE |
| FAQ | Preguntas frecuentes |

## Estructura

```
index.html                       Estructura, 9 pestañas y contenido editorial
assets/css/auditavision.css      Estilos maestros
assets/js/mexico-states-geo.js   Geometría vectorial de los 32 estados
assets/js/audit-database.js      Base de datos fiscal
assets/js/municipios-efipem.js   Padrón municipal (INEGI)
assets/js/audit-engine.js        Motor de la aplicación
herramientas/sello.py            Sube el sello de versión de las cinco hojas
AGENTS.md                        Reglas para agentes de IA
CONTEXT.md                       Estado, decisiones y pendientes
```

El orden de carga importa: geometría y datos **antes** que el motor.

Dependencias externas por CDN: Leaflet 1.9.4 (mapas) y Google Fonts
(Playfair Display, Source Serif 4, JetBrains Mono, Inter).

## Contexto y estado

Antes de trabajar en el proyecto, lee [CONTEXT.md](CONTEXT.md): documenta el
estado actual, lo que está pendiente, el criterio editorial y cómo verificar un
cambio. Está escrito para que cualquier persona o asistente de IA pueda retomar
el trabajo sin contexto previo.

[AGENTS.md](AGENTS.md) es la versión corta y dura, la que los agentes de código
—Antigravity, Astra/Codex, Cursor— leen solos al abrir el proyecto.

## Publicación

El sitio se publica en GitHub Pages desde la rama de trabajo. Cada cambio que
toque `assets/` necesita subir el sello de versión, o el navegador del lector
seguirá enseñando la copia anterior:

```bash
python3 herramientas/sello.py            # dice cuál es el sello vigente
python3 herramientas/sello.py 20260923a  # lo sube
```

El sello aparece al pie de la página publicada: así se sabe si lo que se está
viendo es la última versión o una copia guardada por el navegador.

## Ejecución local

Requiere un servidor HTTP: al abrir el archivo directamente con `file://`
el navegador bloquea la carga de los scripts.

```bash
python3 -m http.server 8000
# luego abrir http://localhost:8000
```

## Fuentes de datos

Transparencia Presupuestaria (SHCP), Auditoría Superior de la Federación,
Banco de México, Diario Oficial de la Federación, Cartografía INE y Gaceta
Parlamentaria de la Cámara de Diputados.
