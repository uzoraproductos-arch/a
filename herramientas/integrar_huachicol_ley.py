# -*- coding: utf-8 -*-
"""Integra al auditor el marco legal del huachicol fiscal, cotejado contra los
textos vigentes que publica la Cámara de Diputados (27-09-2026):

- Ley del IEPS (última reforma DOF 07-11-2025): art. 2o., fr. I, inciso D),
  cuotas por litro actualizadas por acuerdo DOF 22-12-2025; art. 2o.-A,
  cuotas por litro que se reparten a estados y municipios.
- Ley de Coordinación Fiscal (última reforma DOF 03-01-2024): art. 2o.
  (recaudación federal participable, 20 % al Fondo General; la fr. VII excluye
  la cuota del 2o.-A) y art. 4o.-A (9/11 a las entidades por consumo).
- Código Fiscal de la Federación (última reforma DOF 09-04-2026): art. 28,
  fr. I, apartado B (controles volumétricos); arts. 102 (contrabando),
  103, fr. XXIII (presunción por trasladar hidrocarburos sin CFDI con
  Complemento Carta Porte) y 104 (penas).

Escribe en assets/auditor/js/audit-database.js: el bloque
huachicol_fiscal.marco_legal, sus tres fuentes, tres términos del glosario y
una pregunta en la casilla 4 de las preguntas frecuentes. Solo el auditor; la Enciclopedia no se toca.
Idempotente: si ya está integrado, no hace nada.
"""
import json
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BASE = RAIZ / 'assets' / 'auditor' / 'js' / 'audit-database.js'

FUENTES = {
    "lieps": {
        "doc": "Ley del Impuesto Especial sobre Producción y Servicios, texto vigente (última reforma DOF 07-11-2025; cuotas actualizadas por acuerdo DOF 22-12-2025), Cámara de Diputados",
        "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/LIEPS.pdf",
        "sha256": "32639ede8448f91e6ddde556d4b8bceaf349b904bc21631f06e1c8a7a3d416f4"
    },
    "lcf": {
        "doc": "Ley de Coordinación Fiscal, texto vigente (última reforma DOF 03-01-2024), Cámara de Diputados",
        "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/LCF.pdf",
        "sha256": "5c89d48167a4e1170c69e0b1e0294260b806a30d861275d8dca09b0334cd09d4"
    },
    "cff": {
        "doc": "Código Fiscal de la Federación, texto vigente (última reforma DOF 09-04-2026), Cámara de Diputados",
        "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/CFF.pdf",
        "sha256": "be7427b20d3552775ab42018f8f87578078770095bf8cf46322c25e36ee3aa7d"
    }
}

MARCO = {
    "estado": "oficial",
    "cuotas_federales_2026": {
        "fuente": "lieps",
        "articulo": "art. 2o., fracción I, inciso D), numeral 1",
        "nota": "Cuotas de la ley actualizadas para 2026. El estímulo fiscal que Hacienda publica en el DOF puede reducir lo que efectivamente se cobra.",
        "gasolina_menor_91": 6.7001,
        "gasolina_91_o_mas": 5.6579,
        "diesel": 7.3634
    },
    "cuotas_estatales_2026": {
        "fuente": "lieps",
        "articulo": "art. 2o.-A",
        "gasolina_menor_91_centavos": 59.1390,
        "gasolina_91_o_mas_centavos": 72.1605,
        "diesel_centavos": 49.0817
    },
    "reparto": {
        "fuente": "lcf",
        "texto": "El IEPS de combustibles del artículo 2o. entra a la recaudación federal participable, de la que el 20 % forma el Fondo General de Participaciones (LCF, art. 2o.). La cuota del artículo 2o.-A queda fuera de esa bolsa (art. 2o., fracción VII) y se reparte aparte: 9 de cada 11 pesos a las entidades según el consumo en su territorio (art. 4o.-A)."
    },
    "delitos": {
        "fuente": "cff",
        "controles": "Quien fabrique, transporte, almacene, distribuya o venda hidrocarburos o petrolíferos debe llevar controles volumétricos: equipos y programas que registran el volumen de sus operaciones y existencias, y que forman parte de su contabilidad (art. 28, fracción I, apartado B).",
        "contrabando": "Comete contrabando quien introduce mercancías al país omitiendo el pago total o parcial de sus contribuciones (art. 102). Se presume, entre otros casos, cuando se trasladan hidrocarburos o petrolíferos sin la factura electrónica con Complemento Carta Porte (art. 103, fracción XXIII).",
        "penas": "Prisión de tres meses a cinco años si lo omitido llega a $1,815,560, y de tres a nueve años si lo rebasa (art. 104, cantidades actualizadas DOF 28-12-2025)."
    }
}

