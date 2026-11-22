# Borrador para aprobación: página de venta del Vigía de proveedores

**Estado:** **publicado el 22-11-2026 (sello 20261122q)** en `servicio-seguimiento.html#vigia`, junto con el aviso del
tablero (§8). Lo arma `herramientas/vigia_venta.py` (llave `venta` de la ficha `seguimiento` en `servicios_fichas.py`);
la cifra de la ventana se calcula al generar con `vigia_historial.ventana()`, nunca a mano. **Este archivo queda como
registro del texto aprobado**: un cambio al texto se hace en `vigia_venta.py`.

**Reglas que respeta** (AGENTS.md §2 y §0 quater): nunca un monto; ninguna persona ni empresa real (el ejemplo
es ficticio y lo dice); una coincidencia es una señal para revisar, nunca una acusación; el Vigía no evita el
fraude ni cumple por el cliente; las fechas del SAT son `oficial` y lo que calculamos con ellas, `derivado`.

---

## 1. Encabezado

> ### 📡 Entérate antes de que tu proveedor sea definitivo
>
> El SAT publica cada mes a las empresas que presume que facturan operaciones que no existieron. Desde ese día
> y hasta que las vuelve definitivas pasan, en la mitad de los casos, **208 días o más** (cifra auditada: la cuenta está abajo).
> El Vigía revisa tu lista de proveedores contra cada corte y te avisa el mismo día que lo ve, con el documento.

**Botón principal:** «Cotiza tu Vigía» → `servicios-cotiza.html?servicio=seguimiento` (cotización con opciones a
un toque; nunca un monto).
**Botón secundario:** «Pruébalo gratis con un RFC» → `herramienta-inspector-efos.html`.

## 2. El problema, en una línea

Cuando el SAT publica a una empresa como **definitiva**, se considera, con efectos generales, que «las operaciones
contenidas en los comprobantes fiscales expedidos por el contribuyente en cuestión no producen ni produjeron efecto
fiscal alguno» (Código Fiscal de la Federación, art. 69-B, párrafo quinto) (oficial). Quien les dio efecto fiscal
cuenta con treinta días siguientes a la publicación para acreditar que sí recibió los bienes o servicios, o para
corregir su situación fiscal (párrafo octavo) (oficial). Enterarse tarde cuesta tiempo y papeles.

## 3. Por qué el aviso a tiempo vale (la cifra, con su cuenta)

| Qué | Cifra | Estado | De dónde sale |
|---|---|---|---|
| Personas morales de la lista con fecha de presunto y de definitivo | 10,613 | `derivado` | Columnas «fecha de publicación como presunto» y «como definitivo» del listado completo del SAT, corte al 31-10-2026 (huella `475c99628d90…`). Se dejan fuera las celdas que el SAT no escribió como fecha. |
| Días entre una y otra, mediana | 208 | `derivado` | Definitivo − presunto, por empresa; la mitad tardó 208 o más. |
| La mitad central | de 173 a 272 días | `derivado` | Primer y tercer cuartil. |

**Lo que esta cifra no dice:** no es un plazo de la ley ni una promesa de que habrá ese tiempo; es lo que pasó
con las empresas que ya están en la lista. Cada caso tiene sus fechas. Lo calcula `vigia_historial.py --resumen`.

## 4. Cómo funciona, en tres pasos

1. **Nos das tu lista de RFC.** Un CSV, un TXT o lo pegas de Excel (hasta 2,000 por lote, como en «Revisa a tu
   contraparte»). Las personas físicas no se guardan con su RFC: solo su huella.
2. **Cada corte del SAT, la comparamos.** El flujo semanal «Base al día» baja la 69-B, la cuadra y anota en el
   historial del Vigía cada alta y cada cambio de situación con el día en que lo vio.
3. **Te avisamos con el documento.** Qué cambió (presunto, definitivo, desvirtuado, sentencia favorable), el
   oficio del SAT, la fecha y su liga. Qué hacer con tu proveedor lo decides tú.

## 5. Un ejemplo ficticio, paso a paso

> **Todo en este ejemplo es inventado**: la empresa, su RFC y las fechas. No corresponde a ningún contribuyente.
> Así se vería un aviso real.

