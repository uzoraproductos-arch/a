// codigo: canjear un código de acceso, consultar hasta cuándo abre un pase y
// pedir un código («¿No tienes código? Obtén uno») (pedido del autor,
// 29-10-2026; migraciones 20261030000001_codigos.sql y 20261030000002).
// Va por aquí, y no directo a la base, para poner el límite de intentos por IP:
// así nadie prueba códigos al azar. El código maestro de la administración
// entra por aquí mismo y abre su sesión (migración 20261030000009). El canje no guarda nombre ni correo; la
// solicitud guarda el correo solo con el aviso de privacidad aceptado.
//
// Aviso por correo de cada solicitud de código (27-11-2026, pedido del autor), con
// Resend. Tres secretos de la función, ninguno escrito aquí:
//   RESEND_API_KEY      la llave de Resend; sin ella no se manda nada.
//   ADMIN_NOTIFY_EMAIL  a quién se le avisa; sin él no se manda nada.
//   RESEND_FROM         (opcional) el remitente; por defecto «Auditavisión <onboarding@resend.dev>».
// El aviso nunca detiene ni tumba la solicitud: si faltan los secretos se omite en
// silencio, y si Resend falla o tarda más de 4 segundos solo queda un console.warn.
import { base, dentroDelLimite, huellaIp, leeJson, responde, sirve } from "../_comun/comun.ts";

const PASE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

const CORREO = /^[^\s@<>",;]+@[^\s@<>",;]+\.[^\s@<>",;]+$/;
const PANEL = "https://auditavision.com.mx/administracion-codigos.html";
const unaLinea = (t: string) => t.replace(/[\u0000-\u001f\u007f\u2028\u2029]+/g, " ").replace(/\s+/g, " ").trim();

// Avisa a la administración de una solicitud nueva. No lanza nunca.
async function avisaSolicitud(correo: string, nombre: string | null, motivo: string | null): Promise<void> {
  try {
    const llave = Deno.env.get("RESEND_API_KEY"), para = Deno.env.get("ADMIN_NOTIFY_EMAIL");
    if (!llave || !para) return;
    const de = Deno.env.get("RESEND_FROM") || "Auditavisión <onboarding@resend.dev>";
    const mot = unaLinea(motivo ?? ""), nom = unaLinea(nombre ?? ""), cor = unaLinea(correo);
    const cuando = new Intl.DateTimeFormat("es-MX", { timeZone: "America/Mexico_City", dateStyle: "long", timeStyle: "short" }).format(new Date());
    const cuerpo: Record<string, unknown> = {
      from: de,
      to: [para],
      subject: "[Auditavisión] Nueva solicitud de código" + (mot ? ": " + (mot.length > 60 ? mot.slice(0, 59) + "…" : mot) : ""),
      text: [
        "Llegó una solicitud de código de acceso.",
        "",
        "Nombre: " + (nom || "No indicó"),
        "Correo: " + (cor || "No indicó"),
        "Motivo: " + (mot || "Sin motivo"),
        "Fecha y hora: " + cuando + " (Ciudad de México)",
        "",
        "Atiéndela en el panel: " + PANEL,
      ].join("\n"),
    };
    if (CORREO.test(cor)) cuerpo.reply_to = cor;
    const r = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: "Bearer " + llave, "Content-Type": "application/json" },
      body: JSON.stringify(cuerpo),
      signal: AbortSignal.timeout(4000),
    });
    if (!r.ok) console.warn("codigo: Resend no aceptó el aviso de la solicitud (HTTP " + r.status + ")");
    await r.body?.cancel();
  } catch (e) {
    // Solo el tipo de error: nunca la llave ni el correo.
    console.warn("codigo: no se pudo mandar el aviso de la solicitud (" + (e instanceof Error ? e.name : "error") + ")");
  }
}

sirve(async (req) => {
  const j = await leeJson(req, 16000);
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
    // El código maestro de la administración (Ronda 19, 24-11-2026, decisión del
    // autor: «mi código maestro tiene todos los poderes y libertades sin límites»):
    // se revisa antes que los límites de intentos y no cuenta en ellos, así que
    // entra siempre aunque esa conexión ya haya gastado sus intentos. Adivinarlo
    // sigue siendo caro: son 8 letras o números (36^8) y cada prueba es un bcrypt.
    // Si coincide se le devuelve un enlace de un solo uso (token_hash) que el
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
    // Los demás códigos: diez intentos cada diez minutos por IP, buenos o malos,
    // y cuarenta al día.
    if (!(await dentroDelLimite(db, huella, "codigo-canje", 10, 600))) return responde(req, { ok: false, motivo: "espera" }, 429);
    if (!(await dentroDelLimite(db, huella, "codigo-canje-dia", 40, 86400))) return responde(req, { ok: false, motivo: "espera" }, 429);
    const { data, error } = await db.rpc("canjear_codigo", { p_codigo: codigo, p_pase: pase });
    if (error) throw error;
    return responde(req, data);
  }

  if (accion === "solicitar") {
    // Tres solicitudes por hora por IP; el correo solo con el aviso aceptado.
    if (!(await dentroDelLimite(db, huella, "codigo-solicitud", 3, 3600))) return responde(req, { ok: false, motivo: "espera" }, 429);
    const correo = j && typeof j.correo === "string" ? j.correo.slice(0, 254) : "";
    const nombre = j && typeof j.nombre === "string" ? j.nombre.slice(0, 80) : null;
    const motivo = j && typeof j.motivo === "string" ? j.motivo.slice(0, 300) : null;
    const { data, error } = await db.rpc("solicitar_codigo", {
      p_correo: correo,
      p_nombre: nombre,
      p_motivo: motivo,
      p_acepta: j?.acepta_aviso === true,
      p_huella: huella,
    });
    if (error) throw error;
    // Solo si la base la guardó. El aviso corre aparte cuando el entorno lo permite
    // (EdgeRuntime.waitUntil), para no hacer esperar a quien pide; si no, se espera
    // a lo más su límite de 4 segundos. Nunca cambia la respuesta.
    if (data && data.ok !== false) {
      const aviso = avisaSolicitud(correo, nombre, motivo);
      const er = (globalThis as { EdgeRuntime?: { waitUntil?: (p: Promise<unknown>) => void } }).EdgeRuntime;
      if (er && typeof er.waitUntil === "function") er.waitUntil(aviso);
      else await aviso;
    }
    return responde(req, data);
  }

  if (accion === "uso") {
    // La medición de uso (migración 20261118000001): páginas, tiempo y clics,
    // en tandas de hasta 40. Sin IP ni nada que diga quién es; el límite por
    // IP solo frena el abuso. Si se pasa, se tira en silencio.
    const sesion = j && typeof j.sesion === "string" ? j.sesion.slice(0, 24) : "";
    const eventos = j && Array.isArray(j.eventos) ? j.eventos.slice(0, 40) : [];
    if (!sesion || !eventos.length) return responde(req, { ok: false }, 400);
    if (!(await dentroDelLimite(db, huella, "codigo-uso", 120, 600))) return responde(req, { ok: false, motivo: "espera" }, 429);
    const { data, error } = await db.rpc("registrar_uso", { p_pase: pase, p_sesion: sesion, p_eventos: eventos });
    if (error) throw error;
    return responde(req, { ok: true, guardados: data ?? 0 });
  }

  return responde(req, { ok: false, error: "Acción desconocida." }, 400);
});
