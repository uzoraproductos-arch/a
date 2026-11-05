# Plan de implementación: del pilar de transparencia al primer peso

Pedido del autor, 05-11-2026: «hazme un plan de implementación de lo que se
debería de estar haciendo la plataforma con todos estos objetivos». Los
objetivos que dio:

1. Servicios con inteligencia artificial que la gente necesite y que puedan ser
   muy redituables.
2. Seguir siendo el **pilar de transparencia**: la información pública no se
   cobra; las donaciones sí se reciben.
3. Atender una necesidad real de hoy: el fraude en México, con un perfil de
   **plataforma de prevención**.
4. Repartir el trabajo: el autor es el creativo y se profesionaliza; el agente
   programa y desarrolla.

Se apoya en [MODELO-DE-NEGOCIO.md](MODELO-DE-NEGOCIO.md) (los nueve bloques) y
en [LANZAMIENTO.md](LANZAMIENTO.md) §4.4 (donaciones contra servicios). Las
reglas de [AGENTS.md](../AGENTS.md) mandan sobre este documento, sobre todo la
§2: **no se escribe aquí ninguna cifra de mercado ni de fraude sin su
documento**. Los precios salen de los pilotos, no de este plan.

---

## 1. ¿Hay una necesidad real? Lo que dice la ley, no la intuición

«El fraude está por doquier» es una percepción. Lo que sí se sostiene con la
ley vigente es que **hay personas obligadas a revisar, que pierden dinero si no
revisan, y que hoy lo hacen a mano**:

| Quién | Qué le obliga o le cuesta | Dónde lo dice | Qué le resolvemos |
|---|---|---|---|
| Empresas y sus contadores | Si su proveedor sale **definitivo** en la lista 69-B, sus facturas «no producen ni produjeron efecto fiscal alguno», y tiene 30 días para acreditar la operación o corregir | CFF art. 69-B, párrafos quinto y octavo | Saber **el mismo día** que un proveedor entró a la lista, no meses después en una revisión del SAT |
| Despachos contables | Revisan cientos de XML de cada cliente | CFDI 4.0, Anexo 20 | El lector de facturas, por lote, cruzado con la 69-B |
| Áreas de cumplimiento (PLD) | Conocer a su cliente y a su proveedor en actividades vulnerables | LFPIORPI | La ficha del proveedor con cada documento público |
| Regidurías, congresos y medios | Revisar una cuenta pública o un contrato sin equipo técnico | — | El expediente del ente, ya cruzado |
| Ciudadanía | Saber en qué se va su dinero | Constitución art. 6 y 134 | Todo lo que ya es gratis, y seguirá gratis |

**Lo que todavía no sabemos, y se averigua antes de construir de más:** si
pagarían, cuánto, y si prefieren cuota mensual o por revisión. Por eso la
etapa 1 es de entrevistas y pilotos (§4).

### El perfil: «prevención de fraude», no «seguridad»

Se propone decir **«plataforma de prevención y debida diligencia»** y no
«plataforma de seguridad», por tres razones:

1. «Seguridad» suena a policía o a ciberseguridad; no hacemos ninguna de las dos.
2. La plataforma **no acusa** (Constitución art. 20, B, fr. I): señala lo que
   dice un documento y lo rotula «señal para revisar».
3. A las personas privadas no se les nombra (AGENTS.md §2 bis): el producto
   revisa **empresas y entes públicos**, no vigila personas.

---

## 2. Lo gratis y lo de pago: la línea que no se cruza

```
              GRATIS PARA SIEMPRE                    DE PAGO
  ┌──────────────────────────────────┐   ┌──────────────────────────────────┐
  │ Enciclopedia, Planisferio,       │   │ EL TRABAJO   investigación,      │
  │ Noticiero, el Auditor y sus      │   │              taller              │
  │ cuatro modos, estados de cuenta, │   │ LA MEMORIA   tu cartera de       │
  │ dictamen, consultar un RFC en la │   │              proveedores guardada│
  │ 69-B, leer UNA factura           │   │ EL AVISO     te avisamos cuando  │
  │                                  │   │              algo cambia         │
  │ Lo sostienen: DONACIONES         │   │ EL CÓMPUTO   lotes grandes e IA  │
  └──────────────────────────────────┘   └──────────────────────────────────┘
          pilar de transparencia                 lo que paga la operación
```

