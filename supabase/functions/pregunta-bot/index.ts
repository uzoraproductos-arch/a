// pregunta-bot: «Lo que aún no sé» deja de vivir solo en cada navegador. Las
// preguntas sin respuesta y las marcadas «No era lo que buscaba» llegan a
// preguntas_bot, y la vista preguntas_por_atender dice qué fichas faltan
// primero (docs/LANZAMIENTO.md 3.5). Solo se guarda la pregunta.
import { base, dentroDelLimite, huellaIp, leeJson, responde, sello, sirve, texto } from "../_comun/comun.ts";

sirve(async (req) => {
  const j = await leeJson(req, 4000);
  const pregunta = j && texto(j.pregunta, 2, 600), version = j && sello(j.version);
  const motivo = j && (j.motivo === "sin" || j.motivo === "noera") ? j.motivo : null;
  if (!pregunta || !version || !motivo) return responde(req, { ok: false, error: "Falta la pregunta, el motivo o la versión." }, 400);
  const ficha = j && typeof j.ficha === "string" ? j.ficha.slice(0, 300) : null;
  const db = base(), huella = await huellaIp(req);
  if (!(await dentroDelLimite(db, huella, "pregunta", 20, 600))) return responde(req, { ok: true, anotada: false });
  const { error } = await db.from("preguntas_bot").insert({ pregunta, motivo, ficha, version, ip_huella: huella });
  if (error) throw error;
  return responde(req, { ok: true, anotada: true });
});
