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
// Ronda 42 · el agente lector. Si la página no manda fichas, o pide
// modo: "agente", el modelo busca él mismo con tres herramientas de solo
// lectura (_comun/agente.ts): las fichas publicadas, la base fiscal de
// docs/fiscal-2027/ y sus pendientes. Los cuatro candados siguen iguales: la
// evidencia es lo que devolvieron las herramientas (más las fichas que mandó la
// página, leídas aquí), y una cifra fuera de ella tira la respuesta. Tope: tres
// rondas de herramientas. Al modelo la pregunta le llega sin correo, CURP, RFC
// ni teléfono, y en consultas_ia se guarda además sin montos (_comun/anonimo.ts).
// La llave de Anthropic vive en los secretos de Supabase (ANTHROPIC_API_KEY),
// nunca en la página.
import Anthropic from "npm:@anthropic-ai/sdk@0.132.0";
import { agente, ARCHIVOS_FISCALES, contexto, type Contexto, documento, ESQUEMA_AGENTE, type Ficha, type FuenteFiscal, type Pedido, type Vuelta } from "../_comun/agente.ts";
import { anonimo, sinIdentidad } from "../_comun/anonimo.ts";
import { sinDocumento } from "../_comun/cotejo.ts";
import { base, dentroDelLimite, huellaIp, leeJson, responde, sello, SITIO, sirve, texto } from "../_comun/comun.ts";

const MODELO = Deno.env.get("MODELO_IA") ?? "claude-opus-5-5";
const MAX_FICHAS = 8;
/** Las fichas que la página puede adelantarle al agente: pocas, para cuidar el costo. */
const MAX_SEMILLAS = 4;
/** Pasado este tiempo el agente ya no abre otra ronda: redacta con lo que tiene. */
const PLAZO_AGENTE_MS = 75000;

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

