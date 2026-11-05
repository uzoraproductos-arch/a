# Encargo del autor: vigía legislativo, lector de facturas y lo que sigue

Escrito el 05-11-2026 para retomarse en una conversación nueva. Antes de
tocar nada, lee [AGENTS.md](../AGENTS.md) y [ESTADO.md](../ESTADO.md): las
reglas de ahí mandan sobre este documento. Aquí está **qué pidió el autor,
qué ya existe en el código y cómo encaja cada pieza**, para que no haya que
volver a preguntárselo.

Orden pedido por el autor: **1. vigía legislativo**, **2. lector de facturas
(CFDI)**. Después, en cola: 3. CompraNet × 69-B × ASF y 4. la ruta completa
del impuesto.

---

## Lo que el autor dejó claro (y no hay que volver a discutir)

- **El chat responde desde la base, no desde internet.** Internet alimenta la
  base; la base alimenta al Auditor (§5 ter). Nada de lo de abajo cambia eso:
  lo que se trae de la red llega rotulado «sin verificar» y entra a la base
  solo después de cotejarse.
- **El vigía detecta y propone; nunca escribe solo en la base** (§2: un dato
  sin cotejo no entra). Lo aprueba una persona.
- La plataforma quiere servir **al sector público y al privado**: auditor
  virtual de dominio público (gobierno) y herramienta para despachos,
  cumplimiento (PLD / RegTech) y empresas que revisan proveedores.
- El autor está aprendiendo Python para datos fiscales: **explica el porqué
  técnico de cada pieza** (comentarios claros en español, sin jerga de más).

---

## 1. Vigía legislativo (primero)

**Pedido del autor:** «un agente que esté al pendiente de todas las
publicaciones de leyes y reformas desde la página de Diputados o del Senado
para estar a lo último actualizado y así ir llenando nuestra base de datos».

### Lo que ya existe y en qué se apoya

| Pieza | Qué hace | Archivo |
|---|---|---|
| Mesa de redacción | Cada día 8:23 (CDMX) junta titulares sin verificar | `.github/workflows/mesa-de-redaccion.yml`, `herramientas/recolectar_noticias.py` → `docs/noticias/bandeja.json` |
| Revisión semanal | Lunes 7:17: enlaces caídos y «vigías» de documentos con fecha legal | `.github/workflows/semanal.yml`, `herramientas/semanal.py` (`VIGIAS`) → `docs/SEMANAL.md` |
| Leyes citadas | Varios módulos dicen «última reforma DOF dd-mm-aaaa» (p. ej. `asistente_legislativo.py`, `asistente_judicial.py`, `nepotismo.py`, `glosario_fundamentos.py`) | `herramientas/*.py` |

### Lo que se construye

1. **`herramientas/vigia_legislativo.py`**, con el mismo molde que
   `recolectar_noticias.py` (solo lee y escribe una bandeja; no toca páginas):
   - Lee el **sumario del DOF** del día (dof.gob.mx) y la lista de leyes con
     su **última reforma** de la Cámara de Diputados (LeyesBiblio). El Senado,
     solo si su portal da una lista que se pueda leer sin adivinar. **Verifica
     las direcciones exactas al construirlo**: no las supongas, y si el portal
     no responde desde el entorno, el flujo de GitHub sí suele llegar.
   - Filtra por una lista `LEYES` (clave, nombre, liga oficial del texto
     vigente). Para empezar: CFF, LISR, LIVA, LIEPS, Ley Federal de Derechos,
     Ley de Ingresos y PEF del año, LFPRH, Ley de Disciplina Financiera, LGCG,
     LFRCF, LGRA, LAASSP, LOPSRM, Ley Fintech (LRITF), LFPIORPI (antilavado),
     LFPDPPP (datos personales), Constitución.
   - Escribe `docs/legislativo/bandeja.json`: cada hallazgo con ley, fecha
     del DOF, liga, qué artículos (si el sumario lo dice) y estado
     `por cotejar`. Solo título, fecha y liga, **nunca el texto de la reforma
     copiado**.
2. **El cruce que más vale:** comparar la «última reforma» que dice
   Diputados contra la que **cita la plataforma** en cada módulo. Si la
   plataforma cita una fecha anterior, es un aviso: «tal módulo cita la LISR
   con reforma del dd-mm; ya hay una posterior». Así el vigía no solo trae
   novedades: dice **qué parte de Auditavisión quedó vieja**.
3. **Flujo `.github/workflows/vigia-legislativo.yml`**: diario (minuto no
   redondo, fuera de 6-9 h de Pacífico), con el patrón de la mesa de
   redacción (commit de la bandeja a `claude/funny-turing-imtm54`).
4. **Al lector:** una sección «Reformas recientes» (sin verificar hasta su
   cotejo) en Noticias › Seguimiento o en Aprende › leyes; decidir cuál con el
   autor si no es obvio. Las aprobadas pasan a su módulo con su vigencia
   (las estructuras derogadas se marcan, no se borran, §2).
