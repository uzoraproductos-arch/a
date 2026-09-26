# Base de investigación para la calculadora cívica: finanzas públicas y fiscalización

Fecha de consulta: 24 de septiembre de 2026. Proyecto: Auditavisión.

## Propósito y alcance

Preparar la integración gradual de comparaciones financieras en la calculadora cívica, con respaldo documental de la Auditoría Superior de la Federación (ASF). Incluye Cámara de Diputados, Senado, congresos locales, gobiernos de las entidades federativas y ayuntamientos. El cabildo se desglosa cuando la documentación identifica su gasto propio. Este documento entrega investigación y especificación funcional; no incorpora todavía nuevas cifras a la plataforma.

La pregunta central del módulo será: **¿cuánto gasta esta institución, qué parte revisó la ASF y qué significa esa cantidad en una escala que el ciudadano pueda comprender?** Cada respuesta conservará ejercicio, unidad monetaria, alcance y fuente.

La ASF será la fuente principal para resultados de fiscalización. Las cuentas públicas y los presupuestos oficiales complementarán los datos financieros que el informe de auditoría no contenga. Una institución puede estar incluida en un informe y aun así carecer de información suficiente para calcular su gasto total, remuneración individual o costo del cabildo.

## 1. Qué se puede aprovechar de la enciclopedia

Se revisaron CONTEXT.md, enciclopedia.html y fragmentos del motor y la base de datos. La revisión es focalizada, no una validación integral de las cifras existentes.

| Sección existente | Aporte al módulo | Condición para reutilizarla |
|---|---|---|
| 1.2 Del Peso Federal al Peso Estatal | Entidades, participaciones, aportaciones y dependencia de transferencias | Identificar documento, ejercicio y universo de cada importe |
| 1.3 El Eslabón Municipal | Ingresos propios, FORTAMUN, infraestructura social y selección municipal | Conservar claves geográficas y distinguir ausencia de datos de cero |
| 2.1 Maquinaria Financiera, Deuda y Banxico | Contexto de deuda e ingresos | Usarlo como contexto; no atribuir deuda estatal a un congreso |
| 2.2 Inversión, Megaobras y Simulador | Presentación de equivalencias | No convertir montos observados en pérdidas por segundo |
| 2.4 Calculadora Cívica | Entrada del ingreso del usuario y resultados comparativos | Conectar sólo registros trazables y conceptos compatibles |
| 2.5 Bitácora y Alertas ASF | Entrada al expediente de fiscalización | Registrar auditoría, acción y fecha de seguimiento |
| 3.2 Congresos Estatales y 3.4 Estructura Remunerativa | Catálogos y conceptos del Poder Legislativo | Revisar fuentes antes de reutilizar sueldos o presupuestos |

### Hallazgos que conviene resolver antes de conectar los datos

- En `obtenerBanderasRojasEstado`, el porcentaje de adjudicación directa toma **60.0** como valor predeterminado cuando falta un registro. Ese valor es una sustitución del programa, no evidencia de una contratación real.
- Las observaciones faltantes se transforman en **0** mediante expresiones como `asfMontoObservado || 0` y `observacionesASF || 0`. Después pueden aparecer mensajes favorables. Debe conservarse la ausencia como `pendiente`.
- El panel cuenta alertas de tipo favorable bajo la etiqueta **Solventadas**. Un monto pequeño, una ausencia de registro o una condición favorable no prueban que una acción haya sido solventada.
- Los umbrales de 500 millones para estados y 15 millones para municipios se encuentran en el código. No se verificó una metodología oficial de ASF que justifique presentarlos como categorías oficiales de gravedad.
- La descripción municipal permite interpretar FORTAMUN como un fondo de uso amplio. Debe explicarse su destino legal: no equivale a una bolsa sin restricciones.

Estos hallazgos no fueron modificados durante la investigación. Son tareas de saneamiento previas a la integración.

## 2. Instituciones y niveles de análisis

El Congreso federal, los congresos locales y los ayuntamientos no forman una misma cadena jerárquica. El municipio es gobernado por un ayuntamiento; el cabildo no debe clasificarse como un congreso municipal. La Cámara de Diputados aprueba el PEF y revisa la Cuenta Pública con apoyo de la ASF. Los congresos estatales aprueban las leyes de ingresos municipales; los ayuntamientos aprueban sus egresos. Las entidades tienen fiscalización local y la ASF interviene en recursos de su competencia. La Ciudad de México y sus alcaldías requieren tratamiento propio. Fundamento: artículos 74, 79, 115, 116 y 122 de la [Constitución](https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf).

