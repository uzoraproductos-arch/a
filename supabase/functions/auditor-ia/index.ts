// auditor-ia: la fase 3 del Auditor (una capa de inteligencia artificial que
// redacte y entienda preguntas libres). AGENTS.md §5 ter: «solo redacta con lo
// que le entregan las fichas; nunca pone una cifra que no venga de un
// documento». Así se cumple aquí, en cuatro candados:
//   1. La página manda la pregunta y los NÚMEROS de las fichas que su propio
//      buscador encontró; las fichas se leen aquí, del archivo publicado del
//      sitio (asistente-base.js), así que nadie puede colarle texto propio.
//   2. El modelo recibe solo esas fichas y la orden de no salir de ellas.
//   3. Cada cifra de la respuesta se coteja contra las cifras de las fichas:
//      si una no aparece, la respuesta se tira y la página contesta como
//      hoy, sin IA (rechazo «cifra_no_respaldada»).
//   4. Cada consulta queda en consultas_ia (fichas, respuesta, modelo,
//      tokens y si pasó la verificación), para auditar a la IA.
// La llave de Anthropic vive en los secretos de Supabase (ANTHROPIC_API_KEY),
// nunca en la página.
import Anthropic from "npm:@anthropic-ai/sdk@0.132.0";
import { sinDocumento } from "../_comun/cotejo.ts";
import { base, dentroDelLimite, huellaIp, leeJson, responde, sello, SITIO, sirve, texto } from "../_comun/comun.ts";

const MODELO = Deno.env.get("MODELO_IA") ?? "claude-opus-5-5";
const MAX_FICHAS = 8;

type Cifra = { v: string; etq: string; e: string; op?: string };
type Fuente = { tx: string; url?: string };
type Ficha = { t: string; tit: string; txt?: string; ci?: Cifra[]; fu?: Fuente[]; ir?: [string, string] };

// La base publicada, por versión (se queda en memoria mientras viva la función).
const bases = new Map<string, Ficha[]>();
async function fichasDe(version: string): Promise<Ficha[]> {
  const ya = bases.get(version);
  if (ya) return ya;
  const r = await fetch(SITIO + "assets/auditor/js/asistente-base.js?v=" + version, { signal: AbortSignal.timeout(20000) });
  if (!r.ok) throw new Error("no se pudo leer la base publicada: " + r.status);
  const s = await r.text();
  const i = s.indexOf("window.AUDITOR_BASE = "), j = s.lastIndexOf("};");
  if (i < 0 || j < i) throw new Error("la base publicada cambió de formato");
  const b = JSON.parse(s.slice(i + "window.AUDITOR_BASE = ".length, j + 1)) as { fichas: Ficha[] };
  bases.set(version, b.fichas);
  return b.fichas;
}

function documento(n: number, f: Ficha): string {
  const ci = (f.ci ?? []).map((c) => "- " + c.v + " · " + c.etq + " [" + c.e + "]" + (c.op ? " (operación: " + c.op + ")" : "")).join("\n");
  const fu = (f.fu ?? []).map((x) => "- " + x.tx + (x.url ? " <" + x.url + ">" : "")).join("\n");
  return "<ficha numero=\"" + n + "\">\nTítulo: " + f.tit + "\n" + (f.txt ? "Texto: " + f.txt + "\n" : "") +
    (ci ? "Cifras:\n" + ci + "\n" : "") + (fu ? "Fuentes:\n" + fu + "\n" : "") + "</ficha>";
}

const INSTRUCCIONES = `Eres la redacción del Auditor Virtual de Auditavisión, una plataforma ciudadana de fiscalización del gasto público en México.
Contestas la pregunta de una persona usando SOLO las fichas que se te entregan. Reglas, sin excepción:
- Toda cifra que escribas debe aparecer tal cual en alguna ficha. No calcules, no redondees, no estimes, no conviertas unidades. Si la pregunta pide una cuenta que no está hecha en las fichas, di que la plataforma no la tiene.
- Si las fichas no contestan la pregunta, pon sin_respuesta en true y explica en una frase qué sí tienen.
- Respeta el estado de cada cifra: si una ficha marca algo como pendiente, dilo como pendiente y no lo afirmes.
- Escribe en español de México, de tú, claro, corto y cálido: dos o tres párrafos breves como máximo. Nada de listas largas.
- No opines sobre partidos ni personas: describe lo que dicen los documentos.
- En fichas_usadas pon los números de las fichas de las que tomaste algo.`;

const ESQUEMA = {
  type: "object",
  properties: {
    respuesta: { type: "string" },
    fichas_usadas: { type: "array", items: { type: "integer" } },
    sin_respuesta: { type: "boolean" },
  },
  required: ["respuesta", "fichas_usadas", "sin_respuesta"],
  additionalProperties: false,
};

