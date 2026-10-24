# Derechos de autor de las imágenes y recursos de Auditavisión

Revisión pedida por el autor el 24-10-2026, antes de comprar el dominio, crear
la base de datos y lanzar. Se revisaron las 84 imágenes del repositorio, los
mapas, los íconos y las fuentes. Método: dónde se usa cada archivo (búsqueda
en HTML, CSS y JS), sus metadatos (credenciales C2PA, EXIF, XMP), lo que
CONTEXT.md registró de su origen y una revisión visual.

> **No es asesoría legal.** Es un inventario técnico con las fuentes de cada
> conclusión. Antes de cobrar el primer peso conviene que una persona
> abogada revise los renglones en rojo.

## Por qué importa más al cobrar

- **Ley Federal del Derecho de Autor, art. 231, fr. I:** comunicar o usar
  públicamente una obra protegida sin autorización es infracción en materia
  de comercio cuando hay **lucro directo o indirecto**. La sanciona el IMPI
  con multa. Mientras todo es gratis, el riesgo es menor; con donaciones,
  Servicios o suscripciones, el sitio entero puede leerse como actividad con
  lucro indirecto.
- **Obras hechas solo con IA:** la Segunda Sala de la SCJN resolvió el 14 de
  julio de 2025 (amparo directo 6/2025) que no tienen derecho de autor en
  México porque el autor debe ser persona física. Consecuencia doble: se
  pueden usar sin pedir permiso a nadie, **pero tampoco son de Auditavisión**
  (cualquiera puede copiarlas).
- **Credibilidad:** una plataforma que exige cuentas claras no puede usar
  imágenes sin permiso. Un reclamo así es el primero que harían sus críticos.

## Semáforo

🟢 sin riesgo · 🟡 riesgo bajo, documentar · 🔴 **cambiar o regularizar antes de lanzar**

### Imágenes que se ven en el sitio

| Imagen | Dónde se ve | Origen | Estado | Qué se hace |
|---|---|---|---|---|
| `portada/cabecera-pasillo.webp` | Cabecera de **todas** las páginas (`civico.css`) | Pinterest, sin autor acreditado (CONTEXT.md, 08-10-2026) | 🔴 | Reemplazar |
| `portada/pie-noche.jpg` | Pie de **todas** las páginas | Pinterest; lleva la firma «AFERA XV» | 🔴 | Reemplazar. Si se quisiera conservar, pedir permiso por escrito al autor de la firma |
| `portada/pie-planos.jpg` | Guardada como alternativa, no se ve | Pinterest | 🔴 | Borrar del repositorio |
| `herr-inspector-camaras.jpg` | Modo Inspector | Circula en Pinterest, sin autor ni licencia (CONTEXT.md, 24-10-2026). Por su estilo parece ilustración editorial de una publicación | 🔴 | Reemplazar |
| `encabezado-estado-de-cuenta.jpg` | Los 42 estados de cuenta | La envió el autor; **se recortó una marca de agua** de la esquina (CONTEXT.md, 10-10-2026) | 🔴 | Reemplazar. Quitar la marca de agua no la vuelve libre: la marca es la firma de quien la hizo, y quitarla agrava el reclamo |
| `herr-inspector-foroptero-amplia.jpg` | Chat del Auditor Virtual | La entregó el autor (09-10-2026); origen no registrado. Parece fotografía de estudio con una modelo: si es foto de banco de imágenes, además de la licencia de la foto entra el **uso de la imagen de una persona** (art. 231, fr. II) | 🔴 | El autor confirma el origen; si no, reemplazar |
| `herr-calculadora-monedas-amplia.jpg` | Calculadora Cívica | **Pinterest** (confirmado por el autor, 24-10-2026) | 🔴 | Reemplazar |
| `herr-megaobras-plataformas-amplia.jpg` | Megaobras | **Pinterest** (confirmado por el autor) | 🔴 | Reemplazar |
| `herr-ambiente-refineria-amplia.jpg` | Costo Ambiental | **Pinterest** (confirmado por el autor) | 🔴 | Reemplazar |
| `city_day.jpg`, `city_night.jpg` | Fondos | **Generadas con IA de Google**: traen su credencial C2PA (`trainedAlgorithmicMedia`) | 🟢 | Elegidas a propósito por el autor para evitar problemas de derechos |
| `showcase_tren_maya`, `_dos_bocas`, `_deuda_soberana`, `_aifa`, `_ramo33` | Auditoría en imágenes | Generadas con IA de Google (C2PA), rotuladas «Ilustración generada con IA» | 🟢 | — |
| `showcase_lego_expansion`, `_megafarmacia`, `_tren_toluca` | Auditoría en imágenes | **Generadas con IA** (confirmado por el autor, 24-10-2026); sin metadatos. Rotuladas «Imagen ilustrativa» | 🟢 | Rotularlas «Ilustración generada con IA» como las otras. La de LEGO muestra la marca «HUSKY» en una máquina: conviene regenerarla sin marcas |
| `showcase_huachicol.jpg` | Auditoría en imágenes | Ilustración vectorial propia (CONTEXT.md) | 🟢 | — |
| `logo-auditavision.svg` y `assets/brand/` | Toda la plataforma | Marca propia | 🟢 | Ver «Marca» abajo |