**La prueba de la línea:** si alguien pregunta «¿cobran por la información?»,
la respuesta siempre es «no: lo que se ve en el sitio es gratis; se cobra que
lo hagamos por ti, que lo recordemos o que te avisemos».

---

## 3. Los productos, por orden de prioridad

| # | Producto | Para quién | Qué ya existe | Qué falta | Dónde pone la IA |
|---|---|---|---|---|---|
| **1** | **Vigía de proveedores** (tu cartera de RFC vigilada contra la 69-B, cada semana) | Empresas y despachos | Lista 69-B con fechas de presunto y definitivo (`actualizar_69b.py`), lector CFDI | Bajar la lista **solo** cada semana y comparar contra la anterior; cuentas, cartera y correo | Redacta el aviso en sencillo con las fichas: qué pasó, qué párrafo del 69-B aplica, qué plazo corre |
| **2** | **Revisión de facturas por lote** | Despachos | `insp-factura.js` y `lector_cfdi.py` (varios XML, CSV) | Reporte en PDF con folio; lotes de cientos de XML | Resume el lote: qué emisores revisar primero y por qué |
| **3** | **Ficha de debida diligencia del proveedor** | Cumplimiento, PLD, compras | 69-B, ComprasMX, fraccionamiento, ASF | Directorio de sancionados integrado (hoy es búsqueda armada), ficha en PDF con folio | Redacta la ficha; cada cifra se coteja contra las fichas o se tira (`auditor-ia`) |
| **4** | **Taller «Documentar para sancionar»** y «Facturas y la 69-B» | Auditores, órganos de control, contadores | Las 20 matrices de la ASF, `aprende-auditoria.html` | Temario, material y forma de facturar | Ejercicios con casos de la base |
| **5** | **Expediente a la medida** y licencia institucional | Regidurías, medios, universidades | `servicios.html`, los 7 pasos, los 13 compromisos | El formulario conectado y las tarifas de los pilotos | Arma el primer borrador; una persona coteja |
| — | **Donaciones** | Ciudadanía | Página y alcancía en $0 | Forma jurídica y liga de pago | — |

**Por qué el 1 va primero:** es el único que la gente **necesita cada semana**
(un proveedor puede entrar a la lista en cualquier publicación), casi todo es
automático y es lo que ninguna búsqueda manual en el portal del SAT hace por
ellos: avisar. Es la «memoria» y el «aviso» que el modelo de negocio dice que
se cobran.

---

## 4. Las etapas

```
 ETAPA 0            ETAPA 1             ETAPA 2              ETAPA 3
 semanas 1-2        semanas 3-8         meses 3-4            meses 5-6
 Cimientos    ──▶   Pilotos a mano ──▶  Cobro y cuentas ──▶  IA y escala
 (sin cobrar)       (3 despachos,       (pasarela, alertas   (lotes, créditos,
                    1 taller)           por correo)          licencias)
      │                  │                   │                    │
 decisión: forma   decisión: ¿pagaron?  decisión: ¿renuevan?  decisión: ¿contratar
 jurídica          si no, se ajusta     si no, se ajusta      ayuda?
```

Cada etapa termina en una **decisión del autor**: si los pilotos no pagan, no
se construye la etapa 2 tal cual; se ajusta el producto.

### Etapa 0 · Cimientos (semanas 1 y 2)

| Paso | Qué | Quién |
|---|---|---|
| 0.1 | **Forma jurídica y RFC** (asociación civil o persona física con actividad empresarial). Sin esto no hay factura, ni pasarela, ni donativo con recibo | **Autor**, con un contador |
| 0.2 | Conectar el formulario de Servicios a la base (la función `recibir-formulario` ya acepta `solicitud`; hoy el formulario solo arma el texto). **Hecho el 05-11-2026**: manda con folio y antispam, solo si se acepta el aviso | Agente |
| 0.3 | La lista 69-B se baja sola cada semana y deja una bandeja de **altas y cambios** (presunto → definitivo, desvirtuado), con el molde del vigía legislativo. **Hecho el 05-11-2026**: `vigia_69b.py`, cada miércoles, y también avisa de los cambios de razón social por RFC | Agente |
| 0.4 | Página de venta del Vigía de proveedores, con un ejemplo **ficticio** | Agente redacta, autor aprueba |
| 0.5 | Analítica sin cookies, para saber qué páginas se usan | Agente |
| 0.6 | Fecha para quitar el candado (Google no ve el contenido mientras esté puesto) | **Autor** |

