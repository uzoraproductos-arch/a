// El segundo candado del buzón de aprendizaje (Ronda 41). La pregunta ya sale
// anonimizada del navegador (FiscalCalc.anonimiza de fiscal-calculo.js); aquí
// se vuelve a pasar por si llega de otro lado: lo que parezca correo, CURP, RFC,
// teléfono o monto se cambia por su marca antes de tocar la base. El tercer
// candado es la restricción de la tabla (migración 20261128000001).
// Va aparte para probarlo sin red (supabase/pruebas/anonimo_test.ts).

const REGLAS: [RegExp, string][] = [
  [/[\w.+-]+@[\w-]+(?:\.[\w-]+)+/g, "[CORREO]"],
  [/(^|[^A-Za-z\d])[A-Za-zÑñ]{4}\d{6}[HMhm][A-Za-zÑñ]{5}[A-Za-z\d]\d(?![A-Za-z\d])/g, "$1[CURP]"],
  [/(^|[^A-Za-z\d])[A-Za-zÑñ&]{3,4}-?\d{6}-?[A-Za-z\d]{3}(?![A-Za-z\d])/g, "$1[RFC]"],
  [/(^|[^\d$,.])(?:\+?\d{1,3}[ .-]?)?\(?\d{2,3}\)?[ .-]?\d{3,4}[ .-]?\d{4}(?!\d|[,.]\d)/g, "$1[TELEFONO]"],
  [/(?:\$\s?)(?:\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)(?:\s?(?:mil millones|millones|mill[oó]n|mdp|mil|k)(?![A-Za-zÁÉÍÓÚÑáéíóúñ]))?(?:\s?(?:de\s)?(?:pesos|mxn)(?![A-Za-zÁÉÍÓÚÑáéíóúñ]))?/gi, "[MONTO]"],
  [/(?:\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)\s?(?:mil millones|millones|mill[oó]n|mdp|mil|k)(?![A-Za-zÁÉÍÓÚÑáéíóúñ])(?:\s?(?:de\s)?(?:pesos|mxn)(?![A-Za-zÁÉÍÓÚÑáéíóúñ]))?/gi, "[MONTO]"],
  [/(?:\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)\s?(?:de\s)?(?:pesos|mxn)(?![A-Za-zÁÉÍÓÚÑáéíóúñ])/gi, "[MONTO]"],
  [/\d{1,3}(?:,\d{3})+(?:\.\d+)?/g, "[MONTO]"],
  [/\d{5,}(?:\.\d+)?/g, "[MONTO]"],
  [/\$\s?(?=\d)/g, ""],
  [/@/g, " "],
];

/** Las reglas que quitan lo que identifica a una persona (correo, CURP, RFC y teléfono): las cuatro primeras. */
const IDENTIDAD = 4;

/**
 * La pregunta sin correo, CURP, RFC ni teléfono, pero con sus cifras: es lo que
 * auditor-ia le manda al modelo (Ronda 42). Los montos se quedan porque una
 * pregunta libre los necesita para entenderse («¿el tope es de 3.5 millones?»);
 * lo que se guarda en consultas_ia sí pasa por anonimo().
 */
export function sinIdentidad(t: string): string {
  let s = t.replace(/\s+/g, " ").trim();
  for (const [re, marca] of REGLAS.slice(0, IDENTIDAD)) s = s.replace(re, marca);
  return s.replace(/\s+/g, " ").trim();
}

/** La pregunta, sin nada que identifique a una persona ni un monto exacto. */
export function anonimo(t: string): string {
  let s = t.replace(/\s+/g, " ").trim();
  for (const [re, marca] of REGLAS) s = s.replace(re, marca);
  return s.replace(/\s+/g, " ").trim();
}

/** Lo que la tabla rechazaría: una arroba, un signo de pesos con cifra o cinco dígitos seguidos. */
export function traeDatos(t: string): boolean {
  return /@|\d{5,}|\$\s?\d/.test(t);
}
