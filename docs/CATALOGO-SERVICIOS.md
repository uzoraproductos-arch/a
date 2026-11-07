# Del activo al servicio: el catálogo para monetizar Auditavisión

**Pedido del autor, 07-11-2026:** «con nuestro modelo de negocios, lo que
podemos ofrecer, la construcción de nuestra base de datos, nuestros pilares…
nuestro contenido, los servicios, las herramientas, aplicaciones… transmitirlo
a ciertos servicios para poder monetizar… WiseCricket como un competidor…
tener cosas que él tiene o incluso mejorarlas, y si no, basarnos en su
estructura y arquitectura».

Este documento continúa `docs/MODELO-DE-NEGOCIO.md` (los nueve bloques) y
`docs/FRAUDE-MERCADO-Y-HOSPEDAJE.md` §3.1 (lo que hace WiseCricket). **No trae
precios**: §2 de AGENTS.md vale también aquí, y los primeros saldrán de los
encargos piloto.

---

## 0. La regla que no se mueve: «la prueba de la línea»

La información nunca se cobra. Se cobra **que lo hagamos por ti, que lo
recordemos o que te avisemos** (`GRATIS_PAGO` de `apartados.py`). Cada
servicio de este catálogo pasa esa prueba; el que no la pase no entra.

| Se cobra | No se cobra nunca |
|---|---|
| El trabajo: revisar, cruzar, redactar, firmar el entregable | Consultar una cifra, una ley, un mapa o la lista 69-B |
| La memoria: seguir un caso, guardar el historial de una cartera | Retirar, suavizar o retrasar lo que publicamos |
| El aviso: enterarte a tiempo de un cambio | Una cifra «a la medida» del cliente |
| El cómputo: lotes grandes, entregas en formato de tu sistema | Los datos personales de nadie |

---

## 1. El inventario: qué tenemos y qué servicio sale de cada cosa

| # | Activo (ya construido) | Dónde vive | Servicio que sale de ahí | Quién paga | Unidad de cobro |
|---|---|---|---|---|---|
| 1 | Lista 69-B + Vigía 69-B semanal | `sat-69b.js`, `vigia_69b.py` | **Vigía de proveedores**: tu cartera revisada cada semana, con aviso y el plazo que aplica | Empresas, despachos | Por RFC vigilado al mes |
| 2 | Lector de facturas (69-B, cuenta, 4 reglas de ley, REP) | `insp-factura.js`, `lector_cfdi.py` | **Revisión de facturas por lote**, con informe firmado | Despachos, finanzas | Por lote (rango de facturas) |
| 3 | Contratos de ComprasMX + cruce con la 69-B | `contratos-publicos.html` | **Ficha de debida diligencia del proveedor** | Cumplimiento, PLD, compras | Por ficha |
| 4 | Señales de fraccionamiento | `fraccionamiento.py` | **Revisión de compras de una unidad** (para órganos de control y regidurías) | OIC, regidurías, congresos | Por unidad y periodo |
| 5 | Revisa tu estado de resultados (6 dimensiones) | `insp-resultados.js` | **Diagnóstico financiero** de una empresa o de un proveedor que entrega sus estados | Compras, crédito, inversión | Por diagnóstico |
| 6 | Auditor de entes, estados de cuenta, salud financiera, Planisferio | `herramienta-inspector-entes.html`, `planisferio-*.html` | **Expediente del ente antes de la sesión** (cabildo, cuenta pública) | Regidurías, congresos, OSC | Por expediente |
| 7 | Informes de la ASF, «Documentar para sancionar», «Cómo se audita» | `informes-*.html`, `aprende-auditoria.html` | **Taller «Documentar para sancionar»** y otros talleres | OIC, despachos, universidades | Por taller o por persona |
| 8 | Verificador de notas, puntos ciegos, Mesa de redacción | `noticias-verifica.html` | **Revisión documental para medios** antes de publicar | Medios, periodistas | Por revisión |
| 9 | Nepotismo y parentesco (tabla `ALCANCE`) | `herramienta-inspector-nepotismo.html` | **Revisión de integridad de un nombramiento** (qué ley alcanza a cada parentesco) | OIC, áreas jurídicas | Por consulta |
| 10 | Auditor Virtual + dictamen sellado | `herramienta-inspector-pregunta.html` | **Licencia institucional** (universidades, dependencias, medios) | Instituciones | Por año y por usuarios |
| 11 | La base con huella (pilar 12), la bóveda | `docs/BASE-DE-DATOS.md`, `boveda.py` | **Entrega de datos en tu formato** (CSV o API con aviso de cambios). La consulta sigue gratis; se cobra la entrega y el aviso | Medios de datos, academia, despachos | Por suscripción |
| 12 | Mi Auditavisión (tablero en el navegador) | `insp-mia.js` | **Plan profesional**: tu cartera guardada y vigilada por nosotros, no solo en tu navegador | Empresas, despachos | Mensual |

---

## 2. Frente a WiseCricket, módulo por módulo

Cuatro decisiones posibles: **igualar**, **mejorar**, **solo su estructura**
o **no hacerlo**.

