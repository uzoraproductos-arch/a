# Fuentes localizadas — entrega del 28 de septiembre de 2026

Resultado de la búsqueda de los 25 puntos solicitados. **La entrega es parcial:** un documento descargado no convierte automáticamente en oficial la cifra que se buscaba. No se modificaron datos ni chips de la plataforma.

Se descargaron **38 originales completos**: 29 incluidos en esta carpeta y 9 mayores de 25 MB conservados localmente y enlazados. Otros dos PDF de alcaldías se localizaron, pero no se descargaron completos por su tamaño. Estos recuentos son de archivos, no de puntos resueltos.

- [Catálogo de originales, enlaces, fechas y SHA-256](CATALOGO.md).
- [Catálogo en CSV](catalogo-originales.csv) y [registro de intentos de descarga](registro-descargas.json).
- [Población 2026 calculada desde el CSV de CONAPO](CONAPO_Poblacion2026_derivada.csv).
- [Dos solicitudes al Senado listas para presentar](SOLICITUDES_SENADO.md). No se enviaron.

Los PDF se conservan sin conversión ni alteración. Las fechas del registro están en UTC; el catálogo añade la fecha y hora de Ciudad de México (UTC−06:00). Conforme a `FUENTES-POR-CONSEGUIR.md`, los originales mayores de 25 MB se entregan mediante enlace; las copias que sí se descargaron permanecen en `outputs/fuentes-originales-grandes/` del equipo, fuera del commit. Los archivos derivados se identifican expresamente.

## Resultado de los 25 puntos

