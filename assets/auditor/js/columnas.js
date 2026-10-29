/* Auditavisión · Aprende › Noticias relevantes (09-10-2026; página propia,
   noticias-relevantes.html, desde el 11-10-2026).
   Columnas editoriales con datos curiosos de personajes y hechos del dinero
   público, en formato de periódico. Reúnen lo que fueron las secciones 5.2
   («Personajes relevantes») y 5.3 («Datos curiosos») de la Enciclopedia,
   retiradas el 27-09-2026 porque no citaban fuentes: aquí solo entra lo que
   se pudo verificar contra un documento oficial, y cada columna lista los
   suyos. Lo que no se pudo sostener se quedó fuera (ver CONTEXT.md).
   Regla editorial (AGENTS.md §2): presunción de inocencia, nada de
   adjetivos; un proceso no es una condena y una observación de la ASF «por
   aclarar» no es un robo probado. */
(function () {
  'use strict';

  var SEC_N = [['todas', 'Todas'], ['Al momento', 'Al momento'], ['Verificado', 'Verificamos']];
  var SEC_O = [['todas', 'Toda la Columna'], ['Personajes', 'Personajes'], ['Hechos', 'Hechos'], ['Historia', 'Historia']];
  /* Ilustración de cada sección cuando la columna no trae retrato. */
  var ILUS = { Personajes: ['🧑‍⚖️', 'tinta'], Hechos: ['🗂️', 'sepia'], Historia: ['📜', 'oliva'], Verificado: ['🔍', 'sepia'], 'Al momento': ['⏱️', 'tinta'] };

  /* Cada columna: {id, seccion, titulo, balazo, cuerpo[], dato_curioso,
     cifras[{valor, etq, estado, fuente, url}], fuentes[{nombre, url}],
     actualizado, icono?, imagen?{src, alt, credito}}.
     La sección «Verificado» (26-10-2026) coteja lo que circula en redes y
     trae además circula{red, cuenta, fecha, texto} y cotejo[{dice, res,
     explica, fuente, url, quien?, donde?}] y sigue[{que, url}] (qué falta
     revisar para seguir el dinero), con res: consta, matiz,
     no consta o pendiente. Un cotejo pendiente lleva quien y donde, y
     herramientas/pendientes.py lo anota en el Registro de pendientes
     (id red-<columna>-<n>).
     Derecho de réplica (Bloque 4, 27-10-2026): si una persona o empresa aludida
     pide aclarar un dato y procede, su texto va en replica[{quien, fecha, texto}]
     y se publica íntegro, sin comentarios ni apostillas (Ley de réplica, art. 6).
     Todas las columnas llevan al pie la liga para pedirla (derecho-de-replica.html).
     La postura (28-10-2026) es lo que la parte aludida dijo en su propio documento:
     postura[{quien, fecha, texto, url}], en sus palabras y sin calificarla.
     «Al momento» (pedido del autor, 28-10-2026): notas breves de lo que está pasando,
     con el mismo cotejo de Verificamos y además fecha, nota{medio, titulo, fecha, url},
     ejemplo{tit, txt, filas, nota}, datos[{ico, tx, url, de}] (lo que dice la
     plataforma: estado de resultados, salud financiera), glosario[{t, url}] y red (la
     búsqueda que se arma en buscadores y redes, rotulada «sin verificar»). Las escribe
     herramientas/integrar_al_momento.py; no se editan a mano. */
  var RES = { 'consta': ['✅', 'Consta'], 'matiz': ['⚠️', 'Consta, con matices'], 'no consta': ['❌', 'Sin documento oficial'], 'pendiente': ['⏳', 'Pendiente'] };
  var COLUMNAS = [
 {
  "id": "senado-ley-de-ingresos-2027",
  "seccion": "Al momento",
  "icono": "🏛️",
  "fecha": "28-10-2026",
  "titulo": "El Senado aprueba la Ley de Ingresos 2027: de sus 10.6 billones, casi 1.5 son dinero prestado",
  "balazo": "El pleno del Senado la aprobó 75 a 34 y sin cambios, así que va al Ejecutivo para publicarse. De los 10.6 billones de pesos que «prevé obtener», 9.2 billones son ingresos y el resto es dinero prestado. Lo que pagan los turistas extranjeros por entrar a México sube a 1,158 pesos, y el cambio al ISR para automotrices y gasolineras todavía no tiene un documento oficial que podamos abrir.",
  "nota": {
   "medio": "El Financiero",
   "titulo": "Senado aprueba cambios al ISR y aumentos en cuotas de servicios y trámites para 2027",
   "fecha": "28-10-2026",
   "url": "https://www.elfinanciero.com.mx/nacional/2026/10/28/senado-aprueba-cambios-al-isr-y-aumentos-en-cuotas-de-servicios-y-tramites-para-2027/"
  },
  "circula": {
   "red": "Instagram",
   "cuenta": "@elfinanciero_mx (El Financiero)",
   "fecha": "28 de octubre de 2026",
   "texto": "El Senado aprobó la Ley de Ingresos y la Ley Federal de Derechos para 2027, que contemplan una recaudación de más de 10.6 billones de pesos… el pago de visitantes extranjeros pasará de 983 a mil 158 pesos… cambios al ISR para excluir a determinadas empresas automotrices y gasolineras de las restricciones a las deducciones… más de 6.2 billones provendrían de impuestos… endeudamiento de hasta 1.7 billones."
  },
  "cuerpo": [
   "Qué pasó. Según el Canal del Congreso (28 de octubre), el pleno del Senado aprobó la Ley de Ingresos de la Federación para 2027 con 75 votos a favor y 34 en contra en lo general, y 73 a 33 en lo particular. Quedó «en sus términos», como la mandó la Cámara de Diputados el 15 de octubre, y se envió al Ejecutivo. La ley manda publicarla en el Diario Oficial a más tardar 20 días naturales después de aprobada (LFPRH, art. 42, fr. VI).",
   "El punto ciego: no son 10.6 billones de «recaudación». La ley estima $10,636,488.1 millones en total, pero esa suma incluye el dinero que el gobierno pedirá prestado. Los ingresos que entran sin endeudarse, los presupuestarios, son $9,156,528.9 millones; la diferencia, $1,479,959.2 millones, son los ingresos por financiamiento, que la ley suma en su total. Y los 1.7 billones de deuda interna son un techo: lo máximo que puede contratar en el año, no deuda ya contratada.",
   "De dónde sale el dinero. Los impuestos aportan $6,263,886.8 millones, el 58.9 % del total: $3,288,975.3 millones del ISR, $1,768,717.3 millones del IVA y $828,256.0 millones del IEPS, según expuso en tribuna el presidente de la Comisión de Hacienda del Senado. Pemex y la CFE tienen sus propios techos de deuda.",
   "Los derechos. La Cámara de Diputados aprobó el 14 de octubre la Ley Federal de Derechos: la cuota que paga quien visita México sin trabajar aquí (el turista extranjero) sube 17.8 % y queda en 1,158 pesos, y lo que se recaude se reparte 57 % para la Defensa, 15 % para el Instituto Nacional de Migración y 28 % para la Tesorería. Que el Senado también la aprobó lo dicen los medios; el documento del Senado todavía no lo pudimos abrir.",
   "Lo que falta probar. Los medios dicen que el Senado cambió la reforma al ISR para que la industria automotriz y quienes venden gasolina y diésel no tengan el nuevo límite a las deducciones de quien ingresa más de 50 millones de pesos, y que por eso esa ley regresa a la Cámara de Diputados. Hasta leer la minuta del Senado, eso va como pendiente: la falta es nuestra, porque el portal del Senado no abre desde la plataforma."
  ],
  "ejemplo": {
   "tit": "La cuenta, con números redondos",
   "txt": "Si la Ley de Ingresos 2027 fueran 100 pesos:",
   "filas": [
    [
     "Impuestos",
     "$59",
     "$6,263,886.8 millones ÷ $10,636,488.1 millones × 100"
    ],
    [
     "Otros ingresos (petroleros, cuotas, derechos, organismos…)",
     "$27",
     "($9,156,528.9 millones − $6,263,886.8 millones) ÷ $10,636,488.1 millones × 100"
    ],
    [
     "Dinero prestado (financiamiento)",
     "$14",
     "($10,636,488.1 millones − $9,156,528.9 millones) ÷ $10,636,488.1 millones × 100"
    ]
   ],
   "nota": "Es un ejemplo derivado con las cifras del Paquete Económico 2027 que la Ley de Ingresos aprobó sin cambios."
  },
  "cotejo": [
   {
    "dice": "El Senado aprobó la Ley de Ingresos para 2027",
    "res": "consta",
    "explica": "75 a 34 en lo general y 73 a 33 en lo particular; quedó en sus términos y se envió al Ejecutivo. Falta su publicación en el Diario Oficial.",
    "fuente": "Canal del Congreso, «Senado aprueba Ley de Ingresos 2027 por 10.6 billones de pesos» (28-10-2026)",
    "url": "https://www.canaldelcongreso.gob.mx/noticias/10338"
   },
   {
    "dice": "Contemplan una recaudación de más de 10.6 billones de pesos",
    "res": "matiz",
    "explica": "La cifra, $10,636,488.1 millones, consta, pero no es recaudación: es el total de la ley e incluye $1,479,959.2 millones de financiamiento. Lo que entra sin endeudarse son $9,156,528.9 millones.",
    "fuente": "Canal del Congreso (28-10-2026) y Paquete Económico 2027 en la base de la plataforma",
    "url": "https://www.canaldelcongreso.gob.mx/noticias/10338"
   },
   {
    "dice": "Más de 6.2 billones provendrían del cobro de impuestos",
    "res": "consta",
    "explica": "Son $6,263,886.8 millones, el 58.9 % de los ingresos estimados.",
    "fuente": "Canal del Congreso (28-10-2026)",
    "url": "https://www.canaldelcongreso.gob.mx/noticias/10338"
   },
   {
    "dice": "El endeudamiento previsto podría alcanzar hasta 1.7 billones de pesos",
    "res": "consta",
    "explica": "La ley autoriza deuda interna neta hasta por 1 billón 700 mil millones de pesos. Es un techo, no deuda contratada; Pemex y la CFE tienen techos aparte.",
    "fuente": "Canal del Congreso (28-10-2026)",
    "url": "https://www.canaldelcongreso.gob.mx/noticias/10338"
   },
   {
    "dice": "El pago de visitantes extranjeros al ingresar a México pasará de 983 a 1,158 pesos",
    "res": "matiz",
    "explica": "Constan los 1,158 pesos y la subida de 17.8 %, en la versión que aprobó la Cámara de Diputados; es la cuota de quien entra sin permiso para trabajar, el turista. Los 983 pesos de hoy no vienen en la nota oficial, aunque cuadran con esa subida (1,158 ÷ 1.178 ≈ 983, derivado).",
    "fuente": "Canal del Congreso, «Cámara de Diputados aprueba Ley Federal de Derechos 2027» (14-10-2026)",
    "url": "https://www.canaldelcongreso.gob.mx/noticias/10318"
   },
   {
    "dice": "El Senado aprobó también la Ley Federal de Derechos",
    "res": "pendiente",
    "explica": "La nota oficial del Senado que leímos solo trae la Ley de Ingresos. El voto de la Ley de Derechos no lo pudimos abrir.",
    "fuente": "Canal del Congreso (28-10-2026)",
    "url": "https://www.canaldelcongreso.gob.mx/noticias/10338",
    "quien": "Falta de la plataforma: el dictamen y su votación están en la Gaceta del Senado, que no abre desde nuestra sesión",
    "donde": "https://www.senado.gob.mx/66/gaceta_del_senado"
   },
   {
    "dice": "Se excluye a automotrices y gasolineras de las restricciones a las deducciones de quien ingresa más de 50 millones, y la ley del ISR regresa a Diputados",
    "res": "pendiente",
    "explica": "Ningún documento oficial que pudimos abrir trae la reserva ni su votación. Cuando la Cámara de Diputados reciba la minuta, su texto quedará en la Gaceta Parlamentaria.",
    "fuente": "El Financiero y otros medios (28-10-2026)",
    "url": "https://www.elfinanciero.com.mx/nacional/2026/10/28/senado-aprueba-cambios-al-isr-y-aumentos-en-cuotas-de-servicios-y-tramites-para-2027/",
    "quien": "Falta de la plataforma: la minuta del Senado no abre desde nuestra sesión; después la publicará la Gaceta de Diputados",
    "donde": "https://gaceta.diputados.gob.mx/"
   }
  ],
  "cifras": [
   {
    "valor": "$10,636,488.1 millones",
    "etq": "Ley de Ingresos 2027: el total, con financiamiento",
    "estado": "oficial",
    "fuente": "Canal del Congreso (28-10-2026)",
    "url": "https://www.canaldelcongreso.gob.mx/noticias/10338"
   },
   {
    "valor": "$9,156,528.9 millones",
    "etq": "Ingresos presupuestarios 2027: lo que entra sin endeudarse",
    "estado": "oficial",
    "fuente": "Criterios Generales de Política Económica 2027 (en la base)",
    "url": "numeros-paquete-2027-cifras.html"
   },
   {
    "valor": "$1,479,959.2 millones",
    "etq": "Financiamiento dentro del total (total − ingresos presupuestarios)",
    "estado": "derivado",
    "fuente": "Operación con las dos cifras anteriores",
    "url": "numeros-paquete-2027-cifras.html"
   },
   {
    "valor": "$6,263,886.8 millones",
    "etq": "Impuestos estimados para 2027",
    "estado": "oficial",
    "fuente": "Canal del Congreso (28-10-2026)",
    "url": "https://www.canaldelcongreso.gob.mx/noticias/10338"
   },
   {
    "valor": "75 a 34",
    "etq": "Votación en lo general en el pleno del Senado (73 a 33 en lo particular)",
    "estado": "oficial",
    "fuente": "Canal del Congreso (28-10-2026)",
    "url": "https://www.canaldelcongreso.gob.mx/noticias/10338"
   },
   {
    "valor": "$1,158",
    "etq": "Cuota del visitante extranjero sin actividad remunerada en 2027 (+17.8 %)",
    "estado": "oficial",
    "fuente": "Canal del Congreso (14-10-2026)",
    "url": "https://www.canaldelcongreso.gob.mx/noticias/10318"
   }
  ],
  "datos": [
   {
    "ico": "📊",
    "tx": "Cómo se ve 2027: las cifras del Paquete Económico",
    "url": "numeros-paquete-2027-cifras.html",
    "de": "Ingresos, gasto, déficit y deuda de 2027 junto a 2026, con los Criterios Generales."
   },
   {
    "ico": "🧾",
    "tx": "Los impuestos del Paquete 2027",
    "url": "numeros-paquete-2027-impuestos.html",
    "de": "Qué impuestos cambian y cuánto se espera de cada uno."
   },
   {
    "ico": "🗓️",
    "tx": "El itinerario que manda la ley",
    "url": "numeros-paquete-2027-itinerario.html",
    "de": "Diputados a más tardar el 20 de octubre, el Senado el 31 y la publicación 20 días después."
   },
   {
    "ico": "📉",
    "tx": "La deuda",
    "url": "numeros-la-deuda.html",
    "de": "Cuánto debe el país y quién autoriza cada peso prestado."
   },
   {
    "ico": "🔍",
    "tx": "El cotejo de la Ley de Ingresos en Diputados: el techo de deuda y el perdón de multas",
    "url": "noticias-auditavision.html#col-lif-2027-deuda-y-multas",
    "de": "Lo que circuló el 15 de octubre, afirmación por afirmación."
   }
  ],
  "glosario": [
   {
    "t": "LIF (Ley de Ingresos de la Federación)",
    "url": "glosario.html#LIF"
   },
   {
    "t": "Ingresos presupuestarios",
    "url": "glosario.html#Ingresos-Presupuestarios"
   },
   {
    "t": "Techo de endeudamiento neto",
    "url": "glosario.html#Techo-de-Endeudamiento-Neto"
   },
   {
    "t": "ISR",
    "url": "glosario.html#ISR"
   },
   {
    "t": "Derechos (contribución)",
    "url": "glosario.html#Derechos"
   }
  ],
  "red": "Senado Ley de Ingresos 2027 ISR automotrices gasolineras",
  "sigue": [
   {
    "que": "La publicación de la Ley de Ingresos 2027 en el Diario Oficial (a más tardar 20 días naturales después de aprobada)",
    "url": "https://www.dof.gob.mx/"
   },
   {
    "que": "El voto del Senado sobre la Ley Federal de Derechos y su publicación en el Diario Oficial",
    "url": "https://www.senado.gob.mx/66/gaceta_del_senado"
   },
   {
    "que": "La minuta del ISR que regresa a la Cámara de Diputados: el texto de la excepción para automotrices y gasolineras y su votación",
    "url": "https://gaceta.diputados.gob.mx/"
   },
   {
    "que": "El Presupuesto de Egresos 2027, que la Cámara de Diputados debe aprobar a más tardar el 15 de noviembre",
    "url": "https://gaceta.diputados.gob.mx/"
   }
  ],
  "fuentes": [
   {
    "nombre": "Canal del Congreso: Senado aprueba Ley de Ingresos 2027 por 10.6 billones de pesos (28-10-2026)",
    "url": "https://www.canaldelcongreso.gob.mx/noticias/10338"
   },
   {
    "nombre": "Canal del Congreso: Cámara de Diputados aprueba Ley Federal de Derechos 2027 (14-10-2026)",
    "url": "https://www.canaldelcongreso.gob.mx/noticias/10318"
   },
   {
    "nombre": "Canal del Congreso: Aprueban en San Lázaro Ley de Ingresos 2027 (15-10-2026)",
    "url": "https://www.canaldelcongreso.gob.mx/noticias/10320"
   },
   {
    "nombre": "Paquete Económico 2027: Criterios Generales de Política Económica (en la base de la plataforma)",
    "url": "numeros-paquete-2027-cifras.html"
   },
   {
    "nombre": "Punto de partida: El Financiero, «Senado aprueba cambios al ISR y aumentos en cuotas de servicios y trámites para 2027» (28-10-2026)",
    "url": "https://www.elfinanciero.com.mx/nacional/2026/10/28/senado-aprueba-cambios-al-isr-y-aumentos-en-cuotas-de-servicios-y-tramites-para-2027/"
   }
  ],
  "actualizado": "29-10-2026"
 },
 {
  "id": "imss-modalidad-40-gestores",
  "seccion": "Al momento",
  "icono": "⏱️",
  "fecha": "28-10-2026",
  "titulo": "El IMSS acota la Modalidad 40: lo que dice el Diario Oficial y lo que falta probar",
  "balazo": "Desde el 22 de octubre, quien entre a la Modalidad 40 cotiza con su último salario o, cuando mucho, con una UMA más. El esquema de gestores y empresas fantasma que describió el director del IMSS todavía no tiene un documento público.",
  "nota": {
   "medio": "La Jornada",
   "titulo": "Cambios a la modalidad 40, para frenar «abusos y fraudes»: Robledo",
   "fecha": "28-10-2026",
   "url": "https://www.jornada.com.mx/2026/10/28/politica/012n2pol"
  },
  "circula": {
   "red": "La Jornada (prensa)",
   "cuenta": "Zoé Robledo, director general del IMSS, citado por La Jornada",
   "fecha": "28 de octubre de 2026",
   "texto": "La Modalidad 40 del IMSS se acotó tras detectarse un esquema fraudulento de gestores que financiaban a los asegurados para pagar sus cotizaciones. En realidad se trataba de créditos que terminaba pagando el Estado mexicano, con pensiones que llegaban a incrementarse hasta mil por ciento. En otros casos, se les inscribía a empresas fantasma para seguir cotizando y cubrir las semanas requeridas, para luego incorporarse a la Modalidad 40."
  },
  "cuerpo": [
   "Qué pasó. El 10 de octubre, el Consejo Técnico del IMSS aprobó un acuerdo que se publicó en el Diario Oficial el 21 de octubre y rige desde el día hábil siguiente, el 22. La Modalidad 40 (la ley la llama «continuación voluntaria en el régimen obligatorio») no desaparece: quien ya estaba inscrito sigue en las mismas condiciones hasta que termine el periodo que contrató, y conserva las semanas y los salarios que efectivamente pagó.",
   "Qué cambió para quien se inscriba ahora. La ley dice que te inscribes «con el último salario o superior al que tenía en el momento de la baja» (art. 218), hasta el tope general de 25 veces (art. 28). El acuerdo pone, como medida temporal, un techo mucho más bajo: tu último salario registrado o hasta ese salario más una UMA ($3,566.22 al mes en 2026), nunca menos de un salario mínimo. Además, ya no se puede pagar hacia atrás, porque el aseguramiento cuenta desde la fecha de la solicitud; la inscripción será solo digital, y quien se asegura por su cuenta como trabajador independiente (art. 13, fracción I) ya no puede contratarla.",
   "Por qué es dinero público. Las pensiones de quienes eligen el régimen de la ley de 1973 las paga el Gobierno Federal, no un fondo propio de cada trabajador (Ley del Seguro Social, transitorio duodécimo). Por eso una pensión más alta, lograda con cotizaciones altas en los últimos años, la termina pagando el erario. En el Presupuesto 2026 ese gasto pasa por el Ramo 19, Aportaciones a Seguridad Social, con $1,541,518.7 millones; el presupuesto no separa cuánto de eso corresponde a la Modalidad 40.",
   "Lo que falta probar. El acuerdo no habla de fraudes, gestores ni empresas fantasma: dice que el Consejo «tomó conocimiento» de los informes de tres direcciones del IMSS, que no se han publicado. Los casos, el «mil por ciento» y las denuncias de las que habló el director general del IMSS, Zoé Robledo, son, por ahora, declaraciones. Una acusación no es una condena, y quien pagó su Modalidad 40 con su propio dinero no hizo nada indebido.",
   "El punto ciego. La ley dice «último salario o superior» y el acuerdo le pone techo. Si un acuerdo del Consejo Técnico puede acotar lo que dice una ley del Congreso lo decidiría, en su caso, un tribunal. Mientras tanto, la medida vale hasta que el IMSS tenga su análisis financiero, que el propio acuerdo pide a más tardar seis meses después de emitido."
  ],
  "ejemplo": {
   "tit": "La cuenta, con números redondos",
   "txt": "Si tu último salario registrado ante el IMSS era de $10,000.00 al mes, esto es lo más alto con lo que podrías cotizar en la Modalidad 40:",
   "filas": [
    [
     "Antes: la ley (arts. 218 y 28)",
     "$89,155.50",
     "25 × $3,566.22 (UMA mensual 2026)"
    ],
    [
     "Desde el 22-10-2026: el acuerdo",
     "$13,566.22",
     "$10,000.00 + $3,566.22"
    ]
   ],
   "nota": "Es un ejemplo derivado con la UMA mensual de 2026. Tu caso depende de tu historial de semanas y salarios."
  },
  "cotejo": [
   {
    "dice": "La Modalidad 40 del IMSS se acotó",
    "res": "consta",
    "explica": "El punto cuarto del acuerdo limita a los nuevos inscritos a su último salario registrado o hasta ese salario más una UMA, sin pagos hacia atrás. Es una medida temporal: dura hasta que el IMSS tenga su análisis financiero. Quien ya estaba inscrito conserva sus condiciones.",
    "fuente": "DOF 21-10-2026, Acuerdo ACDO.AS2.HCT.101026/302.P.DG del Consejo Técnico del IMSS, puntos cuarto y séptimo",
    "url": "https://sidof.segob.gob.mx/notas/5801708"
   },
   {
    "dice": "Se acotó tras detectarse un esquema fraudulento de gestores que financiaban a los asegurados para pagar sus cotizaciones",
    "res": "pendiente",
    "explica": "El acuerdo solo dice que el Consejo tomó conocimiento de los informes de las direcciones de Incorporación y Recaudación, de Prestaciones Económicas y Sociales y Jurídica; no los publica ni menciona a gestores. La ley pide que el asegurado pague sus cuotas por mes adelantado (art. 218), pero no dice de dónde debe salir el dinero: si un préstamo así fue fraude, lo tiene que probar una investigación.",
    "fuente": "DOF 21-10-2026, Acuerdo ACDO.AS2.HCT.101026/302.P.DG del Consejo Técnico del IMSS, punto primero",
    "url": "https://sidof.segob.gob.mx/notas/5801708",
    "quien": "IMSS: su H. Consejo Técnico y su Dirección Jurídica (los informes de la sesión del 10-10-2026 y las denuncias)",
    "donde": "https://www.imss.gob.mx/transparencia"
   },
   {
    "dice": "En realidad se trataba de créditos que terminaba pagando el Estado mexicano",
    "res": "matiz",
    "explica": "Consta que el Gobierno Federal paga las pensiones de quienes eligen el régimen de 1973: por eso una pensión más alta la paga el erario. Que esas cotizaciones se pagaran con préstamos de gestores no tiene, por ahora, documento público.",
    "fuente": "Ley del Seguro Social, transitorio duodécimo (texto vigente, última reforma DOF 15-01-2026)",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/LSS.pdf"
   },
   {
    "dice": "Pensiones que llegaban a incrementarse hasta mil por ciento",
    "res": "pendiente",
    "explica": "Ningún documento público trae los casos ni cómo se calculó ese porcentaje. Sin los casos no se puede comprobar ni descartar. El acuerdo ordena que la Dirección de Finanzas analice el efecto de la Modalidad 40 en la situación financiera del IMSS a más tardar seis meses después de emitido: ahí debería estar.",
    "fuente": "DOF 21-10-2026, Acuerdo ACDO.AS2.HCT.101026/302.P.DG del Consejo Técnico del IMSS, punto segundo",
    "url": "https://sidof.segob.gob.mx/notas/5801708",
    "quien": "IMSS: Dirección de Finanzas, Unidad de Riesgos Financieros y Actuariales (el análisis financiero, a más tardar el 10-04-2027)",
    "donde": "https://www.imss.gob.mx/transparencia"
   },
   {
    "dice": "Se les inscribía a empresas fantasma para seguir cotizando y cubrir las semanas requeridas",
    "res": "pendiente",
    "explica": "El IMSS no ha dicho qué empresas ni cuántos casos. Una empresa que factura operaciones simuladas aparece en la lista 69-B del SAT, que puedes consultar en nuestra Lista negra del SAT; dar de alta trabajadores que no existen se ve en los registros del propio IMSS, que no son públicos.",
    "fuente": "DOF 21-10-2026, Acuerdo ACDO.AS2.HCT.101026/302.P.DG del Consejo Técnico del IMSS, puntos primero y quinto",
    "url": "https://sidof.segob.gob.mx/notas/5801708",
    "quien": "IMSS: Dirección de Incorporación y Recaudación (qué patrones y cuántos casos)",
    "donde": "https://www.imss.gob.mx/transparencia"
   }
  ],
  "cifras": [
   {
    "valor": "+1 UMA",
    "etq": "lo más que puede subir tu salario de cotización al entrar a la Modalidad 40 desde el 22-10-2026",
    "estado": "oficial",
    "fuente": "DOF 21-10-2026, Acuerdo ACDO.AS2.HCT.101026/302.P.DG del Consejo Técnico del IMSS, punto cuarto",
    "url": "https://sidof.segob.gob.mx/notas/5801708"
   },
   {
    "valor": "25 veces",
    "etq": "el tope general de cotización de la ley, al que antes podía llegar la Modalidad 40 (desde 2016 se mide en UMA)",
    "estado": "oficial",
    "fuente": "Ley del Seguro Social, arts. 28 y 218",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/LSS.pdf"
   },
   {
    "valor": "$3,566.22",
    "etq": "una UMA al mes en 2026",
    "estado": "oficial",
    "fuente": "INEGI, UMA 2026 (DOF 09-01-2026)",
    "url": "https://www.inegi.org.mx/temas/uma/"
   },
   {
    "valor": "$1,541,518.7 millones",
    "etq": "Ramo 19, Aportaciones a Seguridad Social, en 2026: por ahí pasan las pensiones que paga el Gobierno Federal",
    "estado": "oficial",
    "fuente": "PEF 2026, Anexo 1, pp. 33-34",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/PEF_2026.pdf"
   },
   {
    "valor": "10-04-2027",
    "etq": "a más tardar, el análisis financiero del IMSS (10-10-2026 + 6 meses)",
    "estado": "derivado",
    "fuente": "DOF 21-10-2026, Acuerdo ACDO.AS2.HCT.101026/302.P.DG del Consejo Técnico del IMSS, punto segundo",
    "url": "https://sidof.segob.gob.mx/notas/5801708"
   }
  ],
  "datos": [
   {
    "ico": "📊",
    "tx": "El estado de resultados del IMSS en 2025",
    "url": "datos-salud-imss.html#sal-imss_dinero",
    "de": "El seguro de Invalidez y Vida, uno de los dos a los que cotiza la Modalidad 40, cerró con un excedente de $108,197.4 millones; el de Enfermedad y Maternidad gastó $151,126.8 millones más de lo que ingresó, y todo el IMSS cerró con un faltante de $4,398.4 millones (Memoria Estadística 2025, cuadro XIII.45)."
   },
   {
    "ico": "🏛️",
    "tx": "La salud financiera del IMSS",
    "url": "herramienta-inspector-entes.html#ente=federal:imss",
    "de": "Su gasto en la Cuenta Pública 2025 y su ficha en el Auditor de entes, con sus documentos."
   },
   {
    "ico": "🧾",
    "tx": "Busca una empresa en la lista negra del SAT",
    "url": "herramienta-inspector-efos.html",
    "de": "Por RFC o por nombre: las empresas que el SAT presume que facturan operaciones simuladas (art. 69-B del Código Fiscal)."
   },
   {
    "ico": "🔍",
    "tx": "Contrasta otra nota de este tema",
    "url": "herramienta-inspector-nota.html",
    "de": "Pega la liga de una nota y la cotejamos contra los documentos oficiales."
   }
  ],
  "glosario": [
   {
    "t": "Continuación voluntaria (Modalidad 40)",
    "url": "glosario.html#Continuacion-Voluntaria"
   },
   {
    "t": "UMA",
    "url": "glosario.html#UMA"
   },
   {
    "t": "Cuota obrera del IMSS",
    "url": "glosario.html#Cuota-Obrera-del-IMSS"
   },
   {
    "t": "Empresa fantasma",
    "url": "glosario.html#Empresa-Fantasma"
   },
   {
    "t": "IMSS",
    "url": "glosario.html#Instituto-Mexicano-del-Seguro-Social"
   }
  ],
  "red": "Modalidad 40 IMSS",
  "sigue": [
   {
    "que": "El análisis financiero de la Modalidad 40 que el acuerdo pide al IMSS (a más tardar el 10-04-2027)",
    "url": "https://www.imss.gob.mx/transparencia"
   },
   {
    "que": "La propuesta de cambio a las reglas que la Dirección Jurídica debe llevar al Consejo Técnico (hasta 6 meses después del análisis)",
    "url": "https://sidof.segob.gob.mx/notas/5801708"
   },
   {
    "que": "Las denuncias que el IMSS dice haber presentado: en qué fiscalía y en qué etapa van",
    "url": "https://www.gob.mx/fgr"
   },
   {
    "que": "Si un tribunal revisa si un acuerdo del Consejo Técnico puede acotar el art. 218 de la ley",
    "url": "https://www.scjn.gob.mx"
   }
  ],
  "fuentes": [
   {
    "nombre": "DOF 21-10-2026, Acuerdo ACDO.AS2.HCT.101026/302.P.DG del Consejo Técnico del IMSS (texto íntegro en SIDOF)",
    "url": "https://sidof.segob.gob.mx/notas/5801708"
   },
   {
    "nombre": "Ley del Seguro Social, texto vigente (última reforma DOF 15-01-2026): arts. 28, 218 y transitorio duodécimo",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/LSS.pdf"
   },
   {
    "nombre": "Presupuesto de Egresos de la Federación 2026, Anexo 1, pp. 33-34 (Ramo 19)",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/PEF_2026.pdf"
   },
   {
    "nombre": "INEGI, Unidad de Medida y Actualización 2026",
    "url": "https://www.inegi.org.mx/temas/uma/"
   },
   {
    "nombre": "IMSS, Memoria Estadística 2025, cap. XIII, cuadro XIII.45",
    "url": "https://www.imss.gob.mx/sites/all/statics/pdf/estadisticas/memoria/2025/13-RecursosHumanosMaterialesFinancieros.xlsx"
   },
   {
    "nombre": "Punto de partida: La Jornada, «Cambios a la modalidad 40, para frenar “abusos y fraudes”: Robledo» (28-10-2026)",
    "url": "https://www.jornada.com.mx/2026/10/28/politica/012n2pol"
   }
  ],
  "actualizado": "28-10-2026"
 },
 {
  "id": "seguro-popular-51-millones",
  "seccion": "Verificado",
  "icono": "🔎",
  "titulo": "«Con el Seguro Popular se atendieron más de 51 millones; ahorita nada». Lo que dicen el INEGI y la ASF",
  "balazo": "El Seguro Popular llegó a 53.5 millones de afiliados (ASF, Cuenta Pública 2018). Estar afiliado no es lo mismo que haber sido atendido, pero el golpe que se describe sí se ve en los números: las personas sin acceso a servicios de salud pasaron de 20.1 millones en 2018 a 50.4 millones en 2022, y en 2024 eran 44.5 millones (INEGI).",
  "circula": {
   "red": "Instagram (audio de un reel)",
   "cuenta": "Testimonio de una persona que dice trabajar en los servicios de salud «toda la vida»; es una persona privada y no se le nombra. Llegó como audio, sin liga",
   "fecha": "28 de octubre de 2026 (día en que llegó al Auditor)",
   "texto": "—¿Cuántos años tiene trabajando usted aquí? —Toda la vida, gracias a Dios. Siempre, siempre, pero nunca como hoy. Pregúntale a la gente, la gente les va a decir. No digo que esto es nuevo. La corrupción no termina, pero esta ha sido la peor de toda la época en México. La peor. Cuando hicieron el Seguro Popular, yo pensé que estaba mal y resulta que fue lo mejor que se pudo haber instalado en México. Se atendieron más de 51 millones de mexicanos. Ahorita nada. Le dieron en la torre a la salud. ¿Por qué lo quitaron? No es un bienestar, es malestar. Malestar en todos los sentidos. Te voy a decir algo muy importante. Es muy feo llegar a viejo y no servir. Así es que nosotros vamos a servir con lo que podamos y como estemos."
  },
  "cuerpo": [
   "Lo que dice este testimonio es serio, y por eso se coteja como cualquier cifra: con el documento oficial. Habla de tres cosas que sí se pueden medir: cuánta gente tenía el Seguro Popular, cuánta se quedó sin acceso a la salud después, y cuándo y cómo se quitó. Lo demás («la peor corrupción», «es malestar») es la opinión de quien lo vive, y se respeta como tal: no se coteja.",
   "Cuánta gente tenía. El Seguro Popular era el brazo del Sistema de Protección Social en Salud para quien no tenía IMSS ni ISSSTE. Según la Auditoría Superior de la Federación, pasó de 5.3 millones de afiliados en 2004 a 53.5 millones en 2017, y para 2018 las 32 entidades acordaron mantener esa cobertura (auditoría MR-Seguro Popular, Cuenta Pública 2018, con datos de la Comisión Nacional de Protección Social en Salud). Así que «más de 51 millones» se queda corto, pero es la cifra de afiliados: una persona afiliada tenía derecho a atenderse, no necesariamente se atendió. Cuántas consultas dio en realidad está en los informes de resultados del propio sistema, que aún no integramos.",
   "Cuánta gente se quedó sin acceso. El INEGI, que ahora mide la pobreza con la metodología del CONEVAL, cuenta a las personas con «carencia por acceso a los servicios de salud»: en 2018 eran 20.1 millones (16.2 %); en 2020, 35.7 millones (28.2 %); en 2022, 50.4 millones (39.1 %), y en 2024, 44.5 millones (34.2 %). Son 24.4 millones más que en 2018, aunque 5.9 millones menos que en el peor momento, 2022 (comunicado 118/25 del INEGI, cuadro 1). «Ahorita nada» no es literal: en 2024, 4.6 millones de personas dijeron estar afiliadas al IMSS-Bienestar y 13.7 millones se atienden en un centro de salud, hospital o instituto público. Pero el retroceso frente a 2018 es real y está medido.",
   "¿Por qué lo quitaron? El cuándo y el cómo constan en la Ley General de Salud: el decreto del 29 de noviembre de 2019 sustituyó el Seguro Popular por el INSABI desde el 1 de enero de 2020, y el decreto del 29 de mayo de 2023 extinguió el INSABI y pasó sus recursos al IMSS-Bienestar. Tres instituciones en seis años. El porqué es una decisión política del Ejecutivo y del Congreso que aprobó las reformas; la plataforma no la juzga, la mide.",
   "Ojo con la comparación. La medición cuenta si la persona está afiliada o tiene derecho a una institución, no si la atendieron bien ni si había medicinas. Y como las instituciones cambiaron, las series del sistema de salud se rompen en 2020 y en 2023. Quien diga «hoy se atiende más» o «hoy se atiende menos» tiene que decir de qué documento sale cada año.",
   "Una nota de método: lo que circula es el audio de un reel de Instagram, y lo que se cotejó es su transcripción. A quien da el testimonio no se le nombra. Los dos documentos del INEGI y la auditoría de la ASF se leyeron completos. Las restas (24.4 y 5.9 millones) son nuestras: van como derivadas."
  ],
  "dato_curioso": "En 2022, 50.4 millones de personas no tenían acceso a servicios de salud: casi tantas como las que llegó a tener afiliadas el Seguro Popular en su mejor momento (53.5 millones).",
  "cifras": [
   {
    "valor": "53.5 millones",
    "etq": "Afiliados al Seguro Popular en 2017, cobertura que las 32 entidades acordaron mantener en 2018",
    "estado": "oficial",
    "fuente": "ASF, auditoría MR-Seguro Popular, Cuenta Pública 2018 (datos de la CNPSS)",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2018b/Documentos/Auditorias/2018_MR-SEGURO%20POPULAR_a.pdf"
   },
   {
    "valor": "20.1 → 44.5 millones",
    "etq": "Personas con carencia por acceso a los servicios de salud, 2018 y 2024 (16.2 % y 34.2 % de la población)",
    "estado": "oficial",
    "fuente": "INEGI, comunicado 118/25, Pobreza multidimensional 2024, cuadro 1",
    "url": "https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2025/pm/pm2025_08.pdf"
   },
   {
    "valor": "50.4 millones",
    "etq": "Personas sin acceso a servicios de salud en 2022, el punto más alto de la serie (39.1 %)",
    "estado": "oficial",
    "fuente": "INEGI, comunicado 118/25, cuadro 1",
    "url": "https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2025/pm/pm2025_08.pdf"
   },
   {
    "valor": "24.4 millones",
    "etq": "Personas sin acceso a servicios de salud de más en 2024 que en 2018. Operación: 44.5 − 20.1",
    "estado": "derivado",
    "fuente": "Cálculo con el cuadro 1 del comunicado 118/25 del INEGI",
    "url": "https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2025/pm/pm2025_08.pdf"
   }
  ],
  "cotejo": [
   {
    "dice": "Con el Seguro Popular se atendieron más de 51 millones de mexicanos.",
    "res": "matiz",
    "explica": "El padrón llegó a 53.5 millones de afiliados (2017), así que la cifra se queda corta. El matiz: son afiliados, personas con derecho a atenderse, no personas atendidas. Cuántas se atendieron de verdad no lo tenemos todavía.",
    "fuente": "ASF, auditoría MR-Seguro Popular, Cuenta Pública 2018",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2018b/Documentos/Auditorias/2018_MR-SEGURO%20POPULAR_a.pdf"
   },
   {
    "dice": "Cuántas personas afiliadas al Seguro Popular recibieron atención.",
    "res": "pendiente",
    "explica": "Las consultas y servicios que dio el sistema venían en sus informes anuales de resultados, que la plataforma aún no ha integrado.",
    "fuente": "ASF, auditoría MR-Seguro Popular, Cuenta Pública 2018",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2018b/Documentos/Auditorias/2018_MR-SEGURO%20POPULAR_a.pdf",
    "quien": "Falta de la plataforma: la Comisión Nacional de Protección Social en Salud (Secretaría de Salud) publicaba cada año su Informe de Resultados del Sistema de Protección Social en Salud, con las consultas y los servicios dados a los afiliados; aún no lo integramos",
    "donde": "https://www.gob.mx/salud"
   },
   {
    "dice": "Ahorita nada. Le dieron en la torre a la salud.",
    "res": "matiz",
    "explica": "El retroceso consta: sin acceso a servicios de salud había 20.1 millones en 2018, 50.4 millones en 2022 y 44.5 millones en 2024. «Nada» no es literal: en 2024, 4.6 millones dijeron estar afiliados al IMSS-Bienestar y 13.7 millones se atienden en centros de salud u hospitales públicos.",
    "fuente": "INEGI, comunicado 118/25 (cuadro 1) y presentación de resultados de Pobreza multidimensional 2024",
    "url": "https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2025/pm/pm2025_08.pdf"
   },
   {
    "dice": "¿Por qué lo quitaron?",
    "res": "consta",
    "explica": "Que se quitó, cuándo y por qué ley consta: decreto del DOF del 29-11-2019 (Seguro Popular → INSABI desde el 1-01-2020) y decreto del 29-05-2023 (se extingue el INSABI y pasa al IMSS-Bienestar). El porqué de fondo es una decisión política: no se coteja.",
    "fuente": "Ley General de Salud, transitorios de los decretos del 29-11-2019 y del 29-05-2023",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/LGS.pdf"
   },
   {
    "dice": "La corrupción no termina, pero esta ha sido la peor de toda la época en México.",
    "res": "matiz",
    "explica": "Es una opinión, no una cifra: no hay un documento oficial que compare la corrupción de un sexenio con la de otro. Lo que sí se puede revisar son las auditorías de la ASF de cada año, y el Seguro Popular también tuvo las suyas.",
    "fuente": "ASF, auditoría MR-Seguro Popular, Cuenta Pública 2018",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2018b/Documentos/Auditorias/2018_MR-SEGURO%20POPULAR_a.pdf"
   },
   {
    "dice": "No es un bienestar, es malestar.",
    "res": "matiz",
    "explica": "Es la opinión de quien lo vive, y se respeta: no se coteja. Lo medible está arriba: cuánta gente se quedó sin acceso y cuándo cambió el sistema.",
    "fuente": "INEGI, comunicado 118/25",
    "url": "https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2025/pm/pm2025_08.pdf"
   }
  ],
  "sigue": [
   {
    "que": "Los informes de resultados del Sistema de Protección Social en Salud (2012 a 2019): consultas y servicios reales a los afiliados, para compararlos con los del IMSS-Bienestar",
    "url": "https://www.gob.mx/salud"
   },
   {
    "que": "Los servicios y el gasto del IMSS-Bienestar en 2025, que la plataforma aún no encuentra publicados",
    "url": "datos-salud-sistema.html#sal-transicion"
   },
   {
    "que": "Las auditorías de la ASF al INSABI (2020 a 2023) y al IMSS-Bienestar: qué pasó con el dinero que heredaron del Seguro Popular",
    "url": "https://www.asf.gob.mx/"
   },
   {
    "que": "La medición de pobreza 2026 del INEGI, para ver si la carencia de acceso a la salud sigue bajando",
    "url": "https://www.inegi.org.mx/desarrollosocial/pm/"
   }
  ],
  "fuentes": [
   {
    "nombre": "INEGI, Comunicado de prensa 118/25, Pobreza multidimensional 2024 (13-08-2025)",
    "url": "https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2025/pm/pm2025_08.pdf"
   },
   {
    "nombre": "INEGI, Pobreza multidimensional 2024, presentación de resultados",
    "url": "https://www.inegi.org.mx/contenidos/desarrollosocial/pm/doc/pm_presentacion_2024.pdf"
   },
   {
    "nombre": "ASF, Recursos federales transferidos a través del Acuerdo de Coordinación, MR-Seguro Popular, Cuenta Pública 2018",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2018b/Documentos/Auditorias/2018_MR-SEGURO%20POPULAR_a.pdf"
   },
   {
    "nombre": "Ley General de Salud, texto vigente (Cámara de Diputados)",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/LGS.pdf"
   },
   {
    "nombre": "Auditavisión, Datos · Salud pública: del Seguro Popular al IMSS-Bienestar",
    "url": "datos-salud-sistema.html#sal-transicion"
   }
  ],
  "actualizado": "28 de octubre de 2026"
 },
 {
  "id": "isssteson-oxigeno-pensiones-fallecidos",
  "seccion": "Verificado",
  "icono": "🔎",
  "titulo": "ISSSTESON: oxígeno pagado a un paciente fallecido y pensiones a personas muertas. ¿Dónde está el dinero?",
  "balazo": "Las cifras de la nota constan en la auditoría del ISAF al ISSSTESON del primer semestre de 2025. Pero el mismo informe responde dónde está el dinero: de los $2,990,499 en pensiones, $2,458,447 eran cheques que se cancelaron sin cobrarse, $158,619 ya se recuperaron y faltan $373,438 por devolver. Del oxígeno, los $158,400 siguen sin comprobarse.",
  "circula": {
   "red": "Instagram (audio de un reel)",
   "cuenta": "Audio de un reel que nos compartiste sin liga; lo que se coteja es su transcripción, abajo",
   "fecha": "28 de octubre de 2026 (día en que llegó al Auditor)",
   "texto": "¿Dónde está todo este dinero? No hallan si los beneficiados, como bien comentaban, por segundo año consecutivo en la compra de oxígeno a domicilio, pues no pudieron acreditarse la entrega a pacientes por más de 150,000 pesos y volvieron a pagar el oxígeno de un paciente que ya había fallecido el 9 de mayo de 2024. Además, pagaron 2,990,499 pesos en pensiones y jubilaciones a personas que ya estaban muertas según las actas de defunción por el Registro Civil. Morena nos lleva a la justicia social hasta la tumba."
  },
  "cuerpo": [
   "La nota no habla de la Auditoría Superior de la Federación: sus cifras vienen del Instituto Superior de Auditoría y Fiscalización de Sonora (ISAF), que revisa las cuentas del gobierno del estado. El informe es el 2025AE0109010005, la auditoría integral al segundo trimestre de 2025 (lo acumulado de enero a junio) del Instituto de Seguridad y Servicios Sociales de los Trabajadores del Estado de Sonora (ISSSTESON), que da salud y pensiones a la burocracia estatal. Se notificó en marzo de 2026. En ese semestre el Instituto gastó (devengó) $6,322.4 millones, y el ISAF revisó el 86 %.",
   "El oxígeno. En diciembre de 2024 el ISSSTESON compró oxígeno a domicilio para 121 pacientes a Biosistemas y Seguridad Privada, S.A. de C.V., y lo pagó el 14 de marzo de 2025: $173,792. Solo $15,392 tenían el vale con que el Departamento de Servicios Generales autoriza cada entrega, así que $158,400 no se pudieron comprobar. En esa factura venía un paciente que murió el 9 de mayo de 2024, siete meses antes. Además, el gasto de 2024 se cargó al presupuesto de 2025 y se respaldó con un contrato que empezó a valer el 1 de enero de 2025 (observación 2025AE005FN0072, pp. 26 a 30 del informe).",
   "Sí es la segunda vez. En la auditoría del mismo semestre de 2024 (informe 2024AE0109010012), el ISAF ya había encontrado $358,643 de oxígeno de enero a abril de 2024 sin vale y tres pacientes cobrados después de morir. El proveedor ofreció entonces una nota de crédito, y el ISSSTESON prometió revisar cada mes la lista de defunciones. El ISAF la llama falla «recurrente».",
   "Las pensiones. El ISAF cruzó la nómina con la plataforma del Registro Civil de Sonora y encontró 138 pagos, de enero a junio de 2025, a 129 pensiones de personas que ya habían muerto: $2,990,499 (observación 2025AE005FN0145, pp. 67 a 74). La mayoría fueron del mes siguiente a la muerte (126 de los 138 pagos), cuando la baja todavía no llegaba a la nómina. Pero no todos: una pensión se siguió pagando seis meses de 2025 a una persona que murió en abril de 2020.",
   "¿Dónde está el dinero? El propio informe lo cuenta. 114 de esos pagos eran cheques que nunca se cobraron y se cancelaron: $2,458,447. El banco revirtió 4 depósitos ($79,086) y 4 más se descontaron de los gastos de funeral o del pago póstumo a la familia ($79,533). Faltan $373,438, de 18 pagos, que el ISSSTESON debe devolver a su cuenta. Ni esto ni lo del oxígeno se ha solventado: si no se aclara, el ISAF lo turna a la autoridad que determina responsabilidades. Una observación no es una condena (Constitución, art. 20, apartado B, fr. I).",
   "Una nota de método: lo que circula es el audio de un reel de Instagram, y lo que se cotejó es su transcripción; sin liga, no citamos a la cuenta que lo publicó. Un reel nunca es fuente: lo que vale es el informe. Los dos informes del ISAF se leyeron completos. Las cuentas «126 de 138» y la de la pensión de 2020 son nuestras, de la tabla del informe: van como derivadas. Los números de pensión y de afiliación no se publican."
  ],
  "dato_curioso": "Una pensión del ISSSTESON se pagó seis veces en 2025 (de enero a junio, $83,435 en total) a una persona que, según el Registro Civil, murió el 22 de abril de 2020.",
  "cifras": [
   {
    "valor": "$2,990,499",
    "etq": "Pensiones y jubilaciones pagadas de enero a junio de 2025 después de la fecha de defunción (138 pagos)",
    "estado": "oficial",
    "fuente": "ISAF, informe 2025AE0109010005, observación 2025AE005FN0145",
    "url": "https://sigas.isaf.gob.mx/api/File/Informe/24290"
   },
   {
    "valor": "$373,438",
    "etq": "Lo que el ISSSTESON aún debe devolver de esos pagos (18 pagos); el resto eran cheques cancelados ($2,458,447) o ya se recuperó ($158,619)",
    "estado": "oficial",
    "fuente": "ISAF, informe 2025AE0109010005, pp. 70 a 74",
    "url": "https://sigas.isaf.gob.mx/api/File/Informe/24290"
   },
   {
    "valor": "$158,400",
    "etq": "Oxígeno a domicilio de diciembre de 2024 pagado sin vale que compruebe la entrega (de $173,792 facturados)",
    "estado": "oficial",
    "fuente": "ISAF, informe 2025AE0109010005, observación 2025AE005FN0072",
    "url": "https://sigas.isaf.gob.mx/api/File/Informe/24290"
   },
   {
    "valor": "126 de 138",
    "etq": "Pagos de pensión que fueron del mes siguiente a la muerte. Operación: mes del pago menos mes de la defunción, renglón por renglón de la tabla del ISAF",
    "estado": "derivado",
    "fuente": "Cálculo con la tabla de la observación 2025AE005FN0145",
    "url": "https://sigas.isaf.gob.mx/api/File/Informe/24290"
   }
  ],
  "cotejo": [
   {
    "dice": "Por segundo año consecutivo, en la compra de oxígeno a domicilio no pudieron acreditar la entrega a pacientes por más de 150,000 pesos.",
    "res": "consta",
    "explica": "$158,400 sin vale de autorización en la factura de diciembre de 2024 (pagada en marzo de 2025). El ISAF lo marca como recurrente: en 2024 fueron $358,643 de enero a abril.",
    "fuente": "ISAF, informes 2025AE0109010005 (pp. 26 a 30) y 2024AE0109010012 (pp. 33 a 40)",
    "url": "https://sigas.isaf.gob.mx/api/File/Informe/24290"
   },
   {
    "dice": "Volvieron a pagar el oxígeno de un paciente que ya había fallecido el 9 de mayo de 2024.",
    "res": "consta",
    "explica": "El ISAF lo dice así: se pagó el oxígeno de diciembre de 2024 a un paciente que murió el 9 de mayo de 2024. «Volvieron» también consta: en 2024 fueron tres pacientes.",
    "fuente": "ISAF, informe 2025AE0109010005, observación 2025AE005FN0072, inciso b",
    "url": "https://sigas.isaf.gob.mx/api/File/Informe/24290"
   },
   {
    "dice": "Pagaron 2,990,499 pesos en pensiones y jubilaciones a personas que ya estaban muertas según las actas del Registro Civil.",
    "res": "matiz",
    "explica": "La cifra consta, cotejada contra la plataforma del Registro Civil de Sonora. El matiz: $2,458,447 eran cheques que nunca se cobraron y se cancelaron, y $158,619 ya se recuperaron. Lo que salió y no ha vuelto son $373,438. Y 126 de los 138 pagos fueron del mes siguiente a la muerte: falla de control, no necesariamente un desvío.",
    "fuente": "ISAF, informe 2025AE0109010005, observación 2025AE005FN0145, pp. 67 a 74",
    "url": "https://sigas.isaf.gob.mx/api/File/Informe/24290"
   },
   {
    "dice": "¿Dónde está todo este dinero?",
    "res": "matiz",
    "explica": "El informe responde casi todo: $2,458,447 no salieron (cheques cancelados), $79,086 los devolvió el banco y $79,533 se descontaron de gastos de funeral y pagos póstumos. Lo que falta: $373,438 de pensiones y los $158,400 del oxígeno, que el ISAF pide devolver con intereses si no se comprueban.",
    "fuente": "ISAF, informe 2025AE0109010005",
    "url": "https://sigas.isaf.gob.mx/api/File/Informe/24290"
   },
   {
    "dice": "Ya se devolvieron los $373,438 de pensiones y los $158,400 del oxígeno.",
    "res": "pendiente",
    "explica": "Al cierre del informe (marzo de 2026) las dos observaciones seguían sin solventar. No hemos encontrado el seguimiento publicado.",
    "fuente": "ISAF, informes de Cuenta Pública",
    "url": "https://isaf.gob.mx/informes/cuenta-publica",
    "quien": "Le toca al ISSSTESON acreditar ante el ISAF el reintegro y la cancelación del gasto (Ley de Fiscalización Superior para el Estado de Sonora, art. 50). Falta de la plataforma: no hemos encontrado publicado el seguimiento posterior al informe de marzo de 2026",
    "donde": "https://isaf.gob.mx/informes/cuenta-publica"
   },
   {
    "dice": "Morena nos lleva a la justicia social hasta la tumba.",
    "res": "matiz",
    "explica": "Es una opinión política, no una cifra: no se coteja. El informe no habla de partidos: observa a una institución, el ISSSTESON, y si hay responsables los determina la autoridad, persona por persona.",
    "fuente": "ISAF, informe 2025AE0109010005",
    "url": "https://sigas.isaf.gob.mx/api/File/Informe/24290"
   }
  ],
  "sigue": [
   {
    "que": "El seguimiento del ISAF: si el ISSSTESON devolvió los $373,438 de pensiones y los $158,400 del oxígeno, o si se turnó a la autoridad",
    "url": "https://isaf.gob.mx/informes/cuenta-publica"
   },
   {
    "que": "La auditoría del ISAF a la Cuenta Pública 2025 completa del ISSSTESON (el segundo semestre)",
    "url": "https://isaf.gob.mx/informes/cuenta-publica"
   },
   {
    "que": "Si se aplicó la nota de crédito que ofreció el proveedor en 2025 por los pacientes fallecidos de 2024",
    "url": "https://sigas.isaf.gob.mx/api/File/Informe/22455"
   },
   {
    "que": "Los contratos federales de Biosistemas y Seguridad Privada en ComprasMX (31 en 2025, sobre todo con el IMSS y el IMSS-Bienestar)",
    "url": "contratos-publicos.html"
   }
  ],
  "fuentes": [
   {
    "nombre": "ISAF, Informe individual de la auditoría integral 2025AE0109010005 al ISSSTESON, segundo trimestre de 2025 (notificado en marzo de 2026)",
    "url": "https://sigas.isaf.gob.mx/api/File/Informe/24290"
   },
   {
    "nombre": "ISAF, Informe individual de la auditoría integral 2024AE0109010012 al ISSSTESON, segundo trimestre de 2024 (notificado en marzo de 2025)",
    "url": "https://sigas.isaf.gob.mx/api/File/Informe/22455"
   },
   {
    "nombre": "ISAF, informes de Cuenta Pública",
    "url": "https://isaf.gob.mx/informes/cuenta-publica"
   }
  ],
  "actualizado": "28 de octubre de 2026"
 },
 {
  "id": "ine-oic-auditorias-consejerias",
  "seccion": "Verificado",
  "icono": "🔎",
  "titulo": "¿Auditarán también las oficinas de los consejeros del INE? Lo que permite la ley y lo que se denunció en conferencia",
  "balazo": "Sí: la ley del INE dice que los consejeros son servidores públicos del Instituto y que ninguna área puede negarse a una revisión de su Órgano Interno de Control. Pero ese Órgano depende, en lo administrativo, de la presidencia que tendría que revisar, y lo que se dijo de sueldos, plazas y cuentas bancarias todavía no tiene un solo documento.",
  "circula": {
   "red": "Conferencia de prensa de las consejerías del INE",
   "cuenta": "Pregunta de una persona reportera (versión estenográfica de Central Electoral)",
   "fecha": "27 de octubre de 2026",
   "texto": "Y me voy a permitir dar un mensaje a la estructura, porque se tienen que quitar el miedo, el miedo a denunciar y el miedo a decir las cosas como tienen que ser. Por años escuchamos a trabajadores que nos decían lo que estaba pasando y hasta ahora, gracias a Dios, con bien documentado, un periódico logró tener las pruebas para decir lo que estaba pasando en este instituto. Así que yo les digo a los trabajadores que nos pueden estar escuchando que por favor se armen de valor y que si no tienen confianza en las instituciones o en la gente a la que tienen que denunciar aquí en el INE, que se acerquen con nosotros los reporteros, porque vamos a seguir haciendo nuestro trabajo y vamos a seguir denunciando lo que está mal dentro del instituto. Y pregunta concreta para ustedes, consejeros, dicen que se necesitan hacer más auditorías, que el órgano interno de control tiene que deslindar responsabilidades y todo eso. ¿Eso incluye someter a sus oficinas a estas auditorías? Porque sabemos de trabajadores que nos han dicho que les descuentan de su sueldo para quedarse con el dinero, porque nos han dado también ya las cuentas bancarias del órgano interno de control en donde también les rentan las plazas. Y donde hay vocales ejecutivos, vocales distritales y locales, también candidatos a los que han recibido amenazas o que les piden dinero para poder tener audiencias o para poder estar en una lista de candidatos. ¿Hasta ahí le van a entrar? ¿Hasta ahí van a meter a sus oficinas también a las auditorías? Porque si ya se destapó la cloaca, creo que tiene que salir toda la cochinada, porque queremos un INE fuerte y confiable, como hasta hace unos años confiábamos muchos mexicanos en este instituto."
  },
  "cuerpo": [
   "Tras la renuncia anunciada de Guadalupe Taddei, las consejerías del INE dieron una conferencia de prensa. Ahí se preguntó si las auditorías que ellas mismas piden alcanzarán a sus propias oficinas, y se denunciaron descuentos de sueldo, renta de plazas, amenazas y cobros a quienes buscan una audiencia o un lugar en una lista. La pregunta consta en la versión estenográfica que publicó el INE; su texto se tomó del buscador, porque el sitio del INE no abre desde la plataforma.",
   "¿Pueden auditarse las oficinas de los consejeros? La ley dice que sí. El artículo 478 de la LGIPE cuenta como servidores públicos del Instituto al consejero presidente, a los consejeros del Consejo General, de los consejos locales y distritales, a los vocales ejecutivos y a toda persona con empleo o cargo en el INE. El Órgano Interno de Control fiscaliza los ingresos y egresos del Instituto (art. 487), revisa los recursos «a cargo de las áreas y órganos del Instituto», puede visitar sus sedes y recibe denuncias contra cualquiera de sus servidores públicos (art. 490, incisos a, e, l y m). Y todos los órganos están obligados a permitirle la revisión (art. 492). Lo único que no puede tocar son las decisiones electorales (art. 478, numeral 2).",
   "Lo que pocas veces se dice: la Constitución adscribe ese Órgano, en lo administrativo, a la presidencia del Consejo General (art. 41, base V, apartado A), la misma oficina que tendría que revisar, y su estructura, personal y recursos los aprueba el Consejo General a propuesta de su titular (LGIPE, art. 487, numeral 5). Su contrapeso es externo: el titular lo designa la Cámara de Diputados con dos terceras partes de los votos y se coordina con la Auditoría Superior de la Federación. El actual, Víctor Hugo Carvente Contreras, fue designado el 10 de diciembre de 2024 (decreto del DOF del 13 de diciembre de 2024) por seis años.",
   "Lo que se denunció (descuentos de sueldo, plazas rentadas, cuentas bancarias del Órgano, cobros a aspirantes) no tiene todavía ningún documento oficial: es la palabra de quien pregunta, que dice tener testimonios y estados de cuenta. Una acusación no es una condena (Constitución, art. 20, apartado B, fr. I). Si alguien quiere denunciar, la ley le da dos caminos: el propio Órgano Interno de Control (art. 490, inciso l) y, si hay delito, la Fiscalía Especializada en Combate a la Corrupción (art. 487).",
   "Una nota de método: las páginas del INE y las notas de prensa no abrieron desde la plataforma. La pregunta se tomó tal como la muestra el buscador sobre la versión estenográfica; las leyes, el decreto y la encuesta del INEGI se consultaron completos."
  ],
  "dato_curioso": "La confianza en los institutos electorales bajó de 54.7 % en 2023 a 48.1 % en 2025, según la encuesta de calidad gubernamental del INEGI: en 2025, menos de la mitad dijo confiar en ellos.",
  "cifras": [
   {
    "valor": "48.1 %",
    "etq": "Personas que confían en los institutos electorales (INE y los de los estados) en 2025; 54.7 % en 2023 y 53.1 % en 2021",
    "estado": "oficial",
    "fuente": "INEGI, ENCIG 2025 (p. 50) y ENCIG 2023 (p. 212), principales resultados",
    "url": "https://www.inegi.org.mx/contenidos/programas/encig/2025/doc/encig2025_principales_resultados.pdf"
   },
   {
    "valor": "59.9 %",
    "etq": "Personas que creen que en los institutos electorales la corrupción es muy frecuente o frecuente (2025)",
    "estado": "oficial",
    "fuente": "INEGI, ENCIG 2025, principales resultados, p. 50",
    "url": "https://www.inegi.org.mx/contenidos/programas/encig/2025/doc/encig2025_principales_resultados.pdf"
   },
   {
    "valor": "10/12/2024",
    "etq": "Día en que la Cámara de Diputados designó al titular del Órgano Interno de Control del INE, por seis años",
    "estado": "oficial",
    "fuente": "Decreto de la Cámara de Diputados, DOF 13-12-2024",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/marjur/marco/Dip_decreto_OIC_INE_13dic24.pdf"
   },
   {
    "valor": "$28,288.0 millones",
    "etq": "Gasto ejercido del INE en 2025, el dinero que su Órgano Interno de Control debe fiscalizar",
    "estado": "oficial",
    "fuente": "SHCP, Cuenta Pública 2025, datos abiertos",
    "url": "https://www.transparenciapresupuestaria.gob.mx/work/models/PTP/DatosAbiertos/BD_Cuenta_Publica/CSV/cuenta_publica_2025_gf_ecd_epe.csv"
   }
  ],
  "cotejo": [
   {
    "dice": "Un periódico logró tener las pruebas para decir lo que estaba pasando en este instituto.",
    "res": "matiz",
    "explica": "Hubo reportajes de prensa, y el INE publicó el 24 de octubre de 2026 que la Auditoría Superior abrió una investigación de oficio. Pero lo que publica un medio es punto de partida: ninguna autoridad ha resuelto todavía que haya falta o delito. Lo que consta y lo que no está en la columna sobre la renuncia de Guadalupe Taddei.",
    "fuente": "INE, Central Electoral, 24-10-2026",
    "url": "https://centralelectoral.ine.mx/2026/10/24/la-presidencia-del-ine-respalda-la-investigacion-de-la-asf-y-reafirma-su-compromiso-con-el-estado-de-derecho/"
   },
   {
    "dice": "Los consejeros dicen que se necesitan más auditorías y que el Órgano Interno de Control tiene que deslindar responsabilidades.",
    "res": "consta",
    "explica": "El 27 de octubre de 2026 las consejerías anunciaron una transición «basada en la colegialidad, la transparencia y la continuidad» y, según el texto que muestra el buscador, acordaron impulsar a través del Órgano Interno de Control la cooperación con las investigaciones.",
    "fuente": "INE, Central Electoral, 27-10-2026",
    "url": "https://centralelectoral.ine.mx/2026/10/27/inician-consejerias-electorales-una-transicion-institucional-basada-en-la-colegialidad-la-transparencia-y-la-continuidad-del-ine/"
   },
   {
    "dice": "¿Eso incluye someter a sus oficinas a estas auditorías?",
    "res": "consta",
    "explica": "La ley lo permite: los consejeros son servidores públicos del Instituto (LGIPE, art. 478), el Órgano revisa los recursos de todas las áreas y órganos y puede visitar sus sedes (art. 490), y ningún órgano puede negarse (art. 492). No puede revisar decisiones electorales (art. 478, numeral 2). Por juicio político responden ante el Congreso (Constitución, art. 110).",
    "fuente": "LGIPE, texto vigente (última reforma DOF 02-06-2026), arts. 478, 487, 490 y 492",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/LGIPE.pdf"
   },
   {
    "dice": "Respuesta de las consejeras y los consejeros a esta pregunta",
    "res": "pendiente",
    "explica": "Según la prensa, negaron conocer actos irregulares y dijeron estar dispuestos a colaborar. La versión estenográfica la tiene, pero no la pudimos leer completa: hasta cotejarla, no se cita.",
    "fuente": "INE, versión estenográfica del 27-10-2026",
    "url": "https://centralelectoral.ine.mx/2026/10/27/version-estenografica-de-la-conferencia-de-prensa-que-ofrecieron-consejeras-y-consejeros-electorales-a-diversos-medios-de-comunicacion-27-de-octubre-de-2026/",
    "quien": "Falta de la plataforma: el INE publicó la versión estenográfica en Central Electoral, pero su sitio no abre desde la plataforma; hay que leer la respuesta completa y cotejarla",
    "donde": "https://centralelectoral.ine.mx/2026/10/27/version-estenografica-de-la-conferencia-de-prensa-que-ofrecieron-consejeras-y-consejeros-electorales-a-diversos-medios-de-comunicacion-27-de-octubre-de-2026/"
   },
   {
    "dice": "A trabajadores les descuentan de su sueldo para quedarse con el dinero.",
    "res": "no consta",
    "explica": "No hay documento oficial: es lo que, según quien pregunta, le dijeron trabajadores. Una acusación no es una condena. Si ocurre, lo investiga el Órgano Interno de Control (LGIPE, art. 490, inciso l) y, si es delito, la Fiscalía Especializada en Combate a la Corrupción (art. 487).",
    "fuente": "Sin documento oficial",
    "url": ""
   },
   {
    "dice": "Nos han dado las cuentas bancarias del Órgano Interno de Control en donde también les rentan las plazas.",
    "res": "no consta",
    "explica": "Las cuentas no se han publicado ni las ha revisado ninguna autoridad que lo haya informado. El Órgano Interno de Control es justo el señalado, así que su investigación no bastaría: su titular responde por la Ley General de Responsabilidades Administrativas (LGIPE, art. 489) y lo designó la Cámara de Diputados.",
    "fuente": "Sin documento oficial",
    "url": ""
   },
   {
    "dice": "Vocales ejecutivos, distritales y locales; candidatos amenazados o a los que les piden dinero para tener audiencias o para estar en una lista.",
    "res": "no consta",
    "explica": "Sin documento oficial. Según la prensa, se refería a aspirantes a consejerías de los institutos electorales de los estados, que designa el Consejo General del INE (Constitución, art. 116, fr. IV, inciso c, 2o.): de ahí las listas.",
    "fuente": "Sin documento oficial",
    "url": ""
   },
   {
    "dice": "Queremos un INE fuerte y confiable, como hasta hace unos años confiábamos muchos mexicanos en este instituto.",
    "res": "matiz",
    "explica": "La confianza sí bajó: 53.1 % en 2021, 54.7 % en 2023 y 48.1 % en 2025, según el INEGI. El matiz: la encuesta mide «institutos electorales», el INE junto con los de los estados, no el INE solo.",
    "fuente": "INEGI, ENCIG 2025, principales resultados, p. 50",
    "url": "https://www.inegi.org.mx/contenidos/programas/encig/2025/doc/encig2025_principales_resultados.pdf"
   }
  ],
  "sigue": [
   {
    "que": "La respuesta completa de las consejerías en la versión estenográfica del 27 de octubre de 2026",
    "url": "https://centralelectoral.ine.mx/2026/10/27/version-estenografica-de-la-conferencia-de-prensa-que-ofrecieron-consejeras-y-consejeros-electorales-a-diversos-medios-de-comunicacion-27-de-octubre-de-2026/"
   },
   {
    "que": "Los informes semestral y anual del Órgano Interno de Control al Consejo General (LGIPE, art. 489), con lo que investigó y sancionó",
    "url": "https://www.ine.mx/"
   },
   {
    "que": "Cuánto presupuesto y cuánto personal tiene el Órgano Interno de Control del INE en 2026 (lo aprueba el Consejo General, art. 487)",
    "url": "https://www.ine.mx/"
   },
   {
    "que": "Los resultados de la Auditoría Superior sobre las contrataciones del INE",
    "url": "https://www.asf.gob.mx/"
   },
   {
    "que": "El caso que lo originó: la renuncia de Guadalupe Taddei y lo que consta de Cajas Graf",
    "url": "noticias-auditavision.html#col-taddei-renuncia-ine-contratos"
   }
  ],
  "fuentes": [
   {
    "nombre": "INE, Central Electoral: versión estenográfica de la conferencia de prensa de las consejerías (27-10-2026)",
    "url": "https://centralelectoral.ine.mx/2026/10/27/version-estenografica-de-la-conferencia-de-prensa-que-ofrecieron-consejeras-y-consejeros-electorales-a-diversos-medios-de-comunicacion-27-de-octubre-de-2026/"
   },
   {
    "nombre": "INE, Central Electoral: Inician consejerías electorales una transición institucional (27-10-2026)",
    "url": "https://centralelectoral.ine.mx/2026/10/27/inician-consejerias-electorales-una-transicion-institucional-basada-en-la-colegialidad-la-transparencia-y-la-continuidad-del-ine/"
   },
   {
    "nombre": "Ley General de Instituciones y Procedimientos Electorales, texto vigente (última reforma DOF 02-06-2026), arts. 478 a 493",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/LGIPE.pdf"
   },
   {
    "nombre": "Constitución Política, texto vigente (última reforma DOF 07-10-2026), arts. 20, 41, 110 y 116",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf"
   },
   {
    "nombre": "Decreto por el que la Cámara de Diputados designa al titular del Órgano Interno de Control del INE (DOF 13-12-2024)",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/marjur/marco/Dip_decreto_OIC_INE_13dic24.pdf"
   },
   {
    "nombre": "INEGI, Encuesta Nacional de Calidad e Impacto Gubernamental 2025, principales resultados",
    "url": "https://www.inegi.org.mx/contenidos/programas/encig/2025/doc/encig2025_principales_resultados.pdf"
   },
   {
    "nombre": "INEGI, Encuesta Nacional de Calidad e Impacto Gubernamental 2023, principales resultados",
    "url": "https://www.inegi.org.mx/contenidos/programas/encig/2023/doc/encig2023_principales_resultados.pdf"
   }
  ],
  "actualizado": "28 de octubre de 2026"
 },
 {
  "id": "ine-contratos-desde-cordova",
  "seccion": "Verificado",
  "icono": "🗳️",
  "titulo": "¿Investigarán a Lorenzo Córdova? Lo que pidió la Presidenta sobre los contratos del INE y lo que dijo de la UIF",
  "balazo": "La Presidenta pidió que la Auditoría Superior revise los contratos del INE, según la prensa también los de antes de Guadalupe Taddei. Pedir que se revise un periodo no es acusar a nadie: ninguna autoridad ha señalado a Lorenzo Córdova. Del congelamiento de cuentas de la UIF y su amparo solo consta lo que ella dijo.",
  "circula": {
   "red": "Redes sociales",
   "cuenta": "politicomx",
   "fecha": "27 de octubre de 2026",
   "texto": "¿Investigarán a Lorenzo Córdova? La presidenta Claudia Sheinbaum pidió a la ASF revisar todos los contratos del INE, no solamente los correspondientes a la administración de Guadalupe Taddei, sino también los de periodos anteriores, incluido el de Lorenzo Córdova. Sheinbaum señaló que es necesario conocer desde cuándo operan las empresas contratistas del INE y recordó que la UIF, encabezada entonces por Pablo Gómez, congeló cuentas de algunas de estas compañías, medida que posteriormente fue levantada mediante un amparo."
  },
  "cuerpo": [
   "En su conferencia del 26 de octubre de 2026, cuando le preguntaron por la renuncia de Guadalupe Taddei, la Presidenta pidió una auditoría: «que la Auditoría Superior de la Federación haga su auditoría y señale si es que, en efecto, ella está involucrada o no». Consta en la versión estenográfica que publicó la Presidencia. Ese día habló de la gestión de Taddei; no mencionó a Lorenzo Córdova.",
   "En la misma conferencia le preguntaron por la UIF. Dijo que en 2023 la UIF congeló las cuentas de «este proveedor que ha estado saliendo»: «Cuando estaba Pablo Gómez al frente de la UIF hay un congelamiento de cuentas de uno de los proveedores». Agregó que después un amparo obligó a liberarlas y que otras líneas de investigación «tendrá que informarlo la UIF, en su momento». No dijo el nombre de la empresa ni el mes. Habló de un proveedor, no de «algunas de estas compañías».",
   "Lo de Córdova es del día siguiente. Según Informador, El Imparcial y El Financiero, el 27 de octubre pidió que la revisión no se quede en la gestión de Taddei, que alcance periodos anteriores, incluido el de Lorenzo Córdova Vianello, y que se informe desde cuándo tiene el INE contratos con esos contratistas. Cuando lo consultamos, la Presidencia todavía no publicaba la versión estenográfica de ese día. En cuanto salga, se coteja palabra por palabra.",
   "Un dato que la publicación no dice: Córdova presidió el INE del 3 de abril de 2014 al 3 de abril de 2023, y Taddei entró ese mismo mes. El congelamiento fue «en 2023», según la Presidenta, así que pudo haber sido con cualquiera de los dos. Sin el mes, no se sabe. Pedir que se revisen los contratos de un periodo no es una acusación contra quien lo presidió: ninguna autoridad ha abierto un procedimiento contra Lorenzo Córdova, y toda persona se presume inocente mientras no se declare su responsabilidad (Constitución, art. 20, apartado B, fr. I).",
   "Una nota de método: las notas de prensa no abrieron desde la plataforma; se citan por su medio y su liga, como punto de partida y no como fuente. La versión estenográfica del 26 de octubre se consultó en gob.mx."
  ],
  "dato_curioso": "El congelamiento que mencionó la Presidenta fue en 2023, el año en que el INE cambió de presidencia: Lorenzo Córdova salió el 3 de abril y Guadalupe Taddei entró ese mismo mes. Sin el mes, no se puede saber con cuál de los dos ocurrió.",
  "cifras": [
   {
    "valor": "3/04/2014 – 3/04/2023",
    "etq": "Periodo de Lorenzo Córdova como consejero presidente del INE",
    "estado": "oficial",
    "fuente": "INE, Central Electoral, 31-03-2023",
    "url": "https://centralelectoral.ine.mx/2023/03/31/lorenzo-cordova-adriana-favela-ciro-murayama-y-jose-roberto-ruiz-se-despiden-de-la-herradura-de-la-democracia/"
   },
   {
    "valor": "2023",
    "etq": "Año en que, según la Presidenta, la UIF congeló las cuentas de un proveedor del INE",
    "estado": "oficial",
    "fuente": "Presidencia, versión estenográfica del 26-10-2026",
    "url": "https://www.gob.mx/presidencia/articulos/version-estenografica-conferencia-de-prensa-de-la-presidenta-claudia-sheinbaum-pardo-del-26-de-octubre-de-2026"
   }
  ],
  "cotejo": [
   {
    "dice": "La presidenta Claudia Sheinbaum pidió a la ASF revisar los contratos del INE.",
    "res": "consta",
    "explica": "El 26 de octubre de 2026 pidió «que la Auditoría Superior de la Federación haga su auditoría». La ASF ya había abierto una investigación de oficio, según el INE (24-10-2026).",
    "fuente": "Presidencia, versión estenográfica del 26-10-2026",
    "url": "https://www.gob.mx/presidencia/articulos/version-estenografica-conferencia-de-prensa-de-la-presidenta-claudia-sheinbaum-pardo-del-26-de-octubre-de-2026"
   },
   {
    "dice": "No solamente los contratos de la administración de Guadalupe Taddei, sino también los de periodos anteriores, incluido el de Lorenzo Córdova.",
    "res": "pendiente",
    "explica": "Lo publican Informador, El Imparcial y El Financiero sobre la conferencia del 27 de octubre de 2026. La versión estenográfica de ese día aún no estaba publicada cuando la consultamos: hasta cotejarla, solo lo dice la prensa.",
    "fuente": "Solo en prensa (Informador, 27-10-2026)",
    "url": "https://www.informador.mx/mexico/claudia-sheinbaum-exige-una-auditoria-muy-amplia-al-ine-pide-revisar-gestiones-de-guadalupe-taddei-y-lorenzo-cordova-20261027-0066.html",
    "quien": "Presidencia de la República: la versión estenográfica de la conferencia del 27 de octubre de 2026 todavía no estaba publicada cuando la consultamos; suele salir después de la conferencia",
    "donde": "https://www.gob.mx/presidencia/es/archivo/articulos"
   },
   {
    "dice": "¿Investigarán a Lorenzo Córdova?",
    "res": "no consta",
    "explica": "Ninguna autoridad ha abierto un procedimiento contra él. Revisar los contratos de su periodo es revisar al INE, no acusarlo: una revisión no es una acusación y una acusación no es una condena (Constitución, art. 20, B, fr. I).",
    "fuente": "Sin documento oficial",
    "url": ""
   },
   {
    "dice": "Sheinbaum señaló que es necesario conocer desde cuándo operan las empresas contratistas del INE.",
    "res": "pendiente",
    "explica": "También es de la conferencia del 27 de octubre y solo lo dice la prensa por ahora. Lo que sí se puede revisar ya son los contratos del INE en la Plataforma Nacional de Transparencia.",
    "fuente": "Solo en prensa (El Imparcial, 27-10-2026)",
    "url": "https://www.elimparcial.com/mexico/2026/10/27/claudia-sheinbaum-pide-investigar-los-contratos-del-ine-durante-la-gestion-de-lorenzo-cordova-tras-la-renuncia-de-guadalupe-taddei-por-presuntas-irregularidades-y-exige-revisar-a-los-proveedores-de-administraciones-anteriores/",
    "quien": "Presidencia de la República: la versión estenográfica de la conferencia del 27 de octubre de 2026 todavía no estaba publicada cuando la consultamos; suele salir después de la conferencia",
    "donde": "https://www.gob.mx/presidencia/es/archivo/articulos"
   },
   {
    "dice": "La UIF, encabezada entonces por Pablo Gómez, congeló cuentas de algunas de estas compañías.",
    "res": "matiz",
    "explica": "La Presidenta lo dijo el 26 de octubre, pero de un solo proveedor y en 2023: «hay un congelamiento de cuentas de uno de los proveedores». No dijo cuál, y la UIF no lo ha publicado.",
    "fuente": "Presidencia, versión estenográfica del 26-10-2026",
    "url": "https://www.gob.mx/presidencia/articulos/version-estenografica-conferencia-de-prensa-de-la-presidenta-claudia-sheinbaum-pardo-del-26-de-octubre-de-2026"
   },
   {
    "dice": "La medida fue levantada posteriormente mediante un amparo.",
    "res": "pendiente",
    "explica": "Consta que la Presidenta lo dijo («el amparo hace que se las tengan que liberar»), pero no hay documento del congelamiento ni del amparo: ni qué empresa, ni qué juzgado, ni cuándo. Ella misma dijo que lo demás «tendrá que informarlo la UIF, en su momento».",
    "fuente": "Presidencia, versión estenográfica del 26-10-2026",
    "url": "https://www.gob.mx/presidencia/articulos/version-estenografica-conferencia-de-prensa-de-la-presidenta-claudia-sheinbaum-pardo-del-26-de-octubre-de-2026",
    "quien": "La UIF (Hacienda) tiene el expediente del congelamiento y un juzgado federal resolvió el amparo. La UIF guarda reserva de sus investigaciones por ley, así que no se le culpa de no publicarlo; la Presidenta anunció que informará en su momento",
    "donde": "https://www.gob.mx/uif/prensa"
   }
  ],
  "sigue": [
   {
    "que": "La versión estenográfica de la conferencia del 27 de octubre de 2026, para cotejar palabra por palabra lo de Córdova y «desde cuándo»",
    "url": "https://www.gob.mx/presidencia/es/archivo/articulos"
   },
   {
    "que": "Lo que informe la UIF sobre el proveedor cuyas cuentas congeló en 2023 y el amparo que las liberó",
    "url": "https://www.gob.mx/uif/prensa"
   },
   {
    "que": "Los resultados de la Auditoría Superior sobre las contrataciones del INE, y si alcanzan años anteriores a 2023",
    "url": "https://www.asf.gob.mx/"
   },
   {
    "que": "El caso que lo originó: la renuncia de Guadalupe Taddei y lo que consta de Cajas Graf",
    "url": "noticias-auditavision.html#col-taddei-renuncia-ine-contratos"
   }
  ],
  "fuentes": [
   {
    "nombre": "Presidencia de la República: versión estenográfica de la conferencia de prensa del 26 de octubre de 2026",
    "url": "https://www.gob.mx/presidencia/articulos/version-estenografica-conferencia-de-prensa-de-la-presidenta-claudia-sheinbaum-pardo-del-26-de-octubre-de-2026"
   },
   {
    "nombre": "INE, Central Electoral: Lorenzo Córdova, Adriana Favela, Ciro Murayama y José Roberto Ruiz se despiden de la herradura de la democracia (31-03-2023)",
    "url": "https://centralelectoral.ine.mx/2023/03/31/lorenzo-cordova-adriana-favela-ciro-murayama-y-jose-roberto-ruiz-se-despiden-de-la-herradura-de-la-democracia/"
   },
   {
    "nombre": "INE, Central Electoral: La Presidencia del INE respalda la investigación de la ASF (24-10-2026)",
    "url": "https://centralelectoral.ine.mx/2026/10/24/la-presidencia-del-ine-respalda-la-investigacion-de-la-asf-y-reafirma-su-compromiso-con-el-estado-de-derecho/"
   },
   {
    "nombre": "Punto de partida, no fuente: Informador (27-10-2026)",
    "url": "https://www.informador.mx/mexico/claudia-sheinbaum-exige-una-auditoria-muy-amplia-al-ine-pide-revisar-gestiones-de-guadalupe-taddei-y-lorenzo-cordova-20261027-0066.html"
   },
   {
    "nombre": "Punto de partida, no fuente: El Imparcial (27-10-2026)",
    "url": "https://www.elimparcial.com/mexico/2026/10/27/claudia-sheinbaum-pide-investigar-los-contratos-del-ine-durante-la-gestion-de-lorenzo-cordova-tras-la-renuncia-de-guadalupe-taddei-por-presuntas-irregularidades-y-exige-revisar-a-los-proveedores-de-administraciones-anteriores/"
   },
   {
    "nombre": "Punto de partida, no fuente: El Financiero (27-10-2026)",
    "url": "https://www.elfinanciero.com.mx/nacional/2026/10/27/claudia-sheinbaum-mananera-temas-hoy-27-de-octubre-de-2026-en-vivo/"
   }
  ],
  "actualizado": "27 de octubre de 2026"
 },
 {
  "id": "guaymas-comodato-amigo-gnl",
  "seccion": "Verificado",
  "icono": "🚢",
  "titulo": "Guaymas, 54 hectáreas y el gas de Texas: lo que consta del proyecto AMIGO",
  "balazo": "Circula que el Gobierno de Sonora prestó gratis 54 hectáreas a una empresa para licuar gas y mandarlo a Asia. La Secretaría de Energía habla de 41.7 hectáreas, el contrato no está publicado y la obra está detenida por amparos.",
  "circula": {
   "red": "Redes sociales y tribuna del Congreso de Sonora",
   "cuenta": "Publicación en redes y discurso en tribuna (la transcripción no dice quién habla)",
   "fecha": "Octubre de 2026",
   "texto": "El Gobierno del Estado le entregó a una empresa privada un contrato de comodato (el uso 100 % gratuito) de 54 hectáreas de suelo público, terrenos costeros del Parque Industrial Pesquero «Rodolfo Sánchez Taboada», en Guaymas, para procesar gas que viene de Texas y mandarlo a Asia. Las ganancias se van fuera y a Sonora le dejan la basura. En tribuna se agregó: los buques desorientarán a las ballenas, un derrame dejaría sin trabajo a pescadores, se pidió información de más de 100 millones de pesos del Puente Colorado sin respuesta, y se borró la información de la megafarmacia. «Que la verdad sea incómoda no la vuelve falsa»."
  },
  "cuerpo": [
   "El proyecto se llama AMIGO (American Mexican Integrated Gas Operations): una planta para licuar gas natural en Guaymas. Así lo nombra el Congreso de Sonora en su Gaceta, y la Presidencia lo llama «Proyecto LNG Amigo».",
   "Del lado de Estados Unidos sí hay un documento oficial. La Orden 4629 del Departamento de Energía (DOE), del 8 de diciembre de 2020, expediente 20-31-LNG, autoriza a Epcilon LNG LLC, la empresa del proyecto, a exportar gas natural a México para licuarlo y a reexportarlo ya como gas natural licuado desde México, por 20 años, a países con y sin tratado de libre comercio con EE. UU.: hasta 395 mil millones de pies cúbicos al año. La orden le exige empezar a reexportar a más tardar el 8 de diciembre de 2027. La empresa pidió en diciembre de 2025 moverlo dos años, al 8 de diciembre de 2029; en julio de 2026 seguía mandando información para esa solicitud, y no encontramos que el DOE la haya resuelto.",
   "En la conferencia del 21 de octubre de 2026, la Secretaría de Energía lo ubicó en el Parque Industrial Pesquero «General Rodolfo Sánchez Taboada», un área ya ocupada por la industria, el cabotaje y la pesca, con 41.7 hectáreas, el 0.005 % del territorio del municipio. Habló de un máximo de 5 buques al mes (60 al año), el 4 % de las embarcaciones que ya cruzan la zona, y de almacenamiento para 290 mil metros cúbicos de gas. La Presidenta dijo que parte del gas vendría de Texas, que una porción se exportaría y otra se quedaría en el mercado interno, y que hay un amparo que impide avanzar mientras se revisan otra vez los impactos ambientales: «no vamos a cometer una irresponsabilidad».",
   "El 16 de octubre, la Presidenta había dicho que «no hay ningún daño ambiental», que se hizo el estudio de impacto ambiental, que el sitio no está en el ecosistema de la vaquita marina y que la obra «se paró» por los amparos.",
   "Lo que no consta en ningún documento oficial que pudimos abrir es el contrato de comodato. Lo reportó la prensa (N+ Focus), con fecha del 30 de septiembre de 2022 y la Comisión Estatal de Bienes y Concesiones como firmante; según esa misma prensa, el Gobierno del Estado, que encabeza Alfonso Durazo, lo ha negado o lo da por «sin efectos». Un contrato así es información que debe publicarse (Ley General de Transparencia, obligaciones sobre contratos, concesiones y permisos), y no lo encontramos publicado.",
   "El Congreso ya lo había tocado: el 12 de febrero de 2026, diputados del PAN y de MC presentaron un exhorto a la ASEA, al INECC, a la Semarnat, a Turismo, al IMIPAS y al INPI para revisar el impacto ambiental de los tres proyectos de gas del Golfo de California (Saguaro, AMIGO y Vista Pacífico). No se aprobó como urgente y se turnó a comisión. Las demás afirmaciones del discurso (Puente Colorado, megafarmacia) no tienen todavía un documento oficial que podamos citar."
  ],
  "dato_curioso": "La Secretaría de Energía comparó los 60 buques al año con el tráfico que ya existe: serían el 4 % de las embarcaciones de la zona. Cuántas ballenas cruzan esa ruta y en qué meses no lo dice la conferencia; está en el estudio de impacto ambiental, que es justo lo que se litiga.",
  "cifras": [
   {
    "valor": "41.7 ha",
    "etq": "Superficie del proyecto según la Secretaría de Energía (0.005 % del municipio de Guaymas)",
    "estado": "oficial",
    "fuente": "Presidencia, versión estenográfica del 21-10-2026 (Secretaría de Energía)",
    "url": "https://www.gob.mx/presidencia/es/articulos/version-estenografica-conferencia-de-prensa-de-la-presidenta-claudia-sheinbaum-pardo-del-21-de-octubre-de-2026"
   },
   {
    "valor": "60 buques al año",
    "etq": "Máximo de buques metaneros (5 al mes), el 4 % del tránsito actual de la zona",
    "estado": "oficial",
    "fuente": "Presidencia, versión estenográfica del 21-10-2026 (Secretaría de Energía)",
    "url": "https://www.gob.mx/presidencia/es/articulos/version-estenografica-conferencia-de-prensa-de-la-presidenta-claudia-sheinbaum-pardo-del-21-de-octubre-de-2026"
   },
   {
    "valor": "290 mil m³",
    "etq": "Capacidad de almacenamiento de gas que presentó la Secretaría de Energía",
    "estado": "oficial",
    "fuente": "Presidencia, versión estenográfica del 21-10-2026 (Secretaría de Energía)",
    "url": "https://www.gob.mx/presidencia/es/articulos/version-estenografica-conferencia-de-prensa-de-la-presidenta-claudia-sheinbaum-pardo-del-21-de-octubre-de-2026"
   },
   {
    "valor": "395 mil millones de pies³ al año",
    "etq": "Gas natural de EE. UU. que la Orden 4629 del DOE autoriza exportar a México para licuarlo y reexportarlo (20 años)",
    "estado": "oficial",
    "fuente": "Departamento de Energía de EE. UU., Orden DOE/FE 4629 (08-12-2020), expediente 20-31-LNG",
    "url": "https://www.energy.gov/sites/prod/files/2020/12/f81/ord4629.pdf"
   },
   {
    "valor": "12.3 ha",
    "etq": "Diferencia entre las 54 hectáreas que circulan y las 41.7 de la Secretaría de Energía (54 − 41.7)",
    "estado": "derivado",
    "fuente": "Presidencia, versión estenográfica del 21-10-2026 (Secretaría de Energía)",
    "url": "https://www.gob.mx/presidencia/es/articulos/version-estenografica-conferencia-de-prensa-de-la-presidenta-claudia-sheinbaum-pardo-del-21-de-octubre-de-2026"
   }
  ],
  "cotejo": [
   {
    "dice": "El Gobierno del Estado le entregó a una empresa privada un contrato de comodato, de uso gratuito.",
    "res": "pendiente",
    "explica": "El contrato no está en ningún documento oficial que pudimos abrir. Lo reporta la prensa (N+ Focus: firmado el 30-09-2022 por la Comisión Estatal de Bienes y Concesiones) y, según la prensa, el Gobierno de Sonora lo niega. Los contratos y concesiones sobre bienes públicos deben publicarse por ley de transparencia.",
    "fuente": "Plataforma Nacional de Transparencia",
    "url": "https://www.plataformadetransparencia.org.mx/",
    "quien": "Gobierno de Sonora (Comisión Estatal de Bienes y Concesiones): no ha transparentado el contrato ni su estado jurídico, que también le pidieron diputados del Congreso local",
    "donde": "https://www.plataformadetransparencia.org.mx/"
   },
   {
    "dice": "Son 54 hectáreas de suelo público.",
    "res": "matiz",
    "explica": "La Secretaría de Energía dio otra cifra: 41.7 hectáreas, 12.3 menos (derivado: 54 − 41.7). Las 54 hectáreas vienen de la prensa y, según la prensa, de los reportes de la empresa ante el Departamento de Energía de EE. UU., que no pudimos abrir.",
    "fuente": "Presidencia, versión estenográfica del 21-10-2026 (Secretaría de Energía)",
    "url": "https://www.gob.mx/presidencia/es/articulos/version-estenografica-conferencia-de-prensa-de-la-presidenta-claudia-sheinbaum-pardo-del-21-de-octubre-de-2026"
   },
   {
    "dice": "Son terrenos costeros del Parque Industrial Pesquero «Rodolfo Sánchez Taboada», en Guaymas.",
    "res": "consta",
    "explica": "La Secretaría de Energía lo ubicó ahí, en un área ya ocupada por la industria, el cabotaje y la pesca.",
    "fuente": "Presidencia, versión estenográfica del 21-10-2026 (Secretaría de Energía)",
    "url": "https://www.gob.mx/presidencia/es/articulos/version-estenografica-conferencia-de-prensa-de-la-presidenta-claudia-sheinbaum-pardo-del-21-de-octubre-de-2026"
   },
   {
    "dice": "El negocio es procesar gas que viene de Texas para mandarlo a Asia; el gas ni siquiera se queda aquí.",
    "res": "matiz",
    "explica": "La Presidenta dijo que parte del gas vendría de Texas, que una porción se exportaría y otra iría al mercado interno. En esa conferencia no se nombró a Asia como destino. La Orden 4629 del Departamento de Energía de EE. UU. sí confirma que el gas sale de Estados Unidos y que el permiso es para licuarlo en México y reexportarlo a países con y sin tratado de libre comercio con EE. UU.",
    "fuente": "Presidencia, versión estenográfica del 21-10-2026 (Secretaría de Energía)",
    "url": "https://www.gob.mx/presidencia/es/articulos/version-estenografica-conferencia-de-prensa-de-la-presidenta-claudia-sheinbaum-pardo-del-21-de-octubre-de-2026"
   },
   {
    "dice": "La Presidenta habló de soberanía energética y de si tenemos o no suficiente gas.",
    "res": "consta",
    "explica": "Lo justificó por el almacenamiento: dijo que México tiene alrededor de tres días de capacidad.",
    "fuente": "Presidencia, versión estenográfica del 21-10-2026 (Secretaría de Energía)",
    "url": "https://www.gob.mx/presidencia/es/articulos/version-estenografica-conferencia-de-prensa-de-la-presidenta-claudia-sheinbaum-pardo-del-21-de-octubre-de-2026"
   },
   {
    "dice": "Las ganancias se van fuera y a Sonora solo le dejan la basura y la contaminación.",
    "res": "no consta",
    "explica": "Es una valoración. Ningún documento oficial que pudimos abrir dice cuánto pagaría el proyecto en impuestos y derechos, ni cuánto dejaría en Sonora; la conferencia de la Secretaría de Energía no dio esas cifras.",
    "fuente": "Presidencia, versión estenográfica del 21-10-2026 (Secretaría de Energía)",
    "url": "https://www.gob.mx/presidencia/es/articulos/version-estenografica-conferencia-de-prensa-de-la-presidenta-claudia-sheinbaum-pardo-del-21-de-octubre-de-2026"
   },
   {
    "dice": "Los buques grandes desorientarán a las ballenas, y un derrame dejaría sin trabajo a pescadores.",
    "res": "matiz",
    "explica": "El Gobierno federal dice lo contrario: «no hay ningún daño ambiental», hasta 60 buques al año con ruta definida. Pero la obra está detenida por amparos y la propia Presidenta dijo que se revisan otra vez los impactos. El riesgo no está probado ni descartado: se decide en el estudio de impacto ambiental, que se litiga.",
    "fuente": "Presidencia, versión estenográfica del 16-10-2026",
    "url": "https://www.gob.mx/presidencia/es/articulos/version-estenografica-conferencia-de-prensa-de-la-presidenta-claudia-sheinbaum-pardo-del-16-de-octubre-de-2026"
   },
   {
    "dice": "El proyecto ya tiene su autorización de impacto ambiental.",
    "res": "pendiente",
    "explica": "La Presidenta dijo que se hizo el estudio; la prensa reporta fechas y versiones distintas sobre la autorización de la ASEA, y hay suspensiones judiciales. El resolutivo no lo pudimos abrir: falta de la plataforma.",
    "fuente": "Agencia de Seguridad, Energía y Ambiente (ASEA)",
    "url": "https://www.gob.mx/asea",
    "quien": "Falta de la plataforma: el expediente de impacto ambiental está en la ASEA y aún no lo integramos",
    "donde": "https://www.gob.mx/asea"
   },
   {
    "dice": "Pedimos información sobre más de 100 millones de pesos gastados en el Puente Colorado y no han contestado.",
    "res": "no consta",
    "explica": "No encontramos el monto ni las solicitudes en un documento oficial. El puente está en San Luis Río Colorado; según la prensa, la renovación de su concesión la revisa la SICT.",
    "fuente": "Plataforma Nacional de Transparencia",
    "url": "https://www.plataformadetransparencia.org.mx/"
   },
   {
    "dice": "Ya borraron toda la información de la megafarmacia, y este gobierno ha reservado mucha información.",
    "res": "no consta",
    "explica": "Son afirmaciones generales que no pudimos cotejar con un índice de información reservada ni con una página retirada.",
    "fuente": "Plataforma Nacional de Transparencia",
    "url": "https://www.plataformadetransparencia.org.mx/"
   }
  ],
  "sigue": [
   {
    "que": "Pedir el contrato de comodato y su estado jurídico a la Comisión Estatal de Bienes y Concesiones de Sonora",
    "url": "https://www.plataformadetransparencia.org.mx/"
   },
   {
    "que": "El dictamen del exhorto del 12-02-2026 sobre los tres proyectos de gas, turnado a comisión en el Congreso de Sonora",
    "url": "https://congresoson.gob.mx/"
   },
   {
    "que": "El resolutivo de impacto ambiental y lo que diga la ASEA en la nueva revisión",
    "url": "https://www.gob.mx/asea"
   },
   {
    "que": "La resolución de los amparos que detienen la obra",
    "url": "https://www.pjf.gob.mx/"
   },
   {
    "que": "Lo que resuelva el Departamento de Energía de EE. UU. sobre la prórroga al 08-12-2029 (expediente 20-31-LNG)",
    "url": "https://public-inspection.federalregister.gov/2025-23764.pdf"
   },
   {
    "que": "Cuánto pagaría el proyecto en impuestos y derechos, y cuánto se queda en Sonora: no lo ha presentado la Secretaría de Energía",
    "url": "https://www.gob.mx/sener"
   },
   {
    "que": "La ficha del caso en Crisis ambientales (Costo Ambiental), con el presupuesto de la ASEA en el Auditor ambiental",
    "url": "herramienta-ambiente-crisis.html"
   }
  ],
  "fuentes": [
   {
    "nombre": "Departamento de Energía de EE. UU.: Orden DOE/FE 4629, del 8 de diciembre de 2020, expediente 20-31-LNG (Epcilon LNG LLC, exportación de gas a México y reexportación como gas natural licuado)",
    "url": "https://www.energy.gov/sites/prod/files/2020/12/f81/ord4629.pdf"
   },
   {
    "nombre": "Federal Register: aviso de la solicitud de Epcilon LNG para prorrogar al 08-12-2029 el inicio de la reexportación (documento 2025-23764)",
    "url": "https://public-inspection.federalregister.gov/2025-23764.pdf"
   },
   {
    "nombre": "Presidencia: versión estenográfica de la conferencia del 21 de octubre de 2026 (Secretaría de Energía, proyecto en Guaymas)",
    "url": "https://www.gob.mx/presidencia/es/articulos/version-estenografica-conferencia-de-prensa-de-la-presidenta-claudia-sheinbaum-pardo-del-21-de-octubre-de-2026"
   },
   {
    "nombre": "Presidencia: versión estenográfica de la conferencia del 16 de octubre de 2026 (amparo e impacto ambiental)",
    "url": "https://www.gob.mx/presidencia/es/articulos/version-estenografica-conferencia-de-prensa-de-la-presidenta-claudia-sheinbaum-pardo-del-16-de-octubre-de-2026"
   },
   {
    "nombre": "Congreso del Estado de Sonora: Gaceta Parlamentaria No. 2104, acta de la sesión del 12 de febrero de 2026 (exhorto sobre los proyectos Saguaro, AMIGO y Vista Pacífico)",
    "url": "https://gestion.api.congresoson.gob.mx/publico/descarga?uuid=f8cf663d-4257-4f5d-8b08-b05b80a83e72"
   }
  ],
  "actualizado": "26 de octubre de 2026"
 },
 {
  "id": "salud-ventiladores-y-medicinas",
  "seccion": "Verificado",
  "icono": "💊",
  "titulo": "Medicinas y ventiladores del IMSS: lo que consta del robo, de los ventiladores de 2020 y de los contratos que circulan",
  "balazo": "Los ventiladores que el IMSS compró en Hidalgo en 2020 no cumplieron el contrato, se devolvieron sin pagarse y la empresa quedó inhabilitada 27 meses, según el IMSS y el Diario Oficial. Los 800 millones en medicinas que se atribuyen a Amílcar Olán todavía no tienen un contrato oficial detrás.",
  "circula": {
   "red": "Transcripción de un video",
   "cuenta": "Comentario en redes (autor no indicado)",
   "fecha": "Octubre de 2026",
   "texto": "Cuando hablan del robo de medicamentos en los almacenes y las farmacias de los hospitales, me da la sensación de que el gobierno le quiere echar la culpa al personal del IMSS (…). En 2020, a una empresa de un hijo de Bartlett le asignaron mediante adjudicación directa un contrato de 31 millones de pesos para comprar ventiladores respiratorios que ni siquiera cumplían con las especificaciones técnicas. Amílcar Olán (…) tiene contratos de adjudicación directa de medicamentos a sobreprecio por más de 800 millones de pesos en IMSS-Bienestar de Tabasco y Quintana Roo y en el IMSS."
  },
  "cuerpo": [
   "Los ventiladores. El 4 de mayo de 2020 la Secretaría de la Función Pública informó que, desde el 1 de mayo, su Órgano Interno de Control en el IMSS investigaba la compra de ventiladores de la delegación de Hidalgo; después habló de 20 equipos. El 13 de mayo el IMSS informó que, tras la revisión técnica, los equipos «no reúnen los requerimientos y características técnicas-funcionales acordadas en el contrato», que el 8 de mayo levantó el acta para devolverlos al proveedor y que «al momento no se ha erogado ningún recurso por este contrato».",
   "La sanción. El 6 de julio de 2020 el Diario Oficial publicó la circular 11/2020 de la Función Pública: dependencias, entidades, estados y municipios debían abstenerse de contratar con Cyber Robotic Solutions, S.A. de C.V. durante 27 meses (expediente SAN/032/2020, resolución del 2 de julio de 2020), plazo que se alarga si la empresa no paga la multa. La circular no dice el monto de la multa ni menciona al IMSS. La empresa impugnó la sanción ante el Tribunal Federal de Justicia Administrativa, y el Diario Oficial publicó después una medida cautelar.",
   "Lo que no dicen esos documentos: que el contrato fuera por 31 millones de pesos, que se diera por adjudicación directa y que la empresa sea de un hijo de Manuel Bartlett. Eso viene de la investigación periodística de 2020; la circular solo nombra a la empresa.",
   "Los contratos de medicinas. Lo que se dice de Amílcar Olán y de las compras de medicinas a sobreprecio viene de Latinus y de otros medios. La plataforma ya lo había buscado y no encontró un contrato, un informe de la Auditoría Superior ni una resolución que lo nombre: está en «Lo que dejamos fuera y por qué». La cifra nueva de más de 800 millones de pesos tampoco tiene un contrato que la sostenga. Los contratos del IMSS y de IMSS-Bienestar son públicos en ComprasMX; cuando los integremos, esta columna se actualiza.",
   "El robo hormiga. No encontramos un documento oficial reciente en el que el gobierno atribuya el desabasto al robo del personal. Lo que sí hay es un comunicado del IMSS de mayo de 2019 que denunció el robo de medicamentos controlados de una farmacia y aseguró que el abasto estaba garantizado."
  ],
  "dato_curioso": "El IMSS nunca pagó esos ventiladores: los devolvió el 8 de mayo de 2020. Aun así, la empresa quedó inhabilitada, porque la sanción castiga lo que se ofreció y no cumplió, no solo el dinero que salió.",
  "cifras": [
   {
    "valor": "20",
    "etq": "Ventiladores de la compra del IMSS en Hidalgo que investigó la Función Pública",
    "estado": "oficial",
    "fuente": "SFP, comunicado sobre los procedimientos sancionatorios (2020)",
    "url": "https://www.gob.mx/sfp/articulos/funcion-publica-avanza-con-los-procedimientos-sancionatorios-por-la-compra-de-20-ventiladores-del-imss-en-hidalgo-242591"
   },
   {
    "valor": "$0",
    "etq": "Lo que el IMSS había pagado por ese contrato al devolver los equipos",
    "estado": "oficial",
    "fuente": "IMSS, comunicado del 13-05-2020",
    "url": "https://www.gob.mx/imss/prensa/respecto-a-la-informacion-sobre-la-compra-de-ventiladores-por-el-organo-de-operacion-administrativa-desconcentrada-hidalgo-el-imss-informa"
   },
   {
    "valor": "27 meses",
    "etq": "Inhabilitación de Cyber Robotic Solutions para contratar con el gobierno (circular 11/2020)",
    "estado": "oficial",
    "fuente": "DOF, 06-07-2020",
    "url": "https://dof.gob.mx/nota_detalle.php?codigo=5596199&fecha=06/07/2020"
   }
  ],
  "cotejo": [
   {
    "dice": "El gobierno le quiere echar la culpa del desabasto al robo hormiga del personal del IMSS.",
    "res": "no consta",
    "explica": "Es una impresión de quien habla. No encontramos un documento oficial reciente que culpe del desabasto al personal. El IMSS sí denunció en 2019 el robo de medicamentos controlados en una farmacia y dijo que el abasto estaba garantizado.",
    "fuente": "IMSS, comunicado 106 (mayo de 2019)",
    "url": "https://www.gob.mx/imss/prensa/com-106-imss-denuncia-robo-de-medicamentos-controlados"
   },
   {
    "dice": "En 2020 le asignaron a una empresa de un hijo de Bartlett, por adjudicación directa, un contrato de 31 millones de pesos para ventiladores.",
    "res": "matiz",
    "explica": "Consta que el IMSS en Hidalgo compró ventiladores, que no los pagó y que la Función Pública inhabilitó a Cyber Robotic Solutions. El monto de 31 millones, la adjudicación directa y quién es el dueño solo están en la prensa.",
    "fuente": "DOF, circular 11/2020 (06-07-2020)",
    "url": "https://dof.gob.mx/nota_detalle.php?codigo=5596199&fecha=06/07/2020"
   },
   {
    "dice": "Los ventiladores ni siquiera cumplían las especificaciones técnicas.",
    "res": "consta",
    "explica": "El IMSS lo dijo: no reunían los requerimientos y características técnico-funcionales del contrato, y los devolvió.",
    "fuente": "IMSS, comunicado del 13-05-2020",
    "url": "https://www.gob.mx/imss/prensa/respecto-a-la-informacion-sobre-la-compra-de-ventiladores-por-el-organo-de-operacion-administrativa-desconcentrada-hidalgo-el-imss-informa"
   },
   {
    "dice": "Amílcar Olán tiene contratos de adjudicación directa de medicinas a sobreprecio por más de 800 millones de pesos en IMSS-Bienestar de Tabasco y Quintana Roo y en el IMSS.",
    "res": "pendiente",
    "explica": "Es la suma de un medio. Los contratos de 2025 y 2026 del IMSS y de IMSS-Bienestar ya están en Contratos públicos, pero ningún documento oficial dice qué empresas serían de Olán, y sin eso no se le puede atribuir un monto. Los de 2023 y 2024 están en el CompraNet histórico, que aún no integramos.",
    "fuente": "ComprasMX, Datos Abiertos",
    "url": "https://comprasmx.buengobierno.gob.mx/datos-abiertos",
    "quien": "Falta de la plataforma: los contratos de 2023 y 2024 del CompraNet histórico aún no los integramos, y ningún documento oficial abierto liga a Olán con una empresa contratista",
    "donde": "https://comprasmx.buengobierno.gob.mx/datos-abiertos"
   },
   {
    "dice": "Es amigo de Andy López Beltrán y socio de una marca de camisas de moda.",
    "res": "no consta",
    "explica": "Solo está en la prensa y en redes; ningún documento oficial lo dice. Una amistad o una sociedad privada no es, por sí sola, un delito.",
    "fuente": "Solo en prensa",
    "url": ""
   }
  ],
  "sigue": [
   {
    "que": "Los contratos del IMSS en ComprasMX (2025 y 2026), ya integrados: sus proveedores mayores y cuánto fue por adjudicación directa",
    "url": "contratos-publicos.html?i=050GYR"
   },
   {
    "que": "Integrar los contratos de 2023 y 2024 del CompraNet histórico y cotejar los que se atribuyen a empresas ligadas a Olán, cuando un documento oficial las nombre",
    "url": "https://comprasmx.buengobierno.gob.mx/datos-abiertos"
   },
   {
    "que": "Buscar la sentencia del Tribunal Federal de Justicia Administrativa sobre la sanción a Cyber Robotic Solutions",
    "url": "https://www.tfja.gob.mx/"
   }
  ],
  "fuentes": [
   {
    "nombre": "IMSS: Respecto a la compra de ventiladores por el Órgano de Operación Administrativa Desconcentrada Hidalgo (13-05-2020)",
    "url": "https://www.gob.mx/imss/prensa/respecto-a-la-informacion-sobre-la-compra-de-ventiladores-por-el-organo-de-operacion-administrativa-desconcentrada-hidalgo-el-imss-informa"
   },
   {
    "nombre": "SFP: Función Pública investiga desde el 1 de mayo la adquisición de ventiladores en el IMSS (04-05-2020)",
    "url": "https://www.gob.mx/sfp/prensa/funcion-publica-investiga-desde-el-1-de-mayo-adquisicion-de-ventiladores-en-el-imss-secretaria-sandoval-ballesteros"
   },
   {
    "nombre": "SFP: Avanzan los procedimientos sancionatorios por la compra de 20 ventiladores del IMSS en Hidalgo (2020)",
    "url": "https://www.gob.mx/sfp/articulos/funcion-publica-avanza-con-los-procedimientos-sancionatorios-por-la-compra-de-20-ventiladores-del-imss-en-hidalgo-242591"
   },
   {
    "nombre": "DOF: Circular 11/2020 sobre Cyber Robotic Solutions, S.A. de C.V. (06-07-2020)",
    "url": "https://dof.gob.mx/nota_detalle.php?codigo=5596199&fecha=06/07/2020"
   },
   {
    "nombre": "IMSS, comunicado 106: IMSS denuncia robo de medicamentos controlados (mayo de 2019)",
    "url": "https://www.gob.mx/imss/prensa/com-106-imss-denuncia-robo-de-medicamentos-controlados"
   }
  ],
  "actualizado": "26 de octubre de 2026"
 },
 {
  "id": "taddei-renuncia-ine-contratos",
  "seccion": "Verificado",
  "icono": "🗳️",
  "titulo": "La renuncia de Guadalupe Taddei al INE: lo que consta en documentos y lo que solo dice la prensa",
  "balazo": "El INE publicó que su consejera presidenta entregaría su renuncia el 26 de octubre y que respalda la investigación de la Auditoría Superior. El video, los montos y las frases que circulan vienen de medios y aún no tienen documento oficial.",
  "circula": {
   "red": "Redes sociales",
   "cuenta": "Publicación que resume un reportaje de Latinus",
   "fecha": "25 y 26 de octubre de 2026",
   "texto": "Renuncia la presidenta del INE tras salir un video de su hijo brindando en París con un contratista, apoderado de Cajas Graf, proveedora de material electoral del instituto. Latinus suma al menos 245 millones de pesos en contratos para Cajas Graf bajo Taddei en Sonora y en el INE. La ASF abrió una investigación al instituto y a sus proveedores. Taddei habría dicho «No me voy» y al día siguiente anunció su renuncia ante la Cámara de Diputados."
  },
  "cuerpo": [
   "El 25 de octubre de 2026, en un mensaje publicado en Central Electoral, el sitio oficial del INE, Guadalupe Taddei Zavala anunció que el 26 de octubre presentaría ante la Cámara de Diputados su renuncia como consejera presidenta, cargo que ocupaba desde abril de 2023. Según ese mensaje, lo hace para proteger al Instituto, y la decisión no releva a nadie del deber de esclarecer los hechos que deban investigarse.",
   "Un día antes, el 24 de octubre, la Presidencia del INE publicó que respalda la investigación que la Auditoría Superior de la Federación abrió de oficio, que colaborará con ella, que ya envió los antecedentes a su Órgano Interno de Control y que abrirá un micrositio con las contrataciones, sus montos, sus proveedores y sus documentos. El 22 de octubre, en el Consejo General, un partido le pidió separarse del cargo mientras se investigaban las contrataciones señaladas por la prensa; consta en la versión estenográfica de esa sesión.",
   "Lo que todavía no tiene documento oficial: el video de París, quién lo grabó, quién pagó el viaje, la frase «No me voy» y la suma de 245 millones de pesos en contratos. Todo eso viene de Latinus y de otros medios. Tampoco encontramos el comunicado de la propia Auditoría Superior: según los medios, lo dio a conocer el 23 de octubre, pero no lo localizamos en asf.gob.mx. El único documento del INE que nombra a Cajas Graf que pudimos consultar es el fallo de la licitación LP-INE-001/2025, de febrero de 2025, para urnas y mamparas de la elección judicial: ahí Cajas Graf, en participación conjunta con TOL Producciones, no cumplió las especificaciones técnicas. Ese fallo no dice si la empresa ganó otros contratos.",
   "Una nota de método: las páginas del INE no abrieron desde la plataforma; sus textos se tomaron de los comunicados de Central Electoral tal como los muestra el buscador. Ninguna autoridad ha resuelto que haya delito o falta administrativa: una investigación abierta no es una conclusión."
  ],
  "dato_curioso": "El único documento del INE que encontramos con el nombre de Cajas Graf la deja fuera: en febrero de 2025 su propuesta para urnas y mamparas de la elección judicial no cumplió las especificaciones técnicas.",
  "cifras": [
   {
    "valor": "26/10/2026",
    "etq": "Día en que anunció que entregaría su renuncia ante la Cámara de Diputados",
    "estado": "oficial",
    "fuente": "INE, Central Electoral, mensaje del 25-10-2026",
    "url": "https://centralelectoral.ine.mx/2026/10/25/mensaje-de-la-consejera-presidenta-del-instituto-nacional-electoral-guadalupe-taddei-zavala/"
   },
   {
    "valor": "Abril de 2023",
    "etq": "Inicio de su encargo como consejera presidenta",
    "estado": "oficial",
    "fuente": "INE, Central Electoral, mensaje del 25-10-2026",
    "url": "https://centralelectoral.ine.mx/2026/10/25/mensaje-de-la-consejera-presidenta-del-instituto-nacional-electoral-guadalupe-taddei-zavala/"
   }
  ],
  "cotejo": [
   {
    "dice": "Renuncia la presidenta del INE y entrega su renuncia el lunes ante la Cámara de Diputados.",
    "res": "consta",
    "explica": "El INE publicó su mensaje del 25 de octubre de 2026: presentaría su renuncia el 26 de octubre ante la Cámara de Diputados. La aceptación de la Cámara aún no la vimos en un documento.",
    "fuente": "INE, Central Electoral, 25-10-2026",
    "url": "https://centralelectoral.ine.mx/2026/10/25/mensaje-de-la-consejera-presidenta-del-instituto-nacional-electoral-guadalupe-taddei-zavala/"
   },
   {
    "dice": "La Auditoría Superior de la Federación abrió una investigación al instituto y sus proveedores.",
    "res": "matiz",
    "explica": "El INE lo confirma: el 24 de octubre publicó que respalda la investigación que la ASF abrió de oficio. Según la prensa, la ASF lo anunció el 23 de octubre de 2026 y alcanza al INE, a los institutos electorales locales y a sus proveedores. El comunicado de la ASF, con su alcance exacto, no lo localizamos en asf.gob.mx: falta de la plataforma.",
    "fuente": "INE, Central Electoral, 24-10-2026",
    "url": "https://centralelectoral.ine.mx/2026/10/24/la-presidencia-del-ine-respalda-la-investigacion-de-la-asf-y-reafirma-su-compromiso-con-el-estado-de-derecho/"
   },
   {
    "dice": "Cajas Graf es proveedora de material electoral del INE.",
    "res": "matiz",
    "explica": "Consta que participó en la licitación LP-INE-001/2025 (urnas y mamparas de la elección judicial) y que no cumplió las especificaciones técnicas. Que el INE le haya pagado otros contratos solo lo dice la prensa: el contrato no lo pudimos abrir.",
    "fuente": "INE, fallo de la licitación LP-INE-001/2025 (06-02-2025)",
    "url": "https://ine.mx/wp-content/uploads/2025/02/lp-ine-001-2025-fallo.pdf"
   },
   {
    "dice": "Latinus suma al menos 245 millones de pesos en contratos para Cajas Graf bajo Taddei en Sonora y en el INE.",
    "res": "pendiente",
    "explica": "Es la suma de un medio. Para sostenerla hacen falta los contratos firmados por el INE y por el Instituto Estatal Electoral de Sonora, que no pudimos abrir: falta de la plataforma. Otros medios dan cifras distintas. Una nota de método: en los contratos de ComprasMX 2025 y 2026 que integra la plataforma (215,121 contratos de 1,078 instituciones) no aparece Cajas Graf, pero tampoco el INE, que es autónomo y no contrata por ComprasMX. Que no aparezca ahí no prueba nada: los contratos hay que pedirlos al INE y al IEE Sonora.",
    "fuente": "Plataforma Nacional de Transparencia",
    "url": "https://www.plataformadetransparencia.org.mx/",
    "quien": "Falta de la plataforma: los contratos del INE y del IEE Sonora son públicos y aún no los integramos",
    "donde": "https://www.plataformadetransparencia.org.mx/"
   },
   {
    "dice": "Un video muestra al hijo de Taddei brindando en París con el apoderado de Cajas Graf («París a tus pies, chamaquito»), y lo grabó el propio empresario.",
    "res": "no consta",
    "explica": "Es un video difundido por Latinus. No hay documento oficial sobre su contenido, su autoría ni quién pagó el viaje, y un video por sí solo no prueba un acto de corrupción. No lo afirmamos ni lo negamos.",
    "fuente": "Solo en prensa (Latinus)",
    "url": ""
   },
   {
    "dice": "Un día antes, Taddei dijo a los consejeros «No me voy» y llamó «golpeteo político» a los señalamientos.",
    "res": "no consta",
    "explica": "Solo aparece en prensa. Lo que sí consta es que el 22 de octubre, en el Consejo General, un partido le pidió separarse del cargo mientras se investigaba.",
    "fuente": "INE, versión estenográfica del Consejo General, 22-10-2026",
    "url": "https://centralelectoral.ine.mx/2026/10/22/version-estenografica-de-la-sesion-extraordinaria-del-consejo-general-del-ine-22-de-octubre-de-2026"
   }
  ],
  "sigue": [
   {
    "que": "Resultados de la investigación de la Auditoría Superior sobre las contrataciones del INE y de los institutos locales",
    "url": "https://www.asf.gob.mx/"
   },
   {
    "que": "Micrositio del INE con sus contrataciones, montos, proveedores y documentos, anunciado el 24-10-2026",
    "url": "https://www.ine.mx/"
   },
   {
    "que": "Quién ocupa la presidencia del INE y cómo la nombra la Cámara de Diputados",
    "url": "https://www.diputados.gob.mx/"
   },
   {
    "que": "La revisión que pidió la Presidenta de los contratos de periodos anteriores, incluido el de Lorenzo Córdova, y lo que dijo del congelamiento de cuentas de la UIF (27-10-2026)",
    "url": "noticias-auditavision.html#col-ine-contratos-desde-cordova"
   }
  ],
  "fuentes": [
   {
    "nombre": "INE, Central Electoral: Mensaje de la Consejera Presidenta, Guadalupe Taddei Zavala (25-10-2026)",
    "url": "https://centralelectoral.ine.mx/2026/10/25/mensaje-de-la-consejera-presidenta-del-instituto-nacional-electoral-guadalupe-taddei-zavala/"
   },
   {
    "nombre": "INE, Central Electoral: La Presidencia del INE respalda la investigación de la ASF (24-10-2026)",
    "url": "https://centralelectoral.ine.mx/2026/10/24/la-presidencia-del-ine-respalda-la-investigacion-de-la-asf-y-reafirma-su-compromiso-con-el-estado-de-derecho/"
   },
   {
    "nombre": "INE, versión estenográfica de la sesión extraordinaria del Consejo General (22-10-2026)",
    "url": "https://centralelectoral.ine.mx/2026/10/22/version-estenografica-de-la-sesion-extraordinaria-del-consejo-general-del-ine-22-de-octubre-de-2026"
   },
   {
    "nombre": "INE, Dirección Ejecutiva de Administración: fallo de la licitación LP-INE-001/2025 (06-02-2025)",
    "url": "https://ine.mx/wp-content/uploads/2025/02/lp-ine-001-2025-fallo.pdf"
   }
  ],
  "actualizado": "27 de octubre de 2026"
 },
 {
  "id": "lif-2027-deuda-y-multas",
  "seccion": "Verificado",
  "icono": "🧾",
  "titulo": "Ley de Ingresos 2027: el techo de deuda y el perdón de multas, en sus documentos",
  "balazo": "La Cámara de Diputados la aprobó el 15 de octubre con un techo de deuda interna de 1.7 billones de pesos y con un cambio para que las grandes empresas también paguen sus adeudos sin multas ni recargos. El 28 de octubre el pleno del Senado la aprobó sin cambios (75 a 34) y la envió al Ejecutivo.",
  "circula": {
   "red": "Instagram",
   "cuenta": "@pajaropolitico (Animal Político)",
   "fecha": "Octubre de 2026",
   "texto": "Morena y aliados aprobaron la Ley de Ingresos 2027: avala 1.7 billones de pesos en deuda interna y elimina el 100% de multas y recargos fiscales a grandes contribuyentes tras acuerdo de Sheinbaum con el CCE."
  },
  "cuerpo": [
   "El 15 de octubre de 2026 el pleno de la Cámara de Diputados aprobó la Ley de Ingresos de la Federación para 2027: 331 votos a favor y 118 en contra en lo general, y 340 contra 109 en lo particular, según el Canal del Congreso. Estima ingresos por 10 billones 636 mil 488 millones de pesos y autoriza endeudamiento interno neto hasta por un billón 700 mil millones. Ojo: es un techo, lo máximo que el gobierno puede pedir prestado en el año, no deuda ya contratada.",
   "En la discusión, el diputado Ricardo Monreal presentó una reserva al artículo vigésimo primero transitorio, que se aprobó: amplía el programa de regularización fiscal, quita el tope de 300 millones de pesos de ingresos anuales y deja entrar a los contribuyentes que atiende la Administración General de Grandes Contribuyentes del SAT, con créditos firmes o consentidos. No es una condonación del impuesto: para obtener la reducción de multas, recargos y gastos de ejecución hay que pagar completo el adeudo.",
   "El origen está a la vista. El 13 de octubre, en el 50 aniversario del Consejo Coordinador Empresarial, la presidenta Sheinbaum dijo, según la versión estenográfica oficial: «le propuse a la Secretaría de Hacienda que el próximo año a todos, sin tener límite, quienes tengan deudas con el fisco pueden pagar sin recargos» y «sin ninguna multa, sin ningún recargo, a cualquier monto». Lo dijo como propuesta suya; la palabra «acuerdo» la usan los medios.",
   "En el Senado, el 21 de octubre las comisiones unidas de Hacienda y de Estudios Legislativos Primera aprobaron el paquete: 10 a 5 en la primera y 8 a 6 en la segunda. El pleno la aprobó en sus términos, 75 a 34 en lo general y 73 a 33 en lo particular, y la envió al Ejecutivo, según el Canal del Congreso del 28 de octubre. Falta su publicación en el Diario Oficial: hasta entonces no rige."
  ],
  "dato_curioso": "El perdón de multas no es nuevo: la Ley de Ingresos 2026 ya daba un estímulo del 100 % de multas y recargos por adeudos de 2024 y anteriores, pero dejaba fuera a quien ganara más de 300 millones de pesos al año. Lo que cambió para 2027 es ese tope.",
  "cifras": [
   {
    "valor": "$1,700,000 millones",
    "etq": "Techo de endeudamiento interno neto del Gobierno Federal para 2027 (aprobado por Diputados)",
    "estado": "oficial",
    "fuente": "Canal del Congreso, 15-10-2026",
    "url": "https://www.canaldelcongreso.gob.mx/noticias/10320"
   },
   {
    "valor": "$10,636,488 millones",
    "etq": "Ingresos totales estimados para 2027",
    "estado": "oficial",
    "fuente": "Canal del Congreso, 15-10-2026",
    "url": "https://www.canaldelcongreso.gob.mx/noticias/10320"
   },
   {
    "valor": "331 a 118",
    "etq": "Votación en lo general en la Cámara de Diputados (340 a 109 en lo particular)",
    "estado": "oficial",
    "fuente": "Canal del Congreso, 15-10-2026",
    "url": "https://www.canaldelcongreso.gob.mx/noticias/10320"
   },
   {
    "valor": "18 a 11",
    "etq": "Votos en las comisiones unidas del Senado (10 + 8 a favor; 5 + 6 en contra)",
    "estado": "derivado",
    "fuente": "Canal del Congreso, 21-10-2026; suma de las dos comisiones",
    "url": "https://www.canaldelcongreso.gob.mx/noticias/10329"
   }
  ],
  "cotejo": [
   {
    "dice": "Morena y aliados aprobaron la Ley de Ingresos 2027.",
    "res": "matiz",
    "explica": "La aprobaron la Cámara de Diputados (331 a 118 en lo general) y, el 28 de octubre, el pleno del Senado (75 a 34); falta su publicación en el DOF. El voto por partido no viene en las notas oficiales que consultamos.",
    "fuente": "Canal del Congreso, 15 y 21-10-2026",
    "url": "https://www.canaldelcongreso.gob.mx/noticias/10320"
   },
   {
    "dice": "Avala 1.7 billones de pesos en deuda interna.",
    "res": "consta",
    "explica": "Autoriza endeudamiento interno neto hasta por 1 billón 700 mil millones de pesos. Es el máximo permitido para el año, no deuda ya contratada.",
    "fuente": "Canal del Congreso, 15-10-2026",
    "url": "https://www.canaldelcongreso.gob.mx/noticias/10320"
   },
   {
    "dice": "Elimina el 100 % de multas y recargos fiscales a grandes contribuyentes.",
    "res": "matiz",
    "explica": "Es una reducción de multas, recargos y gastos de ejecución, no una condonación del impuesto: hay que pagar completo el adeudo. La reserva aprobada quita el tope de 300 millones de pesos y deja entrar a los grandes contribuyentes. El porcentaje exacto para 2027 no viene en la nota oficial; lo confirmará el texto publicado en el DOF.",
    "fuente": "Canal del Congreso, 16-10-2026",
    "url": "https://www.canaldelcongreso.gob.mx/noticias/10322"
   },
   {
    "dice": "Fue tras un acuerdo de Sheinbaum con el CCE.",
    "res": "matiz",
    "explica": "La presidenta lo anunció el 13 de octubre en el 50 aniversario del CCE como una propuesta suya a Hacienda: «sin ninguna multa, sin ningún recargo, a cualquier monto». Que sea un «acuerdo» con el CCE lo dicen los medios.",
    "fuente": "Presidencia, versión estenográfica del 50 aniversario del CCE (13-10-2026)",
    "url": "https://www.gob.mx/presidencia/articulos/version-estenografica-50-aniversario-del-consejo-coordinador-empresarial"
   }
  ],
  "sigue": [
   {
    "que": "Ya llegó: el pleno del Senado la aprobó 75 a 34 (Canal del Congreso, 28-10-2026). Su nota «Al momento» trae el resto",
    "url": "noticias-auditavision.html#col-senado-ley-de-ingresos-2027"
   },
   {
    "que": "Publicación de la Ley de Ingresos 2027 en el Diario Oficial: el texto final del artículo vigésimo primero transitorio y el porcentaje exacto",
    "url": "https://www.dof.gob.mx/"
   }
  ],
  "fuentes": [
   {
    "nombre": "Canal del Congreso: Aprueban en San Lázaro Ley de Ingresos 2027 (15-10-2026)",
    "url": "https://www.canaldelcongreso.gob.mx/noticias/10320"
   },
   {
    "nombre": "Canal del Congreso: Modificación a Ley de Ingresos busca ampliar beneficios (16-10-2026)",
    "url": "https://www.canaldelcongreso.gob.mx/noticias/10322"
   },
   {
    "nombre": "Canal del Congreso: Senado aprueba Ley de Ingresos 2027 por 10.6 billones de pesos (28-10-2026)",
    "url": "https://www.canaldelcongreso.gob.mx/noticias/10338"
   },
   {
    "nombre": "Canal del Congreso: Comisiones del Senado aprueban Ley de Ingresos 2027 (21-10-2026)",
    "url": "https://www.canaldelcongreso.gob.mx/noticias/10329"
   },
   {
    "nombre": "Presidencia de la República: versión estenográfica del 50 aniversario del Consejo Coordinador Empresarial (13-10-2026)",
    "url": "https://www.gob.mx/presidencia/articulos/version-estenografica-50-aniversario-del-consejo-coordinador-empresarial"
   },
   {
    "nombre": "Cámara de Diputados: Ley de Ingresos de la Federación para el Ejercicio Fiscal 2026",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/LIF_2026.pdf"
   }
  ],
  "actualizado": "29 de octubre de 2026"
 },
 {
  "id": "hr-ratings-baja-mexico-bbb",
  "seccion": "Verificado",
  "icono": "📉",
  "titulo": "HR Ratings baja la nota de la deuda de México a BBB: lo que reconoce Hacienda",
  "balazo": "El 15 de octubre de 2026 Hacienda informó que HR Ratings bajó la calificación de largo plazo de México de BBB+ a BBB, con perspectiva estable. México sigue con grado de inversión ante las ocho agencias que lo califican.",
  "circula": {
   "red": "Redes sociales",
   "cuenta": "Publicación que menciona a @shcp_mx",
   "fecha": "Octubre de 2026",
   "texto": "HR Ratings redujo la calificación crediticia de largo plazo de la deuda soberana de México de BBB+ a BBB por deterioro fiscal, bajo crecimiento y rigidez del gasto. Estima un déficit de los RFSP de 4.6% del PIB para 2026 y prevé deuda de 61.2% del PIB en 2030. La SHCP, encabezada por Édgar Amador, destacó un ajuste fiscal previo de 1.3 puntos del PIB, la deuda en moneda nacional a tasa fija y las reservas internacionales."
  },
  "cuerpo": [
   "Según el comunicado 82 de la Secretaría de Hacienda, del 15 de octubre de 2026, HR Ratings bajó la calificación de largo plazo de la deuda soberana de México de BBB+ a BBB, mantuvo la perspectiva estable y ratificó la de corto plazo en HR3. Hacienda subraya que México conserva el grado de inversión con las ocho agencias que califican su deuda.",
   "En su respuesta, Hacienda recuerda que en 2025 hizo un ajuste fiscal de 1.3 puntos del PIB, el mayor desde 1990; que cerca del 80 % de la deuda del Gobierno Federal está en moneda nacional y a tasa fija; que las reservas internacionales superan los 256 mil millones de dólares, y que existe una Línea de Crédito Flexible del FMI por 24 mil millones de dólares.",
   "Las razones y las proyecciones de la propia calificadora, un déficit de 4.6 % del PIB en 2026 y una deuda de 61.2 % del PIB en 2030, están en el reporte de HR Ratings, que no pudimos abrir desde la plataforma. Hasta cotejarlas, van como pendientes. Algunos medios citan otra proyección (65.6 % en 2033), y por eso no conviene repetir ninguna sin el reporte.",
   "Qué quiere decir: BBB sigue siendo grado de inversión, el escalón más bajo antes de dejar de serlo es BBB-. Una calificación más baja suele encarecer lo que paga el país por pedir prestado, pero cuánto lo encarece no lo dice ningún documento oficial."
  ],
  "dato_curioso": "En octubre de 2025, HR Ratings había ratificado a México en BBB+ y mejorado su perspectiva de negativa a estable. Un año después, mantuvo la perspectiva estable pero bajó un escalón la nota.",
  "cifras": [
   {
    "valor": "BBB+ → BBB",
    "etq": "Calificación de largo plazo de la deuda soberana, según HR Ratings (perspectiva estable)",
    "estado": "oficial",
    "fuente": "SHCP, comunicado 82 (15-10-2026)",
    "url": "https://www.gob.mx/shcp/prensa/comunicado-no-82"
   },
   {
    "valor": "1.3 pp del PIB",
    "etq": "Ajuste fiscal de 2025, el mayor desde 1990, según Hacienda",
    "estado": "oficial",
    "fuente": "SHCP, comunicado 82 (15-10-2026)",
    "url": "https://www.gob.mx/shcp/prensa/comunicado-no-82"
   },
   {
    "valor": "≈ 80 %",
    "etq": "Deuda del Gobierno Federal en moneda nacional y a tasa fija",
    "estado": "oficial",
    "fuente": "SHCP, comunicado 82 (15-10-2026)",
    "url": "https://www.gob.mx/shcp/prensa/comunicado-no-82"
   },
   {
    "valor": "> 256 mil mdd",
    "etq": "Reservas internacionales",
    "estado": "oficial",
    "fuente": "SHCP, comunicado 82 (15-10-2026)",
    "url": "https://www.gob.mx/shcp/prensa/comunicado-no-82"
   }
  ],
  "cotejo": [
   {
    "dice": "HR Ratings redujo la calificación de largo plazo de México de BBB+ a BBB.",
    "res": "consta",
    "explica": "Lo informa la propia Secretaría de Hacienda: de BBB+ a BBB, con perspectiva estable; la de corto plazo se ratificó en HR3.",
    "fuente": "SHCP, comunicado 82 (15-10-2026)",
    "url": "https://www.gob.mx/shcp/prensa/comunicado-no-82"
   },
   {
    "dice": "Fue por deterioro fiscal, bajo crecimiento económico y rigidez del gasto.",
    "res": "pendiente",
    "explica": "Son las razones de la calificadora; están en su reporte, que no pudimos abrir: falta de la plataforma.",
    "fuente": "HR Ratings",
    "url": "https://www.hrratings.com/",
    "quien": "Falta de la plataforma: el reporte de HR Ratings existe y aún no lo integramos",
    "donde": "https://www.hrratings.com/"
   },
   {
    "dice": "Estima un déficit de los RFSP de 4.6 % del PIB para 2026 y deuda de 61.2 % del PIB en 2030.",
    "res": "pendiente",
    "explica": "Son proyecciones de HR Ratings, no de Hacienda. Los medios citan cifras distintas y el reporte no lo pudimos abrir: falta de la plataforma.",
    "fuente": "HR Ratings",
    "url": "https://www.hrratings.com/",
    "quien": "Falta de la plataforma: el reporte de HR Ratings existe y aún no lo integramos",
    "donde": "https://www.hrratings.com/"
   },
   {
    "dice": "Hacienda destacó un ajuste fiscal previo de 1.3 puntos del PIB, la deuda en moneda nacional a tasa fija y las reservas internacionales.",
    "res": "consta",
    "explica": "Las tres cosas están en el comunicado: ajuste de 1.3 puntos del PIB en 2025, cerca del 80 % de la deuda federal en moneda nacional y a tasa fija, y reservas por más de 256 mil millones de dólares.",
    "fuente": "SHCP, comunicado 82 (15-10-2026)",
    "url": "https://www.gob.mx/shcp/prensa/comunicado-no-82"
   },
   {
    "dice": "La SHCP está encabezada por Édgar Amador.",
    "res": "pendiente",
    "explica": "El comunicado 82 no nombra al secretario, y no cotejamos su nombramiento en un documento oficial: falta de la plataforma.",
    "fuente": "Secretaría de Hacienda",
    "url": "https://www.gob.mx/shcp",
    "quien": "Falta de la plataforma: el nombramiento es público y aún no lo integramos",
    "donde": "https://www.gob.mx/shcp"
   }
  ],
  "sigue": [
   {
    "que": "Abrir el reporte de HR Ratings para cotejar sus razones y sus proyecciones de déficit y deuda",
    "url": "https://www.hrratings.com/"
   }
  ],
  "fuentes": [
   {
    "nombre": "SHCP, comunicado No. 82: HR Ratings ratificó la calificación soberana de corto plazo de México en HR3 (15-10-2026)",
    "url": "https://www.gob.mx/shcp/prensa/comunicado-no-82"
   },
   {
    "nombre": "SHCP, comunicado No. 50: HR Ratings ratificó la calificación de México en BBB+ y cambió su perspectiva a estable (28-10-2025)",
    "url": "https://www.gob.mx/shcp/prensa/comunicado-no-50-hr-ratings-ratifico-la-calificacion-crediticia-de-mexico-en-bbb-modificando-su-perspectiva-de-negativa-a-estable"
   }
  ],
  "actualizado": "26 de octubre de 2026"
 },
 {
  "id": "garcia-luna-las-dos-cortes",
  "seccion": "Personajes",
  "icono": "⚖️",
  "titulo": "García Luna: una condena penal en Nueva York y otra civil en Miami",
  "balazo": "Mientras cumple 460 meses de prisión en Estados Unidos, México le cobra en tribunales de Florida el dinero que, según la UIF, salió de contratos de seguridad pública.",
  "cuerpo": [
   "Genaro García Luna fue secretario de Seguridad Pública de 2006 a 2012. El 16 de octubre de 2024, el juez Brian M. Cogan, del Distrito Este de Nueva York, lo sentenció a 460 meses de prisión y a una multa de 2 millones de dólares. Antes, en febrero de 2023 y tras un juicio de cuatro semanas, un jurado lo había declarado culpable de cinco cargos: dirigir una empresa criminal continua, tres conspiraciones relacionadas con la cocaína y hacer declaraciones falsas. La fiscalía estadounidense sostuvo que, a cambio de sobornos, ayudó al Cártel de Sinaloa durante una década. Se trata de una sentencia de primera instancia: en Estados Unidos es la resolución del tribunal de distrito.",
   "En México el caso sigue otro camino, el del dinero. En septiembre de 2021, la Unidad de Inteligencia Financiera (UIF) de Hacienda demandó por la vía civil, en el Condado de Miami-Dade, Florida, a la red de empresas que obtuvo contratos con entes de seguridad. El 22 de mayo de 2025, el Tribunal del Undécimo Circuito Judicial de ese condado dictó sentencia final: García Luna debe pagar 748,829,676.00 dólares y su esposa, Linda Cristina Pereyra, 1,740,025,540.20 dólares. Según la UIF, la ley de Florida permite que la condena sea el triple de lo reclamado. Antes hubo siete resoluciones en contra de la pareja y de sus cinco empresas porque no se presentaron al juicio.",
   "El 19 de mayo de 2026 llegó una tercera condena civil, esta contra integrantes de la familia Weinberg y sus empresas, por unos 578.5 millones de dólares. Con datos de la UIF, la Presidencia explicó que el esquema abarcó 30 contratos con sobreprecio y unos 727.9 millones de dólares y 528 millones de pesos. Que te condenen a pagar no significa que el dinero regrese. Lo efectivamente recuperado es mucho menos: 5,805,693.50 dólares, recibidos el 25 de agosto de 2026 por una póliza de fianza y la venta de 12 propiedades en Florida. En México, la Fiscalía General de la República mantiene abiertas al menos tres investigaciones contra él, según informó la Presidencia en octubre de 2024. Ninguna tiene todavía una sentencia."
  ],
  "dato_curioso": "La Presidencia anunció que los 5.8 millones de dólares recuperados en Florida, unos 100 millones de pesos, se destinarán a escuelas de La Montaña de Guerrero.",
  "cifras": [
   {
    "valor": "460 meses de prisión",
    "etq": "Sentencia penal dictada el 16-10-2024 por el juez Brian M. Cogan (Distrito Este de Nueva York)",
    "estado": "oficial",
    "fuente": "Departamento de Justicia de EE.UU., Fiscalía del Distrito Este de Nueva York",
    "url": "https://www.justice.gov/usao-edny/pr/ex-mexican-secretary-public-security-genaro-garcia-luna-sentenced-over-38-years"
   },
   {
    "valor": "748,829,676.00 dólares",
    "etq": "Condena civil a García Luna, Miami-Dade, 22-05-2025",
    "estado": "oficial",
    "fuente": "UIF, Nota relativa a la sentencia",
    "url": "https://www.gob.mx/uif/prensa/nota-relativa-a-la-sentencia-emitida-r"
   },
   {
    "valor": "1,740,025,540.20 dólares",
    "etq": "Condena civil a Linda Cristina Pereyra, Miami-Dade, 22-05-2025",
    "estado": "oficial",
    "fuente": "UIF, Nota relativa a la sentencia",
    "url": "https://www.gob.mx/uif/prensa/nota-relativa-a-la-sentencia-emitida-r"
   },
   {
    "valor": "578.5 millones de dólares",
    "etq": "Condena civil a integrantes de la familia Weinberg y empresas relacionadas, Florida, 19-05-2026",
    "estado": "oficial",
    "fuente": "SHCP, Comunicado n.º 42",
    "url": "https://www.gob.mx/uif/prensa/shcp-a-traves-de-la-uif-obtiene-nueva-sentencia-a-favor-del-estado-mexicano-por-mas-de-578-millones-de-dolares-en-caso-genaro-garcia-luna?idiom=es"
   },
   {
    "valor": "5,805,693.50 dólares",
    "etq": "Lo efectivamente recuperado, recibido el 25-08-2026 (fianza y venta de 12 propiedades en Florida)",
    "estado": "oficial",
    "fuente": "Presidencia, comunicado del 28-08-2026",
    "url": "https://www.gob.mx/presidencia/prensa/presidenta-informa-que-los-5-8-mdd-recuperados-por-caso-garcia-luna-y-familia-weinberg-se-destinaran-a-escuelas-en-la-montana-de-guerrero?idiom=es"
   }
  ],
  "fuentes": [
   {
    "nombre": "Fiscalía del Distrito Este de Nueva York (DOJ): «Ex-Mexican Secretary of Public Security Genaro Garcia Luna Sentenced to Over 38 Years' Imprisonment», 16-10-2024",
    "url": "https://www.justice.gov/usao-edny/pr/ex-mexican-secretary-public-security-genaro-garcia-luna-sentenced-over-38-years"
   },
   {
    "nombre": "Presidencia de la República: «Presidenta Claudia Sheinbaum informa investigaciones abiertas contra García Luna en UIF y FGR», 18-10-2024",
    "url": "https://www.gob.mx/presidencia/prensa/presidenta-claudia-sheinbaum-informa-investigaciones-abiertas-contra-garcia-luna-en-uif-y-fgr"
   },
   {
    "nombre": "UIF (SHCP): Nota relativa a la sentencia en el juicio civil contra Genaro García Luna y Linda Cristina Pereyra, 22-05-2025",
    "url": "https://www.gob.mx/uif/prensa/nota-relativa-a-la-sentencia-emitida-r"
   },
   {
    "nombre": "SHCP: Comunicado n.º 42, nueva sentencia por más de 578 millones de dólares en el caso García Luna, 20-05-2026",
    "url": "https://www.gob.mx/uif/prensa/shcp-a-traves-de-la-uif-obtiene-nueva-sentencia-a-favor-del-estado-mexicano-por-mas-de-578-millones-de-dolares-en-caso-genaro-garcia-luna?idiom=es"
   },
   {
    "nombre": "Presidencia de la República: los 5.8 mdd recuperados por el caso García Luna y familia Weinberg se destinarán a escuelas en la Montaña de Guerrero, 28-08-2026",
    "url": "https://www.gob.mx/presidencia/prensa/presidenta-informa-que-los-5-8-mdd-recuperados-por-caso-garcia-luna-y-familia-weinberg-se-destinaran-a-escuelas-en-la-montana-de-guerrero?idiom=es"
   }
  ],
  "actualizado": "28 de agosto de 2026"
 },
 {
  "id": "garcia-luna-testigos-y-la-ley-mexicana",
  "seccion": "Personajes",
  "icono": "🗣️",
  "titulo": "García Luna y los testigos colaboradores: lo que dice la ley de cada lado",
  "balazo": "Se repite que en Nueva York «no hubo pruebas, solo dichos de narcos» y que en México eso no valdría. Revisamos los documentos: el testimonio sí es prueba en ambos países, y la ley mexicana también premia y admite al delincuente que colabora. La diferencia real está en otra parte.",
  "cuerpo": [
   "Lo que consta en documento oficial: según la Fiscalía Federal del Distrito Este de Nueva York, tras un juicio de cuatro semanas en febrero de 2023, un jurado declaró a Genaro García Luna culpable de cinco cargos: empresa criminal continua, conspiración internacional para distribuir cocaína, conspiración para distribuirla y poseerla con intención de distribuirla, conspiración para importarla y declaraciones falsas. El 16 de octubre de 2024, el juez Brian M. Cogan le impuso 460 meses de prisión y una multa de 2 millones de dólares (comunicado de sentencia del Departamento de Justicia).",
   "¿Qué pruebas se presentaron? El propio comunicado del Departamento de Justicia dice que fueron «antiguos miembros del Cártel» quienes declararon sobre dónde se entregaban los sobornos: una casa de seguridad en la Ciudad de México con dinero oculto tras una pared falsa, un autolavado en Guadalajara y un restaurante francés frente a la Embajada de Estados Unidos. Es decir, el peso central de la acusación, en la versión oficial de la fiscalía, sí recayó en testigos que fueron parte del delito. Si además se exhibieron documentos, registros o declaraciones de agentes, no lo podemos afirmar ni negar: el expediente y las transcripciones del juicio no están en un sitio oficial que hayamos podido consultar, así que ese punto queda pendiente.",
   "Ahora bien, decir que «no hubo pruebas como tal» no se sostiene en ninguno de los dos sistemas. En Estados Unidos, la Regla 601 de las Reglas Federales de Evidencia establece que toda persona es competente para ser testigo salvo que las reglas digan otra cosa. En México, el Código Nacional de Procedimientos Penales dice que «cualquier hecho puede ser probado por cualquier medio, siempre y cuando sea lícito» (art. 259) y que todos los hechos pueden probarse «por cualquier medio pertinente» (art. 356); la «prueba testimonial» tiene su propia sección en el Código (arts. 360 y siguientes). El testimonio es prueba. La discusión honesta no es si existió, sino cuánto debe pesar.",
   "Tampoco es exacto que en México el dicho de un delincuente que colabora no valga. La Ley Federal contra la Delincuencia Organizada lo prevé expresamente: a quien colabore eficazmente con el Ministerio Público de la Federación se le puede reducir la pena hasta en dos terceras partes, o hasta la mitad si durante el proceso aporta pruebas suficientes para sentenciar a jefes de la organización (art. 35). Y el Código Nacional permite al Ministerio Público no ejercer la acción penal contra el imputado que «aporte información esencial y eficaz para la persecución de un delito más grave» y se comprometa a declarar en juicio (art. 256, fracción V; art. 257). La figura del testigo colaborador, con beneficio a cambio, existe en ambos lados.",
   "Donde la ley mexicana sí pone candados es en la cautela. La misma ley de delincuencia organizada ordena que el juez valore «prudentemente» la imputación que hagan los participantes en el hecho (art. 40), exige que la información del colaborador esté «sustentada en datos o medios de prueba» para que proceda el beneficio (art. 35 Bis) y, en el caso del artículo 36, que esté «corroborada por otros datos o medios de prueba». Además, el tribunal mexicano debe valorar la prueba de manera libre y lógica, explicar por escrito por qué cree o descarta cada prueba, y solo puede condenar con convicción «más allá de toda duda razonable»; la duda favorece al acusado (arts. 265, 359 y 402 del CNPP).",
   "La conclusión justa es más modesta que la consigna. Ni el Código Nacional ni la ley de delincuencia organizada prohíben condenar con base en testigos colaboradores, ni existe en su texto una regla de «testigo único, testigo nulo»: el juez valora libremente y debe motivar. Saber si un tribunal mexicano habría condenado a García Luna con el mismo material es imposible de afirmar, entre otras cosas porque no conocemos, por documento oficial, la totalidad de lo que se presentó en Brooklyn. Lo que sí se puede decir es que el testimonio de un colaborador que busca beneficio merece examen riguroso en cualquier sistema, y que la ley mexicana lo dice con todas sus letras.",
   "Una nota de presunción de inocencia y de rigor: esta columna no juzga la culpabilidad de nadie más mencionado en aquel juicio. Las afirmaciones que testigos hayan hecho sobre terceros no son, por sí solas, hechos probados, y aquí no se reproducen."
  ],
  "dato_curioso": "La Ley Federal contra la Delincuencia Organizada permite que una sentencia extranjera tenga efectos en México: la existencia de una organización delictiva se tiene por acreditada cuando la declara una sentencia judicial irrevocable de «cualquier tribunal nacional o extranjero», aunque la vinculación de cada imputado con ella se debe probar aparte (art. 41, tercer párrafo).",
  "cifras": [
   {
    "valor": "460 meses",
    "etq": "Pena de prisión impuesta a García Luna por el juez Brian M. Cogan",
    "estado": "oficial",
    "fuente": "Departamento de Justicia de EE.UU., Fiscalía del Distrito Este de Nueva York, comunicado de sentencia (16-10-2024)",
    "url": "https://www.justice.gov/usao-edny/pr/ex-mexican-secretary-public-security-genaro-garcia-luna-sentenced-over-38-years"
   },
   {
    "valor": "≈ 38.3 años",
    "etq": "Equivalencia en años de la pena de prisión",
    "estado": "derivado",
    "fuente": "Operación: 460 meses ÷ 12 = 38.33 años; dato base del comunicado de sentencia del Departamento de Justicia",
    "url": "https://www.justice.gov/usao-edny/pr/ex-mexican-secretary-public-security-genaro-garcia-luna-sentenced-over-38-years"
   },
   {
    "valor": "2 millones de dólares",
    "etq": "Multa impuesta en la sentencia",
    "estado": "oficial",
    "fuente": "Departamento de Justicia de EE.UU., comunicado de sentencia (16-10-2024)",
    "url": "https://www.justice.gov/usao-edny/pr/ex-mexican-secretary-public-security-genaro-garcia-luna-sentenced-over-38-years"
   },
   {
    "valor": "5 cargos",
    "etq": "Delitos por los que el jurado lo declaró culpable tras un juicio de cuatro semanas (febrero de 2023)",
    "estado": "oficial",
    "fuente": "Departamento de Justicia de EE.UU., comunicado de sentencia (16-10-2024)",
    "url": "https://www.justice.gov/usao-edny/pr/ex-mexican-secretary-public-security-genaro-garcia-luna-sentenced-over-38-years"
   },
   {
    "valor": "Hasta 2/3",
    "etq": "Reducción máxima de pena al colaborador investigado que aporta antecedentes contra otros miembros de la delincuencia organizada",
    "estado": "oficial",
    "fuente": "Ley Federal contra la Delincuencia Organizada, art. 35, fracción II (texto vigente, última reforma DOF 28-11-2025)",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/LFCDO.pdf"
   },
   {
    "valor": "Hasta 1/2",
    "etq": "Reducción máxima de pena al imputado que, durante el proceso, aporta pruebas suficientes para sentenciar a mandos de la organización",
    "estado": "oficial",
    "fuente": "Ley Federal contra la Delincuencia Organizada, art. 35, fracción III",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/LFCDO.pdf"
   }
  ],
  "fuentes": [
   {
    "nombre": "Departamento de Justicia de EE.UU., Fiscalía del Distrito Este de Nueva York: «Ex-Mexican Secretary of Public Security Genaro Garcia Luna Sentenced to Over 38 Years' Imprisonment» (16-10-2024). Sitio bloqueado desde nuestro entorno; texto leído en resultados de búsqueda del dominio oficial justice.gov",
    "url": "https://www.justice.gov/usao-edny/pr/ex-mexican-secretary-public-security-genaro-garcia-luna-sentenced-over-38-years"
   },
   {
    "nombre": "Código Nacional de Procedimientos Penales, arts. 256, 257, 259, 265, 356, 359, 360, 372 y 402 (Cámara de Diputados, texto vigente, última reforma DOF 28-11-2025)",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/CNPP.pdf"
   },
   {
    "nombre": "Ley Federal contra la Delincuencia Organizada, arts. 35, 35 Bis, 36, 40 y 41 (Cámara de Diputados, texto vigente, última reforma DOF 28-11-2025)",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/LFCDO.pdf"
   },
   {
    "nombre": "Federal Rules of Evidence, edición del 1 de diciembre de 2024, Regla 601 (Tribunales de EE.UU.). Sitio bloqueado desde nuestro entorno; texto leído en resultados de búsqueda del dominio oficial uscourts.gov",
    "url": "https://www.uscourts.gov/sites/default/files/2025-02/federal-rules-of-evidence-dec-1-2024_0.pdf"
   }
  ],
  "actualizado": "28 de noviembre de 2025"
 },
 {
  "id": "garcia-luna-y-garcia-harfuch",
  "seccion": "Personajes",
  "icono": "🚓",
  "titulo": "García Harfuch y la Policía Federal de García Luna: lo que dicen los documentos",
  "balazo": "El hoy secretario de Seguridad entró a la Policía Federal Preventiva en 2008, cuando Genaro García Luna mandaba en la Secretaría de Seguridad Pública. Eso es lo que consta. Ningún documento oficial que hayamos podido revisar lo acusa de nada ni prueba una amistad.",
  "cuerpo": [
   "Omar García Harfuch y Genaro García Luna coincidieron en la misma institución. Eso está documentado. Que fueran amigos o que García Harfuch tenga «vínculos con el entorno García Luna» no lo está. Esta columna separa una cosa de la otra y cuenta solo lo que dicen los documentos oficiales.",
   "Empecemos por la trayectoria. El perfil del senador Omar Hamid García Harfuch en el Sistema de Información Legislativa de la Secretaría de Gobernación (LXVI Legislatura, electo por mayoría relativa en la Ciudad de México y con licencia por tiempo indefinido desde el 30 de septiembre de 2024) registra estos cargos: en 2008, jefe de departamento de la Policía Federal Preventiva de la Secretaría de Seguridad Pública; de 2011 a 2014, coordinador de la Policía Federal en Guerrero; en 2015, titular de la División de Investigación; en 2016, director en jefe de la Agencia de Investigación Criminal de la PGR; en 2019, jefe general de la Policía de Investigación de la Procuraduría capitalina, y de 2019 a 2023, secretario de Seguridad Ciudadana de la Ciudad de México. Ten presente una advertencia que hace la propia página: la Dirección General de Información Legislativa reúne esos datos de fuentes públicas y el legislador no los ha confirmado.",
   "Hay un detalle que conviene corregir con otro documento. El SIL ubica la División de Investigación en la PGR, pero un artículo de la Policía Federal publicado en gob.mx el 28 de noviembre de 2016 dice que esa división pertenecía a la propia Policía Federal: ahí se anuncia que el comisario general José Antonio Vega Michaca «sucede en el cargo al Licenciado Omar Hamid García Harfuch», a quien se había llamado a otro puesto de la administración pública federal. La designación la hizo el comisionado general Manelich Castilla Craviotto, por instrucción del comisionado nacional de Seguridad, Renato Sales Heredia. Es decir, García Harfuch encabezó esa división ya en el sexenio de Enrique Peña Nieto, cuando García Luna ya había dejado la Secretaría de Seguridad Pública.",
   "Ahora, el otro lado. Según el comunicado de la Fiscalía Federal del Distrito Este de Nueva York sobre la sentencia (Departamento de Justicia de Estados Unidos, 16 de octubre de 2024), García Luna fue secretario de Seguridad Pública de 2006 a 2012 y, desde ese puesto, controlaba la Policía Federal. Un jurado lo declaró culpable en febrero de 2023 de cinco delitos: dirigir una empresa criminal continua, tres conspiraciones para traficar cocaína y falsedad de declaraciones. El juez Brian M. Cogan lo condenó a 460 meses de prisión y a una multa de 2 millones de dólares. Si cruzas esas fechas con el perfil del SIL, los periodos se traslapan: García Harfuch trabajó en la Policía Federal Preventiva desde 2008, y García Luna fue el titular de la Secretaría de la que dependía esa corporación hasta 2012. Es un dato derivado y solo dice que fue su subordinado institucional, igual que los miles de elementos que integraban esa policía. No prueba trato personal ni complicidad.",
   "¿Quiénes sí aparecen señalados junto a García Luna? La acusación sustitutiva que presentó el Departamento de Justicia en 2020 (causa 19-576 [S-1] [BMC]) nombra como coacusados a Luis Cárdenas Palomino y a Ramón Pequeño García: los describe como altos mandos que trabajaron a sus órdenes y que habrían recibido millones de dólares en sobornos del Cártel de Sinaloa. A ellos no los han juzgado en Estados Unidos y, mientras no haya sentencia, se presumen inocentes. En el comunicado de esa acusación ni en el de la sentencia aparece el nombre de García Harfuch, y una búsqueda de «Harfuch» en justice.gov no arroja ningún documento.",
   "En México, la Presidencia informó el 18 de octubre de 2024 que la Fiscalía General de la República tiene al menos tres investigaciones abiertas contra García Luna y que la Unidad de Inteligencia Financiera abrió otra por lavado de dinero. En ese comunicado no se menciona a García Harfuch. Te lo decimos con todas sus letras: en los documentos oficiales que pudimos abrir, ninguna autoridad de México ni de Estados Unidos lo acusa ni lo investiga por su relación con García Luna. La «amistad» y los «vínculos con su entorno» circulan en prensa y en columnas de opinión, pero no en un expediente. Mientras eso no cambie, en esta plataforma esas afirmaciones no se sostienen."
  ],
  "dato_curioso": "Aunque García Harfuch ganó un escaño en el Senado en 2024 y rindió protesta el 29 de agosto de ese año, según el SIL pidió licencia por tiempo indefinido el 30 de septiembre de 2024. Al día siguiente, el 1 de octubre, la Secretaría de Gobernación informó que había asumido la Secretaría de Seguridad y Protección Ciudadana.",
  "cifras": [
   {
    "valor": "2008",
    "etq": "Año en que García Harfuch ingresó como jefe de departamento a la Policía Federal Preventiva de la SSP",
    "estado": "oficial",
    "fuente": "Segob, Sistema de Información Legislativa, perfil del senador Omar Hamid García Harfuch (datos de fuentes públicas no confirmados por el legislador)",
    "url": "https://sil.gobernacion.gob.mx/Librerias/pp_PerfilLegislador.php?Referencia=9228910"
   },
   {
    "valor": "2011–2014",
    "etq": "Periodo como coordinador de la Policía Federal en Guerrero",
    "estado": "oficial",
    "fuente": "Segob, Sistema de Información Legislativa, perfil del senador Omar Hamid García Harfuch",
    "url": "https://sil.gobernacion.gob.mx/Librerias/pp_PerfilLegislador.php?Referencia=9228910"
   },
   {
    "valor": "2006–2012",
    "etq": "Años en que García Luna fue secretario de Seguridad Pública y controló la Policía Federal",
    "estado": "oficial",
    "fuente": "Departamento de Justicia de EE.UU., Fiscalía del Distrito Este de Nueva York, comunicado de sentencia del 16 de octubre de 2024",
    "url": "https://www.justice.gov/usao-edny/pr/ex-mexican-secretary-public-security-genaro-garcia-luna-sentenced-over-38-years"
   },
   {
    "valor": "2008–2012",
    "etq": "Años en que García Harfuch sirvió en la Policía Federal mientras García Luna encabezaba la SSP (cruce del año de ingreso según el SIL con el fin del periodo según el DOJ; precisión anual)",
    "estado": "derivado",
    "fuente": "Cálculo propio con el perfil del SIL (Segob) y el comunicado del DOJ del 16 de octubre de 2024",
    "url": "https://sil.gobernacion.gob.mx/Librerias/pp_PerfilLegislador.php?Referencia=9228910"
   },
   {
    "valor": "460 meses",
    "etq": "Pena de prisión impuesta a García Luna, más una multa de 2 millones de dólares",
    "estado": "oficial",
    "fuente": "Departamento de Justicia de EE.UU., Fiscalía del Distrito Este de Nueva York, 16 de octubre de 2024",
    "url": "https://www.justice.gov/usao-edny/pr/ex-mexican-secretary-public-security-genaro-garcia-luna-sentenced-over-38-years"
   }
  ],
  "fuentes": [
   {
    "nombre": "Segob, Sistema de Información Legislativa: perfil del senador Omar Hamid García Harfuch (LXVI Legislatura)",
    "url": "https://sil.gobernacion.gob.mx/Librerias/pp_PerfilLegislador.php?Referencia=9228910"
   },
   {
    "nombre": "Policía Federal (gob.mx), «Designan nuevo Titular de la División de Investigación de la Policía Federal», 28 de noviembre de 2016",
    "url": "https://www.gob.mx/epn%7Cpoliciafederal/articulos/designan-nuevo-titular-de-la-division-de-investigacion-de-la-policia-federal"
   },
   {
    "nombre": "DOJ, Fiscalía del Distrito Este de Nueva York: sentencia de Genaro García Luna, 16 de octubre de 2024",
    "url": "https://www.justice.gov/usao-edny/pr/ex-mexican-secretary-public-security-genaro-garcia-luna-sentenced-over-38-years"
   },
   {
    "nombre": "DOJ, Fiscalía del Distrito Este de Nueva York: acusación sustitutiva contra García Luna, Cárdenas Palomino y Pequeño García (comunicado)",
    "url": "https://www.justice.gov/usao-edny/pr/former-mexican-secretary-public-security-genaro-garcia-luna-charged-engaging-continuing"
   },
   {
    "nombre": "DOJ: acusación sustitutiva, causa 19-576 (S-1) (BMC) (PDF)",
    "url": "https://www.justice.gov/usao-edny/press-release/file/1299686/dl"
   },
   {
    "nombre": "Presidencia de la República, «Presidenta Claudia Sheinbaum informa investigaciones abiertas contra García Luna en UIF y FGR», 18 de octubre de 2024",
    "url": "https://www.gob.mx/presidencia/prensa/presidenta-claudia-sheinbaum-informa-investigaciones-abiertas-contra-garcia-luna-en-uif-y-fgr"
   },
   {
    "nombre": "Segob, «Asumen cargo titulares de Segob, SSPC y CJEF», 1 de octubre de 2024",
    "url": "https://www.gob.mx/segob/prensa/asumen-cargo-titulares-de-segob-sspc-y-cjef-inicia-segundo-piso-de-la-cuarta-transformacion"
   }
  ],
  "actualizado": "18 de octubre de 2024"
 },
 {
  "id": "abelina-lopez-lo-que-observaron-los-auditores",
  "seccion": "Personajes",
  "icono": "🔎",
  "titulo": "Acapulco bajo Abelina López: lo que observaron la ASF y la Auditoría de Guerrero",
  "balazo": "Entre 2022 y 2024, la Auditoría Superior de la Federación dejó más de 237 millones de pesos por aclarar al municipio, y la mayor parte corresponde a 2024.",
  "cuerpo": [
   "Abelina López Rodríguez ha encabezado el Ayuntamiento de Acapulco de Juárez. Aquí reunimos lo que dicen los informes oficiales de las dos auditorías que revisan sus cuentas. Antes de leer, ten presente algo: cada observación se dirige al municipio como ente fiscalizado y no a una persona. Un monto «por aclarar» o un pliego de observaciones es una presunción que el municipio todavía puede solventar con documentos. No prueba un desvío.",
   "Cuenta Pública 2022. En la auditoría 1003 (2022-D-12001-19-1003-2023), la ASF revisó el 100 % de los 763,756.5 miles de pesos del Fondo de Aportaciones para la Infraestructura Social Municipal (FISMDF). Emitió dos pliegos de observaciones. Uno es por 3,890,000.00 pesos, pagados por estudios y servicios profesionales que no corresponden a los rubros de la Ley de Coordinación Fiscal. El otro es por 23,248,143.48 pesos, pagados en dos compras de cemento, arena y grava sin proyecto, bitácora, padrón de beneficiarios ni actas de entrega. Al cierre del informe quedaban 27,138,143.48 pesos pendientes de aclaración. Las otras dos auditorías de ese año, a Participaciones (1004 y 1005), no dejaron montos por aclarar.",
   "Cuenta Pública 2023. Según los índices de informes que publicó la ASF, la única auditoría federal al municipio en ese año fue la 1103 (2023-D-12001-19-1103-2024), sobre Participaciones Federales, con un universo de 1,122,158.6 miles de pesos. Dejó una solicitud de aclaración por 3,721,419.01 pesos por falta de documentación de plazas, sueldos y prestaciones. Ese año la ASF no auditó el FAISMUN de Acapulco.",
   "Cuenta Pública 2024. La auditoría integral 1084 (2024-D-12001-19-1084-2025) revisó 1,348,595.3 miles de pesos de Participaciones, FORTAMUN y FAISMUN, y determinó 206,217,857.91 pesos pendientes por aclarar. El monto se compone de dos pliegos de observaciones y dos solicitudes de aclaración. El primer pliego, por 127,668,501.41 pesos, es por contratos sin actas de entrega-recepción ni evidencia de que se recibieron los bienes o servicios. El segundo, por 58,532,119.10 pesos, es por obras pagadas con FAISMUN y FORTAMUN sin estimaciones, fotografías ni pruebas de laboratorio. Las dos solicitudes de aclaración suman 6,250,598.82 y 13,766,638.58 pesos, por pagos de nómina por encima del tabulador. En su dictamen, la ASF concluye que el municipio «no realizó una gestión eficiente» de esos recursos. Un dato a considerar: la sentencia de la Corte sobre la queja 4/2025-CA consigna que el Congreso local autorizó a la presidenta municipal una licencia a partir del 20 de abril de 2024. El informe abarca todo el ejercicio y no separa periodos.",
   "Sobre 2021: la ASF revisó ese ejercicio completo. En la auditoría 968 (FISMDF) dejó 20,105,931.57 pesos pendientes de aclaración y en la 967 (contratos con gasto federalizado), 64,150,345.80 pesos por aclarar. Esos informes no distinguen entre la administración saliente y la entrante, así que no se pueden atribuir completos al periodo que aquí revisamos.",
   "La Auditoría Superior del Estado de Guerrero (ASE) publicó su propio resumen de las cuentas 2021 a 2023. Ahí acota sus cifras de 2021 al periodo de octubre a diciembre: 82,795,367.33 pesos observados en gestión financiera y 87,623,936.85 pesos en FAISMUN. Para 2022 observa 36,371,714.06 pesos y para 2023, 58,381,460.99 pesos, ambos en gestión financiera. La cifra mayor de ese resumen son los 898,633,453.00 pesos del FAISMUN 2023, el 100 % de lo que recibió el municipio de ese fondo. La ASE los observó porque, según dice, el municipio no entregó los expedientes de 511 obras y 2 acciones. Ese informe ya no tiene validez: la Suprema Corte lo invalidó en la controversia constitucional 174/2025, y hoy la propia ASE lo publica con esa leyenda.",
   "Todas estas cifras son las que constaban al emitirse cada informe. En la etapa de seguimiento, el municipio puede solventarlas total o parcialmente, o la ASF puede convertirlas en otras acciones."
  ],
  "dato_curioso": "En la auditoría de 2024, la ASF encontró que el municipio retuvo 83,420.5 miles de pesos a 3,359 trabajadores por cuotas al ISSSPEG, cuota sindical y cooperación mutualista, sin evidencia de haberlos entregado a esas instituciones.",
  "cifras": [
   {
    "valor": "$27,138,143.48",
    "etq": "Pendiente de aclaración, FISMDF 2022 (auditoría 1003)",
    "estado": "oficial",
    "fuente": "ASF, Informe Individual CP 2022",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2022c/Documentos/Auditorias/2022_1003_a.pdf"
   },
   {
    "valor": "$3,721,419.01",
    "etq": "Por aclarar, Participaciones 2023 (auditoría 1103)",
    "estado": "oficial",
    "fuente": "ASF, Informe Individual CP 2023",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2023c/Documentos/Auditorias/2023_1103_a.pdf"
   },
   {
    "valor": "$206,217,857.91",
    "etq": "Por aclarar, gasto federalizado 2024 (auditoría 1084)",
    "estado": "oficial",
    "fuente": "ASF, Informe Individual CP 2024",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2024c/Documentos/Auditorias/2024_1084_a.pdf"
   },
   {
    "valor": "$237,077,420.40",
    "etq": "Suma por aclarar de las cuentas 2022 a 2024 (27,138,143.48 + 3,721,419.01 + 206,217,857.91)",
    "estado": "derivado",
    "fuente": "ASF, auditorías 1003, 1103 y 1084",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2024c/Documentos/Auditorias/2024_1084_a.pdf"
   },
   {
    "valor": "$898,633,453.00",
    "etq": "Pliego de la ASE por FAISMUN 2023, invalidado por la SCJN",
    "estado": "oficial",
    "fuente": "ASE Guerrero, informe 2023-C-CIF-01-002-2024",
    "url": "https://www.auditoriaguerrero.gob.mx/PDFs/entfisc/2024/informes/cp2023/3erbloque/001_Acapulco_CIF_2023_C_CIF_01_002_2024.pdf"
   }
  ],
  "fuentes": [
   {
    "nombre": "ASF, Informe Individual, auditoría 1003 FISMDF, Cuenta Pública 2022",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2022c/Documentos/Auditorias/2022_1003_a.pdf"
   },
   {
    "nombre": "ASF, Informe Individual, auditoría 1004 Participaciones, Cuenta Pública 2022",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2022c/Documentos/Auditorias/2022_1004_a.pdf"
   },
   {
    "nombre": "ASF, Informe Individual, auditoría 1005 Participaciones (art. 3-B LCF), Cuenta Pública 2022",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2022b/Documentos/Auditorias/2022_1005_a.pdf"
   },
   {
    "nombre": "ASF, Informe Individual, auditoría 1103 Participaciones, Cuenta Pública 2023",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2023c/Documentos/Auditorias/2023_1103_a.pdf"
   },
   {
    "nombre": "ASF, Informe Individual, auditoría integral 1084, Cuenta Pública 2024",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2024c/Documentos/Auditorias/2024_1084_a.pdf"
   },
   {
    "nombre": "ASF, Informe Individual, auditoría 968 FISMDF, Cuenta Pública 2021",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2021b/Documentos/Auditorias/2021_0968_a.pdf"
   },
   {
    "nombre": "ASF, Informe Individual, auditoría 967 Contratos con gasto federalizado, Cuenta Pública 2021",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2021c/Documentos/Auditorias/2021_0967_a.pdf"
   },
   {
    "nombre": "ASE Guerrero, Resumen de auditorías practicadas al Municipio de Acapulco de Juárez, Cuentas Públicas 2021, 2022 y 2023",
    "url": "https://www.auditoriaguerrero.gob.mx/PDFs/entfisc/2024/informes/cp2023/3erbloque/ASE_resumen_de_auditorias_practicadas_al_municipio_de_acapulco_de_juarez.pdf"
   },
   {
    "nombre": "ASE Guerrero, Informe Individual 2023-C-CIF-01-002-2024 (publicado con la leyenda de invalidez de la SCJN)",
    "url": "https://www.auditoriaguerrero.gob.mx/PDFs/entfisc/2024/informes/cp2023/3erbloque/001_Acapulco_CIF_2023_C_CIF_01_002_2024.pdf"
   }
  ],
  "actualizado": "6 de julio de 2026"
 },
 {
  "id": "abelina-lopez-corte-invalida-auditoria-estatal",
  "seccion": "Personajes",
  "icono": "⚖️",
  "titulo": "La Corte anuló la auditoría estatal de 898 millones a Acapulco: qué decidió y qué no",
  "balazo": "La Corte resolvió quién tiene facultades para auditar ese dinero; no decidió si se gastó bien o mal.",
  "cuerpo": [
   "En 2024, la Auditoría Superior del Estado de Guerrero (ASE) abrió la auditoría 2023-C-CIF-01-002-2024 para revisar cómo usó Acapulco el Fondo de Aportaciones para la Infraestructura Social Municipal (FAISMUN) de 2023. El municipio no entregó la información que se le pidió. La ASE emitió entonces un pliego de observaciones por 898,633,453.00 pesos, todo lo que el municipio recibió de ese fondo, y promovió responsabilidades administrativas. Además, abrió un procedimiento por «desacato» contra la presidenta municipal por no responder al requerimiento.",
   "El 27 de mayo de 2025, el síndico del municipio presentó ante la Suprema Corte la controversia constitucional 174/2025. Su argumento fue que el FAISMUN es dinero federal y que una auditoría estatal no tiene facultades para revisarlo. El 25 de junio de 2025, el ministro instructor concedió la suspensión: la ASE debía detener la fiscalización y cualquier acto derivado de ella.",
   "Un día después, el 26 de junio de 2025, un actuario de la ASE fijó en la puerta del Ayuntamiento la notificación del procedimiento de responsabilidad contra la presidenta municipal. El municipio presentó un recurso de queja. El 10 de marzo de 2026, el Pleno lo resolvió por unanimidad de nueve votos (queja 4/2025-CA). Declaró fundada la queja y ordenó a la ASE dejar sin efecto esa notificación y suspender lo que derivara de ella. No sancionó a la ASE ni al Congreso, porque ninguno de los dos conocía oficialmente la suspensión el día de la notificación.",
   "El 6 de julio de 2026, el Pleno resolvió el fondo por unanimidad, con el proyecto del ministro Arístides Rodrigo Guerrero García. La controversia fue parcialmente procedente y fundada, se sobreseyó en una parte, y la Corte declaró la invalidez del informe individual de auditoría y del oficio ASE-1380-2025. La razón es de competencia: conforme a los artículos 74, fracción VI, y 79 de la Constitución, la fiscalización directa de los recursos federales que ejercen los municipios corresponde solo a la Auditoría Superior de la Federación. La Corte siguió el precedente de la controversia 248/2025.",
   "Lo que la Corte no hizo también importa. El ponente dijo en la sesión que el fallo no exime al municipio de ninguna fiscalización ni se pronuncia sobre el manejo del dinero. Según la versión taquigráfica, el proyecto deja a salvo las facultades de los órganos de fiscalización y de los congresos, locales y federales, para pronunciarse sobre la cuenta pública 2023 del municipio. El ministro Irving Espinosa Betanzo añadió que la invalidez «no prejuzga sobre la existencia o inexistencia de irregularidades» y que las autoridades competentes conservan sus facultades mientras las posibles conductas no prescriban.",
   "Al momento de escribir esto, la sentencia de fondo (el engrose) no aparecía publicada en el sitio de la Corte. Esta columna se apoya en la versión taquigráfica oficial de la sesión, en la sentencia de la queja y en el propio informe de la ASE, que hoy se publica con la leyenda de su invalidez."
  ],
  "dato_curioso": "En la Cuenta Pública 2023, la ASF auditó a Acapulco solo en Participaciones (auditoría 1103), no en el FAISMUN, que es el fondo cuya auditoría estatal anuló la Corte.",
  "cifras": [
   {
    "valor": "$898,633,453.00",
    "etq": "Pliego de observaciones de la ASE sobre el FAISMUN 2023, invalidado",
    "estado": "oficial",
    "fuente": "ASE Guerrero, informe 2023-C-CIF-01-002-2024",
    "url": "https://www.auditoriaguerrero.gob.mx/PDFs/entfisc/2024/informes/cp2023/3erbloque/001_Acapulco_CIF_2023_C_CIF_01_002_2024.pdf"
   },
   {
    "valor": "Unanimidad",
    "etq": "Votación del Pleno de la SCJN en la CC 174/2025, 6 de julio de 2026",
    "estado": "oficial",
    "fuente": "SCJN, versión taquigráfica",
    "url": "https://www.scjn.gob.mx/sites/default/files/versiones-taquigraficas/documento/2026-07-07/6%20de%20julio%20de%202026%20-%20Versi%C3%B3n%20definitiva%202._0.pdf"
   },
   {
    "valor": "9 votos",
    "etq": "Unanimidad en la queja 4/2025-CA, 10 de marzo de 2026",
    "estado": "oficial",
    "fuente": "SCJN, sentencia de la queja",
    "url": "https://www2.scjn.gob.mx/juridica/engroses/3/2025/31/2_353218_7619_firmado.pdf"
   }
  ],
  "fuentes": [
   {
    "nombre": "SCJN, versión taquigráfica de la sesión pública del Pleno del 6 de julio de 2026 (CC 174/2025, pp. 88-98)",
    "url": "https://www.scjn.gob.mx/sites/default/files/versiones-taquigraficas/documento/2026-07-07/6%20de%20julio%20de%202026%20-%20Versi%C3%B3n%20definitiva%202._0.pdf"
   },
   {
    "nombre": "SCJN, sentencia del recurso de queja 4/2025-CA, derivado de la CC 174/2025, 10 de marzo de 2026",
    "url": "https://www2.scjn.gob.mx/juridica/engroses/3/2025/31/2_353218_7619_firmado.pdf"
   },
   {
    "nombre": "ASE Guerrero, Informe Individual 2023-C-CIF-01-002-2024, Cuenta Pública 2023 de Acapulco de Juárez",
    "url": "https://www.auditoriaguerrero.gob.mx/PDFs/entfisc/2024/informes/cp2023/3erbloque/001_Acapulco_CIF_2023_C_CIF_01_002_2024.pdf"
   },
   {
    "nombre": "ASF, índice de informes individuales, Cuenta Pública 2023, tercera entrega",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2023c/index.html"
   }
  ],
  "actualizado": "6 de julio de 2026"
 },
 {
  "id": "santa-anna-mesilla-y-perros",
  "seccion": "Historia",
  "icono": "🐕",
  "titulo": "Santa Anna: diez millones por La Mesilla y un peso al mes por cada perro",
  "balazo": "En su último gobierno, el de la Alteza Serenísima, el erario se llenó con la venta de territorio y con impuestos a puertas, ventanas y mascotas.",
  "cuerpo": [
   "Antonio López de Santa Anna ocupó la presidencia de la República en seis ocasiones, según el Instituto Nacional de Estudios Históricos de las Revoluciones de México (INEHRM). La última fue de 1853 a 1855: desembarcó en Veracruz el 1 de abril de 1853 y tomó posesión el 20 de ese mes. El 1 de diciembre de 1853, el Consejo de Estado le otorgó el título de Alteza Serenísima, el grado de Capitán General y un sueldo de 60 000 pesos anuales.",
   "El 30 de diciembre de 1853, James Gadsden y Manuel Díez de Bonilla firmaron el Tratado de La Mesilla. Por él, México cedió ese territorio a cambio de 10 millones de pesos. El Senado de Estados Unidos lo aprobó el 26 de abril de 1854 y México lo ratificó el 31 de mayo de ese año. Si buscas la superficie exacta, verás que las fuentes oficiales no coinciden, por eso aquí no la damos.",
   "Para sostener al gobierno se cobraron contribuciones que hoy suenan insólitas. El INEHRM registra que se exigió un peso mensual por cada perro, con multas de hasta 20 pesos y la muerte del animal si no se pagaba, y que uno de los impuestos más recordados fue el que se cobraba por cada puerta o ventana. El Plan de Ayutla, proclamado el 1 de marzo de 1854, terminó con ese gobierno: Santa Anna renunció a la presidencia en Perote el 12 de agosto de 1855 y se embarcó en Veracruz el 18 de agosto.",
   "Quince años antes, otra cuenta pendiente con el extranjero le había costado una pierna. En la llamada Guerra de los Pasteles, Francia reclamaba más de seiscientos mil pesos, entre ellos los de un pastelero francés de apellido Remontel que decía que el gobierno le debía más de sesenta mil. Durante el bombardeo de Veracruz, Santa Anna perdió la pierna izquierda. El 9 de marzo de 1839 se firmó la paz, y México aceptó pagar lo que pedían los franceses, con un adelanto de doscientos mil pesos, según el material de la Secretaría de Educación Pública."
  ],
  "dato_curioso": "En 1853 y 1854, tener perro te costaba un peso al mes; si no pagabas, la multa llegaba a 20 pesos y el animal era sacrificado (INEHRM).",
  "cifras": [
   {
    "valor": "10 000 000 de pesos",
    "etq": "Precio que Estados Unidos pagó a México por La Mesilla (Tratado del 30 de diciembre de 1853)",
    "estado": "oficial",
    "fuente": "INEHRM, La Dictadura. El último gobierno de Santa Anna",
    "url": "https://www.inehrm.gob.mx/es/inehrm/La_Dictaduta_El_ultimo_Gobierno_de_Antonio_Lopez_de_Santa_Anna"
   },
   {
    "valor": "60 000 pesos anuales",
    "etq": "Sueldo que el Consejo de Estado otorgó a Santa Anna el 1 de diciembre de 1853",
    "estado": "oficial",
    "fuente": "INEHRM, La Dictadura",
    "url": "https://www.inehrm.gob.mx/es/inehrm/La_Dictaduta_El_ultimo_Gobierno_de_Antonio_Lopez_de_Santa_Anna"
   },
   {
    "valor": "1 peso al mes",
    "etq": "Impuesto por cada perro; multa de hasta 20 pesos por no pagarlo",
    "estado": "oficial",
    "fuente": "INEHRM, La Dictadura",
    "url": "https://www.inehrm.gob.mx/es/inehrm/La_Dictaduta_El_ultimo_Gobierno_de_Antonio_Lopez_de_Santa_Anna"
   },
   {
    "valor": "más de 600 000 pesos",
    "etq": "Reclamación de Francia que llevó a la Guerra de los Pasteles (1838-1839); adelanto pactado: 200 000 pesos",
    "estado": "oficial",
    "fuente": "SEP, «Por culpa de un pastelero»",
    "url": "https://nuevaescuelamexicana.sep.gob.mx/contenido/coleccion/5632-por-culpa-de-un-pastelero/"
   }
  ],
  "fuentes": [
   {
    "nombre": "Raúl González Lezama, «La Dictadura. El último gobierno de Antonio López de Santa Anna», INEHRM",
    "url": "https://www.inehrm.gob.mx/es/inehrm/La_Dictaduta_El_ultimo_Gobierno_de_Antonio_Lopez_de_Santa_Anna"
   },
   {
    "nombre": "«Por culpa de un pastelero», Nueva Escuela Mexicana Digital, Secretaría de Educación Pública",
    "url": "https://nuevaescuelamexicana.sep.gob.mx/contenido/coleccion/5632-por-culpa-de-un-pastelero/"
   }
  ],
  "actualizado": "9 de octubre de 2026"
 },
 {
  "id": "partida-secreta",
  "seccion": "Hechos",
  "icono": "🗝️",
  "titulo": "La partida secreta: 104 años en la Constitución y una reforma que la prohibió en 2021",
  "balazo": "Hasta mayo de 2021, la Constitución permitía que el Presupuesto de Egresos tuviera partidas secretas; hoy las prohíbe con una sola línea.",
  "cuerpo": [
   "El texto que estuvo vigente hasta 2021 en la fracción IV del artículo 74 decía: «No podrá haber otras partidas secretas, fuera de las que se consideren necesarias, con ese carácter, en el mismo presupuesto; las que emplearán los secretarios por acuerdo escrito del Presidente de la República». Así lo transcribe el cuadro comparativo del dictamen del Senado, que lo pone al lado del texto nuevo.",
   "Según la exposición de motivos de la iniciativa que presentó el diputado Pablo Gómez Álvarez (Gaceta Parlamentaria, 20 de noviembre de 2018), la figura entró a la Constitución el 14 de enero de 1917, en el artículo 65, y pasó a la fracción IV del artículo 74 el 6 de diciembre de 1977. La misma iniciativa afirma que en 1994, 1995 y 1996 la partida secreta se autorizó en 650 millones de pesos por año y que se canceló en el presupuesto de 1998, aprobado en diciembre de 1997.",
   "La reforma pasó sin un solo voto en contra: 437 a favor en la Cámara de Diputados (25 de abril de 2019) y 94 a favor en el Senado (11 de marzo de 2021). Luego la aprobaron 18 legislaturas locales y el decreto se publicó en el Diario Oficial de la Federación el 17 de mayo de 2021. Desde entonces, el párrafo cuarto de la fracción IV del artículo 74 dice: «No podrá haber partidas secretas en el Presupuesto de Egresos de la Federación»."
  ],
  "dato_curioso": "Entre el voto de la Cámara de Diputados y el del Senado pasaron 686 días, casi dos años, para una reforma que nadie votó en contra.",
  "cifras": [
   {
    "valor": "650 millones de pesos por año (1994, 1995 y 1996)",
    "etq": "Monto de la partida secreta según la exposición de motivos de la iniciativa (cifra citada por el legislador, no tomada del PEF de esos años)",
    "estado": "oficial",
    "fuente": "Iniciativa del Dip. Pablo Gómez Álvarez, Gaceta Parlamentaria 20-11-2018",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/proceso/docleg/64/250_DOF_17may21.pdf"
   },
   {
    "valor": "437 votos a favor, 0 en contra",
    "etq": "Votación en la Cámara de Diputados, 25 de abril de 2019",
    "estado": "oficial",
    "fuente": "Proceso legislativo del decreto DOF 17-05-2021",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/proceso/docleg/64/250_DOF_17may21.pdf"
   },
   {
    "valor": "94 votos a favor, 0 en contra",
    "etq": "Votación en el Senado, 11 de marzo de 2021",
    "estado": "oficial",
    "fuente": "Proceso legislativo del decreto DOF 17-05-2021",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/proceso/docleg/64/250_DOF_17may21.pdf"
   },
   {
    "valor": "686 días",
    "etq": "Entre la votación en Diputados (25-04-2019) y la del Senado (11-03-2021); operación: diferencia de fechas",
    "estado": "derivado",
    "fuente": "Proceso legislativo del decreto DOF 17-05-2021",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/proceso/docleg/64/250_DOF_17may21.pdf"
   }
  ],
  "fuentes": [
   {
    "nombre": "Decreto que reforma el artículo 74 de la Constitución, en materia de partidas secretas, DOF 17-05-2021 (Cámara de Diputados)",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/ref/dof/CPEUM_ref_250_17may21.pdf"
   },
   {
    "nombre": "Proceso legislativo del decreto DOF 17-05-2021: iniciativa, dictámenes, votaciones y declaratoria (Cámara de Diputados)",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/proceso/docleg/64/250_DOF_17may21.pdf"
   },
   {
    "nombre": "Constitución Política de los Estados Unidos Mexicanos, texto vigente (Cámara de Diputados)",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf"
   }
  ],
  "actualizado": "2 de junio de 2026"
 },
 {
  "id": "ovalle-segalmex-asf-fgr",
  "seccion": "Personajes",
  "icono": "🌽",
  "titulo": "Segalmex: lo que la ASF dejó por aclarar y lo que dicen la FGR y el gobierno",
  "balazo": "Dos auditorías a Segalmex suman más de 9 mil millones de pesos por aclarar; la FGR ha procesado a exfuncionarios y su exdirector no aparece en los comunicados.",
  "cuerpo": [
   "Ignacio Ovalle Fernández dirigió Seguridad Alimentaria Mexicana (Segalmex) hasta el 19 de abril de 2022. Ese día, el gobierno informó que Leonel Cota Montaño lo sustituía y que Ovalle pasaba a coordinar el INAFED, en Gobernación. Las auditorías de la ASF revisan a la institución y no nombran a su titular. Para la Cuenta Pública 2019, la ASF dejó 3,396,253,452.70 pesos pendientes por aclarar en la auditoría 283-DE a Segalmex; para la 2020, 5,640,592,176.10 pesos en la auditoría 327-DE. Entre otras cosas, en 2019 la ASF no pudo constatar la existencia física de maíz registrado por 1,496,246.2 miles de pesos.",
   "En la Cuenta Pública 2020, la ASF observó que Segalmex compró en junio de 2020 cien mil títulos de certificados bursátiles fiduciarios privados por 100,000.0 miles de pesos. También vio que Liconsa compró certificados de ese tipo por 850,000.0 miles de pesos entre 2019 y 2020, en contra de los lineamientos para el manejo de las disponibilidades financieras de las paraestatales. El 5 de septiembre de 2024, Gobernación, Hacienda y la Función Pública informaron que se recuperaron 955 millones de pesos invertidos de forma ilícita en bonos bursátiles.",
   "En ese mismo comunicado, la Función Pública precisó que de 9,500 millones de pesos observados en 2019 y 2020 se aclararon 4,700 millones y que las observaciones de auditoría no son, por sí mismas, desvío. La Procuraduría Fiscal reportó 156 denuncias, 47 personas investigadas con orden de aprehensión y 26 vinculadas a proceso. La FGR, por ejemplo, obtuvo en 2022 la vinculación a proceso de René «G», extitular de Administración y Finanzas de Liconsa. En los documentos oficiales consultados no aparece ninguna imputación contra Ovalle. Eso no prueba que no haya una investigación: solo que no se ha hecho pública."
  ],
  "dato_curioso": "En 2021, la propia Segalmex denunció ante la FGR gastos de operación sin comprobar por 29,495.7 miles de pesos, y la FGR determinó el «no ejercicio de la acción penal», según la ASF.",
  "cifras": [
   {
    "valor": "3,396,253,452.70 pesos",
    "etq": "Pendiente por aclarar, auditoría 283-DE a Segalmex, Cuenta Pública 2019",
    "estado": "oficial",
    "fuente": "ASF, auditoría 283-DE, Cuenta Pública 2019",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2019c/Documentos/Auditorias/2019_0283_a.pdf"
   },
   {
    "valor": "5,640,592,176.10 pesos",
    "etq": "Pendiente por aclarar, auditoría 327-DE a Segalmex, Cuenta Pública 2020",
    "estado": "oficial",
    "fuente": "ASF, auditoría 327-DE, Cuenta Pública 2020",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2020c/Documentos/Auditorias/2020_0327_a.pdf"
   },
   {
    "valor": "9,036,845,628.80 pesos",
    "etq": "Suma de lo pendiente por aclarar en las dos auditorías de gestión financiera a Segalmex (3,396,253,452.70 + 5,640,592,176.10)",
    "estado": "derivado",
    "fuente": "ASF, auditorías 283-DE (CP 2019) y 327-DE (CP 2020)",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2020c/Documentos/Auditorias/2020_0327_a.pdf"
   },
   {
    "valor": "1,496,246.2 miles de pesos",
    "etq": "Inventario de maíz cuya existencia física la ASF no pudo constatar (31 de diciembre de 2019)",
    "estado": "oficial",
    "fuente": "ASF, auditoría 283-DE, Cuenta Pública 2019",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2019c/Documentos/Auditorias/2019_0283_a.pdf"
   },
   {
    "valor": "950,000.0 miles de pesos",
    "etq": "Certificados bursátiles privados comprados por Segalmex (100,000.0) y Liconsa (850,000.0), según la ASF",
    "estado": "derivado",
    "fuente": "ASF, auditorías 327-DE y 330-DE, Cuenta Pública 2020",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2020c/Documentos/Auditorias/2020_0330_a.pdf"
   },
   {
    "valor": "955 millones de pesos",
    "etq": "Recursos recuperados de inversiones en bonos bursátiles, según el gobierno federal",
    "estado": "oficial",
    "fuente": "Segob, SHCP y SFP, comunicado del 5 de septiembre de 2024",
    "url": "https://www.gob.mx/segob/prensa/informan-segob-shcp-y-sfp-sobre-el-caso-segalmex?idiom=es"
   },
   {
    "valor": "156 denuncias, 47 investigados, 26 vinculados a proceso",
    "etq": "Saldo penal del caso Segalmex reportado por la Procuraduría Fiscal",
    "estado": "oficial",
    "fuente": "Segob, SHCP y SFP, comunicado del 5 de septiembre de 2024",
    "url": "https://www.gob.mx/segob/prensa/informan-segob-shcp-y-sfp-sobre-el-caso-segalmex?idiom=es"
   }
  ],
  "fuentes": [
   {
    "nombre": "ASF, Cuenta Pública 2019, auditoría de cumplimiento 2019-1-08JBP-19-0283-2020 (283-DE), Gestión Financiera de Segalmex; dictamen del 28 de enero de 2021",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2019c/Documentos/Auditorias/2019_0283_a.pdf"
   },
   {
    "nombre": "ASF, Cuenta Pública 2020, auditoría de cumplimiento 2020-1-08JBP-19-0327-2021 (327-DE), Gestión Financiera de Segalmex; dictamen del 28 de enero de 2022",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2020c/Documentos/Auditorias/2020_0327_a.pdf"
   },
   {
    "nombre": "ASF, Cuenta Pública 2020, auditoría de cumplimiento forense 2020-2-08VST-23-0330-2021, Gestión Financiera de Liconsa",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2020c/Documentos/Auditorias/2020_0330_a.pdf"
   },
   {
    "nombre": "Segalmex, «Presidente de la República designa nuevos nombramientos», 19 de abril de 2022",
    "url": "https://www.gob.mx/segalmex/articulos/presidente-de-la-republica-designa-nuevos-nombramientos-299592?idiom=es"
   },
   {
    "nombre": "Segob, SHCP y SFP, «Informan Segob, SHCP y SFP sobre el caso Segalmex», 5 de septiembre de 2024",
    "url": "https://www.gob.mx/segob/prensa/informan-segob-shcp-y-sfp-sobre-el-caso-segalmex?idiom=es"
   },
   {
    "nombre": "FGR, Comunicado 530/22, «FGR obtiene vinculación a proceso por el caso SEGALMEX», 1 de noviembre de 2022",
    "url": "https://www.gob.mx/fgr/prensa/comunicado-fgr-530-22-fgr-obtiene-vinculacion-a-proceso-por-el-caso-segalmex"
   }
  ],
  "actualizado": "5 de septiembre de 2024"
 },
 {
  "id": "juarez-suspension-de-pagos-1861",
  "seccion": "Historia",
  "icono": "⚓",
  "titulo": "1861: el año en que México dejó de pagar y Europa mandó barcos",
  "balazo": "La ley del 17 de julio de 1861 suspendió el pago de la deuda externa; tres meses después, España, Francia e Inglaterra firmaron en Londres un acuerdo para cobrar.",
  "cuerpo": [
   "En mayo de 1861 el erario estaba en bancarrota. El INEHRM relata que el 7 de mayo, mientras la Cámara de Diputados revisaba las credenciales de Sebastián Lerdo de Tejada, la sesión iba a suspenderse porque anochecía y no había dinero para alumbrar el recinto; los diputados pusieron sobre la mesa el dinero que traían en los bolsillos para poder seguir. Ese mismo mes, el Congreso aceptó suspender los pagos de la deuda interior, pero no los de la externa (decreto publicado el 29 de mayo).",
   "El 17 de julio de 1861 se promulgó un nuevo decreto: la moratoria en los pagos de la deuda externa. El representante inglés, Charles Wyke, y el francés, Alphonse Dubois de Saligny, exigieron que se derogara y fijaron como plazo el 25 de julio a las 4 de la tarde. Al no obtener respuesta, arriaron las banderas de sus legaciones, señal de que rompían relaciones.",
   "El 31 de octubre de 1861, Inglaterra, Francia y España firmaron la Convención de Londres. La Secretaría de la Defensa Nacional explica que su objetivo era ocupar las principales fortalezas de la costa mexicana para captar los ingresos de las aduanas y cobrar la deuda. Juárez buscó un arreglo por separado con Inglaterra; el Congreso rechazó el acuerdo firmado el 21 de noviembre por considerarlo demasiado oneroso, y dos días después el presidente derogó el decreto del 17 de julio. Ya era tarde: la escuadra española llegó a Veracruz el 8 de diciembre de 1861, los ingleses el 6 de enero de 1862 y los franceses al día siguiente.",
   "Lo que cada potencia pedía muestra el tamaño de la cuenta. Según el INEHRM, Inglaterra exigía 40% de los ingresos de las aduanas para una deuda de cincuenta millones de pesos, más 750 000 pesos sustraídos durante la Guerra de Reforma. Francia reclamaba doce millones de pesos por los bonos que el gobierno de Miguel Miramón había contratado con la casa Jecker, que no había entregado más de 750 000 pesos. España e Inglaterra se retiraron tras los Tratados de La Soledad (19 de febrero de 1862); Francia siguió adelante con la intervención."
  ],
  "dato_curioso": "El 7 de mayo de 1861 la Cámara de Diputados no tenía con qué pagar la luz: los diputados juntaron el dinero de sus bolsillos para seguir sesionando (INEHRM).",
  "cifras": [
   {
    "valor": "50 000 000 de pesos",
    "etq": "Deuda con los británicos según la reclamación inglesa, más 750 000 pesos sustraídos en la Guerra de Reforma",
    "estado": "oficial",
    "fuente": "INEHRM, Cinco de mayo. Las razones de la victoria",
    "url": "https://www.inehrm.gob.mx/work/models/inehrm/Resource/440/1/images/5mayo.pdf"
   },
   {
    "valor": "12 000 000 de pesos",
    "etq": "Reclamación francesa por los bonos Jecker; la casa Jecker había entregado no más de 750 000 pesos",
    "estado": "oficial",
    "fuente": "INEHRM, Cinco de mayo. Las razones de la victoria",
    "url": "https://www.inehrm.gob.mx/work/models/inehrm/Resource/440/1/images/5mayo.pdf"
   },
   {
    "valor": "40%",
    "etq": "Parte de los ingresos de las aduanas que Inglaterra exigía para cobrar su deuda",
    "estado": "oficial",
    "fuente": "INEHRM, Cinco de mayo. Las razones de la victoria",
    "url": "https://www.inehrm.gob.mx/work/models/inehrm/Resource/440/1/images/5mayo.pdf"
   }
  ],
  "fuentes": [
   {
    "nombre": "Raúl González Lezama, Cinco de mayo. Las razones de la victoria, INEHRM, 2012",
    "url": "https://www.inehrm.gob.mx/work/models/inehrm/Resource/440/1/images/5mayo.pdf"
   },
   {
    "nombre": "«La Intervención Francesa», Secretaría de la Defensa Nacional",
    "url": "https://www.gob.mx/defensa/documentos/la-intervencion-francesa"
   },
   {
    "nombre": "«#AGNRecuerda el 150 aniversario del triunfo de la República liberal», Archivo General de la Nación, 19 de junio de 2017",
    "url": "https://www.gob.mx/agn/articulos/agnrecuerda-el-150-aniversario-del-triunfo-de-la-republica-liberal"
   }
  ],
  "actualizado": "9 de octubre de 2026"
 },
 {
  "id": "fobaproa-ipab",
  "seccion": "Hechos",
  "icono": "🏦",
  "titulo": "Fobaproa-IPAB: la ley de 1999 y los 35,553 millones que el PEF 2026 le reserva",
  "balazo": "La Ley de Protección al Ahorro Bancario cumple 27 años y su costo sigue apareciendo, año con año, en un ramo propio del Presupuesto de Egresos.",
  "cuerpo": [
   "La Ley de Protección al Ahorro Bancario se publicó en el Diario Oficial de la Federación el 19 de enero de 1999. Su artículo 2o. creó el Instituto para la Protección al Ahorro Bancario (IPAB), un organismo descentralizado, y su artículo 11 fija hoy el seguro de depósitos: el IPAB paga hasta 400 mil unidades de inversión (UDIS) por persona, física o moral, en una misma institución.",
   "Los artículos transitorios ordenaron extinguir el fideicomiso del artículo 122 de la Ley de Instituciones de Crédito (el Fobaproa); el IPAB asumió las operaciones de saneamiento. Pero el Octavo transitorio, fracción III, dejó dicho: «No se aprueba la solicitud de consolidar a la deuda pública las obligaciones contraídas por los Fondos señalados». Y el artículo 47 manda que la Cámara de Diputados prevea «en un ramo específico» del Presupuesto lo que el IPAB requiera.",
   "Ese ramo es el 34. En el Presupuesto de Egresos de la Federación 2026 (DOF 21 de noviembre de 2025) recibe 35,553,400,900 pesos, de los cuales 35,553,400,000 son para «obligaciones surgidas de los programas de apoyo a ahorradores» y 900 pesos para deudores. Además, el IPAB refinancia su deuda en el mercado: para octubre-diciembre de 2026 prevé colocar 64,400 millones de pesos en Bonos de Protección al Ahorro, con vencimientos por 22,205 millones, para una colocación neta de 42,195 millones. Su estrategia declarada es «mantener en términos reales el monto de sus pasivos netos»."
  ],
  "dato_curioso": "El séptimo transitorio de la ley de 1999 prevé que, si las auditorías hallaban préstamos donados a «entidades de interés público que reciban financiamiento público», esas entidades debían devolverlos con cargo a su propio financiamiento público.",
  "cifras": [
   {
    "valor": "35,553,400,900 pesos",
    "etq": "Ramo General 34, Programas de Apoyo a Ahorradores y Deudores de la Banca, PEF 2026",
    "estado": "oficial",
    "fuente": "PEF 2026, DOF 21-11-2025",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/PEF_2026.pdf"
   },
   {
    "valor": "97.4 millones de pesos por día",
    "etq": "Ramo 34 de 2026 entre 365 días; operación: 35,553,400,900 ÷ 365",
    "estado": "derivado",
    "fuente": "PEF 2026",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/PEF_2026.pdf"
   },
   {
    "valor": "400 mil UDIS",
    "etq": "Tope del seguro de depósitos por persona y por institución (art. 11 LPAB)",
    "estado": "oficial",
    "fuente": "Ley de Protección al Ahorro Bancario",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/LPAB.pdf"
   },
   {
    "valor": "42,195 millones de pesos",
    "etq": "Colocación neta de Bonos de Protección al Ahorro, octubre-diciembre de 2026 (64,400 menos vencimientos por 22,205)",
    "estado": "oficial",
    "fuente": "IPAB, Boletín de Prensa 05-2026",
    "url": "https://www.gob.mx/ipab/prensa/boletin-de-prensa-05-2026"
   }
  ],
  "fuentes": [
   {
    "nombre": "Ley de Protección al Ahorro Bancario, DOF 19-01-1999, texto vigente (Cámara de Diputados)",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/LPAB.pdf"
   },
   {
    "nombre": "Presupuesto de Egresos de la Federación 2026, DOF 21-11-2025 (Cámara de Diputados)",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/PEF_2026.pdf"
   },
   {
    "nombre": "IPAB, Boletín de Prensa 05-2026, 25 de septiembre de 2026",
    "url": "https://www.gob.mx/ipab/prensa/boletin-de-prensa-05-2026"
   }
  ],
  "actualizado": "25 de septiembre de 2026"
 },
 {
  "id": "lozoya-agronitrogenados-odebrecht",
  "seccion": "Personajes",
  "icono": "🏭",
  "titulo": "Emilio Lozoya y la planta que Pemex compró tras 14 años sin operar",
  "balazo": "La ASF revisó la compra de Agro Nitrogenados y la FGR lleva desde 2017 un expediente por Odebrecht: esto es lo que dicen los documentos.",
  "cuerpo": [
   "El 20 de diciembre de 2013, Pemex compró por medio de sus filiales los activos de Agro Nitrogenados, S.A. de C.V., en 275.0 millones de dólares (5,427,235.0 miles de pesos, según la ASF). Así lo reconstruye la Auditoría Superior de la Federación en su auditoría de desempeño 469-DE a Pemex Fertilizantes, de la Cuenta Pública 2018. Para entonces, los consejos de las filiales habían autorizado hasta 275 millones de dólares para la compra y otros 200 millones para rehabilitar la planta.",
   "Una semana antes de la compra, el 13 de diciembre de 2013, el INDAABIN fijó el valor de la empresa en 292 millones de dólares, pero advirtió que, «después de estar inactiva durante 14 años», la planta requería «una gran inversión para la rehabilitación y puesta en marcha». En septiembre de 2014, Nafin prestó hasta 390.0 millones de dólares para el proyecto. La ASF anotó que las plantas seguían sin operar al cierre de 2018 y que la empresa no había generado, con su operación, los recursos para sostenerse. Son conclusiones de una auditoría, no una sentencia.",
   "En el caso Odebrecht, la FGR informó en febrero de 2019 que la constructora y Braskem reconocieron ante un tribunal de Nueva York, en diciembre de 2016, pagos por 6 millones de dólares a «oficiales de alto nivel» de Pemex, y que Emilio Lozoya, exdirector general de Pemex, fue entrevistado como imputado en agosto de 2017 y no quiso declarar. En octubre de 2021, la FGR lo señaló como uno de los principales responsables de los casos Odebrecht y Agronitrogenados, dijo que se acogió al criterio de oportunidad y que «sigue siendo procesado». Es una acusación, no una condena: mientras no haya sentencia firme, se presume inocente.",
   "Aparte, por la vía administrativa, la Función Pública lo inhabilitó en mayo de 2019 por 10 años para el servicio público porque omitió una cuenta bancaria en su declaración patrimonial. La Sala Superior del Tribunal Federal de Justicia Administrativa confirmó la sanción en febrero de 2020. Es el primer exdirector de Pemex inhabilitado, según la propia dependencia."
  ],
  "dato_curioso": "El estudio de la consultora Booz & Co. que sirvió para valuar el proyecto advertía, según la ASF, que «la probabilidad de destruir valor económico es alta».",
  "cifras": [
   {
    "valor": "275.0 millones de dólares (5,427,235.0 miles de pesos)",
    "etq": "Precio de los activos de Agro Nitrogenados pagado el 20 de diciembre de 2013",
    "estado": "oficial",
    "fuente": "ASF, auditoría 469-DE, Cuenta Pública 2018",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2018c/Documentos/Auditorias/2018_0469_a.pdf"
   },
   {
    "valor": "292 millones de dólares (3,800.0 millones de pesos)",
    "etq": "Dictamen valuatorio del INDAABIN, 13 de diciembre de 2013",
    "estado": "oficial",
    "fuente": "ASF, auditoría 469-DE, Cuenta Pública 2018",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2018c/Documentos/Auditorias/2018_0469_a.pdf"
   },
   {
    "valor": "14 años",
    "etq": "Tiempo que la planta llevaba inactiva, según el INDAABIN",
    "estado": "oficial",
    "fuente": "ASF, auditoría 469-DE, Cuenta Pública 2018",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2018c/Documentos/Auditorias/2018_0469_a.pdf"
   },
   {
    "valor": "390.0 millones de dólares",
    "etq": "Crédito de Nafin (septiembre de 2014) para reembolsar la compra y rehabilitar la planta",
    "estado": "oficial",
    "fuente": "ASF, auditoría 469-DE, Cuenta Pública 2018",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2018c/Documentos/Auditorias/2018_0469_a.pdf"
   },
   {
    "valor": "6,000,000 de dólares",
    "etq": "Pagos que Odebrecht y Braskem reconocieron en EUA a «oficiales de alto nivel» de Pemex",
    "estado": "oficial",
    "fuente": "Comunicado FGR 46/19",
    "url": "https://www.gob.mx/fgr/prensa/comunicado-fgr-46-19-situacion-actual-del-caso-odebrecht"
   },
   {
    "valor": "10 años",
    "etq": "Inhabilitación administrativa por omitir una cuenta en su declaración patrimonial",
    "estado": "oficial",
    "fuente": "Secretaría Anticorrupción y Buen Gobierno, comunicado 014/2020",
    "url": "https://www.gob.mx/buengobierno/prensa/tribunal-confirma-validez-de-sancion-impuesta-por-funcion-publica-a-emilio-lozoya-ex-director-general-de-pemex"
   }
  ],
  "fuentes": [
   {
    "nombre": "ASF, Informe Individual de la Cuenta Pública 2018, auditoría de desempeño 2018-6-90T9I-07-0469-2019 (469-DE), Pemex Fertilizantes",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2018c/Documentos/Auditorias/2018_0469_a.pdf"
   },
   {
    "nombre": "FGR, Comunicado 46/19, «Situación actual del caso ODEBRECHT», 14 de febrero de 2019",
    "url": "https://www.gob.mx/fgr/prensa/comunicado-fgr-46-19-situacion-actual-del-caso-odebrecht"
   },
   {
    "nombre": "FGR, Comunicado 407/21, «FGR informa», 11 de octubre de 2021",
    "url": "https://www.gob.mx/fgr/prensa/comunicado-fgr-407-21-fgr-informa"
   },
   {
    "nombre": "Función Pública (hoy Secretaría Anticorrupción y Buen Gobierno), comunicado 014/2020: el TFJA confirma la sanción a Emilio Lozoya, febrero de 2020",
    "url": "https://www.gob.mx/buengobierno/prensa/tribunal-confirma-validez-de-sancion-impuesta-por-funcion-publica-a-emilio-lozoya-ex-director-general-de-pemex"
   }
  ],
  "actualizado": "11 de octubre de 2021; lo ocurrido en el proceso penal de 2023 a 2026 sigue pendiente de verificar en un documento oficial"
 },
 {
  "id": "limantour-superavit-y-peso-oro",
  "seccion": "Historia",
  "icono": "🪙",
  "titulo": "Limantour: el superávit, el fin de las alcabalas y un peso de 75 centigramos de oro",
  "balazo": "Entre 1895 y 1905, la Hacienda porfiriana cerró sus cuentas con sobrante, quitó los impuestos al paso de mercancías y ató el peso al oro.",
  "cuerpo": [
   "José Yves Limantour, secretario de Hacienda de Porfirio Díaz, se propuso cuatro metas: nivelar el presupuesto, reanudar el servicio de la deuda externa, modernizar el sistema de impuestos librándolo de las alcabalas y resolver el problema bancario. La Historia del Banco de México registra que para 1896 Limantour informó que las tres primeras se habían alcanzado.",
   "La cronología del Porfiriato publicada por el INEHRM consigna que el ejercicio 1894-1895 arrojó un superávit de 2.5 millones de pesos y que, desde entonces y hasta 1910-1911, el superávit se mantuvo, con una reserva acumulada de 80 millones de pesos en marzo de 1911. El 30 de mayo de 1895 Limantour presentó la iniciativa para abolir las alcabalas, los impuestos que se cobraban por mover mercancías de un lugar a otro dentro del país; desaparecieron el 1 de julio de 1896.",
   "Un estudio publicado por la Auditoría Superior de la Federación muestra de dónde venía el dinero: en el ejercicio 1903-1904 los ingresos sumaron 86.5 millones de pesos y el gasto 83.5 millones, y entre 1895 y 1910 los impuestos al comercio exterior representaron en promedio el 46% de los ingresos.",
   "Faltaba la moneda. La plata, que respaldaba al peso, venía perdiendo precio. El 16 de noviembre de 1904 Limantour presentó la iniciativa de reforma, aprobada el 25 de marzo de 1905: un patrón de cambio oro con circulación de plata, en el que el peso equivalía a 75 centigramos de oro puro y debía contener 27 gramos 73 milésimas de plata pura, una relación de 32 a 1. Un decreto del 3 de abril de 1905 creó la Comisión de Cambios y Moneda, que administró el primer acervo monetario del país: el Fondo Regulador de la Circulación Monetaria."
  ],
  "dato_curioso": "Hasta el 1 de julio de 1896, una mercancía pagaba impuesto solo por cruzar de un lugar a otro dentro de México: eran las alcabalas (INEHRM).",
  "cifras": [
   {
    "valor": "2.5 millones de pesos",
    "etq": "Superávit del ejercicio 1894-1895",
    "estado": "oficial",
    "fuente": "INEHRM, Porfirio Díaz y el Porfiriato. Cronología",
    "url": "https://inehrm.gob.mx/work/models/inehrm/Resource/437/1/images/porfirio_porfiriato.pdf"
   },
   {
    "valor": "80 millones de pesos",
    "etq": "Reserva acumulada del tesoro en marzo de 1911",
    "estado": "oficial",
    "fuente": "INEHRM, Porfirio Díaz y el Porfiriato. Cronología",
    "url": "https://inehrm.gob.mx/work/models/inehrm/Resource/437/1/images/porfirio_porfiriato.pdf"
   },
   {
    "valor": "46%",
    "etq": "Peso promedio de los impuestos al comercio exterior en los ingresos totales, 1895-1910",
    "estado": "oficial",
    "fuente": "ASF, Impuestos, democracia y transparencia",
    "url": "https://www.asf.gob.mx/uploads/63_Serie_de_Rendicion_de_Cuentas/Rc2.pdf"
   },
   {
    "valor": "75 centigramos de oro puro",
    "etq": "Equivalencia del peso según la ley monetaria aprobada el 25 de marzo de 1905 (relación oro-plata 32:1)",
    "estado": "oficial",
    "fuente": "AGN, Legajos núm. 5, 2010",
    "url": "https://bagn.archivos.gob.mx/index.php/legajos/article/download/322/315"
   }
  ],
  "fuentes": [
   {
    "nombre": "Pablo Serrano Álvarez, Porfirio Díaz y el Porfiriato. Cronología (1830-1915), INEHRM, 2012, pp. 177-178 y 214-215",
    "url": "https://inehrm.gob.mx/work/models/inehrm/Resource/437/1/images/porfirio_porfiriato.pdf"
   },
   {
    "nombre": "Eduardo Turrent Díaz, Historia del Banco de México, tomo I, cap. 1.2, Banco de México",
    "url": "https://www.banxico.org.mx/elib/hbm/1/1_2.html"
   },
   {
    "nombre": "Omar Velasco Herrera, «La Comisión de Cambios y Moneda», Legajos. Boletín del Archivo General de la Nación, núm. 5, 2010",
    "url": "https://bagn.archivos.gob.mx/index.php/legajos/article/download/322/315"
   },
   {
    "nombre": "Carlos Elizondo Mayer-Serra, Impuestos, democracia y transparencia, Serie Cultura de la Rendición de Cuentas núm. 2, Auditoría Superior de la Federación",
    "url": "https://www.asf.gob.mx/uploads/63_Serie_de_Rendicion_de_Cuentas/Rc2.pdf"
   }
  ],
  "actualizado": "9 de octubre de 2026"
 },
 {
  "id": "origen-ramo-33",
  "seccion": "Hechos",
  "icono": "🗺️",
  "titulo": "Las aportaciones del Ramo 33 nacieron en 1998 con cinco fondos; hoy son ocho",
  "balazo": "Las aportaciones federales, el dinero que la Federación manda a estados y municipios con destino obligado, tienen fecha de nacimiento: el 29 de diciembre de 1997.",
  "cuerpo": [
   "Ese día el Diario Oficial publicó el decreto que añadió a la Ley de Coordinación Fiscal un Capítulo V, «De los Fondos de Aportaciones Federales», con los artículos 25 a 42. Entró en vigor el 1o. de enero de 1998. Desde entonces el artículo 25 define las aportaciones como recursos que la Federación transfiere a estados y municipios «condicionando su gasto» a los objetivos que la ley fija para cada fondo.",
   "El mismo artículo las distingue de las participaciones: se establecen «con independencia» de lo que los capítulos I a IV dicen sobre la participación de estados y municipios en la recaudación federal. El texto vigente muestra cómo creció la lista: las fracciones VI (educación tecnológica y de adultos) y VII (seguridad pública) se adicionaron en el DOF del 31 de diciembre de 1998, y la VIII (fortalecimiento de las entidades federativas), el 27 de diciembre de 2006.",
   "En el Presupuesto de Egresos de la Federación 2026, el Ramo General 33 tiene 1,041,892,906,925 pesos; el Ramo 28, Participaciones, 1,456,045,894,280 pesos. El primer fondo del capítulo hoy se llama Fondo de Aportaciones para la Nómina Educativa y Gasto Operativo (reforma DOF 09-12-2013); los transitorios de 1997 lo llamaban Fondo de Aportaciones para la Educación Básica y Normal."
  ],
  "dato_curioso": "Uno de cada diez pesos del gasto neto total aprobado para 2026 está en el Ramo 33: 10.2 %.",
  "cifras": [
   {
    "valor": "1,041,892,906,925 pesos",
    "etq": "Ramo General 33, Aportaciones Federales, PEF 2026",
    "estado": "oficial",
    "fuente": "PEF 2026, DOF 21-11-2025",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/PEF_2026.pdf"
   },
   {
    "valor": "10.2 %",
    "etq": "Peso del Ramo 33 en el gasto neto total 2026; operación: 1,041,892,906,925 ÷ 10,193,683,700,000 × 100",
    "estado": "derivado",
    "fuente": "PEF 2026, artículo 2",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/PEF_2026.pdf"
   },
   {
    "valor": "5 fondos en 1998, 8 hoy",
    "etq": "Fracciones del art. 25 LCF: VI y VII adicionadas DOF 31-12-1998; VIII, DOF 27-12-2006 (conteo sobre las notas de reforma)",
    "estado": "derivado",
    "fuente": "Ley de Coordinación Fiscal",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/LCF.pdf"
   }
  ],
  "fuentes": [
   {
    "nombre": "Ley de Coordinación Fiscal, texto vigente, con el decreto DOF 29-12-1997 que adicionó el Capítulo V (Cámara de Diputados)",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/LCF.pdf"
   },
   {
    "nombre": "Presupuesto de Egresos de la Federación 2026, DOF 21-11-2025 (Cámara de Diputados)",
    "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/PEF_2026.pdf"
   }
  ],
  "actualizado": "21 de noviembre de 2025"
 },
 {
  "id": "robles-sedesol-convenios-universidades",
  "seccion": "Personajes",
  "icono": "🏫",
  "titulo": "Rosario Robles, la Sedesol y los convenios con universidades que auditó la ASF",
  "balazo": "La ASF documentó pagos de la Sedesol a la UAEM sin que se cumplieran las metas; en 2024, la Suprema Corte dejó firme una sentencia que la ASF había impugnado.",
  "cuerpo": [
   "Rosario Robles Berlanga firmó como secretaria de Desarrollo Social, entre otros documentos, las Reglas de Operación de Oportunidades publicadas en el DOF el 30 de diciembre de 2013. En esos años, la Sedesol firmó convenios con universidades públicas al amparo del artículo 1, párrafo quinto, de la Ley de Adquisiciones. Ese artículo permite contratar entre entes públicos sin licitación. En la Cuenta Pública 2014, la ASF hizo una auditoría forense (229, DS-064) al Programa de Pensión para Adultos Mayores. Revisó 24 convenios por 1,284,412.1 miles de pesos.",
   "Uno de esos convenios, con la Universidad Autónoma del Estado de México (UAEM), era para abrir ventanillas e incorporar a 1,600,000 adultos mayores. Su monto máximo pasó de 480,000.0 a 576,000.0 miles de pesos. La ASF concluyó que no se incorporó a 226,779 personas de la meta y que la Sedesol hizo «pagos injustificados» a la UAEM por 68,033.7 miles de pesos. En una revisión paralela, la ASF vio que la UAEM recibió 130,000.0 miles de pesos, pagó a dos empresas 86,770.1 miles de pesos y dejó 16,402.3 miles de pesos en sus cuentas. En total fijó recuperaciones probables por 571,780.2 miles de pesos y emitió 5 pliegos de observaciones. Son presunciones de daño que se tienen que aclarar; no son un robo probado.",
   "La propia ASF escribió en ese informe que llevaba cuatro años consecutivos observando este tipo de contratos sin licitación, que había presentado denuncias de hechos y que «no se han obtenido resultados tangibles». En el terreno penal, el 30 de octubre de 2024 la Primera Sala de la Suprema Corte desechó el amparo directo en revisión 4419/2024 que había promovido la Auditoría Superior de la Federación, y quedó firme la sentencia del tribunal colegiado. En la misma sesión declaró sin materia un recurso de reclamación de María del Rosario Robles Berlanga. La lista oficial no detalla el sentido de esa sentencia, y no localizamos una versión pública de las resoluciones previas. Mientras no exista una condena firme, a ella la ampara la presunción de inocencia."
  ],
  "dato_curioso": "Según la ASF, una de las empresas que operó las ventanillas de la UAEM cobraba 41,432.7 pesos al mes por cada ventanilla.",
  "cifras": [
   {
    "valor": "1,284,412.1 miles de pesos",
    "etq": "24 convenios de la Sedesol revisados por la ASF (Cuenta Pública 2014)",
    "estado": "oficial",
    "fuente": "ASF, auditoría forense 229 (DS-064), Cuenta Pública 2014",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2014i/Documentos/Auditorias/2014_0229_a.pdf"
   },
   {
    "valor": "576,000.0 miles de pesos",
    "etq": "Monto máximo, ya ampliado, del convenio Sedesol–UAEM para las ventanillas de adultos mayores",
    "estado": "oficial",
    "fuente": "ASF, auditoría forense 229, Cuenta Pública 2014",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2014i/Documentos/Auditorias/2014_0229_a.pdf"
   },
   {
    "valor": "226,779",
    "etq": "Adultos mayores de la meta que no se incorporaron",
    "estado": "oficial",
    "fuente": "ASF, auditoría forense 229, Cuenta Pública 2014",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2014i/Documentos/Auditorias/2014_0229_a.pdf"
   },
   {
    "valor": "68,033.7 miles de pesos",
    "etq": "Pagos injustificados de la Sedesol a la UAEM por la meta no cumplida",
    "estado": "oficial",
    "fuente": "ASF, auditoría forense 229, Cuenta Pública 2014",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2014i/Documentos/Auditorias/2014_0229_a.pdf"
   },
   {
    "valor": "571,780.2 miles de pesos",
    "etq": "Recuperaciones probables que determinó la ASF en la auditoría",
    "estado": "oficial",
    "fuente": "ASF, auditoría forense 229, Cuenta Pública 2014",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2014i/Documentos/Auditorias/2014_0229_a.pdf"
   },
   {
    "valor": "16,402.3 miles de pesos",
    "etq": "Recursos que la UAEM dejó en sus cuentas bancarias de lo recibido en 2014",
    "estado": "oficial",
    "fuente": "ASF, auditoría forense 229, Cuenta Pública 2014",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2014i/Documentos/Auditorias/2014_0229_a.pdf"
   }
  ],
  "fuentes": [
   {
    "nombre": "ASF, Informe del Resultado de la Cuenta Pública 2014, auditoría forense 14-0-20100-12-0229 (DS-064), Sedesol, Programa de Pensión para Adultos Mayores; dictamen del 28 de enero de 2016",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2014i/Documentos/Auditorias/2014_0229_a.pdf"
   },
   {
    "nombre": "ASF, auditoría forense 14-4-99015-12-0207 (DS-033), Universidad Autónoma del Estado de México, Cuenta Pública 2014",
    "url": "https://www.asf.gob.mx/Trans/Informes/IR2014i/Documentos/Auditorias/2014_0207_a.pdf"
   },
   {
    "nombre": "DOF, 30 de diciembre de 2013: Acuerdo por el que se emiten las Reglas de Operación del Programa Oportunidades 2014 (firma de María del Rosario Robles Berlanga como secretaria de Desarrollo Social)",
    "url": "https://dof.gob.mx/reglas_2014/SEDESOL_301213_13.pdf"
   },
   {
    "nombre": "SCJN, Primera Sala, lista de asuntos fallados en la sesión del 30 de octubre de 2024 (ADR 4419/2024 y recurso de reclamación 492/2024)",
    "url": "https://www.scjn.gob.mx/sites/default/files/listas/documento/2024-10-30/30%20OCTUBRE%202024%20-%20CR%20LISTAS%20SESI%C3%93N%20-%20FALLADOS%20-%20SIN%20DATOS%20SENSIBLES.pdf"
   }
  ],
  "actualizado": "30 de octubre de 2024"
 },
 {
  "id": "banco-de-mexico-1925",
  "seccion": "Historia",
  "icono": "🏦",
  "titulo": "Banco de México, 1925: un banco central pagado con el sobrante del presupuesto",
  "balazo": "El capital del banco salió de los ahorros del gobierno de Calles, y el primer billete, de cinco pesos, se lo quedó el presidente.",
  "cuerpo": [
   "La ley que creó el Banco de México se promulgó el 25 de agosto de 1925. Fijó un capital de 100 millones de pesos en dos series de acciones: la serie A, reservada al gobierno federal, cubría el 51%; la serie B podían suscribirla el propio gobierno, los particulares o los bancos asociados. A cambio, el banco recibió la facultad de crear moneda, tanto acuñando piezas metálicas como emitiendo billetes.",
   "El dinero salió de las cuentas públicas. En 1923 el erario había cerrado con un déficit de 58.7 millones de pesos, y sofocar la rebelión delahuertista costó cerca de 60 millones. Con el secretario de Hacienda Alberto J. Pani, el presupuesto ejercido en 1925 fue de 295.3 millones de pesos y los ingresos sumaron 336.8 millones: el superávit de 41.5 millones fue, según la historia oficial del banco, el cimiento para integrar su capital. La semblanza del propio Banco de México atribuye parte de esos fondos a las economías logradas en el Ejército por el general Joaquín Amaro.",
   "El banco abrió sus puertas el 1 de septiembre de 1925, en una ceremonia encabezada por el presidente Plutarco Elías Calles. Su primer director fue Alberto Mascareñas. Pani le entregó dos cheques contra la Comisión Monetaria con los fondos del capital, y en la Comisión se habían acumulado 42 millones de pesos en monedas metálicas que los empleados sacaron a mano, en sacos de lona, para llevarlas al banco. El gobierno compró el edificio de La Mutua, en 5 de Mayo, por 1.25 millones de pesos, según la Memoria de Hacienda; sigue siendo la oficina matriz del banco."
  ],
  "dato_curioso": "El billete número 1, serie A, del Banco de México fue de cinco pesos y se le regaló al presidente Calles el día de la inauguración, el 1 de septiembre de 1925.",
  "cifras": [
   {
    "valor": "100 millones de pesos",
    "etq": "Capital del Banco de México fijado por la ley del 25 de agosto de 1925",
    "estado": "oficial",
    "fuente": "Historia del Banco de México, t. I, cap. 3.3",
    "url": "https://www.banxico.org.mx/elib/hbm/1/3_3.html"
   },
   {
    "valor": "41.5 millones de pesos",
    "etq": "Superávit del gobierno federal en 1925 (ingresos 336.8 menos egresos 295.3 millones)",
    "estado": "oficial",
    "fuente": "Historia del Banco de México, t. I, cap. 3.2",
    "url": "https://www.banxico.org.mx/elib/hbm/1/3_2.html"
   },
   {
    "valor": "42 millones de pesos",
    "etq": "Monedas metálicas acumuladas en la Comisión Monetaria en agosto de 1925 para el fondo de caja del banco",
    "estado": "oficial",
    "fuente": "Historia del Banco de México, t. I, cap. 3.3",
    "url": "https://www.banxico.org.mx/elib/hbm/1/3_3.html"
   }
  ],
  "fuentes": [
   {
    "nombre": "Banco de México, «Semblanza histórica»",
    "url": "https://www.banxico.org.mx/conociendo-banxico/semblanza-historica-historia-.html"
   },
   {
    "nombre": "Eduardo Turrent Díaz, Historia del Banco de México, tomo I, cap. 3.2, Banco de México",
    "url": "https://www.banxico.org.mx/elib/hbm/1/3_2.html"
   },
   {
    "nombre": "Eduardo Turrent Díaz, Historia del Banco de México, tomo I, cap. 3.3, Banco de México",
    "url": "https://www.banxico.org.mx/elib/hbm/1/3_3.html"
   }
  ],
  "actualizado": "9 de octubre de 2026"
 },
 {
  "id": "casa-blanca-expediente",
  "seccion": "Hechos",
  "icono": "🗂️",
  "titulo": "«Casa Blanca»: el expediente que, según la Función Pública, fue sustituido por una copia",
  "balazo": "Años después de la investigación sobre la «Casa Blanca», la propia Secretaría de la Función Pública denunció la desaparición del expediente original.",
  "cuerpo": [
   "El 11 de marzo de 2021, la Secretaría de la Función Pública informó, en su comunicado 017/2021, que un juez de control vinculó a proceso a tres personas por su presunta responsabilidad en la sustracción del expediente del caso conocido como la «Casa Blanca», sobre el posible conflicto de interés del entonces presidente Enrique Peña Nieto con Grupo Higa.",
   "Según el comunicado, la denuncia se originó en una investigación del Órgano Interno de Control, después de que exfuncionarios señalaran que, antes de entregar la dependencia a la nueva administración, el expediente original se habría sustituido por una copia de la versión pública que presuntamente omitía diversas evidencias. La denuncia, presentada en 2019 ante la Fiscalía Especializada en Combate a la Corrupción, fue por el posible delito de ejercicio ilícito de servicio público.",
   "Los denunciados ocuparon, a finales de la administración anterior, los cargos de Subsecretario de Responsabilidades Administrativas y Contrataciones Públicas, Director General de Denuncias e Investigaciones y Director General Adjunto de Investigaciones. La dependencia, hoy Secretaría Anticorrupción y Buen Gobierno, informó entonces que el asunto seguía en etapa de investigación complementaria. No localizamos un documento oficial posterior con el desenlace del proceso."
  ],
  "dato_curioso": "El comunicado dice que el expediente «no fue archivado de conformidad con la ley en la materia y las normas internas» de la propia Secretaría.",
  "cifras": [
   {
    "valor": "3",
    "etq": "Personas vinculadas a proceso por la presunta sustracción del expediente",
    "estado": "oficial",
    "fuente": "SFP, Comunicado 017/2021",
    "url": "https://www.gob.mx/buengobierno/prensa/vinculan-a-proceso-a-tres-personas-denunciadas-por-la-funcion-publica-por-la-presunta-sustraccion-del-expediente-de-la-casa-blanca"
   }
  ],
  "fuentes": [
   {
    "nombre": "Secretaría de la Función Pública (hoy Anticorrupción y Buen Gobierno), Comunicado 017/2021, 11 de marzo de 2021",
    "url": "https://www.gob.mx/buengobierno/prensa/vinculan-a-proceso-a-tres-personas-denunciadas-por-la-funcion-publica-por-la-presunta-sustraccion-del-expediente-de-la-casa-blanca"
   }
  ],
  "actualizado": "11 de marzo de 2021"
 },
 {
  "id": "gordillo-la-sentencia-reservada",
  "seccion": "Personajes",
  "icono": "🔒",
  "titulo": "Elba Esther Gordillo: cinco años en proceso y una sentencia que se quiso reservar",
  "balazo": "La exdirigente magisterial salió libre en 2018 con una resolución de un tribunal federal que después se intentó guardar cinco años por «seguridad nacional».",
  "cuerpo": [
   "Elba Esther Gordillo Morales fue senadora del PRI de 1997 a 2000, por representación proporcional, y presidió la Comisión de Educación del Senado. Antes fue diputada federal en dos legislaturas y secretaria general del Comité Ejecutivo Nacional del PRI de 1989 a 1995. Así lo registra el Sistema de Información Legislativa de Gobernación. Según el dictamen de la Comisión de Justicia del Senado, el 5 de marzo de 2013 el Juez Sexto de Distrito de Procesos Penales Federales le dictó auto de formal prisión por delincuencia organizada y operaciones con recursos de procedencia ilícita. Era el primer gran paso de un proceso penal; no era una condena.",
   "El expediente dio varias vueltas. El 12 de noviembre de 2013, el Cuarto Tribunal Unitario en Materia Penal del Primer Circuito revocó otro auto de formal prisión que se le había dictado por defraudación fiscal equiparada, por el ISR de 2008, y ordenó reponer el procedimiento porque no se habían admitido las pruebas de su defensa. El 9 de mayo de 2014, para cumplir un amparo, el Juzgado Sexto de Distrito volvió a dictarle formal prisión por delincuencia organizada y por operaciones con recursos de procedencia ilícita (artículo 400 Bis del Código Penal Federal). Así lo informó el Consejo de la Judicatura Federal.",
   "El desenlace llegó en 2018. En el toca penal 156/2018, el Primer Tribunal Unitario en Materia Penal del Primer Circuito la exoneró de los dos delitos al resolver un incidente de sobreseimiento. Lo curioso vino después. Cuando alguien pidió esa sentencia por transparencia, el Comité de Transparencia del Consejo de la Judicatura Federal la reservó por cinco años por «seguridad nacional», porque el caso tocaba delincuencia organizada. El INAI ordenó entregar una versión pública. En esa versión debían quedar tachados, entre otros datos, sus cuentas bancarias, las obras de arte y los nombres de las empresas que le daban servicios personales y médicos. En septiembre de 2019 el Senado constató que la versión pública ya existía. Lo que no está en ningún documento oficial que hayamos podido abrir es el monto exacto que se le imputó."
  ],
  "dato_curioso": "Para entregar la sentencia que la exoneró, el INAI ordenó tachar, entre otros datos, «obras artísticas» y el «nombre de empresas que frecuentaba para servicios personales y médicos».",
  "cifras": [
   {
    "valor": "156/2018",
    "etq": "Toca penal en el que el Primer Tribunal Unitario en Materia Penal del Primer Circuito la exoneró",
    "estado": "oficial",
    "fuente": "Senado, Comisión de Justicia, dictamen del 19-09-2019",
    "url": "http://sil.gobernacion.gob.mx/Archivos/Documentos/2019/10/asun_3937150_20191015_1570723913.pdf"
   },
   {
    "valor": "5 años",
    "etq": "Plazo de reserva por «seguridad nacional» que fijó el Comité de Transparencia del CJF a esa sentencia",
    "estado": "oficial",
    "fuente": "Senado, Comisión de Justicia, dictamen del 19-09-2019",
    "url": "http://sil.gobernacion.gob.mx/Archivos/Documentos/2019/10/asun_3937150_20191015_1570723913.pdf"
   },
   {
    "valor": "ISR del ejercicio 2008",
    "etq": "Impuesto de la causa por defraudación fiscal equiparada, cuyo auto de formal prisión se revocó el 12-11-2013",
    "estado": "oficial",
    "fuente": "CJF, Nota informativa 50/2013",
    "url": "https://www.oaj.gob.mx/documentos/notasInformativas/docsNotasInformativas/2013/notaInformativa50.pdf"
   }
  ],
  "fuentes": [
   {
    "nombre": "Consejo de la Judicatura Federal, Nota informativa DGCS/NI 50/2013, 12-11-2013",
    "url": "https://www.oaj.gob.mx/documentos/notasInformativas/docsNotasInformativas/2013/notaInformativa50.pdf"
   },
   {
    "nombre": "Consejo de la Judicatura Federal, Nota informativa DGCS/NI 55/2014, 09-05-2014",
    "url": "https://www.oaj.gob.mx/documentos/notasInformativas/docsNotasInformativas/2014/notaInformativa55.pdf"
   },
   {
    "nombre": "Senado de la República, Comisión de Justicia (LXIV Legislatura): dictamen sobre la sentencia del toca penal 156/2018, 19-09-2019",
    "url": "http://sil.gobernacion.gob.mx/Archivos/Documentos/2019/10/asun_3937150_20191015_1570723913.pdf"
   },
   {
    "nombre": "Secretaría de Gobernación, Sistema de Información Legislativa: perfil de la senadora Elba Esther Gordillo Morales (LVII Legislatura)",
    "url": "http://sil.gobernacion.gob.mx/Librerias/pp_PerfilLegislador.php?Referencia=595"
   }
  ],
  "actualizado": "19 de septiembre de 2019"
 },
 {
  "id": "gomez-urrutia-de-la-casa-de-moneda-al-congreso",
  "seccion": "Personajes",
  "icono": "⛏️",
  "titulo": "Napoleón Gómez Urrutia: de la Casa de Moneda al sindicato minero y al Congreso",
  "balazo": "Antes de dirigir el sindicato minero, estuvo doce años al frente de la institución que acuña las monedas del país.",
  "cuerpo": [
   "Según el Sistema de Información Legislativa (SIL) de Gobernación, Napoleón Gómez Urrutia nació en Monterrey en 1944, estudió economía en la UNAM y se doctoró en Oxford. De 1979 a 1991 fue director general de la Casa de Moneda de México. Después fue secretario general del Sindicato Nacional de Trabajadores Mineros, Metalúrgicos, Siderúrgicos y Similares de 2002 a 2011, y presidente de esa organización de 2012 a 2024. El propio SIL advierte que su perfil se arma con fuentes públicas y que el legislador no lo ha confirmado.",
   "Llegó al Senado en 2018 por Morena, por representación proporcional, y fue senador en las legislaturas LXIV y LXV. Desde el 25 de septiembre de 2018 presidió la Comisión de Trabajo y Previsión Social. Desde ahí, el 28 de febrero de 2024, su comisión aprobó un dictamen para subir el aguinaldo de 15 a 30 días de salario (artículo 87 de la Ley Federal del Trabajo). Ojo: era la aprobación de una comisión, no una ley publicada en el DOF. El 29 de agosto de 2024 rindió protesta como diputado federal de la LXVI Legislatura. El 12 de septiembre de 2025 pidió licencia por tiempo indefinido, según el mismo registro.",
   "Te debemos una parte de la historia. Su salida a Canadá en 2006, las órdenes de aprehensión de aquellos años y el pleito por el fideicomiso que se formó con la venta de Mexicana de Cananea no aparecen en ningún documento oficial público que lo nombre y que hayamos podido abrir. Ese pleito llegó a la Segunda Sala de la Suprema Corte en 2024, en los amparos directos en revisión 4189/2023, 4190/2023 y 4191/2023, pero esas resoluciones se publican con los nombres tachados. Por eso, en esta columna no te damos cifras sobre ese litigio. Si las encontramos en un documento oficial, actualizaremos la columna."
  ],
  "dato_curioso": "El hombre que dirigió el sindicato minero desde 2002 fue, de 1979 a 1991, director general de la Casa de Moneda de México.",
  "cifras": [
   {
    "valor": "1979–1991",
    "etq": "Director general de la Casa de Moneda de México",
    "estado": "oficial",
    "fuente": "SIL-Segob, perfil de diputado (LXVI)",
    "url": "http://sil.gobernacion.gob.mx/Librerias/pp_PerfilLegislador.php?Referencia=9228830"
   },
   {
    "valor": "2002–2011 y 2012–2024",
    "etq": "Secretario general y luego presidente del sindicato minero",
    "estado": "oficial",
    "fuente": "SIL-Segob, perfil de diputado (LXVI)",
    "url": "http://sil.gobernacion.gob.mx/Librerias/pp_PerfilLegislador.php?Referencia=9228830"
   },
   {
    "valor": "12/09/2025",
    "etq": "Inicio de su licencia por tiempo indefinido como diputado federal",
    "estado": "oficial",
    "fuente": "SIL-Segob, perfil de diputado (LXVI)",
    "url": "http://sil.gobernacion.gob.mx/Librerias/pp_PerfilLegislador.php?Referencia=9228830"
   }
  ],
  "fuentes": [
   {
    "nombre": "Secretaría de Gobernación, Sistema de Información Legislativa: perfil del diputado Napoleón Gómez Urrutia (LXVI Legislatura)",
    "url": "http://sil.gobernacion.gob.mx/Librerias/pp_PerfilLegislador.php?Referencia=9228830"
   },
   {
    "nombre": "Secretaría de Gobernación, Sistema de Información Legislativa: perfil del senador Napoleón Gómez Urrutia (LXIV Legislatura)",
    "url": "http://sil.gobernacion.gob.mx/Librerias/pp_PerfilLegislador.php?Referencia=9222044"
   },
   {
    "nombre": "Senado de la República: «Avanza en Comisión de Trabajo reforma para aumentar aguinaldo de 15 a 30 días de salario», 28-02-2024",
    "url": "https://comunicacionsocial.senado.gob.mx/informacion/comunicados/8300-avanza-en-comision-de-trabajo-reforma-para-aumentar-aguinaldo-de-15-a-30-dias-de-salario"
   },
   {
    "nombre": "SCJN, Segunda Sala: lista de asuntos para la sesión del 13-11-2024 (ADR 4189/2023 y 4191/2023)",
    "url": "https://www.scjn.gob.mx/sites/default/files/listas/documento/2024-10-31/LT%20VER%C3%81N%2013-11-2024.pdf"
   }
  ],
  "actualizado": "12 de septiembre de 2025"
 }
];

  /* Lo que se buscó y no se pudo sostener con un documento oficial. */
  var DESCARTADO = [
 {
  "tema": "Raúl Salinas de Gortari",
  "afirmacion": "Toda la columna (procesos, cuentas en Suiza, partida secreta, «La Paca»)",
  "motivo": "No se pudo abrir ningún documento oficial: los mexicanos solo aparecen en prensa y los extranjeros (GAO, Senado de EE.UU., Justicia de Suiza) están bloqueados en nuestro entorno. Falta de la plataforma: los documentos existen y aún no los integramos."
 },
 {
  "tema": "García Luna",
  "afirmacion": "Estado de la apelación en EE.UU.; empresas y montos de la ficha vieja; búnker, mansiones, yates; testimonios del juicio",
  "motivo": "Sin documento oficial abierto, o las cifras oficiales no coinciden con las de la ficha vieja. Los testimonios son dichos de testigos, no hechos probados."
 },
 {
  "tema": "Elba Esther Gordillo",
  "afirmacion": "Desvío de 2,000-2,600 mdp, compras de lujo, avión, yate, «presidenta vitalicia», crédito fiscal del SAT, devolución de bienes",
  "motivo": "Ningún monto se sostiene en documento oficial; las resoluciones del SAT/TFJA/SCJN localizadas tienen el nombre testado. La ficha vieja además decía que la absolvió la PGR: fue un tribunal."
 },
 {
  "tema": "Napoleón Gómez Urrutia",
  "afirmacion": "55 millones de dólares del fideicomiso de Cananea, exilio de lujo en Vancouver, Interpol y 11 órdenes revocadas",
  "motivo": "No hay documento oficial abierto que lo nombre; los de la SCJN tienen nombres y montos testados y mencionan otro fideicomiso."
 },
 {
  "tema": "Pemexgate",
  "afirmacion": "Multa del IFE al PRI por 1,000 millones de pesos (2003).",
  "motivo": "La resolución existe en el repositorio del INE, pero sus sitios no se pudieron abrir desde nuestro entorno: falta de la plataforma, queda pendiente hasta abrir la resolución."
 },
 {
  "tema": "Amigos de Fox",
  "afirmacion": "Multa del IFE a PAN y PVEM (2003).",
  "motivo": "No se pudo abrir la resolución del IFE ni la sentencia del TEPJF: falta de la plataforma, pendiente."
 },
 {
  "tema": "Casa Blanca",
  "afirmacion": "Resolución de la SFP en agosto de 2016.",
  "motivo": "Fecha equivocada en el material de origen y sin comunicado oficial localizado; la columna se apoya solo en el comunicado 017/2021."
 },
 {
  "tema": "Fobaproa-IPAB",
  "afirmacion": "Saldo actual de los pasivos del IPAB y total pagado desde 1999.",
  "motivo": "Hacienda y el IPAB sí lo publican, pero no se pudo abrir el informe: falta de la plataforma, pendiente."
 },
 {
  "tema": "Partida secreta",
  "afirmacion": "Montos en dólares y acumulados de 1983-2000.",
  "motivo": "Solo aparecen en discursos; no se abrieron los PEF de esos años (DOF no respondió)."
 },
 {
  "tema": "Retratos",
  "afirmacion": "Retratos de dominio público (Wikimedia Commons)",
  "motivo": "Commons no fue accesible desde nuestro entorno; no se pudo comprobar archivo ni licencia. Falta de la plataforma, pendiente."
 },
 {
  "tema": "Santa Anna",
  "afirmacion": "Ocupó la presidencia 11 veces",
  "motivo": "El INEHRM dice seis ocasiones; se usa esa cifra."
 },
 {
  "tema": "Santa Anna",
  "afirmacion": "La Mesilla: 10 millones de dólares y 76,000 km²",
  "motivo": "Las fuentes oficiales hablan de pesos, y la superficie no coincide entre ellas; no se publica."
 },
 {
  "tema": "Santa Anna",
  "afirmacion": "Entierro con honores de la pierna amputada (1842)",
  "motivo": "Sin fuente institucional consultable."
 },
 {
  "tema": "Santa Anna",
  "afirmacion": "Déficit de -4.8% del PIB",
  "motivo": "No existe estimación oficial del PIB de esa época que lo sostenga."
 },
 {
  "tema": "Juárez",
  "afirmacion": "La suspensión de pagos fue por dos años; aprobada 112 a 4; Inglaterra reclamaba casi 70 millones",
  "motivo": "No se pudo abrir la fuente institucional o solo aparece en fuentes no oficiales."
 },
 {
  "tema": "Juárez",
  "afirmacion": "Tratado McLane-Ocampo, fraude de 1871, subordinación a logias",
  "motivo": "Afirmaciones valorativas o sin documento institucional (provienen de Bulnes, 1904)."
 },
 {
  "tema": "Porfirio Díaz",
  "afirmacion": "Primer superávit desde la Independencia; reserva de 62.5 millones oro; deuda al 4%; crédito «AAA»",
  "motivo": "No lo sostiene la fuente institucional (el INEHRM da 80 millones de reserva); la calificación AAA es anacrónica."
 },
 {
  "tema": "Emilio Lozoya Austin",
  "afirmacion": "Recibió 10.5 millones de dólares en sobornos de Odebrecht",
  "motivo": "La cifra de 10.5 millones de dólares viene del acuerdo de culpabilidad de Odebrecht ante el Departamento de Justicia de EUA (diciembre de 2016) y se refiere al total pagado a funcionarios mexicanos, sin atribuirlo a una persona. Desde este entorno no se pudo abrir justice.gov porque el proxy bloquea el dominio. El documento oficial mexicano consultado (Comunicado FGR 46/19) menciona 6 millones de dólares a «oficiales de alto nivel» de Pemex, sin nombrarlos. No se puede atribuir a Lozoya ningún monto como hecho probado."
 },
 {
  "tema": "Emilio Lozoya Austin",
  "afirmacion": "Compraventa con sobreprecio de 200 millones de dólares de la planta Agronitrogenados",
  "motivo": "La auditoría 469-DE de la ASF (Cuenta Pública 2018) da un precio de 275 millones de dólares, un avalúo del INDAABIN de 292 millones de dólares y 200 millones autorizados para rehabilitar la planta. No habla de un sobreprecio de 200 millones de dólares. La prensa cita un sobrecosto de 93.1 millones de dólares de una auditoría de la Cuenta Pública 2015, pero ese informe no se abrió ni se verificó."
 },
 {
  "tema": "Emilio Lozoya Austin",
  "afirmacion": "Planta «chatarra» comprada a AHMSA",
  "motivo": "«Chatarra» es un adjetivo y la regla editorial lo excluye. La ASF habla de dos trenes de urea fuera de operación y de 14 años de inactividad. En el informe consultado, la vendedora es Agro Nitrogenados, S.A. de C.V.; su relación con AHMSA no se verificó en un documento oficial."
 },
 {
  "tema": "Emilio Lozoya Austin",
  "afirmacion": "Episodio del restaurante Hunan (octubre de 2021) y su envío al Reclusorio Norte",
  "motivo": "Solo hay fuentes de prensa. El Comunicado FGR 407/21 no menciona el episodio ni una medida de prisión preventiva."
 },
 {
  "tema": "Emilio Lozoya Austin",
  "afirmacion": "Estado procesal 2023-2026: suspensión del proceso Agronitrogenados en 2023 por la reparación de 216 millones de dólares, reactivación ordenada por un tribunal colegiado en julio de 2026 y vinculación a proceso de su hermana",
  "motivo": "Queda PENDIENTE. Solo se encontró en prensa (La Jornada, Milenio, Infobae). No se localizó la versión pública de las resoluciones ni un comunicado oficial vigente. El Comunicado FGR 242/22 sí existe, pero gob.mx respondió con error 500. La falta es de esta revisión, no se puede atribuir a una dependencia. El último documento oficial verificado es de octubre de 2021."
 },
 {
  "tema": "Rosario Robles Berlanga",
  "afirmacion": "Desvío de más de 7,600 millones de pesos en la «Estafa Maestra»",
  "motivo": "Ningún documento de la ASF consultado consolida esa cifra. Viene de una investigación periodística. Además, las observaciones de la ASF son presunciones por aclarar y no un desvío probado."
 },
 {
  "tema": "Rosario Robles Berlanga",
  "afirmacion": "Convenios con universidades de Edomex, Tabasco y Morelos",
  "motivo": "Solo se verificó en documento oficial el caso de la UAEM (auditorías 229 y 207, Cuenta Pública 2014). No se abrieron los informes de las universidades de Tabasco y Morelos."
 },
 {
  "tema": "Rosario Robles Berlanga",
  "afirmacion": "Pasó 3 años en prisión preventiva en Santa Martha Acatitla y fue absuelta en 2023",
  "motivo": "No se encontró documento oficial accesible sobre la duración ni el lugar de la prisión preventiva, ni sobre la resolución del juez de 2023. Se usó solo lo que consta en la lista oficial de la Primera Sala de la SCJN del 30 de octubre de 2024."
 },
 {
  "tema": "Rosario Robles Berlanga",
  "afirmacion": "Inhabilitación de 10 años por la Función Pública (2019) y su posterior anulación",
  "motivo": "El comunicado de la SFP de noviembre de 2020 que lo menciona no se pudo abrir: gob.mx devolvió solo el menú. Según los extractos del buscador, el comunicado no da el nombre ni deja claro a qué sanción se refiere la «nulidad lisa y llana»."
 },
 {
  "tema": "Ignacio Ovalle Fernández",
  "afirmacion": "Desfalco de más de 15,000 millones de pesos",
  "motivo": "Ningún documento oficial da esa cifra. La Función Pública habló en 2024 de 9,500 millones observados en 2019-2020, de los que aclaró 4,700 millones. Las dos auditorías de gestión financiera a Segalmex suman 9,036.8 millones por aclarar. Nada de eso es un desfalco probado ni se atribuye en lo personal a Ovalle."
 },
 {
  "tema": "Ignacio Ovalle Fernández",
  "afirmacion": "Colocó ilegalmente 950 millones de pesos en títulos bursátiles",
  "motivo": "La cifra coincide con la suma derivada de lo que observó la ASF: 100 millones de Segalmex y 850 millones de Liconsa. Pero los informes no atribuyen la decisión a Ovalle. La versión de que no recordó haber firmado la autorización viene solo de prensa."
 },
 {
  "tema": "Ignacio Ovalle Fernández",
  "afirmacion": "Sin acusación formal de la FGR",
  "motivo": "No se encontró documento oficial que lo afirme ni que lo niegue. La columna solo dice que su nombre no aparece en los comunicados consultados. Tampoco se verificó su salida del INAFED en 2024."
 },
 {
  "tema": "Carlos Romero Deschamps",
  "afirmacion": "Columna completa: Pemexgate (multa de 1,000 millones de pesos al PRI, más de 1,500 millones triangulados), Ferrari Enzo, departamentos en el Bath Club, vuelos de sus perros, muerte en octubre de 2023 y carpetas cerradas o prescritas",
  "motivo": "No se escribió la columna. La resolución del IFE de marzo de 2003 (expediente Q-CFRPAP 01/02) está en el repositorio documental del INE, pero el proxy de este entorno bloquea ese dominio (403), así que no se pudo comprobar la multa ni los montos. Esa falta es de esta revisión, no del INE. No se encontró sentencia del TEPJF accesible. Los lujos familiares, el fallecimiento y el estado de las denuncias de la UIF ante la FGR (2019) solo aparecen en prensa o redes sociales. No se localizó documento oficial que diga si las carpetas se cerraron o prescribieron."
 },
 {
  "tema": "Ignacio Ovalle Fernández",
  "afirmacion": "Director general de Segalmex, Diconsa y Liconsa de 2018 a 2022",
  "motivo": "Solo se verificó su salida, el 19 de abril de 2022, en un comunicado de Segalmex. No se localizó en documento oficial la fecha de su nombramiento ni que haya encabezado también Diconsa y Liconsa."
 },
 {
  "tema": "Hijos de Salinas de Gortari y NXIVM",
  "afirmacion": "Columna completa: Emiliano y Cecilia Salinas Occelli, NXIVM y el caso contra Keith Raniere",
  "motivo": "No se pudo abrir ningún documento oficial de EE.UU. (justice.gov, tribunales federales, PACER y govinfo están bloqueados en nuestro entorno) ni la sentencia SRE-PSC-75/2021 del TEPJF. La afirmación de que la fiscalía señaló a Emiliano Salinas como coconspirador no acusado solo aparece en prensa. Ningún documento localizado los acusa de un delito. Falta de la plataforma: pendiente hasta revisar la transcripción del juicio (EDNY 1:18-cr-00204), el comunicado del DOJ del 27-10-2020 y la sentencia del TEPJF."
 },
 {
  "tema": "Hijos de Salinas de Gortari y NXIVM",
  "afirmacion": "Cecilia Salinas Occelli codirigió ESP en México; reclutamiento de herederos; relación con DOS",
  "motivo": "Ningún documento oficial, ni siquiera un resultado en dominio oficial, lo sostiene. Ponerlos junto a DOS insinuaría un delito que nadie les atribuye."
 },
 {
  "tema": "Fallo por «más de 600 millones» que habría detectado la ASF",
  "afirmacion": "Un tribunal (la SCJN o uno administrativo) dejó sin efecto el pago o la responsabilidad por más de 600 millones de pesos detectados por la ASF.",
  "motivo": "No encontré ninguna resolución así. La que existe es de la SCJN (CC 174/2025, 6 de julio de 2026) y se refiere a 898,633,453.00 pesos observados por la ASE de Guerrero, no por la ASF. La Corte invalidó el informe por falta de competencia, sin juzgar el manejo del dinero. La única resolución sobre responsabilidad es la queja 4/2025-CA (10 de marzo de 2026), que ordenó dejar sin efecto la notificación de un procedimiento por desacato mientras se resolvía el fondo. No encontré resoluciones del TFJA ni del Tribunal de Justicia Administrativa de Guerrero."
 },
 {
  "tema": "Comunicado de prensa SCJN 101/2026",
  "afirmacion": "La Corte difundió el fallo en su comunicado 101/2026.",
  "motivo": "El buscador lo muestra en internet2.scjn.gob.mx (id=8520), pero el servidor devolvió 403 y no pude abrirlo. Por eso no lo cito. El fallo se sostiene con la versión taquigráfica oficial."
 },
 {
  "tema": "«No es exoneración» como frase de los ministros",
  "afirmacion": "Los ministros aclararon que «no es una exoneración».",
  "motivo": "Esa frase textual no aparece en la versión taquigráfica. Lo que sí consta: el ponente dijo que el fallo no exime de fiscalización ni se pronuncia sobre el manejo del dinero, y Espinosa Betanzo dijo que la invalidez no prejuzga sobre irregularidades. La columna usa esas expresiones."
 },
 {
  "tema": "Fecha «julio 2026» y ministro instructor",
  "afirmacion": "La ficha anterior no distinguía entre la resolución de la queja (10 de marzo de 2026) y la del fondo (6 de julio de 2026).",
  "motivo": "Se corrigió con los documentos. Instruyó Javier Laynez Potisek y resolvió el fondo la ponencia de Arístides Rodrigo Guerrero García."
 },
 {
  "tema": "Deudas de CAPAMA, CFE, SAT e ISSSPEG",
  "afirmacion": "El municipio y CAPAMA arrastran una deuda de más de 2,000 mdp, con más de 800 mdp con la CFE y deudas con el SAT y el ISSSPEG.",
  "motivo": "No encontré documento oficial que lo sostenga. Lo único verificado es la observación de la ASF de 2024 sobre 83,420.5 miles de pesos retenidos a trabajadores (ISSSPEG, SUSPEG, mutualista) sin evidencia de entero, y está en la columna como dato curioso."
 },
 {
  "tema": "Presupuesto «más de 4,500 mdp anuales»",
  "afirmacion": "El municipio maneja más de 4,500 mdp al año.",
  "motivo": "No está verificado. La ASE reporta universos de gestión financiera de 4,014,604,066.03 (2021), 4,869,150,735.72 (2022) y 5,071,285,743.04 (2023) pesos, que no coinciden con esa cifra."
 },
 {
  "tema": "Fondos de reconstrucción por Otis y John",
  "afirmacion": "La gestión está bajo escrutinio por fondos de reconstrucción tras Otis (2023) y John (2024).",
  "motivo": "Ningún informe de la ASF dirigido al municipio que revisé audita fondos de reconstrucción. La única mención es que la auditoría 1084 de 2024 registra avances financieros reportados durante una suspensión por huracán en el contrato MAJ/FAISMUN/299-2024/AD."
 },
 {
  "tema": "Soborno de 20,000 pesos en tribuna (13 de octubre de 2020)",
  "afirmacion": "Como diputada federal, confesó en tribuna haber pagado 20,000 pesos al Ministerio Público.",
  "motivo": "Queda fuera del tema de fiscalización y no abrí el Diario de los Debates para verificar la cita textual. No se publica sin ese documento."
 },
 {
  "tema": "Trayectoria y situación actual",
  "afirmacion": "Fue diputada local y federal de 2018 a 2021, fue reelecta para 2024-2027 y pidió licencia para buscar la gubernatura.",
  "motivo": "No lo verifiqué en documentos del INE, del IEPC ni del Congreso. Lo único que consta en documento oficial es la licencia del 20 de abril de 2024, que cita la sentencia de la queja 4/2025-CA. La prensa menciona una licencia reciente para buscar la candidatura a la gubernatura, sin documento oficial abierto. Por eso las columnas no afirman su cargo actual."
 },
 {
  "tema": "Suma de observaciones de la ASF publicada en prensa",
  "afirmacion": "Las observaciones de la ASF suman 282 millones 168 mil pesos en los ejercicios 2021, 2022 y 2024.",
  "motivo": "La cifra no cuadra con los informes. Con los documentos, 2022 + 2023 + 2024 = 237,077,420.40 pesos (derivado), y las auditorías 967 y 968 de 2021 suman 84,256,277.37 pesos, que no se pueden atribuir completos a esta administración."
 },
 {
  "tema": "Cargo partidista de López Beltrán",
  "afirmacion": "Fue secretario de Organización del Comité Ejecutivo Nacional de Morena desde septiembre de 2024 (elegido en el VII Congreso Nacional Extraordinario del 22-09-2024). Renunció el 25-05-2026 para buscar la diputación federal del distrito 6 de Tabasco, y el 15-06-2026 lo sustituyó Manuel Jesús Zavala Salazar como delegado en funciones.",
  "motivo": "Todo esto lo publicó la prensa, que coincide, pero no pude abrir ningún documento oficial que lo confirme. Los sitios del INE (ine.mx y repositoriodocumental.ine.mx) no se pudieron consultar desde este entorno (el proxy los rechaza y el DNS no los resuelve), igual que morena.org. La resolución INE/CG2363/2024, sobre los documentos básicos aprobados en ese congreso, no se pudo abrir. Las sentencias del TEPJF que sí descargué (SUP-JDC-329/2026, SUP-RAP-124/2026, SRE-PSC-261/2024) no lo mencionan. El dato es muy probablemente cierto, pero según la regla editorial queda pendiente hasta abrir el registro de integrantes del CEN de Morena ante el INE (DEPPP). Si falta, es una carencia de esta verificación, no de una dependencia."
 },
 {
  "tema": "Sentencia del TEPJF de octubre de 2026",
  "afirmacion": "La Sala Superior resolvió (según la prensa, el 7-10-2026, expediente SUP-REP-52/2026) que la queja de Movimiento Ciudadano contra López Beltrán por actos anticipados de campaña la resuelva el Consejo Distrital 6 del INE en Tabasco.",
  "motivo": "La sentencia no está publicada en te.gob.mx: probé SUP-REP-0052-2026 y otras variantes del nombre y todas dan 404. Solo se cuenta con la prensa. Además, la resolución es de competencia: no decide el fondo."
 },
 {
  "tema": "Romedic, S.A. de C.V.: contratos",
  "afirmacion": "Romedic obtuvo más de 490 millones de pesos en contratos de los gobiernos de Tabasco (2020-2021, unos 209-216 millones) y de Quintana Roo (diciembre de 2022, cifras de 219, 274 o 304.6 millones según la fuente), con recursos del INSABI (programa E023).",
  "motivo": "No encontré estos contratos en ningún documento oficial que haya podido abrir. Los históricos de CompraNet (compranet.hacienda.gob.mx y compranetinfo) no responden desde este entorno (error 502), y ComprasMX solo cubre de 2025 en adelante. Las cifras salen de MCCI y de la prensa, y no coinciden entre sí. Descargué el informe de la ASF de la Cuenta Pública 2022, auditoría 1614 (Quintana Roo, programa U013), y no nombra a Romedic: su muestra de contratos es otra (SESA-DA-055-2022 y siguientes) y no cubre recursos del E023. Los informes 2021-1547 (Quintana Roo) y 2023-1741 tampoco la mencionan."
 },
 {
  "tema": "Romedic: vínculo con Amílcar Olán",
  "afirmacion": "Romedic se constituyó el 23-01-2020 y sus socios fueron Jorge Amílcar Olán Aparicio y Jorge Luis Olán Rodríguez.",
  "motivo": "La afirmación se apoya en el acta constitutiva o en el Registro Público de Comercio, según la prensa, pero no pude consultar ningún documento oficial de ese registro (SIGER). Sin ese documento no se puede afirmar que la empresa sea de Olán."
 },
 {
  "tema": "Romedic en la lista de distribuidores irregulares de Cofepris",
  "afirmacion": "Romedic estaba boletinada en la lista de distribuidores irregulares de Cofepris desde el 21-12-2022, seis días antes del contrato con Quintana Roo.",
  "motivo": "Abrí el comunicado oficial de Cofepris 72/2022, del 21-12-2022 («Cofepris suma 11 nuevos establecimientos a lista de distribuidores irregulares de medicamentos», gob.mx/cofepris). Confirma 11 establecimientos nuevos, siete de ellos en Tabasco, pero el texto no da sus nombres. La lista está en un enlace acortado (bit.ly/3WqPEdc) que no se pudo abrir, así que no se puede confirmar que Romedic esté en ella. La versión de la lista de abril de 2024 en gob.mx da 404."
 },
 {
  "tema": "ASF sobre Romedic",
  "afirmacion": "Hay auditorías de la ASF sobre los contratos de Romedic con recursos del INSABI.",
  "motivo": "No encontré ningún informe individual de la ASF que nombre a Romedic: la búsqueda en asf.gob.mx no da resultados. Las auditorías al gasto en salud de Quintana Roo que revisé no la mencionan. Que una diputada presentara una denuncia ante la ASF no significa que haya una auditoría ni una observación."
 },
 {
  "tema": "Denuncia de la diputada Pérez-Jaén",
  "afirmacion": "La diputada María Elena Pérez-Jaén Zermeño (PAN) presentó en diciembre de 2023 denuncias ante la FGR y la ASF por la compra de medicamentos de Quintana Roo a Romedic.",
  "motivo": "La nota de Comunicación Social de la Cámara de Diputados existe según los buscadores, pero no se pudo abrir (HTTP 503 y certificado TLS incompleto). Según el extracto, sus cifras vienen de la prensa. Aunque se confirmara, solo acreditaría que se presentó una denuncia, no que haya una investigación ni un hecho probado."
 },
 {
  "tema": "Investigaciones de la FGR",
  "afirmacion": "Hay denuncias ante la Fiscalía Anticorrupción, y la FGR investiga u ordenó la aprehensión de Olán.",
  "motivo": "No encontré ningún comunicado oficial de la FGR. Según la prensa, la fiscal Ernestina Godoy dijo de viva voz el 16-09-2026 que no hay orden de aprehensión contra Olán ni contra López Beltrán. Según la misma prensa, un juez sobreseyó el 28-05-2026 un amparo de Olán porque no existía la orden reclamada, pero no localicé el expediente. La prensa también reporta un amparo de Romedic de enero de 2024 contra la negativa de acceso a una carpeta. Nada de esto se pudo verificar en documentos oficiales, y en todo caso apunta a que no hay acusación formal."
 },
 {
  "tema": "Hacienda/SAT y Portacelis Gas and Oil",
  "afirmacion": "Hacienda o el SAT pidió a la FGR ejercer acción penal contra Portacelis Gas and Oil por 834 millones de pesos de presunto contrabando de combustible (el llamado «huachicol fiscal»), y la empresa estaría ligada a Olán.",
  "motivo": "No hay ningún comunicado de SHCP, SAT, ANAM ni FGR que nombre a Portacelis. La cifra solo aparece, en un sitio oficial, en boca de una senadora del PAN durante una comparecencia (pan.senado.gob.mx), lo que es una afirmación de una legisladora y no un hallazgo de autoridad. El vínculo con Olán viene de la prensa (Reforma y Expansión) a través de un supuesto prestanombres. Según esas mismas notas, Olán no figura como acusado."
 },
 {
  "tema": "UIF",
  "afirmacion": "La UIF analiza operaciones de Romedic, Servicios de Minería Balancán y otras empresas.",
  "motivo": "Solo lo dice TV Azteca. No hay ningún documento ni comunicado de la UIF ni de la SHCP."
 },
 {
  "tema": "Balasto del Tren Maya",
  "afirmacion": "Olán (a través de Grupo Minero El Alicante u otras empresas) vendió balasto a Sedena o a contratistas para los tramos 5, 6 y 7 con un sobreprecio de cerca del 70%, sobornó a laboratoristas y presumió en audios «en seis meses nos ganamos 250 millones».",
  "motivo": "Los audios y la cotización vienen de Latinus y de columnas de opinión. No encontré ningún contrato en CompraNet ni ComprasMX, ni ningún informe de la ASF, que nombre a esas empresas o a Olán. Los informes de la ASF sobre el Tren Maya reportan observaciones generales (incluido balasto fuera de especificación, según la prensa) sin ligarlas a él. Según un punto de acuerdo legislativo, él habría sido subcontratista de otros proveedores, sin contrato directo con el gobierno. La «confirmación de Sedena» que menciona la prensa no la localicé en ningún comunicado oficial. La frase de los audios no es un dato de la plataforma: no se cita."
 },
 {
  "tema": "«El Clan»",
  "afirmacion": "Existe una red de contratismo llamada «El Clan» articulada por amigos de López Beltrán.",
  "motivo": "Es una etiqueta periodística (Latinus y MCCI). Ningún documento oficial usa ese nombre ni establece esa red. Insinuarlo violaría la presunción de inocencia y la regla editorial."
 },
 {
  "tema": "Malecón de Villahermosa (SEDATU)",
  "afirmacion": "Amigos del círculo de Olán obtuvieron contratos de SEDATU por más de 3,000 millones de pesos para el Malecón de Villahermosa.",
  "motivo": "No encontré ningún contrato ni informe de la ASF que vincule a esas empresas con Olán o con López Beltrán. La cifra viene de la ficha retirada y de la prensa."
 },
 {
  "tema": "Denuncia de padres de niños con cáncer",
  "afirmacion": "Padres de niños con cáncer denunciaron a López Beltrán y a Olán ante la FGR.",
  "motivo": "Solo hay un anuncio en la prensa (5-10-2026). No consta que la denuncia se haya presentado, y una denuncia no es una investigación ni una resolución."
 },
 {
  "tema": "Conclusión",
  "afirmacion": "Columna sobre López Beltrán, Olán y los contratos públicos.",
  "motivo": "No se escribe. No logré abrir ni un documento oficial que vincule a Olán o a su familia con contratos públicos concretos (monto, dependencia y fecha), ni ninguna investigación o resolución oficial que nombre a cualquiera de los dos. Hasta el cargo partidista de López Beltrán quedó sin confirmar en el INE, porque su portal no se pudo consultar desde este entorno. Una columna limitada a lo documentado se reduciría a un cargo sin fuente oficial abierta, y cualquier otra cosa insinuaría lo que ningún documento sostiene. Para reabrirla hacen falta: (1) el registro de integrantes del CEN de Morena ante el INE (DEPPP); (2) los contratos de Romedic en CompraNet histórico o en los portales de transparencia de los SESA de Quintana Roo y de la Secretaría de Salud de Tabasco, más el acta en SIGER; (3) la lista en PDF de Cofepris de diciembre de 2022; (4) un comunicado o expediente de FGR, SAT o UIF que nombre a las personas o a las empresas."
 },
 {
  "tema": "Pruebas no testimoniales en el juicio",
  "afirmacion": "Que en el juicio no hubo «pruebas como tal», solo dichos de delincuentes (o, en sentido contrario, que el jurado analizó bitácoras de vuelo, testimonios de agentes de la DEA y documentos patrimoniales).",
  "motivo": "Ninguna de las dos versiones se puede sostener con documento oficial consultado. El comunicado del Departamento de Justicia solo describe testimonios de antiguos miembros del cártel; el expediente 1:19-cr-00576 (EDNY) y sus transcripciones no se pudieron abrir: justice.gov, govinfo.gov y uscourts.gov están bloqueados desde el entorno de la plataforma, y CourtListener no es fuente oficial. Falta de la plataforma, no de ninguna dependencia. Además, «no hubo pruebas» es conceptualmente falso: el testimonio es medio de prueba en ambos sistemas."
 },
 {
  "tema": "Jurisprudencia de la SCJN sobre el coimputado",
  "afirmacion": "Que la Primera Sala de la SCJN prohíbe condenar únicamente con el dicho de un coimputado sin pruebas materiales corroboratorias, y que su declaración tiene «sospecha inicial de falsedad».",
  "motivo": "No se pudo abrir ninguna tesis en sjf2.scjn.gob.mx ni en bj.scjn.gob.mx (protección anti-bots que bloquea el acceso desde el entorno de la plataforma). Los resultados de búsqueda no mostraron una tesis específica sobre el coimputado en el sistema acusatorio. Queda pendiente por falta de la plataforma; no se atribuye omisión a la SCJN, que sí publica su Semanario."
 },
 {
  "tema": "«Testis unus, testis nullus»",
  "afirmacion": "Que en el derecho penal mexicano rige la regla de que un solo testigo no hace prueba y que el testimonio de un coimputado nunca es prueba plena por sí mismo.",
  "motivo": "El CNPP vigente no contiene esa regla: establece valoración libre y lógica (arts. 259, 265, 359, 402). La única regla tasada que se encontró es que nadie puede ser condenado con el solo mérito de su propia declaración (art. 402), que se refiere al acusado, no a un coimputado. La exigencia de corroboración que sí existe está en la LFDO (arts. 35 Bis y 36) y se refiere a la procedencia de beneficios para el colaborador."
 },
 {
  "tema": "Testimonios específicos y montos",
  "afirmacion": "Entregas de 3 y 2 millones de dólares en el restaurante Champs-Élysées por «El Rey» Zambada; pagos mensuales de 1 a 1.5 millones vía «El Grande»; más de 10 millones aportados por «El Lobo»; observaciones de Francisco Cañedo Zavaleta.",
  "motivo": "El comunicado de sentencia del Departamento de Justicia no nombra a los testigos ni da esos montos; solo habla de un restaurante francés frente a la Embajada de EE.UU. El comunicado de detención de 2019 menciona maletines de entre 3 y 5 millones, pero como acusación, no como hecho probado. Sin transcripción oficial accesible, no se publica (falta de la plataforma)."
 },
 {
  "tema": "Dichos sobre terceros (campaña de 2006)",
  "afirmacion": "Que «El Rey» Zambada declaró haber entregado dinero, vía Gabriel Regino, a la campaña presidencial de López Obrador en 2006.",
  "motivo": "No se encontró en documento oficial consultado. Aun si constara en la transcripción, el dicho de un testigo sobre terceros no juzgados no es un hecho probado; publicarlo sin documento sería difamatorio y contrario a la presunción de inocencia."
 },
 {
  "tema": "Frase del juez Cogan",
  "afirmacion": "Cita textual atribuida al juez («Usted tiene una doble vida…»).",
  "motivo": "No aparece en el comunicado oficial consultado y la transcripción de la audiencia de sentencia no estuvo accesible (falta de la plataforma). No se publica una cita textual sin documento."
 },
 {
  "tema": "Instrucciones al jurado sobre testigos cooperantes",
  "afirmacion": "Que en EE.UU. el jurado recibe instrucción de examinar con especial cautela el testimonio de cómplices cooperantes.",
  "motivo": "Se pretendía documentar con las instrucciones modelo del Segundo Circuito y el expediente, pero uscourts.gov, ca2.uscourts.gov y govinfo.gov están bloqueados desde el entorno de la plataforma. Queda pendiente; la columna no lo afirma."
 },
 {
  "tema": "Estado de la apelación",
  "afirmacion": "Que la condena está firme o que sigue apelada ante el Segundo Circuito.",
  "motivo": "Solo hay fuentes no oficiales (dockets de terceros y prensa) sobre la apelación 24-2949; el sitio del Segundo Circuito está bloqueado desde la plataforma. No se afirma ni se niega."
 },
 {
  "tema": "Red de empresas y contratos",
  "afirmacion": "Que empresas ligadas a García Luna obtuvieron al menos 30 contratos del CISEN y el OADPRS por 745.8 millones de dólares, y el litigio de la UIF en Miami por 600 millones.",
  "motivo": "Fuera del tema de esta columna y sin documento oficial abierto en esta investigación; requiere consultar las resoluciones judiciales de Florida y los comunicados de la UIF/FGR antes de publicarse."
 },
 {
  "tema": "Reglas de evidencia de EE.UU.",
  "afirmacion": "Que la «doctrina probatoria dominante» en EE.UU. es la Regla 403 y el plea bargaining «transaccional».",
  "motivo": "Caracterización sin fuente. El texto de la Regla 403 no se pudo abrir (uscourts.gov bloqueado desde el entorno de la plataforma), así que no se puede afirmar que sea la regla que rige la valoración de testigos colaboradores. Solo se verificó la Regla 601 (toda persona es competente para ser testigo)."
 },
 {
  "tema": "Amistad",
  "afirmacion": "García Harfuch y García Luna tienen o tuvieron una relación «estrecha, de amistad».",
  "motivo": "Solo aparece en prensa y en columnas de opinión. Ningún documento oficial que revisamos (perfil del SIL, comunicados del DOJ, Presidencia, Segob y Policía Federal) habla de un trato personal entre ellos. Lo único documentado es la coincidencia institucional: uno fue elemento de la Policía Federal Preventiva y el otro, titular de la SSP. Sin documento, afirmarlo sería un dato inventado."
 },
 {
  "tema": "Vínculos con el entorno de García Luna",
  "afirmacion": "García Harfuch tiene «posibles vínculos con el entorno García Luna».",
  "motivo": "Ningún documento oficial se lo atribuye. Los comunicados del DOJ de 2020 y 2024 nombran como coacusados solo a Luis Cárdenas Palomino y a Ramón Pequeño García, y una búsqueda de «Harfuch» en justice.gov no da resultados. Sin embargo, no pudimos abrir el PDF completo de la acusación sustitutiva porque justice.gov está bloqueado desde el entorno de la plataforma. Es una limitación nuestra, no de ninguna dependencia: lo leímos solo en los fragmentos que devuelve el buscador sobre ese dominio. Insinuar un vínculo así iría contra la presunción de inocencia."
 },
 {
  "tema": "Juicio de Nueva York",
  "afirmacion": "García Harfuch fue mencionado durante el juicio contra García Luna en Brooklyn (2023).",
  "motivo": "No encontramos ningún documento oficial que lo diga: los comunicados del DOJ no lo nombran. Las transcripciones del juicio están en el sistema judicial de Estados Unidos y la plataforma aún no las ha consultado. Queda pendiente por falta de la plataforma, no se le atribuye a ninguna dependencia."
 },
 {
  "tema": "Deslinde público",
  "afirmacion": "García Harfuch dijo que «nunca recibió instrucciones» de García Luna y que solo lo vio «tres o cuatro veces» (enero de 2024).",
  "motivo": "Solo lo encontramos en prensa (Expansión Política, 17 de enero de 2024), de cuando era aspirante, no funcionario. No hallamos versión estenográfica oficial en gob.mx, la SSC capitalina, el Senado ni la Cámara: varias páginas de la SSC y de presidente.gob.mx no respondieron o quedaron bloqueadas desde la plataforma. Es una limitación nuestra, no de ninguna dependencia. Queda pendiente hasta tener la transcripción oficial."
 },
 {
  "tema": "Nombramiento en Guerrero",
  "afirmacion": "García Luna nombró a García Harfuch coordinador de la Policía Federal en Guerrero en 2012.",
  "motivo": "Solo lo dice la prensa, y las fechas no cuadran: el SIL registra el cargo de 2011 a 2014 sin decir quién lo designó, y algunos medios lo fechan en diciembre de 2012, cuando García Luna ya había dejado la SSP. No hay oficio ni comunicado oficial del nombramiento que pudiéramos revisar."
 },
 {
  "tema": "Desvinculación presidencial",
  "afirmacion": "Claudia Sheinbaum (o antes López Obrador) desvinculó públicamente a García Harfuch de García Luna.",
  "motivo": "Solo lo encontramos en notas de prensa y columnas. No hallamos la versión estenográfica oficial: la mañanera del 25 de agosto de 2023 en presidente.gob.mx respondió 403 desde la plataforma, y en la del 9 de enero de 2026 García Harfuch no habla de García Luna. Queda pendiente por falta de la plataforma."
 },
 {
  "tema": "Detención de Cárdenas Palomino en México",
  "afirmacion": "La FGR detuvo a Luis Cárdenas Palomino en 2021 por tortura.",
  "motivo": "El comunicado FGR 253/21 (5 de julio de 2021) informa la detención en Naucalpan de un exservidor público identificado solo como «Luis \"C\"», por probable tortura en hechos de 2012. El nombre completo sale de la prensa y la FGR lo omite, como suele hacer. Por eso no se usa en la columna para identificarlo."
 }
];

  /* Desde el 28-10-2026 la pestaña es un periódico: «Al momento» y
     «Verificado» son noticia (#noticiasDiario); lo demás es la Columna del
     Erario, la opinión (#columnasDiario). La portada (#noticiasPortada) y el
     seguimiento (#noticiasSeguimiento) solo llaman a la nota. */
  var NOTICIA = { 'Al momento': 1, 'Verificado': 1 };
  /* Desde el 29-10-2026 el diario vive en tres páginas (noticias.py, PARTES):
     las columnas completas, en Auditavisión Noticias; el verificador, en
     Verifica una noticia, y los casos abiertos, en Seguimiento. COL es la
     página de las columnas, vacía cuando ya estás en ella. */
  var VERIFICA = document.getElementById('verifica') ? '#verifica' : 'noticias-verifica.html#verifica';
  var raiz = document.getElementById('columnasDiario');
  var raizN = document.getElementById('noticiasDiario');
  var raizP = document.getElementById('noticiasPortada');
  var raizS = document.getElementById('noticiasSeguimiento');
  var COL = (raiz || raizN) ? '' : 'noticias-auditavision.html';
  if (!raiz && !raizN && !raizS && !document.getElementById('columnasReplicas')) return;

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function chip(estado) {
    return '<span class="est-chip est-' + esc(estado) + '">' + esc(estado) + '</span>';
  }
  function figura(c, grande) {
    if (c.imagen) {
      return '<figure class="col-fig"><img src="' + esc(c.imagen.src) + '" alt="' + esc(c.imagen.alt) + '" loading="lazy"' +
        (grande ? '' : ' width="480" height="320"') + '>' +
        '<figcaption>' + esc(c.imagen.credito) + '</figcaption></figure>';
    }
    var il = ILUS[c.seccion] || ['📰', 'tinta'];
    return '<figure class="col-fig col-ilus col-ilus-' + il[1] + '" aria-hidden="true"><span>' + (c.icono || il[0]) + '</span></figure>';
  }

  /* Seguir un caso (pedido del autor, 26-10-2026: «activar una herramienta
     de alarmas, programar cierto tipo de noticias o seguimiento»). Se guarda
     solo en este navegador (localStorage av-sigo: {id: actualizado}); no
     pide correo ni cuenta. Cuando una columna cambia su «actualizado», quien
     la sigue ve el aviso de novedades hasta que la vuelve a abrir. */
  var SIGO_K = 'av-sigo';
  var sigo = (function () { try { return JSON.parse(localStorage.getItem(SIGO_K) || '{}') || {}; } catch (e) { return {}; } })();
  function sigoGuardar() { try { localStorage.setItem(SIGO_K, JSON.stringify(sigo)); } catch (e) { /* sin almacenamiento: se olvida al cerrar */ } }
  function sigue(c) { return Object.prototype.hasOwnProperty.call(sigo, c.id); }
  function novedad(c) { return sigue(c) && sigo[c.id] !== (c.actualizado || ''); }
  function porId(id) { for (var k = 0; k < COLUMNAS.length; k++) if (COLUMNAS[k].id === id) return COLUMNAS[k]; return null; }
  function btnSeguir(c) {
    return '<button type="button" class="col-seguir" data-id="' + esc(c.id) + '" aria-pressed="' + sigue(c) + '">' +
      (sigue(c) ? '🔕 Dejar de seguir este caso' : '🔔 Seguir este caso') + '</button>';
  }
  function panelSigo() {
    var ids = Object.keys(sigo).filter(porId);
    var nuevos = ids.filter(function (id) { return novedad(porId(id)); }).length;
    return '<section class="col-sigo" id="seguimientos" aria-labelledby="colSigoTit">' +
      '<h4 class="col-sigo-tit" id="colSigoTit">🔔 Tus seguimientos' + (nuevos ? ' <span class="col-nuevo">' + nuevos + ' con novedades</span>' : '') + '</h4>' +
      (ids.length ? '<ul>' + ids.map(function (id) {
        var c = porId(id), nov = novedad(c);
        return '<li' + (nov ? ' class="col-sigo-nuevo"' : '') + '><a href="' + COL + '#col-' + esc(id) + '">' + esc(c.titulo) + '</a> <small>' +
          (nov ? '🆕 Actualizada al ' + esc(c.actualizado) + '; la seguías desde la versión del ' + esc(sigo[id] || 'sin fecha') : 'Sin cambios desde el ' + esc(sigo[id] || 'sin fecha')) +
          '</small></li>';
      }).join('') + '</ul>'
        : '<p>Todavía no sigues ningún caso. Abre una columna y toca «🔔 Seguir este caso»: cuando la actualicemos con un documento nuevo, aquí verás el aviso.</p>') +
      '<p class="col-sigo-nota">Se guarda solo en este navegador: no pedimos correo ni cuenta, y nadie más lo ve. Si borras los datos del navegador, se borra la lista.</p>' +
    '</section>';
  }
  function repintarSigo() {
    var viejo = document.getElementById('seguimientos');
    if (viejo) viejo.outerHTML = panelSigo();
  }

  /* «Al momento»: la cuenta con números redondos, como barras a escala. */
  function ejemploHtml(c) {
    var e = c.ejemplo;
    if (!e) return '';
    var num = function (t) { return parseFloat(String(t).replace(/[^0-9.]/g, '')) || 0; };
    var max = Math.max.apply(null, e.filas.map(function (f) { return num(f[1]); }));
    return '<div class="col-ejemplo"><b>🧮 ' + esc(e.tit) + '</b> ' + chip('derivado') + '<p>' + esc(e.txt) + '</p><ul>' +
      e.filas.map(function (f) {
        var w = max ? Math.max(2, Math.round(100 * num(f[1]) / max)) : 0;
        return '<li><span class="col-ej-etq">' + esc(f[0]) + '</span><span class="col-ej-barra"><i style="width:' + w + '%"></i></span>' +
          '<strong>' + esc(f[1]) + '</strong><small>Operación: ' + esc(f[2]) + '</small></li>';
      }).join('') + '</ul>' + (e.nota ? '<p class="col-ej-nota">' + esc(e.nota) + '</p>' : '') + '</div>';
  }
  function datosHtml(c) {
    if (!c.datos || !c.datos.length) return '';
    return '<div class="col-datos"><b>📊 Lo que dicen nuestros datos</b><ul>' + c.datos.map(function (d) {
      return '<li><a href="' + esc(d.url) + '"><span aria-hidden="true">' + d.ico + '</span> ' + esc(d.tx) + ' ➔</a><small>' + esc(d.de) + '</small></li>';
    }).join('') + '</ul></div>';
  }
  function glosarioHtml(c) {
    if (!c.glosario || !c.glosario.length) return '';
    return '<div class="col-glosa"><b>📖 Si una palabra no te queda clara</b><p>' + c.glosario.map(function (g) {
      return '<a href="' + esc(g.url) + '">' + esc(g.t) + '</a>';
    }).join('') + '</p></div>';
  }
  /* Lo que dice la red: búsquedas armadas, nunca un texto copiado ni redactado
     por nosotros. Se rotulan «sin verificar» y llevan a Contrasta una nota. */
  var RED = [
    ['📰', 'Noticias', function (q) { return 'https://news.google.com/search?q=' + encodeURIComponent(q) + '&hl=es-419&gl=MX&ceid=MX:es-419'; }],
    ['▶️', 'YouTube', function (q) { return 'https://www.youtube.com/results?search_query=' + encodeURIComponent(q); }],
    ['💬', 'X', function (q) { return 'https://x.com/search?q=' + encodeURIComponent(q) + '&f=live'; }],
    ['👥', 'Facebook', function (q) { return 'https://www.facebook.com/search/posts/?q=' + encodeURIComponent(q); }],
    ['📜', 'Diario Oficial', function (q) { return 'https://www.google.com/search?q=' + encodeURIComponent(q + ' site:dof.gob.mx'); }]
  ];
  function redHtml(c) {
    if (!c.red) return '';
    return '<div class="col-red"><b>📡 Lo que dice la red ahora</b>' +
      '<p>Búsquedas ya armadas con «' + esc(c.red) + '». <b>Lo que encuentres ahí no lo verificó Auditavisión</b>: una nota o un video no son un documento oficial.</p>' +
      '<p class="col-red-lista">' + RED.map(function (r) {
        return '<a href="' + esc(r[2](c.red)) + '" target="_blank" rel="noopener noreferrer"><span aria-hidden="true">' + r[0] + '</span> ' + r[1] + ' ↗</a>';
      }).join('') + '</p>' +
      '<p class="col-red-pie">¿Encontraste una nota con cifras? <a href="' + VERIFICA + '">Contrástala con los documentos oficiales ➔</a></p></div>';
  }
  /* La franja «Al momento»: las notas breves, de la más nueva a la más vieja. */
  function fechaN(f) { var p = String(f || '').split('-'); return p.length === 3 ? +(p[2] + p[1] + p[0]) : 0; }
  function franja() {
    var b = COLUMNAS.filter(function (c) { return c.seccion === 'Al momento'; })
      .sort(function (x, y) { return fechaN(y.fecha) - fechaN(x.fecha); });
    if (!b.length) return '';
    return '<section class="col-franja" aria-labelledby="colFranjaTit"><h4 class="col-franja-tit" id="colFranjaTit">⏱️ Al momento <small>Lo que está pasando, verificado</small></h4><ol>' +
      b.slice(0, 6).map(function (c) {
        var pend = (c.cotejo || []).filter(function (x) { return x.res === 'pendiente'; }).length;
        var ok = (c.cotejo || []).filter(function (x) { return x.res === 'consta' || x.res === 'matiz'; }).length;
        return '<li><time>' + esc(c.fecha) + '</time><a href="' + COL + '#col-' + esc(c.id) + '">' + esc(c.titulo) + '</a>' +
          '<small>' + ok + ' con documento · ' + pend + ' por probar' + (c.nota ? ' · a partir de ' + esc(c.nota.medio) : '') + '</small></li>';
      }).join('') + '</ol></section>';
  }

  function articulo(c, i) {
    var cifras = (c.cifras || []).map(function (x) {
      return '<li><strong>' + esc(x.valor) + '</strong><span>' + esc(x.etq) + '</span>' +
        '<small>' + chip(x.estado) + ' ' + (x.url ? '<a href="' + esc(x.url) + '" target="_blank" rel="noopener noreferrer">' + esc(x.fuente) + ' ↗</a>' : esc(x.fuente)) + '</small></li>';
    }).join('');
    var fuentes = (c.fuentes || []).map(function (f) {
      return '<li><a href="' + esc(f.url) + '" target="_blank" rel="noopener noreferrer">' + esc(f.nombre) + ' ↗</a></li>';
    }).join('');
    return '<article class="col-art' + (i === 0 ? ' col-art-portada' : '') + '" id="col-' + esc(c.id) + '" data-seccion="' + esc(c.seccion) + '">' +
      figura(c, i === 0) +
      '<div class="col-art-tx">' +
        '<span class="col-kicker">' + (NOTICIA[c.seccion] ? esc(c.seccion === 'Verificado' ? 'Verificamos' : c.seccion) : '✒️ Opinión · ' + esc(c.seccion)) + '</span>' +
        (novedad(c) ? '<span class="col-nuevo">🆕 Novedades desde que lo sigues</span>' : '') +
        '<h4 class="col-titular">' + esc(c.titulo) + '</h4>' +
        '<p class="col-balazo">' + esc(c.balazo) + '</p>' +
        '<p class="col-firma">' + (NOTICIA[c.seccion] ? 'Redacción Auditavisión' : 'La Columna del Erario') + ' · ' + (c.fecha ? esc(c.fecha) + ' · ' : '') + 'Con documentos oficiales</p>' +
        '<button type="button" class="col-leer" aria-expanded="false" aria-controls="col-cuerpo-' + esc(c.id) + '">Leer completa ➔</button>' +
      '</div>' +
      '<div class="col-cuerpo" id="col-cuerpo-' + esc(c.id) + '" hidden>' +
        (c.cuerpo || []).map(function (p, k) { return '<p' + (k === 0 ? ' class="col-capitular"' : '') + '>' + esc(p) + '</p>'; }).join('') +
        ejemploHtml(c) +
        (c.nota ? '<p class="col-nota">📰 <b>De dónde salió:</b> <a href="' + esc(c.nota.url) + '" target="_blank" rel="noopener noreferrer">' + esc(c.nota.medio) + ', «' + esc(c.nota.titulo) + '» ↗</a> · ' + esc(c.nota.fecha) +
          '. Es el punto de partida: lo cotejamos contra el documento oficial.</p>' : '') +
        (c.circula ? '<aside class="col-circula"><b>' + (c.nota ? '📣 Lo que se dijo' : '📣 Lo que circula') + '</b><p>«' + esc(c.circula.texto) + '»</p>' +
          '<small>' + esc(c.circula.cuenta) + ' · ' + esc(c.circula.red) + ' · ' + esc(c.circula.fecha) + '</small></aside>' : '') +
        (c.cotejo ? '<div class="col-cotejo"><b>🔍 Cotejo, afirmación por afirmación</b><ol>' + c.cotejo.map(function (x, k) {
          var r = RES[x.res] || RES.pendiente;
          return '<li class="col-res-' + esc(x.res.replace(' ', '-')) + '"><p class="col-dice">«' + esc(x.dice) + '»</p>' +
            '<p><span class="col-res' + (x.res === 'pendiente' ? ' est-chip est-pendiente" data-pend="red-' + esc(c.id) + '-' + (k + 1) + '"' : '"') + '>' + r[0] + ' ' + r[1] + '</span> ' + esc(x.explica) + '</p>' +
            '<small>' + (x.url ? '<a href="' + esc(x.url) + '" target="_blank" rel="noopener noreferrer">' + esc(x.fuente) + ' ↗</a>' : esc(x.fuente)) + '</small></li>';
        }).join('') + '</ol></div>' : '') +
        datosHtml(c) + glosarioHtml(c) + redHtml(c) +
        (c.sigue ? '<div class="col-sigue"><b>🗓️ Lo que sigue</b><ul>' + c.sigue.map(function (x) {
          return '<li><a href="' + esc(x.url) + '" target="_blank" rel="noopener noreferrer">' + esc(x.que) + ' ↗</a></li>';
        }).join('') + '</ul></div>' : '') +
        (c.dato_curioso ? '<aside class="col-dato"><b>💡 Dato curioso</b><p>' + esc(c.dato_curioso) + '</p></aside>' : '') +
        (cifras ? '<ul class="col-cifras" aria-label="Cifras de la columna">' + cifras + '</ul>' : '') +
        '<div class="col-fuentes"><b>📎 Documentos que la sostienen</b><ol>' + fuentes + '</ol>' +
          (c.actualizado ? '<p class="col-act">Verificado al ' + esc(c.actualizado) + '.</p>' : '') +
        '</div>' +
        (c.replica && c.replica.length ? '<aside class="col-replica"><b>✉️ Réplica</b>' + c.replica.map(function (r) {
          return '<p>' + esc(r.texto) + '</p><small>' + esc(r.quien) + ' · ' + esc(r.fecha) + '</small>';
        }).join('') + '</aside>' : '') +
        (c.postura && c.postura.length ? '<aside class="col-postura"><b>🗣️ Postura de la parte aludida</b>' + c.postura.map(function (r) {
          return '<p>' + esc(r.texto) + '</p><small>' + esc(r.quien) + ' · ' + esc(r.fecha) +
            (r.url ? ' · <a href="' + esc(r.url) + '" target="_blank" rel="noopener noreferrer">su documento ↗</a>' : '') + '</small>';
        }).join('') + '<small>En sus palabras: no la calificamos.</small></aside>' : '') +
        '<p class="col-replica-pie">¿Esta columna te alude con un dato inexacto o falso? <a href="derecho-de-replica.html">Ejerce tu derecho de réplica</a>: se publica gratis, íntegra y sin comentarios.</p>' +
        '<div class="col-acciones">' +
          btnSeguir(c) +
          '<button type="button" class="col-copiar" data-id="' + esc(c.id) + '">🔗 Copiar enlace</button>' +
          '<button type="button" class="col-cerrar">Cerrar la columna ▴</button>' +
        '</div>' +
      '</div>' +
    '</article>';
  }

  var filtros = { n: 'todas', o: 'todas' };
  function suyas(g) { return COLUMNAS.filter(function (c) { return g === 'n' ? NOTICIA[c.seccion] : !NOTICIA[c.seccion]; }); }
  function rejilla(g) {
    var el = g === 'n' ? raizN : raiz, secs = g === 'n' ? SEC_N : SEC_O;
    if (!el) return;
    var todas = suyas(g);
    var lista = todas.filter(function (c) { return filtros[g] === 'todas' || c.seccion === filtros[g]; });
    el.innerHTML =
      '<nav class="col-secciones" aria-label="' + (g === 'n' ? 'Secciones de las noticias' : 'Secciones de la Columna') + '">' +
        secs.map(function (s) {
          var n = s[0] === 'todas' ? todas.length : todas.filter(function (c) { return c.seccion === s[0]; }).length;
          return '<button type="button" data-g="' + g + '" data-sec="' + s[0] + '" aria-pressed="' + (filtros[g] === s[0]) + '">' + s[1] + ' <small>' + n + '</small></button>';
        }).join('') +
      '</nav>' +
      (g === 'n'
        ? '<p class="col-aviso"><b>Noticia, no opinión.</b> Aquí va lo que pasó y lo que consta en el documento oficial. «Al momento» trae las notas breves del día; ' +
          '«Verificamos», el cotejo de lo que circula en redes, afirmación por afirmación. Un proceso abierto no es una condena, y una cifra «por aclarar» no es un robo probado.</p>'
        : '<p class="col-aviso"><b>Opinión, con documentos.</b> La Columna del Erario es nuestro argumento sobre el uso del dinero público, y cada argumento descansa en ' +
          'un documento oficial: una sentencia, una resolución, un informe de la Auditoría Superior o el Diario Oficial. Opinamos sobre decisiones públicas, nunca sobre la vida privada. ' +
          'Estas columnas sustituyen las fichas de personajes de la Enciclopedia, retiradas en septiembre de 2026 porque no citaban fuentes.</p>') +
      (lista.length ? '<div class="col-rejilla">' + lista.map(articulo).join('') + '</div>'
                    : '<p class="col-vacio">Todavía no hay columnas verificadas en esta sección.</p>') +
      (g === 'o' ? '<details class="col-fuera"><summary>🧺 Lo que dejamos fuera y por qué <small>(' + DESCARTADO.length + ')</small></summary>' +
        '<p>Las fichas viejas de la Enciclopedia decían mucho más. Esto es lo que buscamos y no pudimos sostener con un documento oficial. ' +
        'Cuando el documento existe pero aún no lo abrimos, la falta es nuestra y lo decimos así.</p>' +
        '<ul>' + DESCARTADO.map(function (x) {
          return '<li><b>' + esc(x.tema) + ':</b> ' + esc(x.afirmacion) + '<br><span>' + esc(x.motivo) + '</span></li>';
        }).join('') + '</ul>' +
      '</details>' : '');
  }

  /* La portada: la noticia principal, las que le siguen y, al lado, lo
     último de la Columna. Son llamadas (#col-<id>): la nota completa vive
     una sola vez, en su sección. */
  function resumenCotejo(c) {
    if (!c.cotejo) return '';
    var ok = c.cotejo.filter(function (x) { return x.res === 'consta' || x.res === 'matiz'; }).length;
    var pend = c.cotejo.filter(function (x) { return x.res === 'pendiente'; }).length;
    var no = c.cotejo.filter(function (x) { return x.res === 'no consta'; }).length;
    return '<span class="nt-cotejo-mini">' + (ok ? '✅ ' + ok + ' con documento' : '') + (no ? ' · ❌ ' + no + ' sin documento' : '') + (pend ? ' · ⏳ ' + pend + ' por probar' : '') + '</span>';
  }
  function llamada(c, clase) {
    return '<li class="' + clase + '"><a href="' + COL + '#col-' + esc(c.id) + '"><span class="col-kicker">' + esc(c.seccion === 'Verificado' ? 'Verificamos' : c.seccion) + '</span>' +
      '<b>' + esc(c.titulo) + '</b></a>' + resumenCotejo(c) + '</li>';
  }
  function portada() {
    if (!raizP) return;
    var nt = suyas('n'), op = suyas('o');
    var lead = nt[0];
    raizP.innerHTML = franja() +
      '<div class="nt-portada">' +
        (lead ? '<article class="nt-lead">' +
          '<a class="nt-lead-a" href="' + COL + '#col-' + esc(lead.id) + '">' + figura(lead, true) +
            '<span class="col-kicker">' + esc(lead.seccion) + '</span><h3 class="nt-lead-tit">' + esc(lead.titulo) + '</h3></a>' +
          '<p class="nt-lead-balazo">' + esc(lead.balazo) + '</p>' +
          '<p class="col-firma">Redacción Auditavisión · ' + (lead.fecha ? esc(lead.fecha) + ' · ' : '') + 'Con documentos oficiales</p>' + resumenCotejo(lead) +
        '</article>' : '') +
        '<div class="nt-mas"><h3 class="nt-col-tit">Más noticias</h3><ul class="nt-llamadas">' + nt.slice(1, 6).map(function (c) { return llamada(c, 'nt-llamada'); }).join('') + '</ul>' +
          '<a class="nt-ver-todo" href="#al-momento">Todas las noticias (' + nt.length + ') ➔</a></div>' +
        '<aside class="nt-op" aria-label="La Columna del Erario"><h3 class="nt-col-tit">✒️ Opinión</h3><p class="nt-op-lema">La Columna del Erario</p><ul class="nt-llamadas">' +
          op.slice(0, 4).map(function (c) { return llamada(c, 'nt-llamada nt-llamada-op'); }).join('') + '</ul>' +
          '<a class="nt-ver-todo" href="#columnas">Toda la Columna (' + op.length + ') ➔</a></aside>' +
      '</div>';
  }

  /* Seguimiento: los casos abiertos con lo que falta para cerrarlos y, al
     inicio, los que sigue el lector (solo en su navegador). */
  function seguimiento() {
    if (!raizS) return;
    var casos = COLUMNAS.filter(function (c) { return c.sigue && c.sigue.length; });
    var docs = casos.reduce(function (s, c) { return s + c.sigue.length; }, 0);
    raizS.innerHTML = panelSigo() +
      '<h3 class="nt-sub">📂 Casos abiertos: ' + casos.length + ' casos, ' + docs + ' documentos por llegar</h3>' +
      '<ol class="nt-casos">' + casos.map(function (c) {
        return '<li class="nt-caso"><div class="nt-caso-cab"><span class="col-kicker">' + esc(c.seccion === 'Verificado' ? 'Verificamos' : c.seccion) + '</span>' +
          '<a href="' + COL + '#col-' + esc(c.id) + '"><b>' + esc(c.titulo) + '</b></a>' +
          '<small>Revisado al ' + esc(c.actualizado || c.fecha || 'sin fecha') + ' · ' + c.sigue.length + (c.sigue.length === 1 ? ' documento' : ' documentos') + ' por llegar</small></div>' +
          '<ul class="nt-caso-falta">' + c.sigue.slice(0, 3).map(function (x) {
            return '<li><a href="' + esc(x.url) + '" target="_blank" rel="noopener noreferrer">' + esc(x.que) + ' ↗</a></li>';
          }).join('') + (c.sigue.length > 3 ? '<li><a href="' + COL + '#col-' + esc(c.id) + '">y ' + (c.sigue.length - 3) + ' más en la nota ➔</a></li>' : '') + '</ul>' +
          btnSeguir(c) + '</li>';
      }).join('') + '</ol>';
  }

  function abrir(art, abrirla, desplazar) {
    var btn = art.querySelector('.col-leer'), cuerpo = art.querySelector('.col-cuerpo');
    btn.setAttribute('aria-expanded', abrirla ? 'true' : 'false');
    btn.textContent = abrirla ? 'Leyendo ▾' : 'Leer completa ➔';
    cuerpo.hidden = !abrirla;
    var c = porId(art.id.slice(4));
    if (abrirla && c && novedad(c)) {
      sigo[c.id] = c.actualizado || '';
      sigoGuardar();
      var nv = art.querySelector('.col-art-tx .col-nuevo');
      if (nv) nv.remove();
      repintarSigo();
    }
    art.classList.toggle('col-abierta', abrirla);
    if (desplazar) {
      var nav = document.querySelector('.site-top-nav');
      document.body.classList.add('cabecera-compacta');
      var alto = (nav ? nav.getBoundingClientRect().height : 0) + 56;
      window.scrollTo({ top: Math.max(0, art.getBoundingClientRect().top + window.pageYOffset - alto - 12), behavior: 'smooth' });
    }
  }

  document.addEventListener('click', function (e) {
    var sec = e.target.closest('.col-secciones button');
    if (sec) { filtros[sec.getAttribute('data-g')] = sec.getAttribute('data-sec'); rejilla(sec.getAttribute('data-g')); return; }
    var leer = e.target.closest('.col-leer');
    if (leer) {
      var art = leer.closest('.col-art');
      abrir(art, leer.getAttribute('aria-expanded') !== 'true', true);
      return;
    }
    var cerrar = e.target.closest('.col-cerrar');
    if (cerrar) { abrir(cerrar.closest('.col-art'), false, true); return; }
    var seg = e.target.closest('.col-seguir');
    if (seg) {
      var cs = porId(seg.getAttribute('data-id'));
      if (sigue(cs)) delete sigo[cs.id]; else sigo[cs.id] = cs.actualizado || '';
      sigoGuardar();
      [].forEach.call(document.querySelectorAll('.col-seguir[data-id="' + cs.id + '"]'), function (b) { b.outerHTML = btnSeguir(cs); });
      repintarSigo();
      return;
    }
    var copiar = e.target.closest('.col-copiar');
    if (copiar) {
      var url = location.href.split('#')[0] + '#col-' + copiar.getAttribute('data-id');
      var listo = function () { copiar.textContent = '✅ Enlace copiado'; setTimeout(function () { copiar.textContent = '🔗 Copiar enlace'; }, 2200); };
      if (navigator.clipboard) navigator.clipboard.writeText(url).then(listo, function () { prompt('Copia este enlace:', url); });
      else prompt('Copia este enlace:', url);
    }
  });

  /* Réplicas y posturas (pedido del autor, 28-10-2026: «un apartado para
     derecho de réplica, postura»). Lista las columnas que ya traen una u otra;
     vive en la sección #replica de noticias-relevantes.html. */
  var rep = document.getElementById('columnasReplicas');
  if (rep) {
    var con = COLUMNAS.filter(function (c) { return (c.replica && c.replica.length) || (c.postura && c.postura.length); });
    rep.innerHTML = con.length
      ? '<ul class="col-rep-lista">' + con.map(function (c) {
          var n = (c.replica || []).length, m = (c.postura || []).length;
          return '<li><a href="' + COL + '#col-' + esc(c.id) + '">' + esc(c.titulo) + '</a> <small>' +
            [n ? n + (n > 1 ? ' réplicas' : ' réplica') : '', m ? m + (m > 1 ? ' posturas' : ' postura') : ''].filter(Boolean).join(' · ') + '</small></li>';
        }).join('') + '</ul>'
      : '<p class="col-rep-vacio">Hasta hoy nadie aludido en las ' + COLUMNAS.length + ' notas y columnas nos ha pedido una réplica, ' +
        'y no hemos recibido posturas en documento propio. Cuando llegue una, aparecerá aquí y en su nota, y quien sigue el caso recibirá el aviso.</p>';
  }

  rejilla('n');
  rejilla('o');
  portada();
  seguimiento();

  /* Enlace directo a una columna (#col-<id>): abre la pestaña y la columna. */
  function irAColumna() {
    var h = (function () { try { return decodeURIComponent(location.hash.slice(1)); } catch (e) { return ''; } })();
    if (h.indexOf('col-') !== 0) return;
    var art = document.getElementById(h);
    if (!art) return;
    var pest = document.getElementById('pestana-noticias');
    if (pest && pest.getAttribute('aria-selected') !== 'true') pest.click();
    setTimeout(function () { abrir(art, true, true); }, 60);
  }
  window.addEventListener('hashchange', irAColumna);
  if (location.hash.indexOf('#col-') === 0) window.addEventListener('load', function () { setTimeout(irAColumna, 420); });
})();
