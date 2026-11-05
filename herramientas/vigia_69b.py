#!/usr/bin/env python3
"""Vigía de la lista 69-B del SAT (paso 0.3 de docs/PLAN-IMPLEMENTACION.md).

Uso:
    python3 herramientas/vigia_69b.py              # descarga el CSV del SAT
    python3 herramientas/vigia_69b.py archivo.csv  # usa un CSV local

Baja el «Listado completo de contribuyentes (Artículo 69-B del CFF)», lo
compara contra el que ya tiene la plataforma (assets/auditor/data/sat-69b.js)
y deja en docs/sat69b/bandeja.json lo que cambió:

- altas: contribuyentes que no estaban;
- cambios: los que pasaron de una situación a otra (presunto → definitivo,
  presunto → desvirtuado, definitivo → sentencia favorable…);
- bajas: los que ya no aparecen en el listado;
- nombres: empresas (personas morales) con el mismo RFC y otra razón social.
  El RFC no cambia cuando una sociedad cambia de denominación, así que es la
  forma más barata de seguir a una empresa que «se cambia el nombre».

Como el vigía legislativo, **detecta y propone; nunca escribe en la base**:
sat-69b.js no se toca. Para integrar el corte nuevo, el autor (o el agente,
con su visto bueno) corre actualizar_69b.py y sube el sello.

Las personas físicas (RFC de 13 caracteres) van en la bandeja con el RFC
recortado y sin nombre: el repositorio es público y la bandeja es para
contar y avisar, no para exhibir a nadie. La lista completa sigue siendo la
del SAT, con su liga.
"""
import datetime
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import actualizar_69b as a69  # noqa: E402

RAIZ = a69.RAIZ
BANDEJA = os.path.join(RAIZ, "docs", "sat69b", "bandeja.json")
NOMBRE = {"P": "Presunto", "D": "Desvirtuado", "F": "Definitivo", "S": "Sentencia Favorable"}
# Lo que más le importa a quien recibe facturas: el paso a definitivo
# (CFF art. 69-B, párrafo quinto: esas facturas «no producen ni produjeron
# efecto fiscal alguno»). Va primero en la bandeja.
ORDEN = {"F": 0, "P": 1, "S": 2, "D": 3}
TOPE = 3000  # renglones por lista; el resumen siempre trae la cuenta completa


def actual():
    """Los registros y el meta de sat-69b.js (lo que la plataforma ya tiene)."""
    with open(a69.SALIDA, encoding="utf-8") as f:
        t = f.read()
    d = json.loads(t[t.index('{"meta"'):t.rindex("}") + 1])
    return {r[0]: r for r in d["r"]}, d["meta"]


def tapa(r):
    """Renglón para la bandeja. Persona física: RFC recortado y sin nombre."""
    rfc, nombre = r[0], r[1]
    fisica = len(rfc) == 13
    return {
        "rfc": (rfc[:4] + "·" * 6 + rfc[-3:]) if fisica else rfc,
        "persona": "física" if fisica else "moral",
        "nombre": "" if fisica else nombre,
        "situacion": NOMBRE[r[2]],
        "oficio": r[3],
        "fecha": r[4],
        "medio": r[5],
    }


def comparar(viejos, nuevos):
    altas, cambios, bajas, nombres = [], [], [], []
    for rfc, r in nuevos.items():
        v = viejos.get(rfc)
        if v is None:
            altas.append(tapa(r))
        elif v[2] != r[2]:
            c = tapa(r)
            c["de"] = NOMBRE[v[2]]
            cambios.append(c)
        if v is not None and len(rfc) == 12 and " ".join(v[1].split()).upper() != " ".join(r[1].split()).upper():
            n = tapa(r)
            n["antes"] = v[1]
            nombres.append(n)
    for rfc, v in viejos.items():
        if rfc not in nuevos:
            bajas.append(tapa(v))
    llave = lambda x: (ORDEN.get({b: a for a, b in NOMBRE.items()}[x["situacion"]], 9), x["rfc"])
    return sorted(altas, key=llave), sorted(cambios, key=llave), sorted(bajas, key=llave), sorted(nombres, key=llave)


def cuenta(lista):
    c = {}
    for x in lista:
        c[x["situacion"]] = c.get(x["situacion"], 0) + 1
    return c


def main():
    raw = a69.leer(sys.argv[1] if len(sys.argv) > 1 else None)
    huella = hashlib.sha256(raw).hexdigest()
    registros, por_sit, corte = a69.registros_de(raw)
    nuevos = {r[0]: r for r in registros}
    viejos, meta = actual()
    altas, cambios, bajas, nombres = comparar(viejos, nuevos)

    bandeja = {
        "que_es": ("Lo que cambió en la lista 69-B del SAT frente a la copia de la plataforma. Detecta y propone: "
                   "nada de aquí entra a la base hasta correr actualizar_69b.py y subir el sello."),
        "fuente": "SAT, Listado completo de contribuyentes (Artículo 69-B del CFF)",
        "url": a69.URL_PAGINA,
        "csv": a69.URL_CSV,
        "plataforma": {"corte": meta.get("corte", ""), "sha256": meta.get("sha256", ""), "total": meta.get("total", 0)},
        "sat": {"corte": corte, "sha256": huella, "total": len(registros), "porSituacion": por_sit},
        "mismo_archivo": huella == meta.get("sha256"),
        "resumen": {
            "altas": len(altas), "cambios": len(cambios), "bajas": len(bajas), "nombres": len(nombres),
            "altasPorSituacion": cuenta(altas), "cambiosA": cuenta(cambios),
        },
        "privacidad": "Personas físicas: RFC recortado y sin nombre. La lista completa está en la liga del SAT.",
        "para_integrar": "python3 herramientas/actualizar_69b.py && python3 herramientas/sello.py --siguiente",
        "altas": altas[:TOPE],
        "cambios": cambios[:TOPE],
        "bajas": bajas[:TOPE],
        "nombres": nombres[:TOPE],
    }
    # Solo se reescribe si cambió algo más que la fecha: así el flujo semanal
    # no deja un commit por semana cuando el SAT no publicó nada.
    previo = None
    if os.path.exists(BANDEJA):
        with open(BANDEJA, encoding="utf-8") as f:
            previo = json.load(f)
        previo.pop("revisado", None)
    if previo != bandeja:
        bandeja["revisado"] = datetime.date.today().isoformat()
        os.makedirs(os.path.dirname(BANDEJA), exist_ok=True)
        with open(BANDEJA, "w", encoding="utf-8", newline="\n") as f:
            json.dump(bandeja, f, ensure_ascii=False, indent=1)
            f.write("\n")
    r = bandeja["resumen"]
    print("Corte SAT %s (plataforma: %s). Altas %d, cambios %d, bajas %d, nombres %d.%s"
          % (corte, meta.get("corte", ""), r["altas"], r["cambios"], r["bajas"], r["nombres"],
             " Mismo archivo que la plataforma." if bandeja["mismo_archivo"] else ""))


if __name__ == "__main__":
    main()
