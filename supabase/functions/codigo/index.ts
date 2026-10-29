// codigo: canjear un código de acceso y consultar hasta cuándo abre un pase
// (pedido del autor, 29-10-2026; migración 20261030000001_codigos.sql).
// Va por aquí, y no directo a la base, para poner el límite de intentos por IP:
// así nadie prueba códigos al azar. Solo guarda el canje: ni nombre ni correo.
import { base, dentroDelLimite, huellaIp, leeJson, responde, sirve } from "../_comun/comun.ts";

const PASE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

sirve(async (req) => {
  const j = await leeJson(req, 1000);
  const accion = j && j.accion;
  const pase = j && typeof j.pase === "string" && PASE.test(j.pase) ? j.pase : null;
  const db = base(), huella = await huellaIp(req);

  if (accion === "consultar") {
    if (!pase) return responde(req, { ok: false, error: "Falta el pase." }, 400);
    if (!(await dentroDelLimite(db, huella, "codigo-consulta", 60, 600))) return responde(req, { ok: false, motivo: "espera" }, 429);
    const { data, error } = await db.rpc("pase_hasta", { p_pase: pase });
    if (error) throw error;
    return responde(req, { ok: true, hasta: data ?? null });
  }

  if (accion === "canjear") {
    const codigo = j && typeof j.codigo === "string" ? j.codigo.slice(0, 40) : "";
    // Diez intentos cada diez minutos por IP, buenos o malos.
    if (!(await dentroDelLimite(db, huella, "codigo-canje", 10, 600))) return responde(req, { ok: false, motivo: "espera" }, 429);
    const { data, error } = await db.rpc("canjear_codigo", { p_codigo: codigo, p_pase: pase });
    if (error) throw error;
    return responde(req, data);
  }

  return responde(req, { ok: false, error: "Acción desconocida." }, 400);
});
