// Lo que la búsqueda en internet puede devolver (función buscar-web). Va aparte
// para probarlo sin red (supabase/pruebas/web_test.ts).
//
// Regla de la casa (AGENTS.md §2 y §5 ter): de internet solo se devuelven
// ENLACES (título, dirección, sitio, fecha de la página), nunca un texto que
// la IA haya redactado sobre la persona. Lo que diga cada página lo lee el
// lector en su original y, si trae cifras, lo coteja con Contrasta una nota.

/** Sitios oficiales: cualquier subdominio de estos cuenta como oficial. */
export const OFICIALES = [
  "gob.mx", "ine.mx", "scjn.gob.mx", "diputados.gob.mx", "senado.gob.mx", "asf.gob.mx", "dof.gob.mx",
  "inegi.org.mx", "banxico.org.mx", "te.gob.mx", "justice.gov", "uscourts.gov",
];

/** Prensa nacional con hemeroteca en línea. Es una lista editorial: la decide
 *  el autor y se cambia aquí. Lo que viene de ella se marca «prensa». */
export const PRENSA = [
  "eluniversal.com.mx", "jornada.com.mx", "proceso.com.mx", "animalpolitico.com", "milenio.com",
  "elfinanciero.com.mx", "expansion.mx", "eleconomista.com.mx", "aristeguinoticias.com", "elpais.com",
  "reforma.com", "excelsior.com.mx", "sinembargo.mx", "latinus.us",
];

export type Enlace = { titulo: string; url: string; sitio: string; tipo: "oficial" | "prensa"; fecha: string | null };

function bajoDe(host: string, dominio: string): boolean {
  return host === dominio || host.endsWith("." + dominio);
}

/** Clasifica una dirección; null si no es https o no está en ninguna lista. */
export function clasifica(u: string): { sitio: string; tipo: "oficial" | "prensa" } | null {
  let url: URL;
  try {
    url = new URL(u);
  } catch {
    return null;
  }
  if (url.protocol !== "https:" || url.username || url.password) return null;
  const host = url.hostname.toLowerCase().replace(/^www\./, "");
  if (OFICIALES.some((d) => bajoDe(host, d))) return { sitio: host, tipo: "oficial" };
  if (PRENSA.some((d) => bajoDe(host, d))) return { sitio: host, tipo: "prensa" };
  return null;
}

/** El nombre que se busca: letras, espacios y puntos; de 2 a 6 palabras. */
export function nombreValido(v: unknown): string | null {
  if (typeof v !== "string") return null;
  const n = v.normalize("NFC").replace(/\s+/g, " ").trim();
  if (n.length < 5 || n.length > 70) return null;
  if (!/^[\p{L}][\p{L} .'-]*$/u.test(n)) return null;
  const ws = n.split(" ");
  return ws.length >= 2 && ws.length <= 6 ? n : null;
}

/** La clave de la copia: el nombre sin acentos ni mayúsculas. */
export function claveDe(nombre: string): string {
  return nombre.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9ñ]+/g, " ").trim();
}

type Bloque = { type: string; content?: unknown };
type Resultado = { type?: string; url?: string; title?: string; page_age?: string | null };

/** Saca los enlaces de los resultados del buscador, tal como los entregó. Los
 *  bloques de texto del modelo se ignoran: no se publica nada redactado. */
export function enlaces(contenido: Bloque[], tope = 12): Enlace[] {
  const out: Enlace[] = [], vistos = new Set<string>();
  for (const b of contenido) {
    if (b.type !== "web_search_tool_result" || !Array.isArray(b.content)) continue;
    for (const r of b.content as Resultado[]) {
      if (r.type !== "web_search_result" || typeof r.url !== "string") continue;
      const c = clasifica(r.url);
      const url = r.url.split("#")[0];
      if (!c || vistos.has(url)) continue;
      vistos.add(url);
      out.push({
        titulo: String(r.title ?? c.sitio).replace(/\s+/g, " ").trim().slice(0, 200),
        url, sitio: c.sitio, tipo: c.tipo, fecha: typeof r.page_age === "string" ? r.page_age.slice(0, 40) : null,
      });
    }
  }
  // Primero lo oficial, después la prensa; dentro de cada uno, el orden del buscador.
  return out.sort((a, b) => (a.tipo === b.tipo ? 0 : a.tipo === "oficial" ? -1 : 1)).slice(0, tope);
}
