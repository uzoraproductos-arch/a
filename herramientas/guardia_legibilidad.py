#!/usr/bin/env python3
"""Guardia de legibilidad de Auditavisión.

Mide, en un celular simulado (390 x 844), lo mismo que midió la auditoría del
29-09-2026 (docs/ux/PLAN.md §1) y falla si la plataforma no cumple las metas de
la fase indicada. Sirve para que ningún cambio, de una persona o de una IA,
vuelva a achicar la letra o a llenar de emojis los rótulos.

Uso:
    python3 herramientas/guardia_legibilidad.py            # fase 0: solo reporta
    python3 herramientas/guardia_legibilidad.py --fase 1   # falla si no cumple la fase 1
    python3 herramientas/guardia_legibilidad.py --guardar-linea-base
    python3 herramientas/guardia_legibilidad.py --vistas portada calculadora

Requisitos (solo para esta herramienta; el sitio sigue sin instalar nada):
    pip install playwright && python3 -m playwright install chromium

Corrección urgente de una cifra: GUARDIA_OMITIR="motivo" deja pasar el cambio,
pero el motivo se imprime y debe quedar en el mensaje del commit.
"""

import argparse
import functools
import http.server
import json
import os
import socketserver
import sys
import threading
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LINEA_BASE = RAIZ / "herramientas" / "guardia_linea_base.json"

# Las 11 vistas de la auditoría. La portada se mide tal como carga; cada módulo,
# en una página recién cargada, después de abrirlo como lo abre el menú.
VISTAS = [
    "portada",
    "presupuesto",
    "megaobras",
    "proyeccion2027",
    "ambiente",
    "territorio",
    "municipios",
    "calculadora",
    "poderes",
    "verificador",
    "portal",
]

# Metas escalonadas (docs/ux/PLAN.md §5, fase 0). None = no se exige en esa fase.
METAS = {
    1: {
        "pct_menor_12px": 10,
        "emojis_en_rotulos": 0,
        "errores_consola": 0,
        "desborde_px": 0,
    },
    2: {
        "pct_menor_12px": 2,
        "pct_menor_14px": 10,
        "tamanos_distintos": 8,
        "emojis_en_rotulos": 0,
        "tocables_menores_44px": 0,
        "titulo_visible_al_abrir": True,
        "errores_consola": 0,
        "desborde_px": 0,
    },
}

# Se ejecuta dentro de la página. Reglas de conteo, fijas para que la línea
# base y las mediciones siguientes sean comparables:
#  - Solo cuenta texto visible (con caja, sin display:none ni visibility:hidden,
#    opacidad > 0.05). El porcentaje es por caracteres, no por elementos.
#  - Emojis: \p{Extended_Pictographic} sobre el texto visible. «En rótulos» =
#    dentro de títulos, botones, enlaces, pestañas, etiquetas y encabezados de tabla.
#  - Tocable: a, button, input, select, textarea, [onclick], [role=button|tab].
#  - Título visible al abrir: el primer h2/h3 visible dentro de #contenido tiene
#    su borde superior dentro de la pantalla después de abrir el módulo.
MEDIR_JS = r"""
() => {
  const visible = el => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden'
      && s.display !== 'none' && parseFloat(s.opacity) > 0.05;
  };
  const EMOJI = /\p{Extended_Pictographic}/gu;
  const ROTULOS = 'h1,h2,h3,h4,h5,h6,button,a,label,summary,th,legend,[role=tab],[role=button]';
  let total = 0, menor12 = 0, menor14 = 0, emojis = 0, emojisRotulo = 0;
  const tamanos = {};
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = w.nextNode())) {
    const t = n.textContent.trim();
    const el = n.parentElement;
    if (!t || !el || ['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(el.tagName) || !visible(el)) continue;
    const fs = parseFloat(getComputedStyle(el).fontSize);
    total += t.length;
    tamanos[Math.round(fs * 2) / 2] = true;
    if (fs < 12) menor12 += t.length;
    if (fs < 14) menor14 += t.length;
    const e = (t.match(EMOJI) || []).length;
    emojis += e;
    if (e && el.closest(ROTULOS)) emojisRotulo += e;
  }
  const tocables = [...document.querySelectorAll(
    'a,button,input,select,textarea,[onclick],[role=button],[role=tab]')].filter(visible);
  const chicos = h => tocables.filter(el => {
    const r = el.getBoundingClientRect();
    return r.height < h || r.width < h;
  }).length;
  const main = document.getElementById('contenido') || document.body;
  const titulo = [...main.querySelectorAll('h2,h3')].find(visible);
  const top = titulo ? titulo.getBoundingClientRect().top : null;
  return {
    pct_menor_12px: total ? Math.round(100 * menor12 / total) : 0,
    pct_menor_14px: total ? Math.round(100 * menor14 / total) : 0,
    tamanos_distintos: Object.keys(tamanos).length,
    emojis_visibles: emojis,
    emojis_en_rotulos: emojisRotulo,
    tocables: tocables.length,
    tocables_menores_44px: chicos(44),
    tocables_menores_32px: chicos(32),
    titulo_visible_al_abrir: top !== null && top >= 0 && top < innerHeight,
    desplazamiento_px: Math.round(scrollY),
    alto_en_pantallas: +(document.documentElement.scrollHeight / innerHeight).toFixed(1),
    desborde_px: Math.max(0, document.documentElement.scrollWidth - innerWidth),
  };
}
"""


