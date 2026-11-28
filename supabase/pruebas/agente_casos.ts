// Los casos del agente lector (Ronda 42), sin red y sin nada propio de Deno
// ni de Node: quien los corre les pasa la base publicada ya leída.
//   deno test --allow-read supabase/pruebas/agente_test.ts
//   python3 herramientas/prueba_agente.py      (con Node; corre en revision.py)
import {
  agente, contexto, type Contexto, datosFiscales, documento, ejecuta, type Ficha, HERRAMIENTAS, MAX_FICHAS_HERRAMIENTA,
  MAX_LLAMADAS_RONDA, type Pedido, terminos, valida, type Vuelta,
} from "../functions/_comun/agente.ts";
import { anonimo, sinIdentidad } from "../functions/_comun/anonimo.ts";
import { sinDocumento } from "../functions/_comun/cotejo.ts";

export type Base = { fichas: Ficha[]; archivos: Record<string, unknown>; fuentes: Record<string, { nombre?: string; url?: string }> };

function igual(a: unknown, b: unknown, que: string) {
  if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error(que + ": " + JSON.stringify(a) + " ≠ " + JSON.stringify(b));
}
function cierto(x: unknown, que: string) {
  if (!x) throw new Error(que);
}

/** Una vuelta del modelo que pide herramientas. */
function pide(...ll: [string, Record<string, unknown>][]): Vuelta {
  return { content: ll.map(([name, input], k) => ({ type: "tool_use", id: "tu_" + k, name, input })), stop_reason: "tool_use", usage: { input_tokens: 100, output_tokens: 20 }, model: "modelo-de-prueba" };
}
/** Una vuelta final, con la salida en JSON. */
function dice(respuesta: string, fichas_usadas: number[] = [], datos_usados: string[] = [], sin_respuesta = false): Vuelta {
  return { content: [{ type: "text", text: JSON.stringify({ respuesta, fichas_usadas, datos_usados, sin_respuesta }) }], stop_reason: "end_turn", usage: { input_tokens: 200, output_tokens: 50 }, model: "modelo-de-prueba" };
}
/** Un modelo de guion: contesta lo que sigue en la lista y anota lo que le pidieron. */
function guion(vueltas: Vuelta[]) {
  const pedidos: Pedido[] = [];
  const crea = (p: Pedido) => {
    pedidos.push(JSON.parse(JSON.stringify(p)));
    const v = vueltas[Math.min(pedidos.length - 1, vueltas.length - 1)];
    return Promise.resolve(v);
  };
  return { crea, pedidos };
}