| Paso | Día (ficticio) | Qué pasa | Qué recibe el cliente |
|---|---|---|---|
| 1 | 3 de febrero | «Comercializadora Ejemplo, S.A. de C.V.» (RFC de ejemplo `CEJ000000XX0`) entra a la lista de tus proveedores vigilados. | Confirmación: 1 RFC vigilado, sin coincidencias hoy. |
| 2 | 12 de marzo | El SAT publica un corte nuevo y la empresa aparece como **presunta**. | **Aviso del Vigía:** «Tu proveedor CEJ000000XX0 aparece como presunto en el corte del SAT. Oficio …, fecha …, liga al DOF. Una presunción no es una condena: la empresa puede desvirtuarla.» |
| 3 | 12 de marzo | El historial guarda: `[12-mar, P, alta]`. | Su dictamen con folio y huella, para su expediente de control interno. |
| 4 | De marzo a septiembre | Cada corte se vuelve a comparar; mientras no cambie, no hay aviso nuevo. | Nada: el Vigía no hace ruido. |
| 5 | 8 de octubre | El SAT la vuelve **definitiva**. | **Segundo aviso:** el cambio de situación, con los párrafos quinto y octavo del art. 69-B (los treinta días) y la liga. El historial guarda `[8-oct, F, cambio]`. |
| 6 | Cuando lo pida | | **La prueba del aviso previo:** el cliente supo **210 días antes** de que fuera definitiva (8-oct − 12-mar, ficticio) `derivado`, con las dos fechas en el historial. |

Si en el paso 5 la empresa hubiera **desvirtuado** la presunción, el segundo aviso lo diría igual: el Vigía
avisa lo que cambió, no lo califica.

## 6. Lo que el Vigía es y no es

- **Es** una comparación por RFC contra la lista oficial del SAT, cada corte, con fecha y documento.
- **No es** una acusación ni una calificación del proveedor: una coincidencia es una señal para revisar.
- **No evita** el fraude ni cumple tus obligaciones por ti; tampoco sustituye la revisión de tu contador.
- **No guarda** tus facturas ni el nombre de personas físicas. La lista se queda contigo; el aviso dice el RFC
  que tú registraste.

## 7. Preguntas frecuentes (van como preguntas, no como secciones)

- **¿Cuánto cuesta?** Es una suscripción mensual según cuántos RFC vigilas. La cotización te da la forma de
  cobro; no publicamos montos mientras no haya pilotos.
- **¿Qué tan rápido avisa?** El día que el flujo semanal integra el corte nuevo del SAT (los miércoles). El SAT
  publica su listado completo sin calendario fijo.
- **¿Puedo comprobar que me avisaron antes?** Sí: el historial guarda el día en que la plataforma vio cada
  situación, y no se reescribe hacia atrás. Lo que ya estaba en la lista cuando empezó el registro
  (21-11-2026) va como «semilla»: de eso no presumimos aviso previo.
- **¿Y las otras listas?** El Vigía empieza por la 69-B. Las del art. 69, 17-H Bis y 69-B Bis, Sancionados, la
  OFAC y la ONU ya se revisan en «Revisa a tu contraparte»; sumarlas al aviso es la siguiente entrega.

## 8. Lo que falta antes de publicarla (pendientes del autor y técnicos)

1. ~~Aprobación del texto~~: **aprobado el 22-11-2026**, con el nombre «Vigía de proveedores».
2. ~~Cotejar la cita~~: **hecho el 22-11-2026** contra el CFF de la Cámara de Diputados, última reforma DOF
   09-04-2026 (`investigaciones/leyes/CFF.pdf`, huella `be7427b20d35…`). La cita es literal del párrafo quinto: lo que
   pierde efecto son «las operaciones contenidas en los comprobantes», en plural; el plazo de treinta días es del
   párrafo octavo.
3. **El canal: primero el tablero, después el correo** (decisión del 22-11-2026). El aviso vive en «Mis proveedores»
   de Mi Auditavisión (`insp-mia.js`, guardado solo en el navegador, `av-mia`): al abrirlo, compara la lista con el
   historial y dice lo que cambió desde la última visita. No pide datos personales, así que no cambia el aviso de
   privacidad más allá de su renglón en `_AV_NAVEGADOR` si guarda algo nuevo. **El correo va en una segunda entrega**:
   exige guardar una dirección en el servidor, y antes cambia el aviso de privacidad. ~~Falta construir el aviso del
   tablero~~: **hecho el 22-11-2026** (`insp-mia.js`, guarda en `av-mia` la situación vista y el corte; renglón `av-mia`
   en `_AV_NAVEGADOR`).
4. El primer aviso previo «probado con fecha» llegará con el primer corte nuevo del SAT después del 21-11-2026.
