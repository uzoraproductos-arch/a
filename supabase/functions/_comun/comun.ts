// Lo que comparten las funciones de Auditavisión (Supabase Edge Functions).
// Plan: docs/BASE-DE-DATOS.md. Las llaves viven en los secretos del proyecto
// de Supabase, nunca en el repositorio ni en la página.
import { createClient, type SupabaseClient } from "npm:@supabase/supabase-js@2.117.3";

/** El sitio publicado: solo desde aquí se aceptan llamadas del navegador. */
export const SITIO = (Deno.env.get("SITIO") ?? "https://uzoraproductos-arch.github.io/a/").replace(/\/?$/, "/");
const ORIGENES = [new URL(SITIO).origin, ...(Deno.env.get("ORIGENES_EXTRA") ?? "").split(",").map((x) => x.trim()).filter(Boolean)];

export function cabeceras(req: Request): Record<string, string> {
  const o = req.headers.get("origin") ?? "";
  return {
    "Access-Control-Allow-Origin": ORIGENES.includes(o) ? o : ORIGENES[0],
    "Access-Control-Allow-Headers": "authorization, apikey, content-type",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Vary": "Origin",
    "Content-Type": "application/json; charset=utf-8",
  };
}

export function responde(req: Request, cuerpo: unknown, estado = 200): Response {
  return new Response(JSON.stringify(cuerpo), { status: estado, headers: cabeceras(req) });
}

/** La base con la llave de servicio: solo dentro de la función. */
export function base(): SupabaseClient {
  const url = Deno.env.get("SUPABASE_URL"), llave = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!url || !llave) throw new Error("faltan SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY");
  return createClient(url, llave, { auth: { persistSession: false } });
}

/** Huella de la IP con sal: sirve para el límite por minuto sin guardar la IP. */
export async function huellaIp(req: Request): Promise<string> {
  const ip = (req.headers.get("x-forwarded-for") ?? "").split(",")[0].trim() || "sin-ip";
  return sha256(ip + "|" + (Deno.env.get("SAL_IP") ?? "auditavision"));
}

export async function sha256(texto: string): Promise<string> {
  const d = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(texto));
  return [...new Uint8Array(d)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

/** Límite por minuto (función limite_ok de la migración). */
export async function dentroDelLimite(db: SupabaseClient, huella: string, ruta: string, max: number, segundos = 60): Promise<boolean> {
  const { data, error } = await db.rpc("limite_ok", { p_huella: huella, p_ruta: ruta, p_max: max, p_segundos: segundos });
  if (error) throw error;
  return data === true;
}

/** Cloudflare Turnstile: si hay secreto configurado, la prueba es obligatoria. */
export async function esPersona(token: unknown, req: Request): Promise<boolean> {
  const secreto = Deno.env.get("TURNSTILE_SECRET");
  if (!secreto) return true;
  if (typeof token !== "string" || !token) return false;
  const f = new FormData();
  f.append("secret", secreto);
  f.append("response", token);
  const ip = (req.headers.get("x-forwarded-for") ?? "").split(",")[0].trim();
  if (ip) f.append("remoteip", ip);
  const r = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", { method: "POST", body: f });
  const j = await r.json() as { success?: boolean };
  return j.success === true;
}

/** Lee el cuerpo JSON con tope de tamaño. */
export async function leeJson(req: Request, tope = 20000): Promise<Record<string, unknown> | null> {
  const t = await req.text();
  if (t.length > tope) return null;
  try {
    const j = JSON.parse(t);
    return j && typeof j === "object" && !Array.isArray(j) ? j : null;
  } catch {
    return null;
  }
}

export function texto(v: unknown, min: number, max: number): string | null {
  if (typeof v !== "string") return null;
  const t = v.replace(/\s+/g, " ").trim();
  return t.length >= min && t.length <= max ? t : null;
}

/** El sello de versión del sitio (AAAAMMDD + letra), como lo manda la página. */
export function sello(v: unknown): string | null {
  return typeof v === "string" && /^\d{8}[a-z]{0,2}$/.test(v) ? v : null;
}

/** Envoltura: CORS, solo POST y errores sin detalles internos. */
export function sirve(fn: (req: Request) => Promise<Response>) {
  Deno.serve(async (req) => {
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cabeceras(req) });
    if (req.method !== "POST") return responde(req, { ok: false, error: "solo POST" }, 405);
    try {
      return await fn(req);
    } catch (e) {
      console.error(e);
      return responde(req, { ok: false, error: "No pudimos atenderte; intenta de nuevo." }, 500);
    }
  });
}
