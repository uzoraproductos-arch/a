// portales: la fase 2 del Auditor (consultar portales oficiales en vivo). El
// navegador no puede leerlos directo (CORS y llaves), así que esta función lo
// hace por él, SOLO en la lista cerrada de abajo, y guarda la copia con su
// dirección, su fecha y su huella SHA-256 en portales_cache.
//
// Regla de la casa: lo que devuelve es «oficial» porque sale del portal, y se
// cita al portal (url), nunca a esta copia. Si el portal no responde, se dice
// así: no se inventa ni se rellena con una copia vieja sin decir su fecha.
import { base, dentroDelLimite, huellaIp, leeJson, responde, sha256, sirve } from "../_comun/comun.ts";

type Portal = {
  nombre: string;
  // Arma la dirección real (con llave) y la que se publica (sin llave).
  url: (clave: string, llave: string) => { real: string; publica: string; cabeceras?: Record<string, string> };
  clave: RegExp;
  llave: string;
  horas: number;
};

const PORTALES: Record<string, Portal> = {
  // Banxico, Sistema de Información Económica (SIE). Verificado el 24-10-2026:
  // sin llave contesta «Token inválido». Llave gratuita en
  // https://www.banxico.org.mx/SieAPIRest/service/v1/token
  // Clave: series separadas por coma (SF43718 = tipo de cambio FIX; SP1 = INPC).
  "banxico-sie": {
    nombre: "Banco de México, Sistema de Información Económica",
    clave: /^S[A-Z]\d{1,6}(,S[A-Z]\d{1,6}){0,9}$/,
    llave: "BANXICO_TOKEN",
    horas: 6,
    url: (clave, llave) => {
      const u = "https://www.banxico.org.mx/SieAPIRest/service/v1/series/" + clave + "/datos/oportuno";
      return { real: u, publica: u, cabeceras: { "Bmx-Token": llave, "Accept": "application/json" } };
    },
  },
  // INEGI, API de indicadores. Sintaxis de su página de desarrolladores
  // (cotejada por el autor el 30-10-2026):
  //   .../jsonxml/INDICATOR/[IdIndicador]/[Idioma]/[Área]/[Recientes]/[Fuente]/2.0/[Token]?type=json
  // con el ejemplo 1002000001/es/00/true/BISE/2.0. La fuente es BISE (indicadores
  // de bancos de información sociodemográfica, área nacional «00») o BIE
  // (Banco de Información Económica, área nacional «0700»): la clave se pide
  // como «BIE:123456»; sin prefijo es BISE. Se trae la serie entera
  // (Recientes = false). La llave va en la dirección, así que la que se
  // publica la lleva tapada.
  "inegi-bie": {
    nombre: "INEGI, API de indicadores",
    clave: /^(BIE:|BISE:)?\d{4,10}$/,
    llave: "INEGI_TOKEN",
    horas: 24,
    url: (clave, llave) => {
      const [fuente, id] = clave.includes(":") ? clave.split(":") : ["BISE", clave];
      const area = fuente === "BIE" ? "0700" : "00";
      const p = "https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/INDICATOR/" + id + "/es/" + area + "/false/" + fuente + "/2.0/";
      return { real: p + llave + "?type=json", publica: p + "{llave}?type=json" };
    },
  },
};

sirve(async (req) => {
  const j = await leeJson(req, 2000);
  const id = j && typeof j.fuente === "string" ? j.fuente : "";
  const p = PORTALES[id];
  const clave = j && typeof j.clave === "string" ? j.clave.trim().toUpperCase() : "";
  if (!p) return responde(req, { ok: false, error: "Ese portal no está en la lista de fuentes oficiales.", fuentes: Object.keys(PORTALES) }, 400);
  if (!p.clave.test(clave)) return responde(req, { ok: false, error: "La clave no tiene el formato de " + p.nombre + "." }, 400);
  const llave = Deno.env.get(p.llave);
  if (!llave) return responde(req, { ok: false, pendiente: true, error: "La consulta a " + p.nombre + " aún no está configurada (falta su llave)." }, 503);

  const db = base(), huella = await huellaIp(req);
  if (!(await dentroDelLimite(db, huella, "portales", 30, 60))) return responde(req, { ok: false, error: "Demasiadas consultas seguidas; espera un minuto." }, 429);

  // ¿Hay copia vigente? Se devuelve con su fecha de consulta.
  const { data: copia } = await db.from("portales_cache").select("url, sha256, cuerpo, obtenido")
    .eq("fuente", id).eq("clave", clave).gt("vence", new Date().toISOString())
    .order("obtenido", { ascending: false }).limit(1).maybeSingle();
  if (copia) {
    return responde(req, { ok: true, fuente: p.nombre, url: copia.url, consultado: copia.obtenido, sha256: copia.sha256, datos: copia.cuerpo, copia: true, estado: "oficial" });
  }

  const u = p.url(clave, llave);
  let r: Response;
  try {
    r = await fetch(u.real, { headers: u.cabeceras, signal: AbortSignal.timeout(15000) });
  } catch {
    return responde(req, { ok: false, error: p.nombre + " no respondió. Intenta más tarde; no mostramos una cifra sin su documento." }, 502);
  }
  const crudo = await r.text();
  if (!r.ok || crudo.length > 2_000_000) {
    return responde(req, { ok: false, error: p.nombre + " contestó con un error (" + r.status + ")." }, 502);
  }
  let cuerpo: unknown;
  try {
    cuerpo = JSON.parse(crudo);
  } catch {
    return responde(req, { ok: false, error: p.nombre + " cambió de formato: la consulta se detiene hasta revisarlo." }, 502);
  }
  // La huella es del texto tal como lo entregó el portal.
  const h = await sha256(crudo), ahora = new Date();
  const vence = new Date(ahora.getTime() + p.horas * 3600_000);
  const { error } = await db.from("portales_cache").upsert(
    { fuente: id, url: u.publica, clave, sha256: h, cuerpo, bytes: crudo.length, obtenido: ahora.toISOString(), vence: vence.toISOString() },
    { onConflict: "fuente,clave,sha256" });
  if (error) console.error(error);
  return responde(req, { ok: true, fuente: p.nombre, url: u.publica, consultado: ahora.toISOString(), sha256: h, datos: cuerpo, copia: false, estado: "oficial" });
});