### Imágenes que no se ven pero se publicarían

| Archivos | Qué son | Estado | Qué se hace |
|---|---|---|---|
| 28 PNG en la raíz (`am-*`, `cc-*`, `mo-*`, `u-*`, `cab.png`, `drawer.png`, `jud-recursos.png`, `leg-candidatos.png`) | Capturas de pantalla de la propia plataforma (pruebas) | 🟢 | Dejarlas fuera de la publicación (`.vercelignore` o equivalente). Ninguna página las usa |
| 17 PNG en `investigaciones/fuentes-asf` y `fuentes-judicial` | Recortes de páginas de informes de la ASF, la SCJN y el Manual de remuneraciones | 🟢 | Documentos oficiales, citados con su fuente (LFDA art. 148, fr. I). Ninguna página las usa; entran en la decisión 0.3 |

### Recursos de terceros

| Recurso | Licencia | Estado | Qué se hace |
|---|---|---|---|
| **Mapas: mosaicos de CARTO** (`basemaps.cartocdn.com`, 3 mapas en `audit-engine.js`) | CARTO pide **mantener a la vista «© OpenStreetMap contributors © CARTO»**, y su uso gratuito es para fines **no comerciales**; para uso comercial pide licencia Enterprise | 🔴 | Hoy el crédito está **apagado** (`attributionControl: false`): se enciende ya. Antes de cobrar: pedir su llave gratuita o cambiar a mosaicos que permitan uso comercial (por ejemplo, el de OpenStreetMap con su política de uso, o un proveedor con plan comercial) |
| Íconos Lucide 1.49.0 | ISC; el aviso de licencia va dentro de `iconos.js` | 🟢 | — |
| Leaflet 1.9.4 | BSD-2 | 🟢 | — |
| Google Fonts (Playfair Display, Roboto) | SIL Open Font License | 🟢 | — |
| Imagen de la SCJN enlazada desde su sitio (`consulta-obligaciones.svg`, en `investigaciones/`) | Documento oficial | 🟢 | Mejor descargarla con su fuente que enlazarla al servidor de la Corte |

### Marca

| Pendiente | Estado | Qué se hace |
|---|---|---|
| Registro de la marca «Auditavisión» ante el IMPI | 🟡 | El logo es propio, pero sin registro otra persona puede registrar el nombre. Buscarla en MARCia (IMPI) antes de comprar el dominio y registrarla en la clase que corresponda (la persona abogada lo indica) |
| El nombre de otras marcas en los títulos (LEGO, Pemex…) | 🟢 | Se nombran para identificar el tema, sin logotipos: es uso descriptivo |

## Resultado

- **10 en rojo:** cabecera, pie (dos archivos), las cinco imágenes de las
  herramientas (cámaras, foróptero, monedas, plataformas y refinería), el
  encabezado del estado de cuenta y los mapas sin crédito (y su uso
  comercial). Las nueve imágenes salieron de Pinterest (autor, 24-10-2026).
- **0 en amarillo:** las tres de Auditoría en imágenes por confirmar son de IA.
- El resto está en verde.

## Respuesta del autor (24-10-2026)

«Algunas eran propias y otras fueron sacadas de Pinterest.» Sin el detalle de
cuál es cuál, **toda imagen sin prueba de origen se trata como de Pinterest y
se reemplaza**. Solo se quedan las que traen la credencial de IA (C2PA) o
las que el autor confirme una por una como propias (hechas por él o
generadas por él con IA).

### Las que se reemplazan, con su descripción para generarlas

