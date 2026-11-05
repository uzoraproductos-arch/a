# El fraude en números, el registro de empresas, la competencia y el hospedaje

Investigación del 05-11-2026, a pedido del autor: «investigar los números que
hay aquí en México para nosotros defender nuestros servicios», saber si se
puede seguir a las empresas que cambian de razón social, revisar qué hacen
WiseCricket y Legal Hunt, y explicar por qué hay que dejar GitHub Pages y
cuánto cuesta.

Va con la regla de siempre (AGENTS.md §2). Cada cifra es **oficial** (leída
en su documento), **derivado** (con la operación dicha) o **pendiente** (con
quién la debe). Lo que solo sale en prensa o en directorios va **sin
verificar**, y no se usa para vender.

---

## 1. El fraude en México: lo que dicen los documentos

### 1.1 Las personas (INEGI, ENVIPE 2026, datos de 2025)

Fuente: INEGI, Comunicado de prensa 50/26, 10-09-2026. Se leyó el PDF del
comunicado.

| Dato | Cifra | Estado |
|---|---|---|
| El delito más frecuente | **Fraude**, por delante de extorsión y de robo en calle o transporte | oficial |
| Tasa de fraude contra mujeres | 7,947 por cada 100 mil | oficial |
| Tasa de fraude contra hombres | 8,688 por cada 100 mil | oficial |
| Qué incluye «fraude» | Fraude bancario y fraude a la o al consumidor | oficial (nota 1 de la gráfica 1) |
| Lo que perdió en promedio cada víctima de fraude | **$7,551** | oficial |
| Delitos que no se denunciaron o no se investigaron (cifra oculta) | **93.4 %** de 33.8 millones | oficial |
| Costo del delito para los hogares | $267.3 mil millones (1.06 % del PIB) | oficial |