export function casos(b: Base): [string, () => void | Promise<void>][] {
  const ctx: Contexto = contexto(b.fichas, b.archivos, b.fuentes);
  const titulos = (ns: number[]) => ns.map((n) => b.fichas[n].tit).join(" | ");
  const fiscal = (q: string) => ejecuta("consultar_dato_fiscal", { consulta: q }, ctx);
  const tope = fiscal("tope ingresos RESICO personas físicas");

  return [
    ["las palabras de búsqueda: sin vacías, sin plural, sin repetir", () => {
      igual(terminos("¿Cuánto es el tope de los ingresos del RESICO?"), ["tope", "ingreso", "resico"], "términos");
      igual(terminos("¿y de qué?"), [], "una consulta vacía");
    }],
    ["las tres herramientas tienen esquema estricto y solo leen", () => {
      igual(HERRAMIENTAS.map((h) => h.name), ["buscar_fichas", "consultar_dato_fiscal", "consultar_pendientes"], "nombres");
      for (const h of HERRAMIENTAS) cierto(h.strict === true && h.input_schema.additionalProperties === false, "esquema de " + h.name);
    }],
    ["buscar_fichas encuentra la ficha por su tema", () => {
      for (const [q, debe] of [["Tren Maya ASF por aclarar", "Tren Maya"], ["deuda Nuevo León", "Nuevo León"], ["huachicol fiscal", "Huachicol"], ["sueldo presidenta", "Presidenta"]]) {
        const r = ejecuta("buscar_fichas", { consulta: q, limite: 4 }, ctx);
        cierto(r.fichas.length > 0 && b.fichas[r.fichas[0]].tit.includes(debe), "«" + q + "» debía abrir con «" + debe + "»: " + titulos(r.fichas));
        cierto(r.fichas.every((n) => r.texto.includes("<ficha numero=\"" + n + "\">")), "cada ficha va con su número");
      }
    }],
    ["buscar_fichas nunca pasa de seis ni repite la consulta", () => {
      const r = ejecuta("buscar_fichas", { consulta: "presupuesto 987654321", limite: 50 }, ctx);
      igual(r.fichas.length, MAX_FICHAS_HERRAMIENTA, "tope de fichas");
      cierto(!r.texto.includes("987654321"), "la consulta no entra al resultado");
      const nada = ejecuta("buscar_fichas", { consulta: "xyzzy 31415926", limite: 4 }, ctx);
      igual(nada.fichas, [], "sin coincidencias");
      cierto(!/\d/.test(nada.texto), "el «no encontré» no trae cifras");
    }],
    ["la ficha de siempre no cambia; la del agente se recorta y lo dice", () => {
      const f: Ficha = { t: "cifra", tit: "Prueba", txt: "Texto de 2026.", ci: [{ v: "$1,234.5 mdp", etq: "Gasto", e: "oficial", op: "a + b" }], fu: [{ tx: "PEF 2026", url: "https://dof.gob.mx/" }] };
      igual(documento(7, f), "<ficha numero=\"7\">\nTítulo: Prueba\nTexto: Texto de 2026.\nCifras:\n- $1,234.5 mdp · Gasto [oficial] (operación: a + b)\nFuentes:\n- PEF 2026 <https://dof.gob.mx/>\n</ficha>", "formato de la ficha");
      const larga = documento(1, { t: "pagina", tit: "Larga", txt: "a".repeat(1400) + " cifra 777888 " + "b".repeat(400) }, 1500);
      cierto(larga.includes("777888") && larga.includes("[…la ficha sigue en la plataforma]") && larga.length < 1700, "recorte");
    }],
    ["consultar_dato_fiscal trae el valor, el estado y la cita textual", () => {
      igual(tope.datos[0], "resico-pf-tope-2026", "el tope del RESICO");
      cierto(tope.texto.includes("estado=\"oficial\"") && tope.texto.includes("3500000") && tope.texto.includes("Cita textual (") && tope.texto.includes("Art. 113-E"), "valor, estado y cita");
      cierto(tope.datos.includes("resico-pf-tope-2027") && tope.texto.includes("Vigencia desde: 2027-01-01"), "lo de 2027 dice su vigencia");
      const uma = fiscal("UMA 2026");
      igual(uma.datos[0], "uma-2026", "la UMA");
      cierto(uma.texto.includes("117.31") && uma.texto.includes("https://dof.gob.mx/"), "valor y liga del DOF");
      const agui = fiscal("aguinaldo exento");
      cierto(agui.texto.includes("estado=\"auditada\"") && agui.texto.includes("Operación (dato auditado"), "un dato auditado dice su operación");
      igual(fiscal("iva saldo a favor").datos[0], "iva-saldo-a-favor", "el IVA a favor");
    }],
    ["la base fiscal completa entra a la herramienta", () => {
      const ds = datosFiscales(b.archivos);
      igual(new Set(ds.map((d) => d.id)).size, ds.length, "ningún id repetido");
      cierto(ds.every((d) => d.estado === "pendiente" ? d.motivo && d.quien && d.url : (d.citas ?? []).length > 0), "cada dato con su cita, o pendiente con motivo, quién y liga");
    }],
    ["consultar_pendientes dice qué falta, quién lo debe y nunca un valor", () => {
      const rmf = ejecuta("consultar_pendientes", { consulta: "RMF 2027" }, ctx);
      cierto(rmf.datos.includes("rmf-2027"), "la RMF 2027 sigue pendiente: " + rmf.datos.join(", "));
      cierto(rmf.texto.includes("PENDIENTE") && rmf.texto.includes("Quién lo debe:") && !rmf.texto.includes("Valor:"), "pendiente sin valor");
      const todos = ejecuta("consultar_pendientes", { consulta: "" }, ctx);
      const pend = datosFiscales(b.archivos).filter((d) => d.estado === "pendiente").map((d) => d.id);
      igual(todos.datos, pend, "sin consulta, la lista completa");
      for (const id of ["uma-2027", "salario-minimo-2027", "scjn-pj-209-2026"]) cierto(pend.includes(id), "pendiente esperado: " + id);
      const mezcla = fiscal("UMA 2027");
      cierto(mezcla.texto.includes("no lo afirmes ni lo estimes"), "un pendiente que sale en la búsqueda fiscal va como pendiente");
    }],
    ["sin base fiscal, la herramienta lo dice y no entra a la evidencia", async () => {
      const sin = contexto(b.fichas, null);
      const r = ejecuta("consultar_dato_fiscal", { consulta: "UMA" }, sin);
      cierto(r.error === true && r.datos.length === 0, "error sin datos");
      const g = guion([pide(["consultar_dato_fiscal", { consulta: "UMA 2026" }]), dice("La UMA diaria es de 117.31 pesos.", [], ["uma-2026"])]);
      const c = await agente(g.crea, { pregunta: "¿cuánto es la UMA?", ctx: sin });
      igual(c.rechazo, "cifra_no_respaldada", "sin evidencia no pasa ninguna cifra");
    }],
    ["el candado acepta las cifras exactas de las herramientas y tira las inventadas", () => {
      igual(sinDocumento("El tope del RESICO para personas físicas es de $3,500,000 al año (art. 113-E de la LISR) y desde 2027 será de 5,000,000.", tope.texto), [], "cifras exactas, con otro formato");
      igual(sinDocumento("El tope es de 3.5 millones de pesos.", tope.texto), ["3.5"], "la misma cifra en otra forma");
      igual(sinDocumento("El tope es de $4,000,000.", tope.texto), ["4000000"], "cifra inventada");
      igual(sinDocumento("Eso es el 12 % de tus ingresos.", tope.texto), ["12"], "porcentaje calculado");
    }],
    ["el agente busca, redacta y pasa la revisión", async () => {
      const g = guion([
        pide(["consultar_dato_fiscal", { consulta: "tope ingresos RESICO personas físicas" }], ["consultar_pendientes", { consulta: "RMF 2027" }]),
        dice("En 2026 el tope del RESICO para personas físicas es de $3,500,000 al año (LISR, art. 113-E). Desde el 1 de enero de 2027 sube a $5,000,000.", [], ["resico-pf-tope-2026", "resico-pf-tope-2027", "no-existe"]),
      ]);
      const c = await agente(g.crea, { pregunta: "¿cuál es el tope del RESICO?", ctx });
      igual([c.rechazo, c.rondas, c.llamadas, c.herramientas], [null, 1, 2, ["consultar_dato_fiscal", "consultar_pendientes"]], "una ronda, dos herramientas");
      igual(c.datosUsados, ["resico-pf-tope-2026", "resico-pf-tope-2027"], "solo cuentan los datos que de verdad leyó");
      igual([c.tokens_in, c.tokens_out, c.modelo], [300, 70, "modelo-de-prueba"], "tokens sumados");
      igual(g.pedidos[0].tool_choice.type, "auto", "con herramientas al empezar");
      const vuelta = g.pedidos[1].messages[2].content as { type: string; tool_use_id: string }[];
      igual(vuelta.map((x) => [x.type, x.tool_use_id]), [["tool_result", "tu_0"], ["tool_result", "tu_1"]], "todos los resultados en un solo mensaje");
    }],
    ["tope de rondas: a la cuarta vuelta ya no hay herramientas", async () => {
      const g = guion([pide(["buscar_fichas", { consulta: "Tren Maya", limite: 2 }])]);
      const c = await agente(g.crea, { pregunta: "¿y el Tren Maya?", ctx });
      igual([c.rondas, c.llamadas, c.rechazo], [3, 4, "formato"], "tres rondas y una vuelta final");
      igual(g.pedidos.map((p) => p.tool_choice.type), ["auto", "auto", "auto", "none"], "la cuarta va sin herramientas");
      const g2 = guion([pide(["buscar_fichas", { consulta: "Tren Maya", limite: 2 }]), pide(["buscar_fichas", { consulta: "ASF", limite: 2 }]), pide(["buscar_fichas", { consulta: "Fonatur", limite: 2 }]), dice("No encontré lo que buscas; la plataforma sí tiene el expediente del Tren Maya.", [], [], true)]);
      const c2 = await agente(g2.crea, { pregunta: "¿y el Tren Maya?", ctx });
      igual([c2.rondas, c2.llamadas, c2.rechazo], [3, 4, null], "tres rondas y respuesta");
    }],
    ["tope de llamadas por ronda y herramienta que no existe", async () => {
      const cuatro: [string, Record<string, unknown>][] = ["Tren Maya", "Dos Bocas", "AIFA", "Mexicana"].map((q) => ["buscar_fichas", { consulta: q, limite: 1 }]);
      const g = guion([pide(...cuatro, ["navegar_internet", { url: "https://ejemplo.mx" }]), dice("Sin datos.", [], [], true)]);
      const c = await agente(g.crea, { pregunta: "¿obras?", ctx });
      igual(c.herramientas.length, MAX_LLAMADAS_RONDA, "solo corren tres");
      const res = g.pedidos[1].messages[2].content as { is_error?: boolean }[];
      igual(res.map((x) => !!x.is_error), [false, false, false, true, true], "las de más, con error");
    }],
    ["una cifra inventada tira la respuesta, aunque venga en la pregunta o en la consulta", async () => {
      const g = guion([pide(["consultar_dato_fiscal", { consulta: "tope RESICO 4200000" }]), dice("El tope es de $4,200,000 al año.", [], ["resico-pf-tope-2026"])]);
      const c = await agente(g.crea, { pregunta: "¿es cierto que el tope del RESICO es de 4,200,000?", ctx });
      igual([c.rechazo, c.sueltas], ["cifra_no_respaldada", ["4200000"]], "ni la pregunta ni la consulta son evidencia");
      cierto(!c.evidencia.includes("4200000") && !c.evidencia.includes("4,200,000"), "la evidencia solo trae lo que devolvieron las herramientas");
    }],
    ["una respuesta sin fuente leída no pasa; decir que no hay respuesta, sí", async () => {
      const g = guion([pide(["buscar_fichas", { consulta: "Tren Maya", limite: 2 }]), dice("El Tren Maya es una obra federal.", [999999], [])]);
      igual((await agente(g.crea, { pregunta: "¿qué es?", ctx })).rechazo, "ficha_no_citada", "cita una ficha que no leyó");
      const g2 = guion([dice("La plataforma no tiene ese dato.", [], [], true)]);
      const c2 = await agente(g2.crea, { pregunta: "¿qué es?", ctx });
      igual([c2.rechazo, c2.rondas, c2.llamadas], [null, 0, 1], "sin respuesta y sin cifras");
      igual(valida({ respuesta: "Sí.", fichas_usadas: [3], datos_usados: [], sin_respuesta: false }, "", [3], []).rechazo, null, "con ficha leída");
    }],
    ["las fichas que manda la página son evidencia y se pueden citar", async () => {
      const n = ejecuta("buscar_fichas", { consulta: "Tren Maya ASF por aclarar", limite: 1 }, ctx).fichas[0];
      const cifra = (b.fichas[n].ci ?? [])[0];
      cierto(cifra, "la ficha de prueba trae cifras");
      const g = guion([dice("La ASF anotó " + cifra.v + ".", [n], [])]);
      const c = await agente(g.crea, { pregunta: "¿qué dejó la ASF?", ctx, semillas: [{ numero: n, ficha: b.fichas[n] }] });
      igual([c.rechazo, c.usadas, c.rondas], [null, [n], 0], "contesta con la semilla, sin rondas");
      cierto(String(g.pedidos[0].messages[0].content).includes("<ficha numero=\"" + n + "\">"), "la semilla va en el primer mensaje");
    }],
    ["negativa del modelo, salida rota y plazo vencido", async () => {
      const neg: Vuelta = { content: [], stop_reason: "refusal", usage: { input_tokens: 5, output_tokens: 0 }, model: "m" };
      igual((await agente(guion([neg]).crea, { pregunta: "¿x?", ctx })).rechazo, "negativa_modelo", "negativa");
      const rota: Vuelta = { content: [{ type: "text", text: "{no es json" }], stop_reason: "end_turn", usage: { input_tokens: 5, output_tokens: 5 }, model: "m" };
      igual((await agente(guion([rota]).crea, { pregunta: "¿x?", ctx })).rechazo, "formato", "salida rota");
      const corta: Vuelta = { content: [{ type: "text", text: "{\"respuesta\":\"a" }], stop_reason: "max_tokens", usage: { input_tokens: 5, output_tokens: 5 }, model: "m" };
      igual((await agente(guion([corta]).crea, { pregunta: "¿x?", ctx })).rechazo, "formato", "salida cortada");
      const g = guion([dice("Sin datos.", [], [], true)]);
      await agente(g.crea, { pregunta: "¿x?", ctx, ahora: () => 100, limite: 50 });
      igual(g.pedidos[0].tool_choice.type, "none", "con el plazo vencido no se abren rondas");
    }],
    ["al modelo, sin identidad; al registro, además sin montos", () => {
      const q = "Soy XAXX010101000, mi correo es ana@ejemplo.mx y mi cel 55 1234 5678: ¿es cierto que el tope del RESICO es de $3,500,000?";
      igual(sinIdentidad(q), "Soy [RFC], mi correo es [CORREO] y mi cel [TELEFONO]: ¿es cierto que el tope del RESICO es de $3,500,000?", "al modelo");
      igual(anonimo(q), "Soy [RFC], mi correo es [CORREO] y mi cel [TELEFONO]: ¿es cierto que el tope del RESICO es de [MONTO]?", "al registro");
      igual(sinIdentidad("¿qué cambia en 2027 con el art. 113-E?"), "¿qué cambia en 2027 con el art. 113-E?", "una pregunta sin datos personales no cambia");
    }],
  ];
}