| # | Fuente buscada | Resultado y pendiente |
|---|---|---|
| 1 | CONAPO: población a mitad de 2026 | **Localizada.** CSV original de población por edad, sexo y entidad. La suma de las 32 entidades es **134,407,258 personas**. Se entrega un CSV derivado con 33 filas y el procedimiento reproducible. |
| 2 | SAT: Informe Tributario y de Gestión, 2T2026 | **Pendiente el informe exacto.** Se descargaron dos CSV oficiales del padrón con último corte disponible en esos archivos: abril de 2026, **88,085,311 activos**. No valida 63.2 millones ni sustituye el corte de junio. |
| 3 | Segundo Informe de Gobierno 2026 y anexo | **Localizado.** El PDF consolidado tiene 1,342 páginas e incluye el anexo estadístico. 3,109 casos: página impresa 46, página PDF 70. Los otros cuatro datos: impresa 260, PDF 284. Véase la precisión de conceptos debajo. |
| 4 | Resolutivos ambientales: Maya 1–7, Dos Bocas, AIFA e Interurbano | **Pendiente.** Se localizaron rutas y páginas oficiales, pero no se obtuvo el conjunto de resolutivos originales. No se certifican hectáreas, condicionantes ni vigencias a partir de una MIA o de una nota de prensa. Rutas documentadas debajo. |
| 5 | IPAB, 4T2025 y serie desde 1999 | **Informe localizado; serie histórica pendiente.** Está dentro del anexo de deuda pública de SHCP. Pasivos netos al 31-12-2025: **1,023,571 millones de pesos**, preliminares, página C24/PDF 24. No es el costo histórico del rescate. |
| 6 | Constitución CDMX y Ley Orgánica de Alcaldías | **Textos localizados.** Artículo 53, apartado A, numeral 10, y artículo 19 de la ley. Establecen 10, 12 o 15 concejales según población. Ediciones descargadas: reformas al 23-12-2024 y al 31-03-2025 respectivamente; pendiente comprobar reformas posteriores antes de presentarlas como texto vigente a septiembre de 2026. |
| 7 | Cuenta Pública CDMX 2024, 16 alcaldías | **Localizados el Tomo I y los enlaces de las 16 cuentas individuales.** Se descargaron completas 14 cuentas; Coyoacán y Milpa Alta superaron el límite de descarga de 95 MB y se dejan enlazadas. Gasto por alcaldía: Tomo I, página 61. Pendiente extraer y conciliar ingresos y gastos de los anexos, sin tratar a las alcaldías como municipios de EFIPEM. |
| 8 | Dietas brutas/netas 2026 de 32 congresos locales | **Parcial: 1 de 32.** Tabulador oficial de Guanajuato localizado. Los otros 31 congresos y la comparación homogénea siguen pendientes. No se extrapolan cifras. |
| 9 | Solicitud al Senado: aguinaldo efectivamente pagado en 2025 | **Borrador preparado; presentación y respuesta pendientes.** Se distingue el pago de 2025 del presupuesto/manual de 2026 y se pide conciliación documental. |
| 10 | Solicitud al Senado: Anexo 5 en Excel | **Borrador preparado; presentación y respuesta pendientes.** Se pide el archivo nativo existente y sus criterios, sin atribuirle cifras a la imagen. |
| 11 | Comparecencia de Procuradora Fiscal, 02-10-2025 | **Pendiente la estenográfica exacta.** Se localizó una aclaración oficial posterior, del 09-10-2025, que impide presentar 600,000 mdp como cálculo oficial de Hacienda. Véase nota debajo. |
| 12 | SHCP/PFF: querellas por 16,000 mdp | **Referencia oficial localizada, en otro formato.** La estenográfica de Presidencia del 09-10-2025 recoge la explicación del secretario de Hacienda: acumulado histórico de casos querellados; no exclusivamente el buque de Altamira. Pendiente comunicado independiente y desglose temporal. |
| 13 | ASF: ANAM/SAT e importación de combustibles, CP2022–2024 | **Pendiente.** No se identificó con certeza el informe individual y su monto específico; no se sustituyó por auditorías aduaneras de otro objeto. |
| 14 | Pemex TRI, CP2024/2025; pérdida de Dos Bocas | **Documentos corporativos localizados; pérdida de la refinería pendiente.** El PDF 2024 contiene estados financieros de TRI. El archivo 2025 es un aviso de extinción de la subsidiaria e integración a Pemex desde el 19-03-2025, no estados financieros separados. |
| 15 | Birmex, CP2024/2025; pérdida de Megafarmacia | **Documentos de auditoría localizados; pérdida de la instalación pendiente.** El PDF 2024 es un dictamen de seis páginas con abstención de opinión, no un estado de actividades completo. El archivo 2025 contiene el informe de auditoría y dictamen presupuestario. No permiten por sí solos aislar Megafarmacia. |
| 16 | Fonadin/Banobras: costo y pérdida FARAC | **Pendiente.** No se obtuvo el estado financiero y la conciliación que permitan distinguir rescate, deuda vigente, intereses y recuperación. |
| 17 | ASF: Agronitrogenados y Fertinal | **Informe pertinente localizado:** CP2017, auditoría 492-DE a Pemex Fertilizantes, 66 páginas. Contiene antecedentes de adquisiciones. Pendiente conciliar costo, rehabilitación, deuda, recuperaciones y pérdida, así como los demás ejercicios 2014–2019. |
| 18 | ASF: Estela de Luz, CP2011 | **Informe localizado:** auditoría 56, 73 páginas. Páginas 27–28 distinguen finiquito del contrato y total contratado por el fideicomiso. Pendiente fijar el alcance de “costo final”; no son conceptos intercambiables. |
| 19 | ASF: Búnker SSP, CP2009–2012 | **Pendiente.** No se identificó con certeza el informe que corresponda a esta instalación; se descartó confundirlo con inmuebles del CISEN. |
| 20 | ASF: Refinería Bicentenario en Tula | **Parcial:** auditoría CP2010, 1115, 12 páginas, sobre estudios y proyecto. Pendiente costo acumulado multianual y separación de inversiones reutilizadas. |
| 21 | ASF: Enciclomedia, CP2004–2006 | **Pendientes los informes originales solicitados.** Se entrega una evaluación retrospectiva de política educativa CP2011, auditoría 395, que menciona Enciclomedia. Es contexto, no sustituto de la fiscalización 2004–2006. |
| 22 | Cartera 2013: monto original Interurbano | **Dato localizado en fuente oficial retrospectiva:** Libro Blanco SCT 2018, página impresa 39/PDF 41: clave **13093110008**, monto inicial **34,114,855,980 pesos**, registro de diciembre de 2013. Pendiente recuperar la ficha original de la cartera. |
| 23 | ASF/Sedena: costo total AIFA | **Parcial:** auditoría CP2022, 342, 36 páginas. Su universo de 2022 no es el costo acumulado de construcción. Pendiente integrar 2019–2022 con alcance consistente y sin doble conteo. |
| 24 | INEGI: PIB1988 e IMSS1988–1996 | **PIB localizado; IMSS pendiente.** EHM2014, capítulo 8, cuadro 8.6/PDF 20: PIB1988 **958,230 millones de pesos a precios de 1993**, valores básicos. Se descargaron además Trabajo y Salud. Población asegurada con familiares no equivale a trabajadores asegurados del IMSS. |
| 25 | Banxico: deuda al cierre de 1994 | **Informe localizado; saldo nominal comparable pendiente.** Páginas impresas 80–81/PDF 92–93: deuda económica amplia al cierre **36.9% del PIB** y consolidada con Banxico **35.6%**. Los cuadros 23–24 presentan saldos promedio, no de cierre. |

## Precisiones para el cotejo editorial

### Población: original y cálculo

