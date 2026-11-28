// El agente lector de auditor-ia (Ola 4, entrega B, Ronda 42). Cuando el
// buscador de la página y el calculador no contestan, el modelo puede BUSCAR
// él mismo en lo publicado, con tres herramientas de solo lectura:
//   buscar_fichas          las fichas de asistente-base.js
//   consultar_dato_fiscal  los datos de docs/fiscal-2027/ con su cita textual
//   consultar_pendientes   lo que esa base sigue debiendo, con quién lo debe
// El candado de cifras no cambia: todo lo que devuelve una herramienta se suma
// a la evidencia de esa consulta, y sinDocumento() tira la respuesta si trae
// una cifra que no salió de ahí. Dos cuidados para que el candado no se pueda
// rodear: (1) una herramienta nunca repite en su resultado lo que el modelo le
// escribió (si lo repitiera, una cifra inventada en la consulta entraría a la
// evidencia), y (2) lo que el modelo escribe nunca entra a la evidencia.
// Tope de costo: tres rondas de herramientas, tres llamadas por ronda y, a la
// cuarta vuelta, se le quitan las herramientas (tool_choice: none).
// Va aparte y sin nada de Deno ni de la red, para probarlo sin conexión
// (supabase/pruebas/agente_casos.ts, que corre herramientas/prueba_agente.py).
import { sinDocumento } from "./cotejo.ts";

export type Cifra = { v: string; etq: string; e: string; op?: string };
export type Fuente = { tx: string; url?: string };
export type Ficha = { t: string; tit: string; txt?: string; ci?: Cifra[]; fu?: Fuente[]; ir?: [string, string]; k?: string; nota?: string };

/** Los cuatro archivos publicados de la base fiscal y su tabla de fuentes. */
export const ARCHIVOS_FISCALES = ["tarifas-y-topes", "reforma-2027", "fiscalizacion-y-plazos", "calendario-y-pendientes-2027"] as const;
export type Cita = { fuente: string; articulo?: string; cita: string };
export type Dato = {
  id: string; concepto: string; estado: string; archivo: string; grupo: string;
  valor?: Record<string, unknown>; tabla?: Record<string, unknown>[]; unidad?: string; operacion?: string; nota?: string;
  vigencia_desde?: string; en_letra?: string[]; citas?: Cita[]; motivo?: string; quien?: string; url?: string;
};
export type FuenteFiscal = { nombre?: string; publicacion?: string; url?: string };

export const MAX_FICHAS_HERRAMIENTA = 6;
export const MAX_DATOS_HERRAMIENTA = 5;
export const MAX_RONDAS = 3;
export const MAX_LLAMADAS_RONDA = 3;
const TOPE_TEXTO = 1500;

// ---------------------------------------------------------------- el texto