sirve(async (req) => {
  const j = await leeJson(req, 6000);
  const pregunta = j && texto(j.pregunta, 2, 600), version = j && sello(j.version);
  const ids = j && Array.isArray(j.fichas) ? [...new Set(j.fichas.filter((x): x is number => Number.isInteger(x) && x >= 0))].slice(0, MAX_FICHAS) : [];
  if (!pregunta || !version || !ids.length) return responde(req, { ok: false, error: "Falta la pregunta, la versión o las fichas." }, 400);
  if (!Deno.env.get("ANTHROPIC_API_KEY")) return responde(req, { ok: false, pendiente: true, error: "La capa de IA aún no está configurada." }, 503);

  const db = base(), huella = await huellaIp(req);
  // Tope de costo: 10 preguntas por minuto y 100 por día por persona.
  if (!(await dentroDelLimite(db, huella, "ia", 10, 60)) || !(await dentroDelLimite(db, huella, "ia-dia", 100, 86400))) {
    return responde(req, { ok: false, error: "Llegaste al límite de preguntas a la IA por ahora; el Auditor sigue contestando sin ella." }, 429);
  }
  const todas = await fichasDe(version);
  const fichas = ids.map((i) => todas[i]).filter(Boolean);
  if (!fichas.length) return responde(req, { ok: false, error: "Esas fichas no existen en esta versión." }, 400);

  const anota = (x: Record<string, unknown>) =>
    db.from("consultas_ia").insert({ pregunta, fichas: ids, version, modelo: MODELO, ip_huella: huella, ...x }).then(({ error }) => error && console.error(error));

  const cliente = new Anthropic();
  let r;
  try {
    r = await cliente.beta.messages.create({
      model: MODELO,
      max_tokens: 4000,
      betas: ["server-side-fallback-2026-07-01"],
      fallbacks: "default",
      output_config: { effort: "low", format: { type: "json_schema", schema: ESQUEMA } },
      system: [{ type: "text", text: INSTRUCCIONES, cache_control: { type: "ephemeral" } }],
      messages: [{
        role: "user",
        content: fichas.map((f, k) => documento(ids[k], f)).join("\n\n") + "\n\n<pregunta>" + pregunta + "</pregunta>",
      }],
    });
  } catch (e) {
    console.error(e);
    await anota({ rechazo: "error_api" });
    return responde(req, { ok: false, rechazo: "error_api" }, 502);
  }
  const uso = { tokens_in: r.usage.input_tokens, tokens_out: r.usage.output_tokens, modelo: r.model };
  if (r.stop_reason === "refusal") {
    await anota({ ...uso, rechazo: "negativa_modelo" });
    return responde(req, { ok: false, rechazo: "negativa_modelo" });
  }
  const tx = r.content.filter((b) => b.type === "text").map((b) => (b as { text: string }).text).join("");
  let sal: { respuesta: string; fichas_usadas: number[]; sin_respuesta: boolean };
  try {
    sal = JSON.parse(tx);
  } catch {
    await anota({ ...uso, rechazo: "formato" });
    return responde(req, { ok: false, rechazo: "formato" });
  }

  // Candado 3: cada cifra de la respuesta tiene que estar en las fichas.
  const sueltas = sinDocumento(sal.respuesta, fichas.map((f, k) => documento(ids[k], f)).join("\n"));
  const usadas = (sal.fichas_usadas ?? []).filter((n) => ids.includes(n));
  const rechazo = sueltas.length ? "cifra_no_respaldada" : (!sal.sin_respuesta && !usadas.length ? "ficha_no_citada" : null);
  await anota({ ...uso, respuesta: sal.respuesta.slice(0, 6000), verificada: !rechazo, rechazo });
  if (rechazo) return responde(req, { ok: false, rechazo, ...(sueltas.length ? { cifras_sin_documento: sueltas.slice(0, 10) } : {}) });
  return responde(req, {
    ok: true,
    respuesta: sal.respuesta,
    sin_respuesta: sal.sin_respuesta,
    fichas_usadas: usadas,
    // Lo que la página muestra debajo: de dónde sale cada cosa y a dónde ir.
    fuentes: usadas.map((n) => ({ ficha: n, tit: todas[n].tit, ir: todas[n].ir ?? null, fu: (todas[n].fu ?? []).slice(0, 3) })),
    modelo: r.model,
    aviso: "Redactado por inteligencia artificial solo con fichas de la plataforma; cada cifra se cotejó contra ellas.",
  });
});