class _Silencioso(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def servir_repo():
    """Sirve el repositorio en un puerto libre de 127.0.0.1 y devuelve la URL."""
    manejador = functools.partial(_Silencioso, directory=str(RAIZ))
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), manejador)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{srv.server_address[1]}/", srv


def medir_vista(navegador, url, vista):
    ctx = navegador.new_context(viewport={"width": 390, "height": 844},
                                device_scale_factor=2, is_mobile=True, has_touch=True)
    pagina = ctx.new_page()
    errores = []
    pagina.on("pageerror", lambda e: errores.append(str(e)[:200]))
    pagina.on("console", lambda m: errores.append(m.text[:200]) if m.type == "error" else None)
    pagina.goto(url, wait_until="load", timeout=60000)
    pagina.wait_for_function("() => window.AuditEngine", timeout=30000)
    pagina.wait_for_timeout(1500)
    if vista != "portada":
        pagina.evaluate("m => window.AuditEngine.seleccionarModuloExplorer(m)", vista)
        pagina.wait_for_timeout(1500)
    datos = pagina.evaluate(MEDIR_JS)
    datos["errores_consola"] = len(errores)
    datos["detalle_errores"] = errores[:5]
    ctx.close()
    return datos


def medir_tiempo_interactivo(navegador, url):
    """Carga la portada en un Android de gama media simulado: CPU 4x más lenta y
    4G lento (1.6 Mbps de bajada, 150 ms de latencia). Devuelve los segundos hasta
    que el motor está listo para usarse."""
    ctx = navegador.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
    pagina = ctx.new_page()
    cdp = ctx.new_cdp_session(pagina)
    cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
    cdp.send("Network.enable")
    cdp.send("Network.emulateNetworkConditions", {
        "offline": False, "latency": 150,
        "downloadThroughput": 1.6 * 1024 * 1024 / 8, "uploadThroughput": 750 * 1024 / 8})
    t0 = time.monotonic()
    pagina.goto(url, wait_until="load", timeout=180000)
    pagina.wait_for_function("() => window.AuditEngine", timeout=180000)
    segundos = round(time.monotonic() - t0, 1)
    ctx.close()
    return segundos


def revisar(resultados, fase):
    """Devuelve la lista de incumplimientos contra las metas de la fase."""
    metas = METAS.get(fase)
    if not metas:
        return []
    fallas = []
    for vista, datos in resultados["vistas"].items():
        for clave, meta in metas.items():
            valor = datos.get(clave)
            if isinstance(meta, bool):
                if valor is not meta and vista != "portada":
                    fallas.append(f"{vista}: {clave} = {valor} (meta: {meta})")
            elif valor is not None and valor > meta:
                fallas.append(f"{vista}: {clave} = {valor} (meta: ≤ {meta})")
    return fallas


