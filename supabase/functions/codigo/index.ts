// codigo: canjear un código de acceso, consultar hasta cuándo abre un pase y
// pedir un código («¿No tienes código? Obtén uno») (pedido del autor,
// 29-10-2026; migraciones 20261030000001_codigos.sql y 20261030000002).
// Va por aquí, y no directo a la base, para poner el límite de intentos por IP:
// así nadie prueba códigos al azar. El código maestro de la administración
// entra por aquí mismo y abre su sesión (migración 20261030000009). El canje no guarda nombre ni correo; la
// solicitud guarda el correo solo con el aviso de privacidad aceptado.
import { base, dentroDelLimite, huellaIp, leeJson, responde, sirve } from "../_comun/comun.ts";

const PASE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

sirve(async (req) => {
  const j = await leeJson(req, 2000);
  const accion = j && j.accion;
  const pase = j && typeof j.pase === "string" && PASE.test(j.pase) ? j.pase : null;
  const db = base(), huella = await huellaIp(req);

  if (accion === "consultar") {
    if (!pase) return responde(req, { ok: false, error: "Falta el pase." }, 400);
    if (!(await dentroDelLimite(db, huella, "codigo-consulta", 60, 600))) return responde(req, { ok: false, motivo: "espera" }, 429);
    const { data, error } = await db.rpc("pase_consulta", { p_pase: pase });
    if (error) throw error;
    return responde(req, { ok: true, hasta: data ?? null });
  }

  if (accion === "canjear") {
    const codigo = j && typeof j.codigo === "string" ? j.codigo.slice(0, 40) : "";
    // Diez intentos cada diez minutos por IP, buenos o malos.
    if (!(await dentroDelLimite(db, huella, "codigo-canje", 10, 600))) return responde(req, { ok: false, motivo: "espera" }, 429);
    // Y cuarenta al día: el código maestro son 8 números y no debe poder
    // adivinarse probando fechas (migración 20261030000009).
    if (!(await dentroDelLimite(db, huella, "codigo-canje-dia", 40, 86400))) return responde(req, { ok: false, motivo: "espera" }, 429);
    // El código maestro de la administración: si coincide, se abre su sesión
    // sin correo. Se le devuelve un enlace de un solo uso (token_hash) que el
    // navegador cambia por la sesión en /auth/v1/verify; el correo no viaja.
    const maestro = await db.rpc("revisar_codigo_admin", { p_codigo: codigo });
    if (maestro.error) throw maestro.error;
    if (maestro.data) {
      const u = await db.auth.admin.getUserById(maestro.data as string);
      if (u.error || !u.data.user?.email) throw u.error ?? new Error("la administración no tiene correo");
      const l = await db.auth.admin.generateLink({ type: "magiclink", email: u.data.user.email });
      if (l.error) throw l.error;
      return responde(req, { ok: true, admin: true, token_hash: l.data.properties.hashed_token });
    }
    const { data, error } = await db.rpc("canjear_codigo", { p_codigo: codigo, p_pase: pase });
    if (error) throw error;
    return responde(req, data);
  }

  if (accion === "solicitar") {
    // Tres solicitudes por hora por IP; el correo solo con el aviso aceptado.
    if (!(await dentroDelLimite(db, huella, "codigo-solicitud", 3, 3600))) return responde(req, { ok: false, motivo: "espera" }, 429);
    const { data, error } = await db.rpc("solicitar_codigo", {
      p_correo: j && typeof j.correo === "string" ? j.correo.slice(0, 254) : "",
      p_nombre: j && typeof j.nombre === "string" ? j.nombre.slice(0, 80) : null,
      p_motivo: j && typeof j.motivo === "string" ? j.motivo.slice(0, 300) : null,
      p_acepta: j?.acepta_aviso === true,
      p_huella: huella,
    });
    if (error) throw error;
    return responde(req, data);
  }

  return responde(req, { ok: false, error: "Acción desconocida." }, 400);
});
