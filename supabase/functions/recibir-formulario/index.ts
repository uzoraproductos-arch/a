// recibir-formulario: lo que la gente escribe en la plataforma (Servicios, fe
// de erratas, temas, reportes y el cajón «Cuéntanos lo que viste») llega a la
// tabla envios. Los formularios ya arman el texto; esta función es el «Enviar»
// (CANAL_SOLICITUD y CANAL_COMUNIDAD, docs/LANZAMIENTO.md 3.4).
import { base, dentroDelLimite, esPersona, huellaIp, leeJson, responde, sirve, texto } from "../_comun/comun.ts";

const TIPOS = ["solicitud", "errata", "tema", "reporte", "algo_raro", "compartir"];

sirve(async (req) => {
  const j = await leeJson(req);
  if (!j) return responde(req, { ok: false, error: "Mensaje ilegible o demasiado largo." }, 400);
  const tipo = typeof j.tipo === "string" && TIPOS.includes(j.tipo) ? j.tipo : null;
  const asunto = texto(j.asunto, 3, 200), cuerpo = texto(j.texto, 10, 8000);
  if (!tipo || !asunto || !cuerpo) return responde(req, { ok: false, error: "Falta el tipo, el asunto o el texto." }, 400);
  const pagina = typeof j.pagina === "string" && /^[a-z0-9-]+\.html([?#].*)?$/.test(j.pagina) ? j.pagina : null;
  const documento = typeof j.documento === "string" && /^https?:\/\/\S{4,400}$/.test(j.documento) ? j.documento : null;
  // Fe de erratas: sin documento no se puede corregir (la misma regla que seguimos nosotros).
  if (tipo === "errata" && !documento) return responde(req, { ok: false, error: "Para una errata necesitamos el enlace al documento oficial." }, 400);
  const acepta = j.acepta_aviso === true;
  const correo = acepta && typeof j.correo === "string" && /^[^@\s]{1,64}@[^@\s]{1,190}\.[^@\s]{2,}$/.test(j.correo) ? j.correo : null;

  if (!(await esPersona(j.turnstile, req))) return responde(req, { ok: false, error: "No pudimos comprobar que eres una persona." }, 403);
  const db = base(), huella = await huellaIp(req);
  if (!(await dentroDelLimite(db, huella, "formulario", 5, 600))) {
    return responde(req, { ok: false, error: "Recibimos varios envíos tuyos seguidos; espera unos minutos." }, 429);
  }
  const { data, error } = await db.from("envios")
    .insert({ tipo, asunto, texto: cuerpo, pagina, documento, correo, acepta_aviso: acepta, ip_huella: huella })
    .select("id").single();
  if (error) throw error;
  return responde(req, { ok: true, folio: "AV-" + String(data.id).padStart(6, "0") });
});
