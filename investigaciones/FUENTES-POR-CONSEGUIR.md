# Fuentes por conseguir

Lista de tarea del autor (28-09-2026). Cada renglón es un dato que hoy está
en `pendiente` en la plataforma, el documento oficial que lo resuelve y
dónde buscarlo. Cuando un documento llegue, se coteja, se integra con su
página y su huella SHA-256, y el chip cambia a `oficial`.

## Cómo entregarlos

- **Formato: el PDF original, tal como lo baja la página oficial.** No en
  Word: al convertirlo cambian las páginas (y citamos por página) y ya no se
  puede comprobar que es idéntico al del gobierno. Si el portal ofrece Excel
  o CSV, ese también, sin abrirlo ni guardarlo de nuevo.
- **Anota junto a cada archivo** la dirección exacta de donde lo bajaste y
  la fecha. Esa liga es la que aparece en la plataforma.
- **Cómo subirlos:** en GitHub, rama **`claude/funny-turing-imtm54`** (no
  `main`), carpeta `investigaciones/entregas/`, botón «Add file → Upload
  files». GitHub acepta hasta 25 MB por archivo por esa vía; si pesa más,
  mándame solo la liga.
- **Nombre sugerido:** `ORGANISMO_documento_fecha.pdf`, por ejemplo
  `SAT_InformeTributario_2T2026.pdf`.

## Lo que ya no necesitas buscar

Las leyes federales y el Diario Oficial sí los puedo bajar yo desde aquí.
Ya están guardadas 31 leyes vigentes en `investigaciones/leyes/` (índice en
su `README.md`). Tampoco hace falta la reforma a la Ley Aduanera: su texto
vigente confirma la reforma del DOF 19-11-2025.

---

## A. Prioridad 1: solo tú puedes (el entorno de trabajo los bloquea)

| # | Dato que falta | Documento | Dónde | Qué cambia en la plataforma |
|---|---|---|---|---|
| A1 | Población a mitad de 2026: nacional y de las 32 entidades | CONAPO, *Proyecciones de la Población de México y de las Entidades Federativas 2020-2070*, base «población a mitad de año» | https://www.gob.mx/conapo → Documentos → «Proyecciones de la población». También en https://datos.gob.mx buscando «proyecciones de la población CONAPO». Bajar el CSV o XLSX | Los 134.4 millones de la calculadora y del ticket ambiental, y el reparto por habitante de los Ramos 28 y 33 por estado |
| A2 | Padrón de contribuyentes activos | SAT, *Informe Tributario y de Gestión*, 2.º trimestre de 2026, apartado del padrón | https://www.sat.gob.mx (buscador: «Informe Tributario y de Gestión»). Datos abiertos del SAT: http://omawww.sat.gob.mx/cifras_sat/ | Los 63.2 millones de la calculadora (hoy sin fuente) |
| A3 | Página exacta del dato de la Agencia Nacional de Aduanas | *Segundo Informe de Gobierno* (1-09-2026), PDF completo y su Anexo Estadístico | https://www.gob.mx/presidencia (buscar «Segundo Informe de Gobierno») | Huachicol: 3,109 casos, 109.4 millones de litros, $4,600 mdp, 3,434 sellos y 118 denuncias (1-09-2025 a 30-06-2026), hoy tomados de la prensa |
| A4 | Resolutivos de impacto ambiental de las megaobras: número, fecha, hectáreas y condicionantes | SEMARNAT, resolutivo de la Manifestación de Impacto Ambiental de: Tren Maya (tramos 1 a 7), Refinería Olmeca (Dos Bocas), AIFA y Tren Interurbano México-Toluca | Portal dgiraDocs de la SEMARNAT: https://apps1.semarnat.gob.mx:8443/dgiraDocs/ (buscar por nombre del proyecto). Basta el resolutivo; el estudio completo solo si pesa poco | Huella ambiental de cada obra, que hoy no se muestra |
| A5 | Historia de la deuda del rescate bancario | IPAB, *Informe al Congreso* del 4.º trimestre de 2025 (pasivos netos) y, si existe, la serie de pasivos desde 1999 | https://www.gob.mx/ipab → Documentos / Informes | Los $2,470,000 mdp del FOBAPROA en el simulador, que no tienen fuente |
| A6 | Número de concejales por alcaldía | *Constitución Política de la Ciudad de México* (art. 53) y *Ley Orgánica de Alcaldías de la Ciudad de México* | https://www.congresocdmx.gob.mx → Marco legal. O la Consejería Jurídica: https://data.consejeria.cdmx.gob.mx | Glosario de concejalías, hoy sin cita |
| A7 | Finanzas de las 16 alcaldías (el INEGI no las incluye en EFIPEM) | *Cuenta Pública de la Ciudad de México 2024*, tomo o apartado de alcaldías | https://www.finanzas.cdmx.gob.mx → Cuenta Pública → 2024 | Las alcaldías aparecen vacías en el padrón municipal |

## B. Huachicol fiscal: pasar de «dicho en prensa» a «documento»

> 28-09-2026: intenté B1 y el portal de Comunicación Social de la Cámara no responde desde aquí (503). **B1 pasa a ti.**