Fuente: [catálogo CONAPO](https://www.datos.gob.mx/dataset/proyecciones-de-poblacion), recurso `00_Pob_Mitad_1950_2070.csv`. El archivo descargado contiene entidades, sin una fila de total nacional. El nombre del recurso menciona 1950–2070; la cobertura estatal descargada comienza en 1970.

Se filtra `ANIO = 2026`, se suman `POBLACION` de las 110 edades y ambos sexos por `CVE_GEO`, y luego las 32 entidades. Son 7,040 registros. Todos los totales del archivo pequeño llevan estado **derivado**; no se redondearon ni estimaron. La reproducción está en `derivar_poblacion.py` y comprueba la huella del original.

### Huachicol: qué dicen las fuentes

En el Segundo Informe, los **3,109** son casos de clasificación arancelaria incorrecta de petrolíferos e hidrocarburos. No deben llamarse decomisos. La página 260, en el apartado de acompañamiento técnico a la Administración Pública Federal, cubre del 01-09-2025 al 30-06-2026 y habla de **109.4 millones de litros no declarados detectados**, **4,600 mdp de recaudación asociada de IVA e IEPS**, **3,434 sellos digitales cancelados** y **118 denuncias penales**. No dice que los 4,600 mdp sean una estimación anual de evasión ni atribuye toda la secuencia exclusivamente a ANAM.

La [estenográfica oficial del 9 de octubre de 2025](https://www.gob.mx/presidencia/articulos/version-estenografica-conferencia-de-prensa-de-la-presidenta-claudia-sheinbaum-pardo-del-09-de-octubre-de-2025), consultada en navegador, contiene la aclaración de Presidencia de que no había un dato oficial consolidado de Hacienda sobre aquella estimación. El secretario Edgar Amador explica que los **16,000 mdp** corresponden a casos querellados históricamente. Esta referencia acredita declaraciones oficiales; no es una auditoría, una sentencia ni una estimación anual independiente. La comparecencia del 2 de octubre permanece pendiente.

### IPAB y deuda histórica

SHCP, anexo de deuda pública 4T2025, página C24: pasivos totales **1,228,468 mdp**; pasivos netos **1,023,571 mdp**. La página C29 reporta una **posición financiera** de **1,023,024 mdp**, con otra base de cálculo. No mezclar las dos medidas. Son cifras preliminares de cierre, no suma de erogaciones desde 1999 ni prueba de los 2,470,000 mdp del simulador.

Banxico 1994 presenta metodologías históricas de deuda económica amplia y consolidada con el banco central. No se empalman automáticamente con SHRFSP. Los **310,211 millones de nuevos pesos** del cuadro 23 son saldo promedio anual; no usarlos como saldo al 31 de diciembre.

### Alcaldías y remuneraciones

CDMX, Tomo I, página 61: gasto programable ejercido conjunto **49,617.0 mdp**. El cuadro de ministraciones de la página 64 tiene una cobertura distinta y no sustituye ese total. El catálogo enumera las 16 cuentas individuales.

Los textos jurídicos descargados establecen 10 concejales para hasta 300 mil habitantes, 12 para más de 300 mil y hasta 500 mil, y 15 para más de 500 mil. La ley remite al último censo; no recalcular la integración electa usando proyecciones de 2026.

Guanajuato, tabulador 2026, nivel 20 Diputado/a: **percepción mensual bruta 224,437.56 pesos** y **neta 144,097.16 pesos**, según sus columnas. Incluye componentes que requieren distinguirse de “dieta” o sueldo nominal; no comparar el bruto total de un congreso con la dieta base de otro. No se obtuvo una tabla de los 32 congresos.

### Pistas ambientales que aún no son documentos entregados

- [ASEA: página del resolutivo de Dos Bocas](https://www.gob.mx/asea/documentos/resolutivo). El enlace publicado a `Resolutivo_vPublica.pdf` en el servidor `104.209.210.233` no completó la descarga. No se sustituyó por el logotipo o por una captura.
- [AIFA: página oficial de la MIA regional](https://www.gob.mx/aifa/documentos/manifestacion-de-impacto-ambiental-mia-modalidad-regional-del-proyecto-de-la-construccion-de-un-aeropuerto-mixto-civil-militar). Una MIA presentada no equivale al resolutivo de autorización.
- Para Tren Maya fase 1 se localizó una respuesta oficial que refiere el oficio `SGPA/DGIRA/DG/06043`; la ruta del resolutivo `04CA2020V009.pdf` devolvió 404. No se usa ese indicio para completar fecha, superficie o condiciones de los siete tramos.

## Qué falta después de esta entrega

Obtener el ITG2T2026, los resolutivos ambientales, la serie IPAB desde 1999, 31 tabuladores legislativos y las respuestas del Senado. Completar los informes exactos de la comparecencia, ANAM/SAT, Fonadin, Búnker y Enciclomedia. Conciliar costos y pérdidas por obra, ingresos de alcaldías, serie de trabajadores IMSS y saldo nominal de deuda al cierre de 1994. Las cifras no resueltas conservan estado **pendiente**.

La localización y el cotejo puntual de fuentes son distintos de su integración a la plataforma: esta entrega no realiza esa integración.