def imprimir(resultados, base):
    cols = ["pct_menor_12px", "pct_menor_14px", "tamanos_distintos", "emojis_en_rotulos",
            "tocables_menores_44px", "titulo_visible_al_abrir", "errores_consola"]
    cortos = ["<12px%", "<14px%", "tamaños", "emoji-rót", "toc<44", "título", "errores"]
    print(f"\n{'vista':<16}" + "".join(f"{c:>11}" for c in cortos))
    for vista, d in resultados["vistas"].items():
        fila = f"{vista:<16}"
        for c in cols:
            v = d.get(c)
            previo = (base or {}).get("vistas", {}).get(vista, {}).get(c)
            txt = ("sí" if v else "no") if isinstance(v, bool) else str(v)
            if isinstance(v, (int, float)) and not isinstance(v, bool) and isinstance(previo, (int, float)) and previo != v:
                txt += f"({v - previo:+})"
            fila += f"{txt:>11}"
        print(fila)
    if "tiempo_interactivo_s" in resultados:
        print(f"\nTiempo hasta usar la portada (Android simulado): {resultados['tiempo_interactivo_s']} s")


def main():
    ap = argparse.ArgumentParser(description="Guardia de legibilidad de Auditavisión")
    ap.add_argument("--fase", type=int, default=0, choices=[0, 1, 2],
                    help="0 = solo reporta; 1 y 2 = falla si no se cumplen las metas")
    ap.add_argument("--vistas", nargs="+", choices=VISTAS, default=VISTAS)
    ap.add_argument("--url", help="medir un sitio ya servido en lugar de servir el repo")
    ap.add_argument("--sin-tiempo", action="store_true", help="omitir la carga con CPU y red lentas")
    ap.add_argument("--guardar-linea-base", action="store_true")
    ap.add_argument("--json", help="guardar el resultado completo en este archivo")
    args = ap.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Falta Playwright: pip install playwright && python3 -m playwright install chromium")

    srv = None
    url = args.url
    if not url:
        url, srv = servir_repo()

    resultados = {"fecha": time.strftime("%Y-%m-%d %H:%M"), "vistas": {}}
    with sync_playwright() as p:
        ejecutable = os.environ.get("GUARDIA_CHROMIUM")  # opcional: un Chromium ya instalado
        navegador = p.chromium.launch(executable_path=ejecutable) if ejecutable else p.chromium.launch()
        for vista in args.vistas:
            print(f"midiendo {vista}…", file=sys.stderr)
            resultados["vistas"][vista] = medir_vista(navegador, url, vista)
        if not args.sin_tiempo:
            print("midiendo tiempo con CPU y red lentas…", file=sys.stderr)
            resultados["tiempo_interactivo_s"] = medir_tiempo_interactivo(navegador, url)
        navegador.close()
    if srv:
        srv.shutdown()

    base = json.loads(LINEA_BASE.read_text(encoding="utf-8")) if LINEA_BASE.exists() else None
    imprimir(resultados, base)

    if args.json:
        Path(args.json).write_text(json.dumps(resultados, ensure_ascii=False, indent=1), encoding="utf-8")
    if args.guardar_linea_base:
        LINEA_BASE.write_text(json.dumps(resultados, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"\nLínea base guardada en {LINEA_BASE.relative_to(RAIZ)}")

    fallas = revisar(resultados, args.fase)
    errores = [f"{v}: {d['detalle_errores']}" for v, d in resultados["vistas"].items() if d["errores_consola"]]
    if errores:
        print("\nErrores de consola:\n  " + "\n  ".join(errores))
    if not fallas:
        print(f"\nFase {args.fase}: " + ("cumple." if args.fase else "solo reporte, sin metas exigidas."))
        return 0
    print(f"\nFase {args.fase}: {len(fallas)} incumplimientos")
    for f in fallas[:40]:
        print("  - " + f)
    motivo = os.environ.get("GUARDIA_OMITIR")
    if motivo:
        print(f"\nGUARDIA_OMITIR activo: «{motivo}». Anótalo en el mensaje del commit.")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