Para la calculadora propongo esta clasificación:

| Selector | Unidad que se compara | Evitar |
|---|---|---|
| Legislativo federal | Diputados o Senado, individualmente | Sumar ingresos y egresos de la misma cámara |
| Legislativo local | Congreso de una entidad | Confundir su gasto con el presupuesto estatal completo |
| Gobierno estatal | Gobierno o ente concreto identificado por la fuente | Agregar poderes y organismos sin revisar consolidación |
| Ayuntamiento | Administración municipal definida en la cuenta pública | Confundir una auditoría de un fondo con todo el municipio |
| Cabildo | Unidad administrativa o conjunto documentado de partidas | Estimar su costo dividiendo el presupuesto municipal |

La ficha de cabildo debería incluir presidencia, sindicaturas y regidurías sólo conforme al desglose institucional disponible. Si no existe separación contable suficiente, el resultado será «Gasto específico del cabildo: pendiente de desglose oficial».

## 3. Qué representa cada número

Presupuesto aprobado, modificado, comprometido, devengado, ejercido y pagado deben conservarse como conceptos diferentes. El artículo 38 de la [Ley General de Contabilidad Gubernamental](https://www.diputados.gob.mx/LeyesBiblio/pdf/LGCG.pdf) establece los momentos del registro presupuestario. Para interpretarlos se usarán las [normas del CONAC](https://www.conac.gob.mx/es/CONAC/Normatividad_Vigente): el devengado reconoce una obligación y el pagado refleja su liquidación. No deben sustituirse entre sí por conveniencia visual.

En fiscalización se distinguirán:

- **Universo seleccionado:** operaciones que delimitan esa auditoría.
- **Muestra auditada:** porción efectivamente revisada dentro de ese universo.
- **Monto por aclarar:** importe sujeto a aclaración o al procedimiento correspondiente.
- **Recuperaciones operadas:** recuperación reportada por la ASF, conservando el corte y la definición de la fuente.
- **Acciones y seguimiento:** registros individualizados; no todas las acciones tienen importe monetario.

La ASF explica que montos inicialmente observados pueden aclararse después de la notificación. Por eso el módulo no debe traducirlos automáticamente a dinero robado o perdido. Tampoco debe restar recuperaciones de una publicación a observaciones de otra sin conciliar sus expedientes. Véase el [marco general de gasto federalizado de la Cuenta Pública 2024](https://informe.asf.gob.mx/Documentos/Auditorias/MR-GENERAL_a.pdf).

Para el gasto local, las participaciones y las aportaciones tienen reglas distintas. El destino de FORTAMUN se regula en el artículo 37; el de infraestructura social, en el 33. El artículo 49 regula las aportaciones y contiene excepciones que impiden describir su régimen de afectación de manera absoluta. La base jurídica debe comprobarse en la [Ley de Coordinación Fiscal](https://www.diputados.gob.mx/LeyesBiblio/pdf/LCF.pdf), sin extrapolar una regla de un fondo a todos los demás.

## 4. Cuatro expedientes comprobados para diseñar la integración

Los ejemplos tienen distintos ejercicios y alcances. Sirven para construir el modelo de datos, no para ordenarlos en una clasificación comparativa nacional. Las cifras siguientes conservan la unidad original: **miles de pesos**. Son `oficial`, pues se transcriben del informe, no se estiman.

### A. Cámara de Diputados: Cuenta Pública 2024

Auditoría **2024-0-01100-19-0031-2025**, Gestión Financiera.

| Concepto | Miles de pesos | Localizador |
|---|---:|---|
| Presupuesto asignado | 8,982,854.4 | Página 4 |
| Presupuesto modificado | 9,371,736.5 | Página 4 |
| Presupuesto pagado | 9,371,736.5 | Páginas 4–5 |
| Universo seleccionado de egresos | 6,833,879.4 | Página 1 |
| Muestra auditada | 6,537,228.2 | Página 1 |

El informe registra 26 resultados sin irregularidades detectadas y circunscribe su conclusión a la muestra revisada. No equivale a una certificación general de toda la actividad institucional. La diferencia entre presupuesto pagado y universo seleccionado demuestra por qué deben existir campos separados. [Informe individual, páginas 1, 4–5 y 43](https://informe.asf.gob.mx/Documentos/Auditorias/2024_0031_a.pdf).

### B. Senado: Cuenta Pública 2024

Auditoría **2024-0-01200-19-0032-2025**, Gestión Financiera.

| Concepto | Miles de pesos | Localizador |
|---|---:|---|
| Universo de ingresos | 5,045,707.6 | Página 1 |
| Universo de egresos | 5,045,707.6 | Página 1 |
| Muestra de egresos | 3,560,328.5 | Página 1 |
| Pagado al cierre de 2024 | 4,978,781.8 | Página 1 |
| Compromisos devengados al cierre, pagados en el primer bimestre de 2025 | 66,925.8 | Página 1 |

Sumar los universos de ingresos y egresos produciría una escala inadecuada para representar el gasto. Tampoco corresponde presentar lo devengado pendiente de pago al cierre como un faltante. [Informe individual, páginas 1–2](https://www.asf.gob.mx/Trans/Informes/IR2024b/Documentos/Auditorias/2024_0032_a.pdf).

### C. Jalisco: distribución de participaciones, Cuenta Pública 2024

Auditoría **2024-A-14000-19-1168-2025**.

| Concepto | Miles de pesos | Localizador |
|---|---:|---|
| Universo y muestra de participaciones para distribución municipal | 22,182,434.8 | Página 2 |
| Revisión adicional de FEIEF | 16,915.0 | Página 2 |
| Monto total auditado declarado por el informe | 22,199,349.8 | Página 2 |

Esta revisión estudia distribución y pago a municipios. No representa el gasto total del gobierno estatal. La suma de participaciones y FEIEF ya está contenida en el monto total: agregar los tres renglones duplicaría recursos. [Informe individual, páginas 1–2](https://www.asf.gob.mx/Trans/Informes/IR2024a/Documentos/Auditorias/2024_1168_a.pdf).

### D. Puebla: FORTAMUN, Cuenta Pública 2023

Auditoría **2023-D-21114-19-1654-2024**.

El universo y la muestra son **302,154.3 miles de pesos**, relativos a operaciones seleccionadas de servicios municipales. El informe presenta tres resultados sin irregularidades detectadas. Su cobertura del 100% corresponde al universo seleccionado, no a toda la hacienda municipal. No proporciona un costo específico del cabildo. [Informe individual, páginas 2–4](https://www.asf.gob.mx/Trans/Informes/IR2023c/Documentos/Auditorias/2023_1654_a.pdf).

## 5. Operaciones propuestas para la calculadora

Son decisiones de diseño para Auditavisión, no indicadores oficiales de la ASF. Todo resultado calculado llevará `derivado`, los insumos y la operación. Los resultados no se activarán si faltan insumos compatibles.

| Pregunta del usuario | Operación | Condición y texto de interpretación |
|---|---|---|
| ¿A cuántos ingresos anuales como el mío equivale? | Monto en pesos / ingreso anual del usuario | Equivalencia monetaria; no empleos que puedan financiarse |
| ¿Qué porcentaje del gasto corresponde a personal? | Servicios personales / gasto total × 100 | Mismo ente, ejercicio, corte y momento contable |
| ¿Cuánto cambió el presupuesto? | (Modificado − aprobado) / aprobado × 100 | Cambio autorizado; no sobrecosto por sí mismo |
| ¿Qué parte del universo revisó esta auditoría? | Muestra / universo × 100 | No se rotula como porcentaje de toda la institución |
| ¿Qué proporción de la muestra sigue por aclarar? | Monto pendiente / muestra × 100 | Sólo si el pendiente pertenece a esa misma muestra y corte |
| ¿Cuánto representa por habitante? | Gasto / población de referencia | Identificar fuente, territorio y año de población |
| ¿Cuál es el promedio por día? | Gasto anual / días del ejercicio | Promedio histórico, no desembolso en tiempo real |
| ¿Cuánto cuesta el cabildo? | Suma de partidas documentadas del cabildo | No sumar el total municipal; evitar partidas superpuestas |

Reglas de cálculo:

1. Conservar el número tal como está publicado y su unidad. Convertir miles de pesos a pesos multiplicando por 1,000; marcar la conversión como `derivado`. No inventar precisión que la fuente no ofrece.
2. Denominadores nulos, desconocidos o iguales a cero producen «No calculable», nunca cero ni infinito.
3. Para un ingreso mensual constante, la anualización es ingreso mensual × 12. Mostrar ese supuesto y permitir ingreso anual real. El valor declarado por el usuario no es un dato oficial.
4. Mantener separado el ingreso bruto del neto. No comparar un salario neto con una remuneración bruta sin advertir la diferencia.
5. Un costo institucional incluye operación y personal de distintas funciones. Dividirlo entre legisladores no produce el sueldo de cada legislador. Si se ofrece esa división, su nombre será «Gasto institucional por escaño», con denominador documentado para el ejercicio.
6. No convertir una equivalencia salarial en «trabajadores que podrían contratarse»: faltan prestaciones, contribuciones patronales y otros costos.
7. No calcular «mi impuesto robado». El impuesto individual no puede rastrearse proporcionalmente a una observación de auditoría mediante una simple regla de tres.
8. Evitar sumar presupuesto federal transferido, ingreso estatal recibido y gasto municipal financiado con la misma transferencia. Son etapas del mismo flujo.

Para la primera integración conviene elegir equivalencia con ingreso anual, diferencia aprobado/modificado y cobertura de la auditoría. Son operaciones comprensibles y permiten probar la trazabilidad antes de incorporar índices más complejos.

## 6. Experiencia de uso propuesta

El usuario selecciona ámbito, institución, ejercicio y concepto. La calculadora muestra el monto con su chip, unidad, documento y alcance. Después incorpora su ingreso para obtener la equivalencia. Un enlace «Qué revisó la ASF» abre universo, muestra, resultados y seguimiento.

El ticket exportable debe conservar institución, ejercicio, concepto exacto, monto, operación, fuente y fecha de consulta. No basta con compartir una cantidad llamativa. Si cambia el ejercicio de la ficha, se recalculan únicamente los indicadores con datos de ese ejercicio.

El resultado de fiscalización debe poder decir: «No se detectaron irregularidades en la muestra revisada», «Monto pendiente de aclaración al corte informado» o «Seguimiento pendiente de incorporación». Ninguna de estas etiquetas se deduce del color de un semáforo interno.

En el ámbito municipal se mostrará por separado «Ayuntamiento» y, cuando haya evidencia, «Cabildo». La ausencia del desglose del cabildo no impide consultar la información municipal disponible.

## 7. Estructura mínima de la información

Conviene mantener cuatro colecciones relacionadas, sin reemplazar indiscriminadamente la base actual:

| Colección | Campos indispensables |
|---|---|
| Instituciones | Identificador, nombre oficial, ámbito, tipo, clave geográfica, institución superior, vigencia |
| Importes financieros | Institución, ejercicio, periodo, concepto, momento contable, valor original, unidad, moneda, fuente, página, estado |
| Auditorías | Clave completa, fiscalizador, cuenta pública, objeto, universo, muestra, dimensión ingreso/egreso, entrega, dictamen, documento |
| Acciones y seguimiento | Auditoría, acción, resultado, concepto monetario, importe al corte, estado procedimental, fecha, fuente |

Cada dato requiere además fecha de consulta y notas sobre consolidación. Para los derivados: fórmula, identificadores de insumos y política de redondeo. Para los pendientes: motivo concreto, como «sin desglose de cabildo» o «documento no recuperado».

El estado documental `oficial`, `derivado` o `pendiente` es distinto del estado procesal de una acción. Un monto oficial puede seguir pendiente de aclaración. Una fuente oficial tampoco significa que la plataforma deba reproducir el dato sin revisar unidad y alcance.

Las auditorías se identifican por su clave completa y su fiscalizador. El catálogo geográfico debe conservar la vigencia del ejercicio para evitar unir municipios creados o modificados en años diferentes.

## 8. Fuentes complementarias y uso concreto

| Fuente | Para qué sirve | Límite de uso |
|---|---|---|
| [Informes de auditoría ASF](https://www.asf.gob.mx/Section/Section/58_Informes_de_auditoria) | Entradas por Cuenta Pública y entrega | Una entrega parcial no es el cierre de todo el ejercicio |
| [Programa anual de auditorías ASF](https://www.asf.gob.mx/es/Section/358_PAAF) | Identificar revisiones programadas | Programada no significa concluida ni observada |
| [Informes especiales ASF](https://www.asf.gob.mx/Section/59_Informes_especiales_de_auditoria) | Localizar cortes de seguimiento | Comprobar que incluya las acciones de interés |
| [Cuenta Pública federal 2025](https://www.cuentapublica.hacienda.gob.mx/es/CP/2025) | Marco financiero anual; Tomo IV para Legislativo | El índice fue localizado; importes de 2025 no extraídos en esta entrega |
| [Analíticos PEF 2026](https://www.pef.hacienda.gob.mx/es/PEF2026/analiticos_presupuestarios) | Presupuesto y clasificación aprobados | No confundir con el proyecto PPEF ni con gasto pagado |
| [EFIPEM, INEGI](https://www.inegi.org.mx/programas/finanzas/default.html) | Estadística de ingresos y egresos locales | Verificar cobertura, año y carácter preliminar; no sustituye una auditoría |
| [Informes financieros del Congreso CDMX](https://www.congresocdmx.gob.mx/estados-financieros-404-1.html) | Ejemplo de fuente local para desgloses | Directorio localizado; importes y documentos de cada periodo pendientes |
| [Sistema de Alertas SHCP](https://www.disciplinafinanciera.hacienda.gob.mx/es/DISCIPLINA_FINANCIERA/Entidades_Federativas_2026) | Contexto del endeudamiento estatal | Mide endeudamiento, no corrupción ni desempeño del cabildo |

La consulta de la ASF puede mostrar ejercicios más recientes que los ejemplos seleccionados. Se conservarán ambos campos: año de la Cuenta Pública y fecha del informe. Los ejemplos de 2023 y 2024 no deben presentarse como gasto de 2026.

## 9. Secuencia de integración y verificaciones

**Primera parte: trazabilidad.** Incorporar expedientes individuales y sus importes, corregir los valores predeterminados y distinguir los estados documentales de los procesales. Usar los cuatro casos anteriores como ejemplos de alcance diferente.

**Segunda parte: calculadora.** Conectar selección institucional e ingreso del usuario. Validar conversión de unidades, anualización y tratamiento de datos ausentes. La suma de componentes sólo se permitirá si no hay duplicidad.

**Tercera parte: cobertura local.** Construir el inventario de congresos y cuentas públicas estatales; incorporar municipios con documentos recuperables. Mantener una lista de cobertura real, sin llenar vacíos mediante promedios nacionales.

**Cuarta parte: seguimiento.** Incorporar acciones por clave y corte. Conservar el historial de cambios en lugar de sobrescribir silenciosamente los montos.

Criterios de aceptación para programar:

- Cada resultado abre un documento y un localizador comprobables.
- El Senado no duplica su gasto por sumar la dimensión de ingresos.
- Jalisco no duplica el FEIEF incluido en el total auditado.
- Puebla no presenta el universo de contratos como presupuesto municipal ni como costo del cabildo.
- Un importe faltante produce `pendiente`; no genera un semáforo favorable.
- El costo institucional nunca se etiqueta automáticamente como salario.
- Las operaciones preservan ejercicio, corte y momento contable.
- El ticket mantiene fuente, alcance y fórmula, incluso al compartirse.

## 10. Pendientes y límites de esta entrega

La investigación entrega un marco funcional documentado y cuatro expedientes de ejemplo. **No constituye todavía un padrón nacional completo ni una base exhaustiva de finanzas públicas.**

Quedan pendientes: extraer y conciliar la serie financiera de cada congreso local y gobierno estatal; recuperar los desgloses de cabildos; obtener la cobertura municipal por ejercicio; incorporar los cortes actuales de seguimiento de ASF; verificar remuneraciones individuales; seleccionar población oficial para indicadores por habitante; y validar el texto vigente de la ley federal de fiscalización antes de programar plazos procesales. El enlace directo consultado de esa ley no pudo recuperarse, por lo que no se codifican plazos a partir de versiones antiguas.

También queda pendiente la integración en la calculadora: la solicitud actual se atendió como investigación preparatoria. No se cambiaron index.html, enciclopedia.html ni assets, ni se ejecutaron pruebas de interfaz para una modificación que no se realizó.

La carpeta de trabajo no tiene un repositorio Git reconocido (`git status` devuelve «not a git repository»). Por ello esta entrega se guarda localmente; no fue posible realizar el ciclo de pull, commit y push de AGENTS.md. No se sustituyó ni clonó encima de la carpeta existente.