GLOSARIO = [
    {
        "termino": "Huachicol Fiscal",
        "definicion": "Meter o vender combustible sin pagar sus impuestos: importarlo declarado como otra mercancía, facturar menos litros de los que se venden o vender más de lo que se compró con factura. No es el robo en ductos. Lo que se evade es sobre todo el IEPS de gasolinas y diésel, y con él el IVA. El Gobierno lo reconoce como una de las principales fuentes de evasión del IEPS en la exposición de motivos de la Ley de Ingresos 2027; ninguna autoridad ha publicado todavía cuánto se pierde.",
        "ley": "Ley del IEPS, arts. 2o. y 2o.-A · Código Fiscal de la Federación, arts. 102 a 104 · Iniciativa de Ley de Ingresos 2027, pp. CXXI a CXXV",
        "categoria": "💰 Hacendario & Deuda"
    },
    {
        "termino": "Controles Volumétricos",
        "definicion": "Equipos y programas informáticos que registran el volumen de hidrocarburos y petrolíferos que una empresa recibe, guarda y entrega, incluidas sus existencias. Son obligatorios para quien los fabrica, transporta, almacena, distribuye o vende, forman parte de su contabilidad y deben generar reportes diarios y mensuales. Son la herramienta del SAT para detectar litros vendidos sin factura.",
        "ley": "Código Fiscal de la Federación, art. 28, fracción I, apartado B",
        "categoria": "🔍 Fiscalización Superior"
    },
    {
        "termino": "Contrabando (Delito Fiscal)",
        "definicion": "Introducir mercancías al país, o sacarlas, sin pagar total o parcialmente sus contribuciones, sin el permiso que se requiera o cuando están prohibidas. La ley presume contrabando, entre otros casos, cuando se trasladan hidrocarburos sin la factura electrónica con Complemento Carta Porte. Se castiga con prisión de tres meses a cinco años, o de tres a nueve cuando lo omitido rebasa $1,815,560.",
        "ley": "Código Fiscal de la Federación, arts. 102, 103 (fracción XXIII) y 104",
        "categoria": "🔍 Fiscalización Superior"
    }
]

FAQ = {
    "pregunta": "¿Qué es el huachicol fiscal y cómo te afecta si no tienes una gasolinera?",
    "respuesta": "Es vender o importar combustible sin pagar sus impuestos. No es el robo en ductos: es papel, no pico y pala. Te afecta por tres caminos, todos escritos en ley:<br>• <strong>Tú sí pagas.</strong> En 2026 cada litro de gasolina menor a 91 octanos lleva una cuota federal de IEPS de $6.7001, la de 91 octanos o más $5.6579 y el diésel $7.3634 (Ley del IEPS, art. 2o., fr. I, inciso D; el estímulo fiscal que publica Hacienda puede reducirlas).<br>• <strong>Tu estado y tu municipio reciben menos.</strong> Ese IEPS entra a la bolsa de la que sale el 20 % que se reparte a los estados (Ley de Coordinación Fiscal, art. 2o.). Además hay una cuota aparte, de 49 a 72 centavos por litro (Ley del IEPS, art. 2o.-A), de la que 9 de cada 11 pesos van a las entidades según lo que se consume en su territorio (LCF, art. 4o.-A). Litro que se vende sin impuestos, peso que no llega.<br>• <strong>El faltante se cubre con más deuda o con menos gasto.</strong><br>Cuánto se pierde: ninguna autoridad lo ha publicado. La Ley de Ingresos 2027 propone que el SAT publique sus estudios de evasión a más tardar 35 días después de cerrar 2027 (art. 30). Mientras tanto, cualquier cifra que circule es una estimación."
}


def main():
    s = BASE.read_bytes().decode('utf-8')
    if '"marco_legal"' in s and '"termino": "Huachicol Fiscal"' in s:
        print('ya integrado')
        return
    nl = '\r\n' if '\r\n' in s else '\n'

    def dump(obj, sangria):
        txt = json.dumps(obj, ensure_ascii=False, indent=2)
        return nl.join((sangria + l) if i else l for i, l in enumerate(txt.split('\n')))

    # 1) Fuentes: después de la del Observatorio.
    ancla = '"url": "https://elceo.com/economia/costo-huachicol-pemex-hacienda-cifra2-consultores/"' + nl + '      }'
    assert s.count(ancla) == 1, 'ancla fuentes'
    extra = ''.join(',' + nl + '      "' + k + '": ' + dump(v, '      ') for k, v in FUENTES.items())
    s = s.replace(ancla, ancla + extra)

    # 2) Marco legal: antes de "anam" dentro de huachicol_fiscal.
    i = s.index('"huachicol_fiscal": {')
    j = s.index('    "anam": {', i)
    s = s[:j] + '    "marco_legal": ' + dump(MARCO, '    ') + ',' + nl + s[j:]

    # 3) Glosario: al final de la lista.
    g = s.index('"glosario": [')
    fin = s.index(nl + '  ],', g)
    s = s[:fin] + ''.join(',' + nl + '    ' + dump(t, '    ') for t in GLOSARIO) + s[fin:]

    # 4) Pregunta frecuente: casilla 4 (auditoría social), que es la que
    #    pinta el auditor; la lista "faqs" solo la usaba la Enciclopedia.
    c = s.index('"casilla_id": "c-fiscalizacion-asf"')
    it = s.index('"items": [', c)
    fin = s.index(nl + '      ]', it)
    item = {"q": FAQ["pregunta"], "a": FAQ["respuesta"]}
    s = s[:fin] + ',' + nl + '        ' + dump(item, '        ') + s[fin:]

    BASE.write_bytes(s.encode('utf-8'))
    print('integrado')


if __name__ == '__main__':
    main()