5. **Al chat (§5 ter):** «¿qué leyes cambiaron esta semana?», «¿cuándo se
   reformó el Código Fiscal?» → la sección, con `ir`. Sus preguntas van en
   `herramientas/preguntas_auditor.json`.

---

## 2. Lector de facturas (CFDI 4.0) en Auditavisión (segundo)

**Pedido del autor:** implementar en la plataforma el código que lee una
factura (se le enseñó en la conversación, en Python, con
`xml.etree.ElementTree`) y cruzarla contra la lista 69-B.

### Diseño

- **Una aplicación nueva del Modo Inspector**
  (`herramienta-inspector-factura.html`, generada con Python como las demás,
  §5 bis). Entra sola al catálogo del chat (`_inspector()` de `asistente.py`);
  su intención («¿esta factura es de una empresa fantasma?», «revisa mi
  factura», «tengo un XML») se agrega en `inspector()` de `asistente.js`.
- **Todo ocurre en el navegador** (`DOMParser`), sin subir el XML a ningún
  lado: una factura trae datos personales (RFC de personas físicas). Que la
  página lo diga. Nada se guarda.
- Lee: UUID (TimbreFiscalDigital), fecha, emisor (RFC, nombre, régimen),
  receptor, subtotal, impuestos trasladados y retenidos, total, conceptos.
  Espacios de nombres: `http://www.sat.gob.mx/cfd/4` y
  `http://www.sat.gob.mx/TimbreFiscalDigital`. Si es CFDI 3.3
  (`http://www.sat.gob.mx/cfd/3`), que lo diga y lo lea igual o avise.
- Acepta **varios XML a la vez** (tabla), porque así trabaja un despacho.
- **Cruce con `window.SAT_69B`** (`assets/auditor/data/sat-69b.js`, de
  `herramientas/actualizar_69b.py`), separando, como pidió el autor para
  CompraNet:
  - **Lo que declaró la autoridad (`oficial`)**: el RFC está en la 69-B con
    su situación (Presunto, Definitivo, Desvirtuado, Sentencia favorable), su
    oficio y su fecha.
  - **Señales para revisar (`derivado`)**: p. ej. la factura tiene fecha
    **posterior** a la publicación del emisor como definitivo; o la emitió
    mientras era presunto. Rotuladas «señal para revisar», nunca
    «irregularidad». Desvirtuado y sentencia favorable se dicen como lo que
    son: **a favor del contribuyente**.
  - **Ojo, dato que falta:** `sat-69b.js` guarda una sola fecha por RFC (la
    de su situación actual). Para comparar contra la fecha de presunto y de
    definitivo hay que conservar ambas en `actualizar_69b.py` (el CSV del SAT
    trae columnas por etapa; revisa los índices antes de cambiar nada).
- **Personas físicas:** el RFC del emisor o receptor persona física no se
  muestra completo ni se guarda (§2 bis). La 69-B es pública, pero el lector
  solo dice lo que el listado dice.
- **El script de Python** queda también como herramienta y como material de
  aprendizaje: `herramientas/lector_cfdi.py` (uno o varios XML → tabla CSV +
  cruce 69-B), con una factura de ejemplo **ficticia** en `docs/ejemplos/`
  (RFC genérico `XAXX010101000`, nada real) y su prueba en `revision.py`.
- «Generar dictamen» de la app (`conApp()`): respalda qué hace y de dónde
  salen sus datos; nunca copia el resultado de la factura del lector.

---

## 3. En cola: CompraNet × 69-B × ASF por año

Pedido del autor (textual, conversación del 05-11-2026): «Integra el
histórico de contratos de CompraNet (upcp-compranet.hacienda.gob.mx) y la
serie de la ASF desde la Cuenta Pública 2000. Haz una aplicación del Modo
Inspector que cruce contratos × lista 69-B × ASF por año: distingue lo que ya
declaró la autoridad (oficial) de las señales que detectamos nosotros
(derivado, «señal para revisar»), incluida la comparación entre la fecha del
contrato y la fecha del DOF. El chat solo menciona el hallazgo, o el
antecedente si hoy no hay nada, y lleva a esa sección. Lo que no tenga fuente
queda pendiente con su ficha.»

Se apoya en `herramientas/actualizar_comprasmx.py` (ComprasMX, que ya cruza
con la 69-B) y en la misma lógica de fechas del lector de facturas: **conviene
hacer primero el lector, porque deja lista la comparación de fechas contra la
69-B**. Si el portal histórico no responde desde el entorno, el autor sube los
archivos (como con ComprasMX) y se anota como pendiente con su ficha.

## 4. En cola: la ruta completa del impuesto

Ley de Ingresos → lo que recauda el SAT → PEF → Cuenta Pública → lo que audita
la ASF, en una sola vista. Es la propuesta de política pública del autor
(«revisar en qué se gasta lo que se cobra»). Las cifras se leen de los módulos
que ya las cotejan; ninguna se escribe a mano.

---

## Terminado = AGENTS.md §5

`python3 herramientas/revision.py --base origin/claude/funny-turing-imtm54`,
sello si se toca `assets/`, preguntas de prueba nuevas, `ESTADO.md` al día y
decir qué quedó pendiente y por qué.