### Etapa 1 · Pilotos a mano (semanas 3 a 8)

El servicio se presta **a mano antes de automatizarlo**: así se aprende qué
quiere el cliente sin programar de más.

| Paso | Qué | Quién |
|---|---|---|
| 1.1 | **10 entrevistas**: 4 despachos contables, 3 áreas de cumplimiento, 3 auditores | **Autor** (guion lo prepara el agente) |
| 1.2 | **3 pilotos** del Vigía de proveedores: el despacho manda su lista de RFC; cada semana el agente corre el cruce y el autor manda el reporte por correo | Los dos |
| 1.3 | **1 taller** piloto, con precio escrito y factura | **Autor** |
| 1.4 | Registro de señales tempranas: cada aviso con su fecha, para probar después que llegamos antes | Agente |

**Lo que se mide:** ¿pagaron?, ¿cuánto?, ¿qué pidieron que no teníamos?

### Etapa 2 · Cobro y cuentas (meses 3 y 4)

| Paso | Qué |
|---|---|
| 2.1 | Pasar el sitio a un hospedaje que permita cobrar (recomendado: Cloudflare Pages + Supabase Pro; comparación y costos en [FRAUDE-MERCADO-Y-HOSPEDAJE.md](FRAUDE-MERCADO-Y-HOSPEDAJE.md) §4) |
| 2.2 | Cuentas sin contraseña (liga al correo) y «Mi Auditavisión»: tu cartera de RFC y tus avisos |
| 2.3 | Avisos por correo cuando la bandeja semanal de la 69-B toca un RFC de tu cartera |
| 2.4 | Pasarela (tarjeta y OXXO) y CFDI de cada cobro; la liga de donaciones en `CANAL_DONACION` |
| 2.5 | **Datos personales:** una cartera puede traer RFC de personas físicas. Se guardan cifrados, solo los ve su dueño, y el aviso de privacidad lo dice **antes** de recibir el primero (LFPDPPP) |

### Etapa 3 · IA y escala (meses 5 y 6)

| Paso | Qué |
|---|---|
| 3.1 | Lotes grandes de facturas y su reporte en PDF con folio |
| 3.2 | La IA redacta avisos, fichas y resúmenes **solo con las fichas** (la regla de `auditor-ia`: cifra que no esté, se tira) |
| 3.3 | Créditos por uso para lo que cuesta cómputo; licencia para despachos con varias personas |
| 3.4 | Informe anual: cuánto entró por cada vía (compromiso de la política de independencia) |

---

## 4 bis. Hacia dónde va: «Mi Auditavisión», un tablero que no se queda con tus datos

