# La base de datos de Auditavisión

Pedido del autor, 24-10-2026: «se necesita construir la base de datos» para
el pendiente 3 del Auditor Virtual (portales externos y capa de inteligencia
artificial). Es la fase 3 de [LANZAMIENTO.md](LANZAMIENTO.md), ya construida y
probada. Falta solo lo que toca al autor: crear la cuenta y poner las llaves.

## Qué guarda y qué no

| Sí guarda | No guarda |
|---|---|
| Lo que escribe la gente: solicitudes, erratas, temas, reportes, el foro | **Ninguna cifra fiscal.** Las cifras siguen en los archivos que genera Python, con su fuente y su huella |
| «Lo que aún no sé»: las preguntas que el Auditor no supo contestar | Direcciones IP en claro: solo su huella con sal, para el límite por minuto |
| La copia de lo que se consulta en Banxico e INEGI, con dirección, fecha y huella SHA-256 | Llaves: viven en los secretos de Supabase, nunca en el repositorio ni en la página |
| La bitácora de la IA: fichas que recibió, lo que contestó, el modelo, los tokens y si pasó la verificación | |
| Perfiles, alertas, suscripciones y donaciones (fases 3 a 5) | |

## Cómo está hecha

```
   Página (navegador, llave pública)
        │  POST
        ▼
   Funciones de Supabase (llave de servicio, secreta)
   ├─ recibir-formulario ──▶ envios          (antispam + 5 envíos / 10 min)
   ├─ pregunta-bot ────────▶ preguntas_bot   («Lo que aún no sé»)
   ├─ portales ────────────▶ portales_cache  (Banxico SIE; INEGI por verificar)
   └─ auditor-ia ──────────▶ consultas_ia    (Claude, con cuatro candados)
                                  │
                    lee las fichas del sitio publicado
                    (assets/auditor/js/asistente-base.js)
```

| Archivo | Qué es |
|---|---|
| `supabase/migrations/20261024000001_auditavision.sql` | Las 14 tablas y vistas, con seguridad por renglón en todas |
| `supabase/functions/*/index.ts` | Las cuatro funciones (Deno) y lo que comparten (`_comun/`) |
| `supabase/pruebas/permisos.sql` | 26 pruebas de permisos: qué ve y qué escribe el público, una persona con cuenta y la administración |
| `supabase/pruebas/cotejo_test.ts` | Pruebas del candado de cifras de la IA |
| `herramientas/prueba_base_datos.py` | Corre la migración y las pruebas en un PostgreSQL local, sin cuenta ni red |

## Los cuatro candados de la IA (AGENTS.md §5 ter)

1. **No recibe texto ajeno.** La página manda la pregunta y los números de
   las fichas que encontró su buscador; la función lee esas fichas del sitio
   publicado. Nadie le puede colar una cifra.
2. **Solo ve esas fichas**, con la orden de no calcular, no redondear y no
   salir de ellas.
3. **Cada cifra se coteja.** Si la respuesta trae una cifra que no está en
   las fichas, se tira y el Auditor contesta como hoy, sin IA.
4. **Todo queda anotado** en `consultas_ia`, para auditar a la IA como a
   cualquier otra fuente.

Modelo: `claude-opus-5-5` (se cambia con el secreto `MODELO_IA`), esfuerzo
bajo, salida en JSON con esquema, y si el modelo se niega, la API reintenta
con otro (`fallbacks: "default"`). Tope: 10 preguntas por minuto y 100 por
día por persona.

## Lo que le toca al autor (decisiones 0.1 a 0.5 de LANZAMIENTO.md)

| Paso | Qué | Costo |
|---|---|---|
| 1 | Crear el proyecto en supabase.com (región más cercana a México) | Gratis para probar; Pro, US$25 al mes, para producción |
| 2 | Pasarle al agente la dirección del proyecto. **Nunca la llave de servicio por chat**: va directo en Supabase → Edge Functions → Secrets | — |
| 3 | Secretos: `SITIO`, `SAL_IP` (cualquier frase larga), `TURNSTILE_SECRET` (antispam de Cloudflare, gratis) | — |
| 4 | `BANXICO_TOKEN`: gratis en banxico.org.mx/SieAPIRest/service/v1/token | Gratis |
| 5 | `INEGI_TOKEN`: gratis en inegi.org.mx (API de indicadores) | Gratis |
| 6 | `ANTHROPIC_API_KEY`, solo si quieres la capa de IA | Por pregunta, según el modelo |

Con eso, el agente corre `supabase db push` y `supabase functions deploy`, y
conecta los botones «Enviar» y «Lo que aún no sé» de la página.

## Pendiente, y por qué

- **INEGI** sin verificar: desde el entorno de desarrollo su portal no
  respondió. La dirección sigue la documentación de su API; se prueba al
  poner la llave.
- **Transparencia Presupuestaria y el DOF** no están en `portales`: publican
  archivos de datos abiertos, no una API de consulta. Entran por la fase 4
  (GitHub Actions semanal que descarga, regenera y abre un PR).
- **La página todavía no llama a las funciones**: no hay proyecto ni
  dirección. Los formularios siguen armando el texto y «Lo que aún no sé»
  sigue en el navegador hasta que se configure.
- **La IA no se probó contra la API real**: falta la llave. El candado de
  cifras sí está probado sin red.

Para comprobar la base en cualquier momento:

```bash
python3 herramientas/prueba_base_datos.py
deno test supabase/pruebas/cotejo_test.ts
```
