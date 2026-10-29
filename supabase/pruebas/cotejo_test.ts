// deno test supabase/pruebas/cotejo_test.ts
import { cifras, sinDocumento } from "../functions/_comun/cotejo.ts";

function igual(a: unknown, b: unknown, que: string) {
  if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error(que + ": " + JSON.stringify(a) + " ≠ " + JSON.stringify(b));
}

const FICHA = "Tren Maya: dejó $785.3 mdp por aclarar y promovió 14 pliegos. El tramo 4, Izamal-Cancún, concentra $352.3 mdp: el 45 % del total. Gasto: $1,234,567.8 mdp en 2026.";

Deno.test("lee las cifras con o sin separadores", () => {
  igual(cifras("$1,234,567.8 y 1 234 567.8 y 1234567.80"), ["1234567.8", "1234567.8", "1234567.8"], "separadores");
  igual(cifras("el tramo 4, 352.3 mdp"), ["4", "352.3"], "una coma de enumeración no une cifras");
});

Deno.test("deja pasar una respuesta que solo usa cifras de la ficha", () => {
  igual(sinDocumento("La ASF dejó $785.3 mdp por aclarar; el tramo 4 concentra el 45 %.", FICHA), [], "respuesta fiel");
  igual(sinDocumento("En 2026 se gastaron 1 234 567.8 millones.", FICHA), [], "misma cifra con otro formato");
});

Deno.test("detiene una cifra inventada, redondeada o calculada", () => {
  igual(sinDocumento("Dejó unos $785 mdp por aclarar.", FICHA), ["785"], "redondeo");
  igual(sinDocumento("Es el 46 % del total.", FICHA), ["46"], "porcentaje inventado");
  igual(sinDocumento("Entre los dos suman $1,137.6 mdp.", FICHA), ["1137.6"], "suma que la ficha no trae");
});