Pedido del autor, 05-11-2026: «hacer algo como WiseCricket y comernos a Legal
Hunt… que el usuario pueda subir un estado de resultados o facturas y
nosotros evaluarlas, sin retener información privada». Tiene dos ejemplos:
la plataforma Fortuvision, del propio autor, y
[getquin](https://www.getquin.com/), un rastreador gratuito de inversiones
con comunidad, un plan de pago y servidores en la Unión Europea.

**La idea:** un tablero de la salud fiscal de tu negocio. Funciona como
getquin con un portafolio, pero el portafolio son tus facturas, tus
proveedores y tu estado de resultados.

```
        LO QUE SUBES                    DÓNDE SE LEE              LO QUE VES
┌──────────────────────────┐    ┌────────────────────┐    ┌──────────────────────────────┐
│ Tus facturas (XML)        │──▶│                    │──▶│ Señales para revisar por      │
│ Tu estado de resultados   │──▶│  EN TU NAVEGADOR   │──▶│ factura, por proveedor y por  │
│ (Excel o CSV)             │    │  (no se sube nada) │    │ razón financiera              │
│ Tu lista de proveedores   │──▶│                    │──▶│ Su cruce con la 69-B, los     │
└──────────────────────────┘    └────────────────────┘    │ contratos públicos y la ASF   │
                                         │                └──────────────────────────────┘
                     solo si TÚ quieres  ▼
                ┌──────────────────────────────────────┐
                │ Guardar tu cartera de RFC para que el │  ← lo único que se guarda,
                │ Vigía te avise cada semana            │    cifrado y con tu permiso
                └──────────────────────────────────────┘
```

**Las reglas, para que la promesa «no retenemos tu información» sea cierta y
se pueda comprobar:**

1. **Lo que se lee en el navegador no sale de él.** Ya funciona así el Lector
   de facturas (`insp-factura.js`). El estado de resultados seguiría el mismo
   molde: un lector en JavaScript, con su gemelo en Python para las pruebas.
2. **Lo único que se guarda es lo que el usuario decide guardar** (su cartera
   de RFC para las alertas), con cuenta, cifrado y aviso de privacidad propio
   (LFPDPPP). Nunca el XML, nunca el estado de resultados.
3. **No se pide la CIEC ni la e.firma.** Esa es la diferencia con WiseCricket,
   y también es una promesa de privacidad.
4. **Sin certificación todavía, se dice así:** «no tenemos certificación ISO
   27001; por eso tu información no se sube». Es más honesto que prometer
   seguridad que no está auditada.
5. **Señales, no dictámenes:** las razones financieras y las comparaciones son
   `derivado` y se dicen «señal para revisar». La ley que aplica va citada,
   como en el lector de facturas.

**Por entregas (después de la etapa 1, porque necesita cuentas):**

| Entrega | Qué | Depende de |
|---|---|---|
| A | **Lector de estado de resultados** en el navegador: razones básicas (margen, gasto sobre ingreso), con su fórmula a la vista y el aviso de que no es un dictamen | Nada: se puede hacer ya |
| B | **Facturas por lote** en el navegador: cientos de XML, un resumen por proveedor y su cruce con la 69-B | Nada: crece del lector actual |
| C | **Mi Auditavisión**: el tablero que junta A y B en una sola vista, guardado **solo en ese navegador** (IndexedDB) | A y B |
| D | **La cartera en la nube** para las alertas del Vigía, con cuenta y pago | Etapa 2: hospedaje, cuentas, aviso propio |
| E | **Comunidad**: preguntas entre usuarios en el Ágora, sin datos de nadie | Moderación (decisión del autor) |

**Pendiente del autor:** contar qué hacía Fortuvision y qué funcionó, para no
repetir lo que no sirvió.

## 5. La ruta del autor, en paralelo

Las credenciales ayudan a vender, pero **la plataforma no depende de ellas**:
lo que se entrega es revisión documental con su fuente, no un dictamen
pericial (ese ya se cotiza aparte, con su responsable profesional, por regla de
`INDEPENDENCIA`). Si una credencial no llega, el producto sigue valiendo.

| Cuándo | Formación | Cómo se vuelve producto |
|---|---|---|
| Ahora | Curso de auditoría forense con IA | Cada módulo, una mejora: técnicas de detección → nuevas «señales para revisar»; casos → ejercicios del taller |
| Después | Certificación PLD de la CNBV | Respaldo para vender la ficha de debida diligencia a áreas de cumplimiento |
| Después | CFE de la ACFE | Credibilidad internacional del método |
| Quizá | Maestría en Estudios Fiscales | La ruta completa del impuesto (encargo 4) |

**Antes de pagar un curso**, conviene revisar: qué documento entrega al final
(constancia del curso, no es lo mismo que una certificación oficial), si tiene
reconocimiento de validez oficial cuando eso importa, y si la beca tiene
condiciones (fecha límite real, reembolso).

---

## 6. Lo que decide el autor, en una lista

1. La forma jurídica (etapa 0.1). Es la que más frena todo.
2. La fecha para quitar el candado.
3. Si los primeros pilotos son de despachos contables (recomendado).
4. Si se vende a municipios y tesorerías, y con qué límites.
5. Al final de cada etapa: seguir, ajustar o parar.

## 7. Puntos ciegos

- **El hospedaje actual no es para cobrar**: hay que mudarse antes del primer
  peso (etapa 2.1).
- **La lista 69-B no se actualiza sola hoy**: `actualizar_69b.py` se corre a
  mano. Sin eso, no hay aviso que vender (etapa 0.3).
- **El directorio de sancionados no está integrado**: hoy el chat solo arma la
  búsqueda.
- **Una cartera de RFC es un dato sensible del cliente**: confidencialidad y
  cifrado desde el primer piloto, aunque sea por correo.
- **No se mide nada todavía**: sin analítica no sabremos qué funciona.
- **El producto no acusa**: «señal para revisar», nunca «empresa fantasma»
  como afirmación, también en la publicidad.