/** Minúsculas, sin acentos y sin signos: así se comparan la consulta y la base. */
export function plano(s: string): string {
  return String(s ?? "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9ñ]+/g, " ").trim();
}

const VACIAS = new Set(("a al algo ante asi aun bajo cada como con contra cual cuales cuando cuanta cuantas cuanto cuantos de del desde donde dos e el ella ellas ellos en entre era es esa ese eso esta estan estas este esto estos fue ha hace hacia hay la las le les lo los mas me mi mis muy ni no nos o otra otro para pero por porque que quien quienes se segun ser si sin sobre son su sus tambien te tiene tienen tu tus un una uno unos y ya dice dicen cierto puedo puede debo debe").split(" "));

/** Las palabras que sirven para buscar: sin las vacías, sin plural y sin repetir. */
export function terminos(consulta: string): string[] {
  const out: string[] = [];
  for (const p of plano(consulta).split(" ")) {
    if (!p || VACIAS.has(p) || (p.length < 3 && !/^\d+$/.test(p))) continue;
    const raiz = p.length > 5 && p.endsWith("es") ? p.slice(0, -2) : p.length > 4 && p.endsWith("s") ? p.slice(0, -1) : p;
    if (!out.includes(raiz)) out.push(raiz);
    if (out.length >= 12) break;
  }
  return out;
}

type Campos = { a: string; b: string; c: string };
const PESO = { a: 6, b: 3, c: 1 };

function puntos(ts: string[], idx: Campos[], pesoTipo?: (i: number) => number): { i: number; p: number }[] {
  if (!ts.length) return [];
  const n = idx.length;
  const donde = ts.map((t) => idx.map((x) => (x.a.includes(" " + t) ? PESO.a : x.b.includes(" " + t) ? PESO.b : x.c.includes(" " + t) ? PESO.c : 0)));
  const idf = donde.map((col) => Math.log(1 + n / (1 + col.filter(Boolean).length)));
  const out: { i: number; p: number }[] = [];
  for (let i = 0; i < n; i++) {
    let p = 0, hay = 0, enTitulo = 0;
    for (let k = 0; k < ts.length; k++) {
      const w = donde[k][i];
      if (w) { p += w * idf[k]; hay++; if (w === PESO.a) enTitulo++; }
    }
    if (!hay) continue;
    // Premia a la ficha que trae casi todas las palabras, y más si están en su título.
    p *= (hay / ts.length) ** 2 * (enTitulo === ts.length ? 1.5 : 1) * (pesoTipo ? pesoTipo(i) : 1);
    out.push({ i, p });
  }
  return out.sort((x, y) => y.p - x.p || x.i - y.i);
}

// ---------------------------------------------------------------- las fichas

/** La ficha tal como la lee el modelo. Sin tope (el modo de siempre) va entera. */
export function documento(n: number, f: Ficha, tope = 0): string {
  const ci = (f.ci ?? []).map((c) => "- " + c.v + " · " + c.etq + " [" + c.e + "]" + (c.op ? " (operación: " + c.op + ")" : "")).join("\n");
  const fu = (f.fu ?? []).map((x) => "- " + x.tx + (x.url ? " <" + x.url + ">" : "")).join("\n");
  const txt = f.txt && tope && f.txt.length > tope ? f.txt.slice(0, tope) + " […la ficha sigue en la plataforma]" : f.txt;
  return "<ficha numero=\"" + n + "\">\nTítulo: " + f.tit + "\n" + (txt ? "Texto: " + txt + "\n" : "") +
    (ci ? "Cifras:\n" + ci + "\n" : "") + (fu ? "Fuentes:\n" + fu + "\n" : "") + "</ficha>";
}

/** El índice de las fichas de una versión: se arma una vez y se guarda con ella. */
export function indiceFichas(fichas: Ficha[]): Campos[] {
  return fichas.map((f) => ({
    a: " " + plano(f.tit),
    b: " " + plano((f.k ?? "") + " " + (f.ci ?? []).map((c) => c.etq).join(" ")),
    c: " " + plano((f.txt ?? "") + " " + (f.nota ?? "") + " " + (f.fu ?? []).map((x) => x.tx).join(" ")),
  }));
}

const PESO_TIPO: Record<string, number> = { fuente: 0.6, pagina: 0.9 };

/** Los números de las mejores fichas para una consulta (seis como mucho). */
export function buscarFichas(fichas: Ficha[], idx: Campos[], consulta: string, limite?: unknown): number[] {
  const lim = Math.min(MAX_FICHAS_HERRAMIENTA, Math.max(1, Number.isInteger(limite) ? limite as number : 4));
  return puntos(terminos(consulta), idx, (i) => PESO_TIPO[fichas[i].t] ?? 1).slice(0, lim).map((x) => x.i);
}

// ---------------------------------------------------------------- la base fiscal

/** Los datos de los archivos publicados de docs/fiscal-2027/, uno por renglón. */
export function datosFiscales(archivos: Record<string, unknown>): Dato[] {
  const out: Dato[] = [];
  for (const archivo of ARCHIVOS_FISCALES) {
    const j = archivos[archivo];
    if (!j || typeof j !== "object") continue;
    for (const [grupo, lista] of Object.entries(j as Record<string, unknown>)) {
      if (!Array.isArray(lista)) continue;
      for (const x of lista) if (x && typeof x === "object" && typeof x.id === "string" && typeof x.concepto === "string") out.push({ ...x, archivo, grupo });
    }
  }
  return out;
}

export function indiceDatos(datos: Dato[]): Campos[] {
  return datos.map((d) => ({
    a: " " + plano(d.concepto),
    b: " " + plano(d.id + " " + d.grupo + " " + (d.unidad ?? "") + " " + (d.citas ?? []).map((c) => c.fuente + " " + (c.articulo ?? "")).join(" ") + " " + (d.quien ?? "")),
    c: " " + plano((d.nota ?? "") + " " + (d.operacion ?? "") + " " + (d.motivo ?? "") + " " + (d.citas ?? []).map((c) => c.cita).join(" ") + " " + Object.keys(d.valor ?? {}).join(" ")),
  }));
}

function nombreFuente(clave: string, fuentes: Record<string, FuenteFiscal>): FuenteFiscal {
  const f = fuentes[clave];
  return f ? { nombre: (f.nombre ?? clave) + (f.publicacion ? ", " + f.publicacion : ""), url: f.url } : { nombre: clave.replace(/_/g, " ") };
}

function valorTx(v: unknown): string {
  return Array.isArray(v) ? v.map(valorTx).join(", ") : v && typeof v === "object" ? Object.entries(v).map(([k, x]) => k.replace(/_/g, " ") + " " + valorTx(x)).join("; ") : String(v);
}

/** El dato tal como lo lee el modelo. Un pendiente nunca lleva valor: lleva por qué falta y quién lo debe. */
export function datoTx(d: Dato, fuentes: Record<string, FuenteFiscal>): string {
  const r = ["<dato id=\"" + d.id + "\" estado=\"" + d.estado + "\">", "Concepto: " + d.concepto];
  if (d.estado === "pendiente") {
    r.push("Estado: PENDIENTE. La plataforma no tiene este dato; no lo afirmes ni lo estimes.");
    if (d.motivo) r.push("Por qué falta: " + d.motivo);
    if (d.quien) r.push("Quién lo debe: " + d.quien);
    if (d.url) r.push("Dónde debe publicarse: <" + d.url + ">");
  } else {
    if (d.valor) r.push("Valor: " + valorTx(d.valor));
    if (d.tabla) r.push("Tabla:\n" + d.tabla.map((x) => "- " + valorTx(x)).join("\n"));
    if (d.en_letra?.length) r.push("En letra: " + d.en_letra.join("; "));
    if (d.unidad) r.push("Unidad: " + d.unidad);
    if (d.vigencia_desde) r.push("Vigencia desde: " + d.vigencia_desde);
    if (d.operacion) r.push("Operación (dato auditado, calculado por la plataforma): " + d.operacion);
    if (d.nota) r.push("Nota: " + d.nota);
    for (const c of d.citas ?? []) {
      const f = nombreFuente(c.fuente, fuentes);
      r.push("Cita textual (" + f.nombre + (c.articulo ? ", " + c.articulo : "") + ")" + (f.url ? " <" + f.url + ">" : "") + ": «" + c.cita + "»");
    }
  }
  return r.join("\n") + "\n</dato>";
}

// ---------------------------------------------------------------- las herramientas

export type Contexto = {
  fichas: Ficha[]; idxFichas: Campos[];
  /** null si los archivos fiscales no se pudieron leer: la herramienta lo dice y el agente sigue con las fichas. */
  datos: Dato[] | null; idxDatos: Campos[]; fuentes: Record<string, FuenteFiscal>;
};

export function contexto(fichas: Ficha[], archivos: Record<string, unknown> | null, fuentes: Record<string, FuenteFiscal> = {}): Contexto {
  const datos = archivos ? datosFiscales(archivos) : null;
  return { fichas, idxFichas: indiceFichas(fichas), datos, idxDatos: indiceDatos(datos ?? []), fuentes };
}

const consultaEsquema = { type: "string", description: "Palabras clave en español, pocas y concretas (el tema, la institución, el concepto). No es una pregunta completa." };

export const HERRAMIENTAS = [
  {
    name: "buscar_fichas",
    description: "Busca en las fichas publicadas de Auditavisión (gasto público, presupuesto, deuda, ASF, megaobras, estados y municipios, sueldos de servidores públicos, glosario, leyes, noticias verificadas y pendientes). Devuelve las fichas más cercanas con su texto, sus cifras con estado y sus fuentes. Úsala para cualquier tema que no sea una regla fiscal del contribuyente.",
    strict: true,
    input_schema: {
      type: "object",
      properties: { consulta: consultaEsquema, limite: { type: "integer", description: "Cuántas fichas traer: de 1 a 6. Con 4 suele bastar." } },
      required: ["consulta", "limite"],
      additionalProperties: false,
    },
  },
  {
    name: "consultar_dato_fiscal",
    description: "Busca en la base fiscal 2026-2027 de la plataforma (ISR, IVA, RESICO, UMA, salario mínimo, deducciones personales, retenciones, plataformas digitales, reforma 2027, facultades de comprobación del SAT, plazos y calendario fiscal). Devuelve cada dato con su valor, su estado (oficial o auditada), su vigencia y su cita textual del documento oficial. Úsala para cualquier regla, tasa, tope o plazo fiscal.",
    strict: true,
    input_schema: { type: "object", properties: { consulta: consultaEsquema }, required: ["consulta"], additionalProperties: false },
  },
  {
    name: "consultar_pendientes",
    description: "Dice qué sigue PENDIENTE en la base fiscal (por ejemplo la RMF 2027, la UMA y el salario mínimo de 2027, tarifas actualizadas, criterios de la SCJN, multas): por qué falta, quién lo debe publicar y donde. Úsala antes de afirmar que algo de 2027 ya está definido, o cuando un dato no aparezca. Con la consulta vacía lista todos los pendientes.",
    strict: true,
    input_schema: { type: "object", properties: { consulta: consultaEsquema }, required: ["consulta"], additionalProperties: false },
  },
];

export type Resultado = { texto: string; fichas: number[]; datos: string[]; error?: boolean };

/** Corre una herramienta. Su texto es lo único que entra a la evidencia: nunca repite la consulta. */
export function ejecuta(nombre: string, entrada: unknown, ctx: Contexto): Resultado {
  const e = (entrada && typeof entrada === "object" ? entrada : {}) as Record<string, unknown>;
  const consulta = typeof e.consulta === "string" ? e.consulta.slice(0, 200) : "";
  if (nombre === "buscar_fichas") {
    const ns = buscarFichas(ctx.fichas, ctx.idxFichas, consulta, e.limite);
    if (!ns.length) return { texto: "Ninguna ficha de la plataforma coincide con esas palabras. Prueba con otras más generales o con otra herramienta.", fichas: [], datos: [] };
    return { texto: ns.map((n) => documento(n, ctx.fichas[n], TOPE_TEXTO)).join("\n\n"), fichas: ns, datos: [] };
  }
  if (nombre === "consultar_dato_fiscal" || nombre === "consultar_pendientes") {
    if (!ctx.datos) return { texto: "La base fiscal no está disponible en este momento. No afirmes ningún dato fiscal de memoria.", fichas: [], datos: [], error: true };
    const soloPend = nombre === "consultar_pendientes";
    const ts = terminos(consulta);
    let ds = puntos(ts, ctx.idxDatos).map((x) => ctx.datos![x.i]).filter((d) => !soloPend || d.estado === "pendiente");
    if (soloPend && !ds.length) {
      // Sin coincidencia (o sin consulta): la lista completa, en corto, para que el agente sepa qué falta.
      ds = ctx.datos.filter((d) => d.estado === "pendiente");
      return {
        texto: "Pendientes de la base fiscal de la plataforma (ninguno tiene valor todavía):\n" +
          ds.map((d) => "- [" + d.id + "] " + d.concepto + (d.quien ? " · lo debe: " + d.quien : "") + (d.url ? " <" + d.url + ">" : "")).join("\n"),
        fichas: [], datos: ds.map((d) => d.id),
      };
    }
    ds = ds.slice(0, MAX_DATOS_HERRAMIENTA);
    if (!ds.length) return { texto: "La base fiscal de la plataforma no tiene un dato con esas palabras. No lo afirmes de memoria: revisa con consultar_pendientes si es algo que sigue pendiente.", fichas: [], datos: [] };
    return { texto: ds.map((d) => datoTx(d, ctx.fuentes)).join("\n\n"), fichas: [], datos: ds.map((d) => d.id) };
  }
  return { texto: "Esa herramienta no existe.", fichas: [], datos: [], error: true };
}

// ---------------------------------------------------------------- el agente

export const INSTRUCCIONES_AGENTE = `Eres el agente lector del Auditor Virtual de Auditavisión, una plataforma ciudadana de fiscalización del gasto público en México. Una persona hizo una pregunta que el buscador de la página no pudo contestar. Tu trabajo es buscar en lo publicado por la plataforma con tus herramientas y redactar la respuesta SOLO con lo que encuentres.

Por qué importa: la plataforma vive de que cada cifra tenga su documento. Un programa revisa tu respuesta y la descarta entera si trae un solo número que no esté, tal cual, en los resultados de tus herramientas o en las fichas que venían con la pregunta. Lo que tú sepas de memoria no cuenta como fuente, aunque sea correcto.

Cómo trabajar:
- Tienes como máximo tres rondas de búsqueda. Pide en una misma ronda las búsquedas que no dependan una de otra. Si con la primera ronda alcanza, contesta.
- Las consultas a las herramientas son palabras clave, no la pregunta completa. No pongas en ellas datos personales ni montos de la persona.
- Regla fiscal, tasa, tope o plazo: consultar_dato_fiscal. Algo de 2027 que podría no estar definido aún: consultar_pendientes. Todo lo demás: buscar_fichas.

Cómo contestar:
- Toda cifra que escribas (montos, porcentajes, fechas, años, números de artículo) debe aparecer tal cual en lo que recuperaste. No calcules, no redondees, no conviertas unidades, no escribas una cifra en otra forma (si la fuente dice 3500000, no escribas 3.5 millones). Tampoco repitas una cifra de la pregunta si no la encontraste en la evidencia.
- Si la pregunta pide una cuenta con los montos de la persona, no la hagas: explica la regla con su fuente y di que la cuenta se hace en el simulador fiscal de la plataforma.
- Respeta el estado de cada dato: lo «pendiente» se dice como pendiente, con quién lo debe; lo «auditada» es una cuenta de la plataforma sobre datos oficiales; lo de 2027 rige desde la fecha que diga su vigencia.
- Si lo que encontraste no contesta la pregunta, pon sin_respuesta en true y di en una frase qué sí tiene la plataforma sobre el tema. Es mejor eso que una respuesta forzada.
- Escribe en español de México, de tú, claro, corto y cálido: dos o tres párrafos breves. Sin listas largas, sin encabezados, sin emojis. Cuando cites una ley, nombra su artículo si viene en la evidencia.
- No opines sobre partidos ni personas: describe lo que dicen los documentos. Esto no es asesoría fiscal ni legal.
- En fichas_usadas pon los números de las fichas de las que tomaste algo, y en datos_usados los id de los datos fiscales que usaste.`;

export const ESQUEMA_AGENTE = {
  type: "object",
  properties: {
    respuesta: { type: "string" },
    fichas_usadas: { type: "array", items: { type: "integer" } },
    datos_usados: { type: "array", items: { type: "string" } },
    sin_respuesta: { type: "boolean" },
  },
  required: ["respuesta", "fichas_usadas", "datos_usados", "sin_respuesta"],
  additionalProperties: false,
};

type Bloque = { type: string; text?: string; id?: string; name?: string; input?: unknown };
export type Mensaje = { role: "user" | "assistant"; content: unknown };
export type Vuelta = { content: Bloque[]; stop_reason: string | null; usage: { input_tokens: number; output_tokens: number }; model: string };
/** Lo que el agente le pide a la API en cada vuelta; index.ts le suma el modelo y lo demás. */
export type Pedido = { system: string; tools: typeof HERRAMIENTAS; tool_choice: { type: "auto" | "none" }; messages: Mensaje[] };

export type Salida = { respuesta: string; fichas_usadas: number[]; datos_usados: string[]; sin_respuesta: boolean };
export type Corrida = {
  rechazo: string | null; sal?: Salida; sueltas: string[];
  /** Todo lo que leyó el modelo, y nada de lo que escribió. */
  evidencia: string; fichas: number[]; datos: string[]; usadas: number[]; datosUsados: string[];
  herramientas: string[]; rondas: number; llamadas: number; tokens_in: number; tokens_out: number; modelo: string | null;
};

export type Semilla = { numero: number; ficha: Ficha };

/** La revisión final: cifras contra la evidencia y citas contra lo que de verdad se leyó. */
export function valida(sal: Salida, evidencia: string, fichas: number[], datos: string[]): { rechazo: string | null; sueltas: string[]; usadas: number[]; datosUsados: string[] } {
  const sueltas = sinDocumento(String(sal.respuesta ?? ""), evidencia);
  const usadas = [...new Set((sal.fichas_usadas ?? []).filter((n) => fichas.includes(n)))];
  const datosUsados = [...new Set((sal.datos_usados ?? []).filter((d) => datos.includes(d)))];
  const rechazo = sueltas.length ? "cifra_no_respaldada" : (!sal.sin_respuesta && !usadas.length && !datosUsados.length ? "ficha_no_citada" : null);
  return { rechazo, sueltas, usadas, datosUsados };
}

/**
 * El bucle del agente. `crea` es la llamada a la API (en las pruebas, un guion).
 * `limite` es el instante (ms) después del cual ya no se abren más rondas.
 */
export async function agente(
  crea: (p: Pedido) => Promise<Vuelta>,
  o: { pregunta: string; ctx: Contexto; semillas?: Semilla[]; maxRondas?: number; ahora?: () => number; limite?: number },
): Promise<Corrida> {
  const max = Math.min(MAX_RONDAS, Math.max(0, o.maxRondas ?? MAX_RONDAS));
  const semillas = o.semillas ?? [];
  const inicial = semillas.map((s) => documento(s.numero, s.ficha, TOPE_TEXTO)).join("\n\n");
  const evidencia: string[] = inicial ? [inicial] : [];
  const fichas = new Set<number>(semillas.map((s) => s.numero)), datos = new Set<string>();
  const c: Corrida = { rechazo: null, sueltas: [], evidencia: "", fichas: [], datos: [], usadas: [], datosUsados: [], herramientas: [], rondas: 0, llamadas: 0, tokens_in: 0, tokens_out: 0, modelo: null };
  const cierra = (rechazo: string | null): Corrida => ({ ...c, rechazo, evidencia: evidencia.join("\n\n"), fichas: [...fichas], datos: [...datos] });
  const messages: Mensaje[] = [{
    role: "user",
    content: (inicial ? "Fichas que el buscador de la página encontró más cercanas (pueden no servir):\n\n" + inicial + "\n\n" : "") + "<pregunta>" + o.pregunta + "</pregunta>",
  }];

  for (;;) {
    const sinTiempo = o.limite != null && (o.ahora ?? Date.now)() > o.limite;
    const ultima = c.rondas >= max || sinTiempo;
    const r = await crea({ system: INSTRUCCIONES_AGENTE, tools: HERRAMIENTAS, tool_choice: { type: ultima ? "none" : "auto" }, messages });
    c.llamadas++;
    c.tokens_in += r.usage?.input_tokens ?? 0;
    c.tokens_out += r.usage?.output_tokens ?? 0;
    c.modelo = r.model ?? c.modelo;
    if (r.stop_reason === "refusal") return cierra("negativa_modelo");
    const pide = r.content.filter((b) => b.type === "tool_use");
    if (r.stop_reason === "tool_use" && pide.length) {
      // Con las herramientas quitadas no debería pedirlas; si lo hace, no se le sigue el juego.
      if (ultima) return cierra("formato");
      c.rondas++;
      messages.push({ role: "assistant", content: r.content });
      const resultados = pide.map((b, k) => {
        if (k >= MAX_LLAMADAS_RONDA) return { type: "tool_result", tool_use_id: b.id, content: "Tope de búsquedas por ronda: esta no se hizo.", is_error: true };
        const res = ejecuta(b.name ?? "", b.input, o.ctx);
        c.herramientas.push(b.name ?? "");
        if (!res.error) evidencia.push(res.texto);
        res.fichas.forEach((n) => fichas.add(n));
        res.datos.forEach((d) => datos.add(d));
        return { type: "tool_result", tool_use_id: b.id, content: res.texto, ...(res.error ? { is_error: true } : {}) };
      });
      messages.push({ role: "user", content: resultados });
      continue;
    }
    if (r.stop_reason !== "end_turn") return cierra("formato");
    let sal: Salida;
    try {
      sal = JSON.parse(r.content.filter((b) => b.type === "text").map((b) => b.text ?? "").join(""));
      if (!sal || typeof sal.respuesta !== "string") throw new Error("sin respuesta");
    } catch {
      return cierra("formato");
    }
    const fin = cierra(null);
    const v = valida(sal, fin.evidencia, fin.fichas, fin.datos);
    return { ...fin, sal, rechazo: v.rechazo, sueltas: v.sueltas, usadas: v.usadas, datosUsados: v.datosUsados };
  }
}
