// deno test --allow-read supabase/pruebas/agente_test.ts
// Los casos viven en agente_casos.ts; aquí solo se lee la base publicada del
// repositorio (asistente-base.js y docs/fiscal-2027/), sin red.
import { ARCHIVOS_FISCALES } from "../functions/_comun/agente.ts";
import { type Base, casos } from "./agente_casos.ts";

const raiz = new URL("../../", import.meta.url);
const lee = (r: string) => Deno.readTextFileSync(new URL(r, raiz));
const s = lee("assets/auditor/js/asistente-base.js");
const i = s.indexOf("window.AUDITOR_BASE = "), j = s.lastIndexOf("};");
const base: Base = {
  fichas: JSON.parse(s.slice(i + "window.AUDITOR_BASE = ".length, j + 1)).fichas,
  archivos: Object.fromEntries(ARCHIVOS_FISCALES.map((n) => [n, JSON.parse(lee("docs/fiscal-2027/" + n + ".json"))])),
  fuentes: JSON.parse(lee("docs/fiscal-2027/fuentes.json")).fuentes,
};
for (const [nombre, fn] of casos(base)) Deno.test(nombre, fn);