| # | Dato | Documento | Dónde |
|---|---|---|---|
| B1 | Lo que dijo la Procuradora Fiscal el 2-10-2025 ($600,000 mdp) | Versión estenográfica de la reunión de la Comisión de Hacienda y Crédito Público con la Procuradora Fiscal, o boletín de la Cámara | https://comunicacionsocial.diputados.gob.mx (boletines de esa fecha) y https://gaceta.diputados.gob.mx |
| B2 | Querellas por $16,000 mdp | Comunicado de la SHCP o de la Procuraduría Fiscal | https://www.gob.mx/shcp/prensa (octubre de 2025) |
| B3 | Si la ASF auditó a Aduanas o al SAT en la importación de combustibles | Informe individual de auditoría (Cuentas Públicas 2022 a 2024) | https://www.asf.gob.mx → Informes de auditoría; buscar «Agencia Nacional de Aduanas» o «hidrocarburos» |

## C. Megaobras: la pérdida de nueve obras y el costo del AIFA (primero lo intento yo)

| # | Obra | Documento que lo resuelve | Dónde |
|---|---|---|---|
| C1 | Refinería Olmeca (Dos Bocas) | Estado de actividades de Pemex Transformación Industrial en la Cuenta Pública 2024 y 2025, e informes de la ASF (Cuentas Públicas 2019 a 2024) | https://www.cuentapublica.hacienda.gob.mx (tomo de empresas productivas del Estado) · https://www.asf.gob.mx |
| C2 | Megafarmacia del Bienestar | ~~Estado de actividades de Birmex~~ (hecho: CP 2024, −$717.3 mdp, pero es de toda la empresa). Falta un documento que separe la Megafarmacia: auditoría de la ASF a Birmex (CP 2023 o 2024) | https://www.asf.gob.mx |
| C3 | FARAC (rescate carretero) | Estados financieros del Fonadin (Banobras) | https://www.gob.mx/banobras → Fonadin → información financiera |
| C4 | Agronitrogenados y Fertinal | Informes de la ASF (Cuentas Públicas 2014 a 2019), Pemex Fertilizantes | https://www.asf.gob.mx |
| C5 | Estela de Luz | Informe de la ASF, Cuenta Pública 2011 | https://www.asf.gob.mx |
| C6 | «Búnker» de la SSP | Informes de la ASF, Cuentas Públicas 2009 a 2012 | https://www.asf.gob.mx |
| C7 | Refinería Bicentenario (Tula) | Informes de la ASF, Cuentas Públicas 2009 a 2014 | https://www.asf.gob.mx |
| C8 | Enciclomedia | Informes de la ASF, Cuentas Públicas 2004 a 2006 | https://www.asf.gob.mx |
| C9 | Tren Interurbano México-Toluca | Registro original de 2013 en la Cartera de Programas y Proyectos de Inversión (clave y monto) e informes de la ASF | https://www.transparenciapresupuestaria.gob.mx → Proyectos de inversión · https://www.asf.gob.mx |
| C10 | AIFA, costo total de construcción | Informes de la ASF (Cuentas Públicas 2019 a 2022) o documento de la Sedena. Si no aparece: solicitud por la Plataforma Nacional de Transparencia | https://www.asf.gob.mx · https://www.plataformadetransparencia.org.mx |

## D. Evaluación de los presidentes: series históricas (primero lo intento yo)

| # | Dato | Documento | Dónde |
|---|---|---|---|
| D1 | PIB de 1988 en una serie comparable | INEGI, *Estadísticas Históricas de México 2014*, capítulo de Cuentas Nacionales, o el PIB base 1993 del Banco de Información Económica | https://www.inegi.org.mx (buscar «Estadísticas Históricas de México») |
| D2 | Saldo de la deuda pública al cierre de 1994 | SHCP, *Informe sobre la situación económica, las finanzas públicas y la deuda pública*, 4.º trimestre de 1994, o Banxico, *Informe Anual 1994* | https://www.banxico.org.mx → Publicaciones → Informes anuales |
| D3 | Trabajadores asegurados en el IMSS, 1988 a 1996 | IMSS, *Memoria Estadística* de esos años, o *Estadísticas Históricas de México* (INEGI) | https://www.imss.gob.mx → Estadísticas · https://www.inegi.org.mx |

## E. Remuneraciones (tú, por la Plataforma Nacional de Transparencia)

| # | Dato | Cómo conseguirlo |
|---|---|---|
| E1 | Dieta 2026 de los diputados de los 32 congresos locales | https://www.plataformadetransparencia.org.mx → Consulta pública → cada congreso → «Remuneración bruta y neta» (art. 70, fr. VIII). Exportar a Excel. Otra vía: el presupuesto 2026 de cada estado en su periódico oficial |
| E2 | Aguinaldo del Senado: el Manual dice 40 días y el anexo paga unos 60 | Solicitud al Senado por la PNT: «¿Cuántos días de dieta se pagaron como aguinaldo a cada senador en 2025 y con qué fundamento, dado que el Manual de Percepciones señala 40 días y el Anexo 23.2.2 reporta $382,207?» |
| E3 | Asesores del Senado contratados por honorarios | Solicitud al Senado por la PNT, pidiendo el Anexo 5 del Manual en Excel (hoy es una imagen) |

## F. No buscar todavía: salen con fecha

| Publicación | Fecha |
|---|---|
| ASF, 2.ª entrega de la Cuenta Pública 2025 | 30-10-2026 |
| SHCP, avance del gasto al 3.er trimestre de 2026 | Fin de octubre de 2026 |
| INEGI, Cuentas Económicas y Ecológicas 2025 | Diciembre de 2026 |
| INEGI, EFIPEM 2025 definitiva | Sin fecha |
| SAT, estudios de evasión (art. 30 de la LIF 2027) | Principios de 2028 |