| Módulo de WiseCricket | Decisión | Cómo lo hacemos nosotros | Estado |
|---|---|---|---|
| Auditoría de cada CFDI contra la ley | **Mejorar** | Mismas señales con su artículo, más la 69-B y los contratos públicos del emisor, **sin pedir la CIEC** | Hecho (4 reglas); faltan retenciones de ISR y más reglas, cada una cotejada |
| Complementos de pago (REP) | **Igualar** | Empate por UUID en el lote | Hecho |
| Pide correcciones al proveedor | **Igualar** | Borrador de carta con cada señal y su artículo; la manda el cliente | Siguiente entrega |
| Conciliación banco, póliza y CFDI | **Igualar, por etapas** | El estado de cuenta en CSV se lee en el navegador, como el estado de resultados | Por hacer |
| Materialidad | **Mejorar** | **Expediente de materialidad del art. 69-B**: contrato, factura, pago y la prueba pública de que el proveedor existe (contratos, domicilio, listas). Lo que el octavo párrafo del 69-B pide para no perder la deducción | Guía y servicio por encargo; es el servicio más cercano a la profesión del autor |
| Wiki de contratos | **Solo estructura** | Ya existe para los contratos públicos; los del cliente, solo por encargo | — |
| «Fiscalista digital» | **Mejorar el mensaje** | «Tu revisor de proveedores» que mira **hacia afuera** | Hecho en la página |
| Descarga masiva del SAT y buzón tributario | **No** | Piden la CIEC o la e.firma: romperían «tus archivos no se suben» | Decisión tomada |
| IVA, ISR y pagos provisionales | **No** | Es trabajo de despacho; nos haría competir con nuestros clientes | Decisión tomada |
| ISO/IEC 27001 | **No por ahora; compensar** | «No guardamos tus archivos» es más fuerte para una empresa chica que un certificado; la certificación se evalúa cuando haya ingresos | Decisión del autor |
| Logos de clientes | **Solo estructura** | Los sustituyen las cifras oficiales; cuando haya pilotos, su testimonio con permiso escrito | Pendiente de pilotos |
| Arquitectura de su página | **Copiada la estructura** | Portada, ejemplo, módulos, cómo funciona, hoy/con, perfiles, novedades, cierre | Hecho (sello 20261107o) |

**Lo que solo tenemos nosotros** (nadie en el mercado leído lo ofrece):
la 69-B vigilada por cartera, los contratos públicos del proveedor, el cruce
con la ASF, el fraccionamiento, la revisión del dinero público para regidurías
y la metodología con fundamento de cada señal.

---

## 3. Los paquetes (la estructura de «planes» de WiseCricket, con nuestros servicios)

| Plan | Para quién | Qué incluye | Cómo se cobra |
|---|---|---|---|
| **Gratis** | Cualquiera | Toda la consulta, el Auditor, los lectores en tu navegador, buscar un RFC | Nunca |
| **Profesional** | Empresa con un RFC | Vigía de proveedores, Mi Auditavisión guardado por nosotros, carta al proveedor | Suscripción mensual (rango por número de RFC vigilados) |
| **Despacho** | Despachos contables y jurídicos | Lo anterior para varios clientes, revisión de lotes con informe, expediente de materialidad con descuento | Suscripción por número de clientes |
| **Por encargo** | Cualquiera | Ficha de debida diligencia, expediente, revisión documental, diagnóstico financiero | Cotización por escrito |
| **Institución** | Universidades, OIC, medios | Licencia del Auditor, talleres, entrega de datos | Convenio anual |

---

## 4. El orden recomendado para cobrar el primer peso

| Paso | Qué | Por qué primero |
|---|---|---|
| 1 | **Expediente de materialidad (art. 69-B)** y **Ficha de debida diligencia** como encargos piloto | Ya hay herramienta, el dolor es legal y tiene plazo, y el autor es abogado |
| 2 | **Taller «Documentar para sancionar»** | El material ya existe; un taller se vende sin plataforma de pago |
| 3 | **Carta al proveedor** (entrega 3) | Cierra el ciclo del Lector y lo iguala con WiseCricket |
| 4 | **Vigía de proveedores con aviso por correo** | Es la suscripción: hábito y memoria |
| 5 | **Conciliación con el estado de cuenta en CSV** | Iguala el módulo que más usan los despachos |

---

## 4 bis. Lo que tomamos de getquin

Su estudio está en `docs/FRAUDE-MERCADO-Y-HOSPEDAJE.md` §3.4. Lo que entra al
catálogo: **planes con su lista de «qué agrega»** a la vista, la pregunta
**«¿Cómo nos sostenemos?»**, **contadores de la base** en la portada, una
**página por función** para Google, **«Deja el Excel de proveedores»**,
**seguir** a un ente o un proveedor y un **calendario de plazos** del 69-B.
Lo que no: publicidad y carteras compartidas.

## 5. Puntos ciegos

1. **No hay precios ni clientes.** Ningún paquete tiene precio hasta 3 a 5 pilotos con cotización escrita.
2. **El cobro no está montado:** falta la forma jurídica, la facturación (CFDI propio) y el canal de pago.
3. **Materialidad es práctica jurídica.** Si se ofrece como asesoría, la responsabilidad profesional es del autor; si se ofrece como reunión de documentos, hay que decirlo así.
4. **El Vigía con aviso necesita guardar la cartera del cliente** en nuestra base: rompe «nada se guarda» para ese plan, y el aviso de privacidad tiene que decirlo.
5. **Vender a los auditados** (municipios) sigue siendo decisión del autor (`MODELO-DE-NEGOCIO.md`, «Lo que decide el autor», 6).

## 6. Lo que decide el autor

1. Si el **expediente de materialidad** entra como servicio de la página, y con qué alcance (asesoría jurídica o reunión de documentos).
2. Si los **planes** se muestran en la página sin precio («se cotiza») o se esperan a los pilotos.
3. Si el plan Profesional guarda la cartera en nuestra base (y el cambio al aviso de privacidad).
4. La **entrega de datos** como suscripción: si pasa la prueba de la línea a su juicio.