// Lo que lee el agente, por versión: las fichas con su índice y la base fiscal
// publicada. Si un archivo fiscal no se puede leer, el agente sigue con las
// fichas y la herramienta fiscal dice que no está disponible (no se guarda en
// memoria, para volver a intentarlo en la siguiente consulta).
const contextos = new Map<string, Contexto>();
async function contextoDe(version: string): Promise<Contexto> {
  const ya = contextos.get(version);
  if (ya) return ya;
  const fichas = await fichasDe(version);
  const lee = async (n: string) => {
    const r = await fetch(SITIO + "docs/fiscal-2027/" + n + ".json?v=" + version, { signal: AbortSignal.timeout(10000) });
    if (!r.ok) throw new Error("no se pudo leer " + n + ": " + r.status);
    return await r.json();
  };
  try {
    const [fu, ...js] = await Promise.all([lee("fuentes"), ...ARCHIVOS_FISCALES.map(lee)]);
    const archivos = Object.fromEntries(ARCHIVOS_FISCALES.map((n, k) => [n, js[k]]));
    const ctx = contexto(fichas, archivos, ((fu as { fuentes?: Record<string, FuenteFiscal> }).fuentes) ?? {});
    contextos.set(version, ctx);
    return ctx;
  } catch (e) {
    console.error(e);
    return contexto(fichas, null);
  }
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
  const cruda = j && texto(j.pregunta, 2, 600), version = j && sello(j.version);
  const ids = j && Array.isArray(j.fichas) ? [...new Set(j.fichas.filter((x): x is number => Number.isInteger(x) && x >= 0))].slice(0, MAX_FICHAS) : [];
  const esAgente = !!j && (j.modo === "agente" || !ids.length);
  if (!cruda || !version) return responde(req, { ok: false, error: "Falta la pregunta o la versión." }, 400);
  if (!Deno.env.get("ANTHROPIC_API_KEY")) return responde(req, { ok: false, pendiente: true, error: "La capa de IA aún no está configurada." }, 503);
  // Al modelo, la pregunta sin lo que identifica a una persona; al registro, además sin montos.
  const pregunta = sinIdentidad(cruda), registro = anonimo(cruda).slice(0, 600);

  const db = base(), huella = await huellaIp(req);
  // Tope de costo: 10 preguntas por minuto y 100 por día por persona.
  if (!(await dentroDelLimite(db, huella, "ia", 10, 60)) || !(await dentroDelLimite(db, huella, "ia-dia", 100, 86400))) {
    return responde(req, { ok: false, error: "Llegaste al límite de preguntas a la IA por ahora; el Auditor sigue contestando sin ella." }, 429);
  }
  // El agente hace hasta cuatro llamadas al modelo por consulta: su tope es más corto.
  if (esAgente && (!(await dentroDelLimite(db, huella, "ia-agente", 4, 60)) || !(await dentroDelLimite(db, huella, "ia-agente-dia", 40, 86400)))) {
    return responde(req, { ok: false, error: "Llegaste al límite de búsquedas con la IA por ahora; el Auditor sigue contestando sin ella." }, 429);
  }
  const cliente = new Anthropic();
  if (esAgente) return await modoAgente(req, cliente, db, { pregunta, registro, version, ids: ids.slice(0, MAX_SEMILLAS), huella });

  const todas = await fichasDe(version);
  const fichas = ids.map((i) => todas[i]).filter(Boolean);
  if (!fichas.length) return responde(req, { ok: false, error: "Esas fichas no existen en esta versión." }, 400);

  const anota = (x: Record<string, unknown>) =>
    db.from("consultas_ia").insert({ pregunta: registro, fichas: ids, version, modelo: MODELO, ip_huella: huella, ...x }).then(({ error }) => error && console.error(error));

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

// ---------------------------------------------------------------- el agente lector

type Base = ReturnType<typeof base>;

async function modoAgente(
  req: Request, cliente: Anthropic, db: Base,
  o: { pregunta: string; registro: string; version: string; ids: number[]; huella: string },
): Promise<Response> {
  const ctx = await contextoDe(o.version);
  const semillas = o.ids.filter((n) => ctx.fichas[n]).map((n) => ({ numero: n, ficha: ctx.fichas[n] }));
  const crea = (p: Pedido) =>
    cliente.beta.messages.create({
      model: MODELO,
      max_tokens: 4000,
      betas: ["server-side-fallback-2026-07-01"],
      fallbacks: "default",
      output_config: { effort: "low", format: { type: "json_schema", schema: ESQUEMA_AGENTE } },
      system: [{ type: "text", text: p.system, cache_control: { type: "ephemeral" } }],
      // El esquema de las herramientas es JSON llano (agente.ts no depende del SDK).
      tools: p.tools as unknown as Anthropic.Beta.BetaToolUnion[],
      tool_choice: p.tool_choice,
      // deno-lint-ignore no-explicit-any
      messages: p.messages as any,
    }, { timeout: 45000, maxRetries: 1 }) as unknown as Promise<Vuelta>;

  const anota = (x: Record<string, unknown>) =>
    db.from("consultas_ia").insert({ pregunta: o.registro, version: o.version, modelo: MODELO, ip_huella: o.huella, agente: true, ...x })
      .then(({ error }) => error && console.error(error));

  let c;
  try {
    c = await agente(crea, { pregunta: o.pregunta, ctx, semillas, limite: Date.now() + PLAZO_AGENTE_MS });
  } catch (e) {
    console.error(e);
    await anota({ fichas: o.ids, rechazo: "error_api" });
    return responde(req, { ok: false, agente: true, rechazo: "error_api" }, 502);
  }
  // En el registro quedan los nombres de las herramientas, nunca lo que el modelo les escribió.
  await anota({
    fichas: c.fichas.slice(0, 60), datos: c.datos.slice(0, 60), herramientas: c.herramientas.slice(0, 12), rondas: c.rondas,
    tokens_in: c.tokens_in, tokens_out: c.tokens_out, ...(c.modelo ? { modelo: c.modelo } : {}),
    respuesta: c.sal ? c.sal.respuesta.slice(0, 6000) : null, verificada: !c.rechazo && !!c.sal, rechazo: c.rechazo,
  });
  if (c.rechazo || !c.sal) {
    return responde(req, { ok: false, agente: true, rechazo: c.rechazo ?? "formato", ...(c.sueltas.length ? { cifras_sin_documento: c.sueltas.slice(0, 10) } : {}) });
  }
  const porId = new Map((ctx.datos ?? []).map((d) => [d.id, d]));
  return responde(req, {
    ok: true,
    agente: true,
    respuesta: c.sal.respuesta,
    sin_respuesta: c.sal.sin_respuesta,
    fichas_usadas: c.usadas,
    datos_usados: c.datosUsados,
    herramientas: c.herramientas,
    rondas: c.rondas,
    // Lo que la página muestra debajo: de dónde sale cada cosa y a dónde ir.
    fuentes: [
      ...c.usadas.map((n) => ({ ficha: n, tit: ctx.fichas[n].tit, ir: ctx.fichas[n].ir ?? null, fu: (ctx.fichas[n].fu ?? []).slice(0, 3) })),
      ...c.datosUsados.map((id) => {
        const d = porId.get(id)!;
        const fu = d.estado === "pendiente"
          ? (d.url ? [{ tx: "Dónde debe publicarlo " + (d.quien ?? "la dependencia obligada"), url: d.url }] : [])
          : (d.citas ?? []).slice(0, 3).map((x) => {
            const f = ctx.fuentes[x.fuente];
            return { tx: (f?.nombre ?? x.fuente.replace(/_/g, " ")) + (x.articulo ? ", " + x.articulo : ""), ...(f?.url ? { url: f.url } : {}) };
          });
        return {
          dato: id, tit: d.concepto, estado: d.estado, fu,
          ir: d.estado === "pendiente" ? ["pendientes.html#fiscal-" + id, "Registro de pendientes"] : ["fiscal-reforma-2027.html", "La base fiscal 2026-2027"],
        };
      }),
    ],
    modelo: c.modelo,
    aviso: "Redactado por inteligencia artificial solo con lo que encontró en las fichas y en la base fiscal de la plataforma; cada cifra se cotejó contra eso. No es asesoría fiscal ni legal: verifica en los documentos.",
  });
}