La prensa publicó una tasa total de fraude de 8,290 por cada 100 mil
habitantes ([ADN40](https://www.adn40.mx/seguridad/2026-09-10/fraude-y-extorsion-lideran-delitos-en-mexico-en-2025-envip-del-inegi)).
Esa cifra **no está en el comunicado**. Para usarla hay que cotejarla en los
tabulados de la ENVIPE 2026, así que por ahora queda como **pendiente de
cotejo**. La falta es de la plataforma, porque el INEGI sí publica los
tabulados.

### 1.2 Las empresas (INEGI, ENVE 2024, datos de 2023)

Fuente: INEGI, Comunicado de prensa 780/24, 10-12-2024. Se leyó el PDF.

| Dato | Cifra | Estado |
|---|---|---|
| Unidades económicas víctimas de algún delito | 1.3 millones, el **27.2 %** del país | oficial |
| Unidades económicas grandes víctimas de algún delito | **47.3 %** | oficial |
| Delitos contra unidades económicas | 2.9 millones (2.2 por unidad víctima) | oficial |
| Delitos más frecuentes | Extorsión (1,562 por cada 10 mil), robo de mercancía (1,030), robo hormiga (1,002) | oficial |
| Delitos contra unidades económicas que no se denunciaron o no se investigaron | **90.3 %** | oficial |
| Costo total del delito para las unidades económicas | **$124.3 mil millones (0.51 % del PIB)** | oficial |
| Lo que gastaron en protegerse | $67.2 mil millones (54.0 % del costo) | oficial |
| Cuánto del costo corresponde al fraude contra empresas | — | **pendiente** |

**Pendiente:** el comunicado agrupa el fraude («fraude bancario y fraude al
consumo del establecimiento») sin dar su costo aparte. El desglose debe estar
en los tabulados de la ENVE 2024 del INEGI
(<https://www.inegi.org.mx/programas/enve/2024/>). La falta es de la
plataforma: hay que integrarlo.

### 1.3 Las facturas falsas (SAT, lista 69-B)

Fuente: el listado completo del artículo 69-B del CFF, que la plataforma ya
tiene con su huella SHA-256 (`assets/auditor/data/sat-69b.js`, corte «31 de
diciembre de 2025»). Las cuentas son nuestras sobre el archivo oficial.

| Situación | Contribuyentes | Estado |
|---|---|---|
| Definitivo (sus facturas «no producen ni produjeron efecto fiscal alguno», párrafo quinto) | **11,270** (8,642 empresas y 2,628 personas físicas) | derivado (conteo del archivo del SAT) |
| Presunto (tiene 15 días para desvirtuar; párrafo segundo) | 986 | derivado |
| Sentencia favorable | 1,638 | derivado |
| Desvirtuado | 340 | derivado |
| **Total en la lista** | **14,234** | derivado |

**El monto facturado por las empresas fantasma es pendiente.** La prensa
repite cifras de 1.6 a 2 billones de pesos, pero no encontramos el documento
del SAT que las sostenga. Al SAT le toca publicarlo, y no lo ha hecho:
falta de transparencia de esa dependencia.

### 1.4 Las quejas por fraude financiero (CONDUSEF)

- La CONDUSEF publica sus cifras **por entidad**. Por ejemplo, en Ciudad de
  México hubo 40,688 reclamaciones en 2025 y alrededor del 31.6 % fueron por
  posible fraude.
- **No encontramos su total nacional de 2025.** Las notas de prensa dan
  cifras que no cuadran entre sí: 1.57 millones de reclamaciones en un
  trimestre, 43,871 en un semestre y «más de ocho millones» en 2024.
- Las cifras de la CONDUSEF quedan **pendientes**: hay que bajar sus
  comunicados y su estadística (<https://www.condusef.gob.mx>) y cotejarlas
  una por una. Hoy el servidor de su estadística respondió con error 503.

### 1.5 Las carpetas de investigación por fraude (SESNSP)

El Secretariado Ejecutivo publica cada mes la incidencia del fuero común, y
el fraude es uno de sus subtipos. **El total nacional de 2025 es pendiente.**
Sale de sumar el subtipo «Fraude» en sus datos abiertos, y eso es trabajo de
la plataforma. Es un buen candidato para un módulo con huella, como los demás.

### 1.6 Qué dicen estos números para vender, sin exagerar

- **El fraude es el delito que más le pasa a la gente** (ENVIPE), y casi nadie
  lo denuncia: el 93.4 % de los delitos queda fuera de toda carpeta de
  investigación. Lo que no se denuncia no aparece en ninguna estadística
  oficial. Por eso la prevención (revisar antes de pagar) vale más que la
  denuncia.
- **Una de cada cuatro empresas** fue víctima de algún delito, y entre las
  grandes, casi una de cada dos (ENVE). El costo del delito para las
  empresas equivale al 0.51 % del PIB.
- **Hay 11,270 contribuyentes definitivos en la 69-B.** Una factura de
  cualquiera de ellos no sirve para deducir, y la lista cambia. Este es el
  argumento del Vigía de proveedores, y es el que sí se puede probar con
  documento.
- **Lo que no se dice:** que el fraude «cuesta X billones» sin documento, o
  que el producto «evita el fraude». El producto avisa de señales para
  revisar con documento oficial, y nada más.

---

## 2. Las actas constitutivas y los cambios de razón social

### 2.1 Dónde vive cada cosa

| Sistema | De quién | Qué tiene | ¿Público? |
|---|---|---|---|
| **SIGER 2.0** (Registro Público de Comercio), <https://rpc.economia.gob.mx> | Secretaría de Economía y registros estatales | El **folio mercantil electrónico** de cada sociedad: constitución, reformas de estatutos (ahí entra el **cambio de denominación**), poderes, fusiones, escisiones, disolución | La publicidad es el objeto del registro (Reglamento del RPC), pero consultar boletas o certificados puede costar derechos. **Por cotejar** qué se ve sin pago y qué no. |
| **PSM** (Publicaciones de Sociedades Mercantiles), <https://psm.economia.gob.mx> | Secretaría de Economía (Acuerdo, DOF 12-06-2015) | Los **avisos** que la ley obliga a publicar: convocatorias a asambleas, reducciones de capital, fusiones y escisiones, balances de liquidación, entre otros | Sí: la consulta de publicaciones es abierta, según su manual |
| **Lista 69-B** del SAT | SAT | RFC, nombre y situación de quien facturó operaciones simuladas | Sí, con descarga |
| **ComprasMX** | Gobierno federal | Contratos públicos por RFC del proveedor | Sí, ya integrado (`assets/auditor/data/comprasmx/`) |

### 2.2 Cómo lo hacen los periodistas

- **Siguen el RFC, no el nombre.** Una sociedad puede cambiar su
  denominación, pero su RFC no cambia. Quien cambia de razón social para
  «limpiarse» sigue apareciendo con el mismo RFC en la 69-B, en ComprasMX y
  en las facturas.
- **Cruzan el folio mercantil** (quién la constituyó, cuándo, con qué capital
  y qué poderes otorgó) con la 69-B, los contratos y las auditorías de la ASF.
- **Leen los avisos del PSM:** una fusión o una liquidación justo después de
  ganar contratos es una pregunta que conviene hacer.

### 2.3 Qué hace ya la plataforma con esto (hoy)

- **El Vigía 69-B** (`herramientas/vigia_69b.py`, flujo semanal) compara la
  lista nueva del SAT con la nuestra **por RFC**. Además de las altas y los
  cambios de situación, avisa cuando una **empresa con el mismo RFC aparece
  con otra razón social**. Es la forma más barata de seguir los cambios de
  nombre, y sale de un documento oficial.
- ComprasMX ya junta los contratos por RFC.

### 2.4 Qué se puede agregar y con qué cuidado

1. **Avisos del PSM por RFC o denominación** (siguiente paso posible): leer las
   publicaciones de las empresas que ya están en la 69-B o en ComprasMX, como
   punto de partida y con su liga. Antes hay que cotejar las condiciones de
   uso del sistema y si permite consultas automáticas. Si no las permite, se
   hace a mano y por caso.
2. **El folio mercantil del SIGER:** por caso, a pedido y pagado por el
   cliente si causa derechos. No se descarga en masa.
3. **Las personas:** en las actas aparecen socios y apoderados que son
   **personas privadas**. Por AGENTS.md §2 bis no se nombran, y además su
   nombre es un dato personal protegido por la ley de datos personales. En un
   informe para un cliente sí puede ir, como trabajo privado y con su aviso de
   privacidad. En la parte pública de la plataforma, nunca.
4. **El beneficiario controlador** (quién está realmente detrás) no es
   público en México: lo tiene el SAT. **No se infiere** de apellidos ni de
   domicilios. Un apellido igual nunca es prueba (§5 ter).

---

## 3. La competencia: WiseCricket y Legal Hunt

Leído el 05-11-2026 **en sus propios portales**, después de que el autor abrió
la red de la sesión. Es lo que cada empresa dice de sí misma: es su
publicidad, no un cotejo de que funcione así.

### 3.1 WiseCricket (wisecricket.ai) · WISE CRICKET, S.A.P.I. de C.V.

**Cómo se presenta:** «Plataforma de inteligencia fiscal con IA para
empresas». Promete conectar «cada transacción con su materialidad» y cruza
«el SAT, tu ERP, tus bancos y tus contratos».

| Módulo (como lo nombran) | Qué dicen que hace |
|---|---|
| Descarga y auditoría de CFDI | «Descarga todos tus CFDI, sin límite». Revisa cada factura «contra la ley» y dice «el artículo, el monto y cómo corregirlo». Presume detectar «riesgos que otros validadores (solo Anexo 20) dejan pasar». |
| Complementos de pago | Detecta facturas pagadas sin complemento y se lo pide al proveedor por correo, en lote. |
| Conciliación | Liga «cada movimiento bancario con su póliza y su factura, con reglas e IA». |
| IVA e ISR | Determinación mensual del IVA, pagos provisionales de ISR y papeles de trabajo; compara el IVA precargado por el SAT contra la contabilidad. |
| Auditoría contrato a cobro/pago | Convierte contratos escaneados en un calendario de obligaciones y los liga a facturas y pagos. |
| Wiki de contratos | Base de datos de contratos, con preguntas en lenguaje natural y detección de cláusulas que se contraponen. |
| Buzón tributario | Revisa a diario el buzón de cada RFC (hasta 80 buzones) y ordena las notificaciones por plazo (cita CFF arts. 134 y 135). |
| Expediente de materialidad | Reúne el soporte de las operaciones para una carta invitación o una auditoría del SAT. |

**Cómo se conecta:** al SAT con **RFC y CIEC**, y a la contabilidad por el ERP
(nombran SAP, Oracle, CONTPAQi, Microsoft Dynamics, Intelisis, Odoo y Aspel).
Los estados de cuenta se suben.

**Lo demás que dicen:**
- **A quién le vende:** a direcciones de finanzas con varios RFC y miles de
  facturas al mes, y a despachos que llevan decenas o cientos de empresas.
  Su portal muestra ocho clientes: fondos, FIBRAs, desarrolladores
  industriales y servicios financieros.
- **Seguridad:** dicen tener certificación ISO/IEC 27001:2022 y que la
  información del cliente «nunca se utiliza para entrenar modelos de IA».
- **Precio:** no lo publican. «Depende del volumen de información», con
  usuarios ilimitados y prueba de 7 días.

**Lo que no encontramos en su portal:** ninguna mención a la lista 69-B, a
las EFOS, a los contratos públicos ni a la ASF. **WiseCricket mira la
información del propio cliente, no a sus proveedores frente a los documentos
públicos.**

### 3.2 Legal Hunt (legalhunt.com.mx) · Legal Hunt Mex, S.A.P.I. de C.V.

**Cómo se presenta:** «Gobierno corporativo sin papel». Ofrece tres cosas:

- **Libros corporativos:** registro de accionistas, actas de asamblea,
  sesiones de consejo y variaciones de capital, en Word, PDF y Excel.
- **Firma electrónica con constancia NOM-151:** emitida por un prestador de
  servicios de certificación, con validación biométrica.
- **Conexión con el SIGER 2.0:** dice ser «la única plataforma en México que
  integra en tiempo real» con él. Promete alertas «ante cualquier movimiento
  registral: inscripciones, variaciones de capital, cambios de
  representación», por correo y WhatsApp, y descarga de boletas. Es su
  afirmación: no consta cómo se conecta.

**Precios publicados (MXN al mes):**

| Plan | Precio | Qué incluye |
|---|---|---|
| Kick-Off | $399 | 20 firmas, **10 búsquedas en listas negras** y 2 empresas con libros |
| Sprint | $699 | 40 firmas, **15 búsquedas en listas negras** y 4 empresas |
| Velocity | $2,099 | 60 firmas, **20 búsquedas en listas negras** y empresas ilimitadas |
| Planes «Solo Firmas» | $1,299 a $9,999 más IVA | De 100 a 1,100 firmas |

- **IA:** no la ofrece.
- **Sus clientes:** empresas de entretenimiento, fintech, servicios
  financieros, agroindustria, hotelería, SOFOM y notarías. Tiene domicilio en
  Jalisco (WhatsApp con lada 33).

### 3.3 Dónde queda Auditavisión (el hueco, ya con sus portales)

| | WiseCricket | Legal Hunt | Auditavisión |
|---|---|---|---|
| Mira hacia | Dentro: tus CFDI, tu ERP, tus bancos, tus contratos | Dentro: tus libros y tus firmas | **Afuera: tu proveedor y el dinero público**, con documentos oficiales |
| La lista 69-B | No la menciona | «Búsquedas en listas negras» contadas por plan (10 a 20 al mes) | **Toda la lista, gratis y con huella**; el Vigía 69-B avisa cada semana |
| Cambios de una empresa | — | Alertas del SIGER (su folio mercantil) | Cambios de razón social por RFC en la 69-B; contratos en ComprasMX |
| Tus facturas | Las descarga del SAT con tu CIEC | — | **Se leen en tu navegador, no se suben** |
| Precio | A cotizar, para corporativos | $399 a $2,099 al mes | Lo público, gratis; lo que se cobra es el trabajo, la memoria y el aviso |

**Qué sacamos de esto:**

1. **El hueco existe y es nuestro.** Ninguno de los dos cruza al proveedor
   contra la 69-B, los contratos públicos, la ASF y el DOF. El **Vigía de
   proveedores** (producto 1 del plan) no tiene competidor directo en estos
   dos.
2. **Legal Hunt da la referencia de precio.** Una PYME en Jalisco paga hoy de
   $399 a $2,099 al mes por libros, firmas y un puñado de «búsquedas en listas
   negras». Un vigía que revisa **toda la cartera cada semana** cabe en ese
   rango y da más, porque no cuenta búsquedas.
3. **A WiseCricket no se le compite en su terreno** (ERP, CIEC, conciliación y
   pagos provisionales): exige certificación de seguridad, integraciones y
   capital. Sí se le compite en su promesa de «materialidad». La parte
   externa de la materialidad, que el proveedor existe, no está en la 69-B y
   no tiene historial de contratos raros, es justo lo que sale de los
   documentos públicos.
4. **La auditoría interna privada** (revisar las facturas del propio cliente)
   la haríamos a nuestro modo: **por lote y en el navegador, sin pedir la
   CIEC**. Es otra promesa de privacidad, más modesta, y para despachos chicos
   pesa.
5. **Legal Hunt puede ser aliada.** Ellos llevan los libros de la empresa;
   nosotros revisamos a sus proveedores. Pueden recomendarse uno al otro sin
   pisarse.

## 4. Por qué dejar GitHub Pages, y a dónde

### 4.1 El porqué

La documentación oficial de GitHub
([límites de GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits))
dice que Pages **no está pensado ni permitido** como hospedaje gratuito para
«tu negocio en línea, tu sitio de comercio electrónico o cualquier otro sitio
dirigido principalmente a facilitar transacciones comerciales o a dar
software comercial como servicio (SaaS)». Además:

- tiene un límite suave de 100 GB de transferencia al mes y de 1 GB por sitio;
- no deja poner encabezados propios. Por eso el caché queda fijo en
  `max-age=600` y tenemos que subir el sello a mano en cada cambio (AGENTS.md
  §4);
- no hace redirecciones reales: hoy las hacemos con páginas HTML.

Mientras Auditavisión sea solo información pública gratuita, Pages sirve.
**El día que cobre**, aunque sea por el Vigía de proveedores, tiene que estar
en otro lado.

### 4.2 Las opciones

| Opción | Costo | A favor | En contra |
|---|---|---|---|
| **A. Cloudflare Pages + Supabase Pro** (recomendada) | Pages: $0 en su plan gratuito. Supabase Pro: **US$25 al mes** de base, más el cómputo (con US$10 de crédito); su propio ejemplo con dos proyectos chicos da US$35 ([precios de Supabase](https://supabase.com/pricing)) | Ya usamos Cloudflare (el antispam Turnstile). Sin límite de transferencia, encabezados y redirecciones propios, vistas previas por rama (útil para las ramas `ux/`) | **Por cotejar** en sus términos que el plan gratuito permita uso comercial (los blogs dicen que sí). Límite de 20 mil archivos por sitio: hoy hay unas 660 páginas más los datos, así que cabe |
| **B. Vercel Pro + Supabase Pro** (lo que decía LANZAMIENTO.md) | Vercel Pro: **US$20 al mes por miembro**, más Supabase | Muy cómodo; su plan gratuito (Hobby) es solo para uso no comercial | Cuesta más, y el cobro crece por persona del equipo |
| **C. Quedarse en Pages y cobrar en otro dominio** | Solo Supabase | No se muda nada | Dos sitios, dos marcas. Y si la página gratuita lleva a la de pago, sigue siendo un sitio con fines comerciales. No la recomiendo |

**Por qué Supabase Pro sí o sí antes de cobrar:** en el plan gratuito, un
proyecto **se pausa tras una semana sin uso** (dice su página de precios). Un
cliente que paga por alertas no puede encontrarse la base dormida. Además,
Pro da respaldos diarios.

**Cuánto es en pesos:** US$25 a US$45 al mes, al tipo de cambio que publique
Banxico el día del pago. No lo convertimos aquí, porque el tipo de cambio
cambia.

**Cuándo:** en la etapa 2 del plan (meses 3 y 4), antes del primer cobro, no
antes. Mudarse lleva un día: el sitio no se compila y es HTML estático.

---

## 5. Lo que quedó hecho con esta investigación (código)

- **Paso 0.2.** El formulario de Servicios ya manda la solicitud a la base:
  la función `recibir-formulario`, tipo `solicitud`, con antispam. Le
  devuelve un folio al lector. Como lleva nombre y correo, solo se envía si el
  lector acepta el aviso de privacidad, y el aviso ya lo dice.
- **Paso 0.3.** El Vigía 69-B (`herramientas/vigia_69b.py` y
  `.github/workflows/vigia-69b.yml`) corre cada miércoles y deja en
  `docs/sat69b/bandeja.json` las altas, los cambios de situación, las bajas y
  los cambios de razón social por RFC. Detecta y propone: no toca la base.
  Las personas físicas van con el RFC recortado y sin nombre.

## 6. Pendientes que deja

1. Cotejar la tasa total de fraude 2025 en los tabulados de la ENVIPE 2026.
2. Sacar de los tabulados de la ENVE 2024 el costo del fraude contra empresas.
3. El total nacional de la CONDUSEF de 2025 (posible fraude, monto, cuánto se
   recuperó).
4. El total nacional de carpetas por fraude del SESNSP de 2025.
5. Cotejar en la práctica lo que dicen WiseCricket y Legal Hunt (lo de §3 es
   su publicidad); revisar sus avisos de privacidad y términos.
6. Cotejar los términos de Cloudflare Pages (uso comercial en el plan
   gratuito) y los del PSM (consultas automáticas).
