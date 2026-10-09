/* Auditavisión · Aprende › Noticias relevantes (09-10-2026).
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

  var EDICION = '9 de octubre de 2026';
  var SECCIONES = [
    ['todas', 'Todas'],
    ['Personajes', 'Personajes'],
    ['Hechos', 'Hechos'],
    ['Historia', 'Historia']
  ];
  /* Ilustración de cada sección cuando la columna no trae retrato. */
  var ILUS = { Personajes: ['🧑‍⚖️', 'tinta'], Hechos: ['🗂️', 'sepia'], Historia: ['📜', 'oliva'] };

  /* Cada columna: {id, seccion, titulo, balazo, cuerpo[], dato_curioso,
     cifras[{valor, etq, estado, fuente, url}], fuentes[{nombre, url}],
     actualizado, icono?, imagen?{src, alt, credito}} */
  var COLUMNAS = [
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
 }
];

  var raiz = document.getElementById('columnasDiario');
  if (!raiz) return;

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
        '<span class="col-kicker">' + esc(c.seccion) + '</span>' +
        '<h4 class="col-titular">' + esc(c.titulo) + '</h4>' +
        '<p class="col-balazo">' + esc(c.balazo) + '</p>' +
        '<p class="col-firma">Redacción Auditavisión · Con documentos oficiales</p>' +
        '<button type="button" class="col-leer" aria-expanded="false" aria-controls="col-cuerpo-' + esc(c.id) + '">Leer la columna ➔</button>' +
      '</div>' +
      '<div class="col-cuerpo" id="col-cuerpo-' + esc(c.id) + '" hidden>' +
        (c.cuerpo || []).map(function (p, k) { return '<p' + (k === 0 ? ' class="col-capitular"' : '') + '>' + esc(p) + '</p>'; }).join('') +
        (c.dato_curioso ? '<aside class="col-dato"><b>💡 Dato curioso</b><p>' + esc(c.dato_curioso) + '</p></aside>' : '') +
        (cifras ? '<ul class="col-cifras" aria-label="Cifras de la columna">' + cifras + '</ul>' : '') +
        '<div class="col-fuentes"><b>📎 Documentos que la sostienen</b><ol>' + fuentes + '</ol>' +
          (c.actualizado ? '<p class="col-act">Verificado al ' + esc(c.actualizado) + '.</p>' : '') +
        '</div>' +
        '<div class="col-acciones">' +
          '<button type="button" class="col-copiar" data-id="' + esc(c.id) + '">🔗 Copiar enlace a esta columna</button>' +
          '<button type="button" class="col-cerrar">Cerrar la columna ▴</button>' +
        '</div>' +
      '</div>' +
    '</article>';
  }

  var filtro = 'todas';
  function pintar() {
    var lista = COLUMNAS.filter(function (c) { return filtro === 'todas' || c.seccion === filtro; });
    raiz.innerHTML =
      '<header class="col-cabezal">' +
        '<div class="col-cabezal-linea"><span>Edición del ' + EDICION + '</span><span>Cada cifra, con su documento</span></div>' +
        '<h3 class="col-nombre">La Columna del Erario</h3>' +
        '<p class="col-lema">Personajes y hechos del dinero público que vale la pena conocer</p>' +
        '<nav class="col-secciones" aria-label="Secciones del diario">' +
          SECCIONES.map(function (s) {
            var n = s[0] === 'todas' ? COLUMNAS.length : COLUMNAS.filter(function (c) { return c.seccion === s[0]; }).length;
            return '<button type="button" data-sec="' + s[0] + '" aria-pressed="' + (filtro === s[0]) + '">' + s[1] + ' <small>' + n + '</small></button>';
          }).join('') +
        '</nav>' +
      '</header>' +
      '<p class="col-aviso">Estas columnas sustituyen las fichas de personajes de la Enciclopedia, retiradas en septiembre de 2026 porque no citaban fuentes. ' +
        'Aquí solo entra lo que sostiene un documento oficial: una sentencia, una resolución, un informe de la Auditoría Superior o el Diario Oficial. ' +
        'Un proceso abierto no es una condena, y una cifra «por aclarar» no es un robo probado.</p>' +
      (lista.length ? '<div class="col-rejilla">' + lista.map(articulo).join('') + '</div>'
                    : '<p class="col-vacio">Todavía no hay columnas verificadas en esta sección.</p>') +
      '<details class="col-fuera"><summary>🧺 Lo que dejamos fuera y por qué <small>(' + DESCARTADO.length + ')</small></summary>' +
        '<p>Las fichas viejas de la Enciclopedia decían mucho más. Esto es lo que buscamos y no pudimos sostener con un documento oficial. ' +
        'Cuando el documento existe pero aún no lo abrimos, la falta es nuestra y lo decimos así.</p>' +
        '<ul>' + DESCARTADO.map(function (x) {
          return '<li><b>' + esc(x.tema) + ':</b> ' + esc(x.afirmacion) + '<br><span>' + esc(x.motivo) + '</span></li>';
        }).join('') + '</ul>' +
      '</details>';
  }

  function abrir(art, abrirla, desplazar) {
    var btn = art.querySelector('.col-leer'), cuerpo = art.querySelector('.col-cuerpo');
    btn.setAttribute('aria-expanded', abrirla ? 'true' : 'false');
    btn.textContent = abrirla ? 'Leyendo la columna ▾' : 'Leer la columna ➔';
    cuerpo.hidden = !abrirla;
    art.classList.toggle('col-abierta', abrirla);
    if (desplazar) {
      var nav = document.querySelector('.site-top-nav');
      document.body.classList.add('cabecera-compacta');
      var alto = nav ? nav.getBoundingClientRect().height : 0;
      window.scrollTo({ top: Math.max(0, art.getBoundingClientRect().top + window.pageYOffset - alto - 12), behavior: 'smooth' });
    }
  }

  raiz.addEventListener('click', function (e) {
    var sec = e.target.closest('.col-secciones button');
    if (sec) { filtro = sec.getAttribute('data-sec'); pintar(); return; }
    var leer = e.target.closest('.col-leer');
    if (leer) {
      var art = leer.closest('.col-art');
      abrir(art, leer.getAttribute('aria-expanded') !== 'true', true);
      return;
    }
    var cerrar = e.target.closest('.col-cerrar');
    if (cerrar) { abrir(cerrar.closest('.col-art'), false, true); return; }
    var copiar = e.target.closest('.col-copiar');
    if (copiar) {
      var url = location.href.split('#')[0] + '#col-' + copiar.getAttribute('data-id');
      var listo = function () { copiar.textContent = '✅ Enlace copiado'; setTimeout(function () { copiar.textContent = '🔗 Copiar enlace a esta columna'; }, 2200); };
      if (navigator.clipboard) navigator.clipboard.writeText(url).then(listo, function () { prompt('Copia este enlace:', url); });
      else prompt('Copia este enlace:', url);
    }
  });

  pintar();

  /* Enlace directo a una columna (#col-<id>): abre la pestaña y la columna. */
  function irAColumna() {
    var h = decodeURIComponent(location.hash.slice(1));
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