Descripciones originales para la misma herramienta de IA que hizo las demás.
No copian ninguna imagen de Pinterest ni el estilo de un artista. Se guarda
la descripción usada junto a la imagen, en el registro de créditos.

| Archivo nuevo (nombre nuevo por la caché) | Medida | Descripción para generarla |
|---|---|---|
| `portada/cabecera-avenida.webp` | 736 × 760, borde izquierdo desvanecido | Avenida peatonal de una ciudad mexicana al amanecer, con un edificio de gobierno de cantera al fondo, dos personas caminando de espaldas, piso mojado que refleja la luz, paleta azul marino y gris claro, estilo de acuarela arquitectónica con trazos de dibujo técnico, sin texto ni logotipos |
| `portada/pie-ciudad.jpg` | 1472 × 660 | Panorama nocturno de una ciudad latinoamericana con edificios de distintas alturas y ventanas iluminadas, cielo nublado violeta, ilustración digital sobria de tonos fríos, sin letreros legibles ni marcas |
| `herr-inspector-vigilancia.jpg` | 736 × 1308, vertical | Collage de papel recortado: un poste con varias cámaras de seguridad que miran en distintas direcciones, en lugar del lente una lupa, fondo carbón con renglones de cifras y tablas presupuestales desenfocadas, tonos sepia y crema |
| `encabezado-sesion.jpg` | 736 × 240, franja | Ilustración estilo cartel de los años cincuenta: una mesa redonda de sesión con personas de traje revisando documentos, al centro una gráfica de pastel, paleta rojo, verde y crema, sin texto |
| `herr-inspector-lente.jpg` | 1200 × 670 | Fotografía de estudio en blanco y negro de un foróptero de optometría visto de frente, sin persona, fondo gris desenfocado, iluminación lateral suave |
| `herr-calculadora-pesos.jpg` | 1200 × 670 | Primer plano de una pila de monedas de pesos mexicanos genéricas (sin reproducir una moneda real con detalle) sobre una mesa de madera, luz cálida, fondo desenfocado |
| `herr-megaobras-plataforma.jpg` | 1200 × 670 | Plataforma petrolera marina en el Golfo de México con oleaje y grúas, vista aérea, cielo gris, fotografía realista, sin logotipos |
| `herr-ambiente-humo.jpg` | 1200 × 670 | Refinería al atardecer con chimeneas humeantes reflejadas en un humedal, una persona con mascarilla de espaldas, aves volando, tonos verdes oscuros, ilustración cinematográfica |

`pie-planos.jpg` se borra sin reemplazo (no se usa).

**Confirmado por el autor (24-10-2026):** las nueve de Auditoría en imágenes
son generadas con IA y se quedan; las del encabezado, los estados de cuenta y
las herramientas salieron de Pinterest y se reemplazan todas.

## Cómo se reemplazan (sin costo)

1. **Generarlas con IA** en la misma herramienta que las de Auditoría en
   imágenes, con descripciones originales (nunca «al estilo de» un artista
   vivo ni copiando una imagen de Pinterest), y guardar la descripción usada.
   Se rotulan «Ilustración generada con IA», como ya se hace.
2. **Bancos con licencia libre** que permiten uso comercial sin atribución
   obligatoria (Unsplash, Pexels) o Wikimedia Commons (cada imagen con su
   licencia; CC BY pide el crédito). Se guarda la liga y la licencia.
3. **Fotos propias** del autor.

**Regla nueva para AGENTS.md (propuesta):** ninguna imagen entra al
repositorio sin su renglón en el registro de créditos (archivo, origen,
licencia, liga, fecha). Una página «Créditos» al pie del sitio los muestra,
con la misma lógica de «todo dato con su fuente».

Para cambiar una imagen, cámbiale también el nombre (CONTEXT.md, 09-10-2026),
y sube el sello.

## Fuentes

- SCJN, Segunda Sala, amparo directo 6/2025 (14-07-2025), reportado por
  Expansión: https://expansion.mx/tecnologia/2025/07/16/obras-hechas-con-ia-no-tienen-derecho-de-autor-scjn
- Ley Federal del Derecho de Autor, art. 231 (Cámara de Diputados; verificar
  la redacción vigente en el DOF antes de citarla en un documento legal).
- CARTO, términos de los mapas base: https://carto.com/legal/basemap-terms/ ·
  llave gratuita y límites: https://www.carto.com/basemaps/apikey/ ·
  preguntas frecuentes: https://docs.carto.com/faqs/carto-basemaps
