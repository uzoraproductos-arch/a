// buscar-web: lo que hay en internet sobre un personaje (pedido del autor,
// 24-10-2026). El chat ya ofrece las búsquedas armadas en portales oficiales
// y en las noticias; esta función, cuando el autor ponga la llave, las hace
// por el lector y le devuelve los enlaces en la misma respuesta.
//
// Tres candados (AGENTS.md §2 y §5 ter):
//   1. Solo se busca en una lista cerrada de sitios: los oficiales y una lista
//      editorial de prensa (_comun/web.ts). Nada de foros, redes ni blogs.
//   2. Se devuelven SOLO los enlaces del buscador (título, dirección, sitio,
//      tipo y fecha). Lo que el modelo escriba se tira: la plataforma no
//      publica un texto redactado por IA sobre una persona.
//   3. Cada búsqueda queda en busquedas_web, pública, con el modelo, los
//      tokens y la fecha; la misma búsqueda no se repite en un día.
// La llave de Anthropic vive en los secretos de Supabase (ANTHROPIC_API_KEY).
import Anthropic from "npm:@anthropic-ai/sdk@0.132.0";
import { claveDe, enlaces, nombreValido, OFICIALES, PRENSA } from "../_comun/web.ts";
import { base, dentroDelLimite, huellaIp, leeJson, responde, sirve } from "../_comun/comun.ts";

const MODELO = Deno.env.get("MODELO_IA") ?? "claude-opus-5-5";
const AVISO = "Enlaces encontrados en internet, sin verificar por Auditavisión: lo oficial va primero y la prensa al final. " +
  "Una nota de prensa no es un documento oficial, y un proceso no es una condena.";

const INSTRUCCIONES = `Buscas en internet documentos sobre una persona de la vida pública de México, para una plataforma ciudadana de fiscalización del gasto público.
- Haz de una a tres búsquedas: primero documentos oficiales (sentencias, comunicados, el Diario Oficial, auditorías de la ASF, el INE, el Congreso) y después notas de prensa.
- Busca a esa persona y no a otra con un nombre parecido.
- No escribas ningún resumen ni opinión: la plataforma solo publica los enlaces que encuentre el buscador. Al terminar, contesta solo «listo».`;

sirve(async (req) => {
  const j = await leeJson(req, 2000);
  const nombre = j && nombreValido(j.nombre);
  if (!nombre) return responde(req, { ok: false, error: "Escribe el nombre de la persona: de dos a seis palabras, sin cifras." }, 400);
  if (!Deno.env.get("ANTHROPIC_API_KEY")) return responde(req, { ok: false, pendiente: true, error: "La búsqueda en internet aún no está configurada." }, 503);

  const db = base(), clave = claveDe(nombre);
  // ¿Ya se buscó hoy? Se devuelve la copia con su fecha.
  const { data: copia } = await db.from("busquedas_web").select("nombre, enlaces, obtenido")
    .eq("clave", clave).gt("vence", new Date().toISOString())
    .order("obtenido", { ascending: false }).limit(1).maybeSingle();
  if (copia) return responde(req, { ok: true, nombre: copia.nombre, enlaces: copia.enlaces, consultado: copia.obtenido, copia: true, aviso: AVISO });

  // Tope de costo: 5 búsquedas por minuto y 30 por día por persona.
  const huella = await huellaIp(req);
  if (!(await dentroDelLimite(db, huella, "web", 5, 60)) || !(await dentroDelLimite(db, huella, "web-dia", 30, 86400))) {
    return responde(req, { ok: false, error: "Llegaste al límite de búsquedas por ahora; las búsquedas armadas del chat siguen funcionando." }, 429);
  }

  const cliente = new Anthropic();
  let r;
  try {
    r = await cliente.beta.messages.create({
      model: MODELO,
      max_tokens: 4000,
      betas: ["server-side-fallback-2026-07-01"],
      fallbacks: "default",
      output_config: { effort: "low" },
      system: [{ type: "text", text: INSTRUCCIONES, cache_control: { type: "ephemeral" } }],
      tools: [{ type: "web_search_20260209", name: "web_search", max_uses: 3, allowed_domains: [...OFICIALES, ...PRENSA] }],
      messages: [{ role: "user", content: "<persona>" + nombre + "</persona>" }],
    });
  } catch (e) {
    console.error(e);
    return responde(req, { ok: false, error: "El buscador no respondió. Usa las búsquedas armadas del chat." }, 502);
  }
  if (r.stop_reason === "refusal") return responde(req, { ok: false, rechazo: "negativa_modelo" });

  // Si el turno se pausó (pause_turn), se usa lo que ya trajo el buscador.
  const lista = enlaces(r.content as { type: string; content?: unknown }[]);
  const usos = (r.usage as { server_tool_use?: { web_search_requests?: number } }).server_tool_use?.web_search_requests ?? null;
  const ahora = new Date();
  const { error } = await db.from("busquedas_web").insert({
    clave, nombre, enlaces: lista, modelo: r.model, tokens_in: r.usage.input_tokens, tokens_out: r.usage.output_tokens,
    busquedas: usos, obtenido: ahora.toISOString(), vence: new Date(ahora.getTime() + 86400_000).toISOString(),
  });
  if (error) console.error(error);
  return responde(req, { ok: true, nombre, enlaces: lista, consultado: ahora.toISOString(), copia: false, aviso: AVISO });
});
