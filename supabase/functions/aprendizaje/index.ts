// aprendizaje: el buzón de aprendizaje verificado (Ola 4, Ronda 41). Quien
// quiere manda su duda desde el chat para que la administración la investigue.
// La pregunta sale del navegador ya sin RFC, CURP, correos, teléfonos ni
// montos; aquí se vuelve a anonimizar, se limita por conexión y se guarda con
// anotar_aprendizaje, que suma una vez si la misma duda ya estaba como nueva.
// No se guarda nombre, correo ni la huella de la conexión: la huella solo
// sirve para el límite, como en las demás funciones.
import { anonimo, traeDatos } from "../_comun/anonimo.ts";
import { base, dentroDelLimite, huellaIp, leeJson, responde, sello, sirve, texto } from "../_comun/comun.ts";

const MODOS = ["inspector", "periodista", "ciudadano", "ambientalista"];

sirve(async (req) => {
  const j = await leeJson(req, 3000);
  const cruda = j && texto(j.pregunta, 4, 400);
  if (!cruda) return responde(req, { ok: false, error: "Falta la pregunta, o pasa de 400 caracteres." }, 400);
  const pregunta = anonimo(cruda).slice(0, 400);
  if (pregunta.length < 4 || traeDatos(pregunta)) return responde(req, { ok: false, error: "La pregunta trae datos que no se guardan." }, 400);
  const modo = j && typeof j.modo === "string" && MODOS.includes(j.modo) ? j.modo : null;
  const db = base(), huella = await huellaIp(req);
  // Diez dudas por hora desde la misma conexión: es un buzón, no un chat.
  if (!(await dentroDelLimite(db, huella, "aprendizaje", 10, 3600))) return responde(req, { ok: true, anotada: false });
  const { data, error } = await db.rpc("anotar_aprendizaje", { p_pregunta: pregunta, p_modo: modo, p_sin: j.sin === true, p_version: sello(j.version) });
  if (error) throw error;
  return responde(req, { ok: true, anotada: true, nueva: data === true });
});
