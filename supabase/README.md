# Base de datos de Auditavisión (Supabase)

Guarda **solo lo que escriben las personas**: formularios y preguntas sin
respuesta del Auditor Virtual. Las cifras fiscales siguen en los archivos
estáticos que genera Python (ver `docs/LANZAMIENTO.md`).

| Archivo | Qué crea |
|---|---|
| `migrations/20261024000001_formularios.sql` | `mensajes` (formularios) y `preguntas_bot` («Lo que aún no sé»), con el público solo escribiendo |

**Cómo se aplica:** Supabase › SQL Editor › New query › pegar el archivo
completo › Run. Cada archivo nuevo se corre una sola vez, en orden.

**Llaves:** la **publicable** (`sb_publishable_…`, antes «anon») puede ir en
la página. La **secreta** (`sb_secret_…`, antes «service_role») nunca va en
el repositorio, ni en un chat, ni en la página.
