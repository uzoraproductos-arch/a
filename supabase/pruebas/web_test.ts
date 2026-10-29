// deno test supabase/pruebas/web_test.ts
// Pruebas de lo que buscar-web puede devolver (sin red).
import { clasifica, claveDe, enlaces, nombreValido } from "../functions/_comun/web.ts";

function assertEquals(a: unknown, b: unknown) {
  if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error(JSON.stringify(a) + " ≠ " + JSON.stringify(b));
}

Deno.test("clasifica: oficial, prensa y lo demás fuera", () => {
  assertEquals(clasifica("https://www.dof.gob.mx/nota.php?id=1")?.tipo, "oficial");
  assertEquals(clasifica("https://comunicacionsocial.diputados.gob.mx/x")?.tipo, "oficial");
  assertEquals(clasifica("https://www.justice.gov/usao-edny/pr/x")?.tipo, "oficial");
  assertEquals(clasifica("https://www.proceso.com.mx/nacional/x")?.tipo, "prensa");
  assertEquals(clasifica("https://gob.mx.sitio-falso.com/x"), null);
  assertEquals(clasifica("http://www.dof.gob.mx/x"), null);
  assertEquals(clasifica("https://usuario:clave@www.gob.mx/x"), null);
  assertEquals(clasifica("https://www.facebook.com/x"), null);
});

Deno.test("nombreValido: solo nombres, sin cifras ni código", () => {
  assertEquals(nombreValido("  Rocío   Nahle "), "Rocío Nahle");
  assertEquals(nombreValido("Genaro García Luna"), "Genaro García Luna");
  assertEquals(nombreValido("Fulano"), null);
  assertEquals(nombreValido("Fulano 123"), null);
  assertEquals(nombreValido("<script>alert(1)</script>"), null);
  assertEquals(claveDe("Rocío Nahle García"), "rocio nahle garcia");
});

Deno.test("enlaces: solo resultados del buscador, oficiales primero, sin texto del modelo", () => {
  const contenido = [
    { type: "text", text: "Fulana desvió 500 millones" },
    { type: "server_tool_use" },
    {
      type: "web_search_tool_result", content: [
        { type: "web_search_result", url: "https://www.proceso.com.mx/a#c", title: "Nota", page_age: "2026-01-02" },
        { type: "web_search_result", url: "https://www.foro-anonimo.net/b", title: "Rumor" },
        { type: "web_search_result", url: "https://www.asf.gob.mx/c", title: "Informe" },
        { type: "web_search_result", url: "https://www.proceso.com.mx/a", title: "Repetida" },
      ],
    },
    { type: "web_search_tool_result", content: { type: "web_search_tool_result_error", error_code: "max_uses_exceeded" } },
  ];
  const l = enlaces(contenido);
  assertEquals(l.map((x) => x.sitio), ["asf.gob.mx", "proceso.com.mx"]);
  assertEquals(l[1].url, "https://www.proceso.com.mx/a");
  assertEquals(l[1].fecha, "2026-01-02");
  assertEquals(JSON.stringify(l).includes("500 millones"), false);
});
