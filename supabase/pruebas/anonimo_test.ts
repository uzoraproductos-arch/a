// deno test supabase/pruebas/anonimo_test.ts
import { anonimo, traeDatos } from "../functions/_comun/anonimo.ts";

function igual(a: unknown, b: unknown, que: string) {
  if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error(que + ": " + JSON.stringify(a) + " ≠ " + JSON.stringify(b));
}

Deno.test("deja igual lo que ya viene anonimizado", () => {
  const q = "¿Me conviene el RESICO si cobro [MONTO] al mes y mi RFC es [RFC]?";
  igual(anonimo(q), q, "ya anónima");
  igual(anonimo("¿me conviene el 7 % o el 16 % de IVA en 2027 según el art. 25?"), "¿me conviene el 7 % o el 16 % de IVA en 2027 según el art. 25?", "tasas, años y artículos se quedan");
});

Deno.test("quita lo que identifica y los montos", () => {
  igual(anonimo("escríbanme a ana.perez@correo.com.mx"), "escríbanme a [CORREO]", "correo");
  igual(anonimo("mi curp es BADD110313HCMLNS09"), "mi curp es [CURP]", "CURP");
  igual(anonimo("la empresa EKU9003173C9 y yo, XAXX010101000"), "la empresa [RFC] y yo, [RFC]", "RFC");
  igual(anonimo("mi cel es 55 1234 5678"), "mi cel es [TELEFONO]", "teléfono");
  igual(anonimo("gané $360,000.50, me retuvieron 55000 y gasté 35 mil pesos"), "gané [MONTO], me retuvieron [MONTO] y gasté [MONTO]", "montos");
  igual(anonimo("facturo 1.5 millones al año"), "facturo [MONTO] al año", "millones");
});

Deno.test("nada de lo que devuelve lo rechazaría la tabla", () => {
  for (const q of ["a@b.mx 5512345678 $80,000", "XAXX010101000 gana 123456789 pesos", "@@@ $ 9 99999"]) {
    igual(traeDatos(anonimo(q)), false, q);
  }
});
