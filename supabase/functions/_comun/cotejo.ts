// El candado de cifras de auditor-ia: toda cifra de la respuesta tiene que
// estar en las fichas que recibió la IA. Va aparte para probarlo sin red
// (supabase/pruebas/cotejo_test.ts).

/** Las cifras de un texto, normalizadas: «$1,234.5», «1 234.5» y «1234.50» son la misma. */
export function cifras(t: string): string[] {
  return (t.match(/\d{1,3}(?:[ ,]\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?/g) ?? []).map((x) => String(Number(x.replace(/[ ,]/g, ""))));
}

/** Las cifras de la respuesta que no aparecen en las fichas. */
export function sinDocumento(respuesta: string, fichas: string): string[] {
  const ok = new Set(cifras(fichas));
  return [...new Set(cifras(respuesta).filter((c) => !ok.has(c)))];
}
