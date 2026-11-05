# Auditavisión en el lienzo de los nueve bloques

Pedido del autor, 02-11-2026: «actúa como si fuera tu negocio Auditavisión…
hay nueve bloques… y varias preguntas en diferentes apartados que me gustaría
que se enlistaran y se respondieran con lo que se ha creado».

Los nueve bloques y sus 41 preguntas son los del lienzo de *Generación de
Modelos de Negocio* (Osterwalder y Pigneur, 2010). El autor subió el libro y
cuatro PDF más el 02-11-2026 (commit `32ab8a15`). Se retiraron de la rama el
mismo día, porque GitHub Pages los dejaba públicos y el candado no protege
los PDF:

- El libro tiene derechos de autor, y la traducción no es oficial.
- Tres son folletos de cursos de terceros.
- El informe de la ASF ya se cita por su liga oficial.

Los originales siguen en el Drive del autor, en «gasto público › doctrina», y
quedan en el historial de git.

Lo que los cuatro documentos de auditoría aportan de método está en la
Enciclopedia: `aprende-auditoria.html` (ver «Metodología» abajo).

**Estados:** ✅ hecho (existe y funciona) · 🟡 a medias (escrito o diseñado,
sin terminar) · ❌ falta.

**Resultado:** de 41 preguntas, **16 ✅, 16 🟡 y 9 ❌**. El bloque más débil
es Flujos de ingresos: hoy no entra dinero ni hay forma de pagar. El más
sólido es Propuestas de valor.

```
 ┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
 │ 8 SOCIOS     │ 7 ACTIVIDADES│ 2 PROPUESTA  │ 4 RELACIONES │ 1 SEGMENTOS  │
 │ GitHub,      │ Cotejar      │ Cada cifra   │ Autoservicio │ Ciudadanía   │
 │ Supabase,    │ documentos   │ con su       │ (Auditor),   │ (gratis);    │
 │ Cloudflare,  │ y verificar  │ documento;   │ co-creación, │ periodistas, │
 │ Anthropic    ├──────────────┤ IA que no    ├──────────────┤ OSC, cabil-  │
 │ (posibles:   │ 6 RECURSOS   │ inventa      │ 3 CANALES    │ dos, univer- │
 │ universida-  │ Base cotejada│              │ Sitio, Google│ sidades,     │
 │ des, OSC)    │ y el método  │              │ (candado)    │ gobiernos    │
 ├──────────────┴──────────────┴───────┬──────┴──────────────┴──────────────┤
 │ 9 COSTOS  tiempo del autor, dominio,│ 5 INGRESOS  hoy $0; donaciones y    │
 │ IA; al cobrar US$45/mes fijos       │ 5 servicios escritos, sin canal     │
 └─────────────────────────────────────┴─────────────────────────────────────┘
```

| Bloque | ✅ | 🟡 | ❌ |
|---|---|---|---|
| 1. Segmentos de clientes | 1 | 1 | 0 |
| 2. Propuestas de valor | 3 | 1 | 0 |
| 3. Canales (6 preguntas + 5 fases) | 4 | 4 | 3 |
| 4. Relaciones con clientes | 2 | 2 | 0 |
| 5. Flujos de ingresos | 0 | 2 | 3 |
| 6. Recursos clave | 2 | 1 | 1 |
| 7. Actividades clave | 1 | 2 | 1 |
| 8. Asociaciones clave | 3 | 1 | 0 |
| 9. Estructura de costos | 0 | 2 | 1 |
| **Total** | **16** | **16** | **9** |

## La propuesta de valor, constituida (02-11-2026)

La definición del autor:

> «Auditavisión es una plataforma digital que sirve como investigador virtual,
> reportero y noticiero; revisa las finanzas públicas del Estado mexicano desde
> el gasto más hormiga, mantiene un control de sus operaciones en sus tres
> niveles, más de lo que la misma ASF llega a detectar.»

| Su frase | Qué se sostiene hoy | Cómo decirlo |
|---|---|---|
| «investigador, reportero, noticiero» | ✅ Son los modos Inspector y Periodista, y la pestaña Noticias. | Igual. |
| «desde el gasto más hormiga» | 🟡 En lo federal se llega a cada contrato de ComprasMX. Muchos municipios no publican sus gastos menores. | «Hasta el contrato más chico que se publica, y lo que no se publica, con el nombre de quien lo debe». |
| «mantiene un control» | ❌ El control interno es de cada institución (Marco Integrado de Control Interno de la ASF). | «Vigila». |
| «en sus tres niveles» | 🟡 Están los 32 estados y 2,479 municipios, con distinta profundidad. | «Federación, estados y municipios», con un semáforo de cobertura. |
| «más de lo que la ASF detecta» | ❌ No está probado. La ASF hizo 2,264 auditorías a la Cuenta Pública 2024 y puede exigir documentos (`integrar_cuenta_publica.py`), pero revisa después de que cierra el año: la última entrega de 2024 salió en febrero de 2026. | «Llegamos antes y cruzamos lo que nadie cruza». Se prueba con el registro de señales tempranas. |

**La frase propuesta:** «Auditavisión es el auditor ciudadano del dinero
público de México: vigila a la Federación, los estados y los municipios hasta
el contrato más chico que se publica, cruza lo que nadie cruza y te avisa antes
de que llegue la auditoría. Cada cifra trae su documento.»

### ¿Por qué alguien pagaría?

**La prueba ácida: si mañana cerramos, ¿quién se queja?** Hoy, nadie, porque
nadie depende todavía de la plataforma:

- el candado no deja entrar;
- no hay avisos por correo;
- no hay un caso que la prensa nos cite.

Ser indispensable se gana con **hábito** (los avisos), **memoria** (la bóveda y
la memoria de promesas) y **prueba** (que nos citen).

La ciudadanía no paga: la consulta es gratis por regla. Pagan quienes pierden
dinero, tiempo o reputación por no saber algo a tiempo.

| # | Segmento | Lo que les duele | Lo que se les vende | Motivo para pagar |
|---|---|---|---|---|
| 1 | Empresas y sus contadores | Las facturas de un proveedor que está en la lista 69-B pueden dejar de servirles para deducir (Código Fiscal, art. 69-B). Contratar con una empresa sancionada también es un riesgo. | Ficha de debida diligencia del proveedor y un aviso si entra a una lista | Alto |
| 2 | Auditores, despachos y personal de órganos de control | Formarse y certificarse: pagan diplomados de 80 h. | Taller «Documentar para sancionar» | Alto |
| 3 | Regidurías y congresos locales, de cualquier partido | Votar sin equipo técnico | Expediente del ente antes de la sesión. Mismo producto y mismo precio para todos. | Medio |
| 4 | Municipios y tesorerías (los auditados) | Observaciones de la ASF que se repiten cada año | Capacitación preventiva, nunca «limpiar» su expediente. **Lo decide el autor.** | Medio |
| 5 | Medios y periodistas | Tiempo y riesgo de réplica | Revisión documental, licencia del verificador | Bajo en dinero, alto en alcance |

**Por qué podemos llegar a ser indispensables:**

- **Memoria.**
  - La plataforma une promesa → Presupuesto → Cuenta Pública → ASF, y la bóveda guarda copia de los documentos.
  - Con el INAI extinto desde el 20-03-2025, la transparencia federal depende de una secretaría del Ejecutivo.
- **El cruce.** Los informes de la ASF se cruzan con los contratos, la lista 69-B y las notas.
- **Confianza revisable.**
  - La IA tira cualquier respuesta con una cifra que no está en las fichas.
  - Hay fe de erratas y derecho de réplica con plazos de ley.

### Propuestas, en orden

1. **Validar antes de construir (30 días).**
   - 10 entrevistas, 2 por segmento.
   - 3 pilotos con precio escrito.
2. **Registro de señales tempranas.**
   - Cada señal se anota con su fecha.
   - Si la ASF la observa después, queda probado que llegamos antes.
3. **Ficha de debida diligencia del proveedor**, armada con ComprasMX, la lista 69-B y los sancionados.
4. **Avisos por correo:** seguir a un municipio o a un proveedor.
5. **«Gasto hormiga» por solicitud de acceso:** modelos de solicitud para pedir viáticos y fondos revolventes. Lo que no se entregue va al Registro de pendientes.
6. **Semáforo de cobertura** por nivel de gobierno.

### Lo que el autor aclaró (02-11-2026)

- **«Control»** quiere decir seguimiento y vigilancia de hacia dónde va el
  dinero, como principio de transparencia; por eso los mapas. Hecho: el mapa
  del dinero (`numeros-mapa-del-gasto-federalizado.html`) tiene siete capas que
  el lector opera: Ramos 28 y 33, por habitante, dependencia, deuda, por
  aclarar ante la ASF, **No cuadra** y **Obras con alerta ambiental**. La
  contaminación por estado no tiene capa: no hay cifra estatal cotejada.
- **Los servicios** se quedan en su pestaña: `servicios.html#sectores` dice qué
  se ofrece a cada sector, y se sumó la **Revisión de un proveedor**.
- **«Superiores a la autoridad»** quiere decir una base más completa y mejor
  cruzada que la de cada portal. Se sostiene comparando portal contra portal:
  la ASF publica sus informes; Hacienda, la Cuenta Pública; el INEGI, lo que
  reportan los estados; aquí se cruzan («No cuadra» es el primer ejemplo).
- **Respaldo histórico**, porque la transparencia puede disminuir: la bóveda
  (`boveda.py`) guarda cada miércoles la huella de los documentos que
  respaldan los datos. Falta guardar las copias fuera de GitHub (almacenamiento
  «boveda» de Supabase) y pedir copia a archive.org (`--archivo`).
- **Medios:** la Mesa de redacción sigue a ocho medios por nombre y junta la
  misma historia cuando varios la cuentan. Solo titular, medio, fecha y liga,
  sin verificar.
- **Elecciones del 6 de junio de 2027 y buscadores.** La gente va a buscar a
  su gobierno en Google. Tres cosas deciden si nos encuentra:
  1. **El candado** (`CANDADO = True`): mientras esté puesto, Google solo ve el
     canje. Es la decisión que más pesa.
  2. **Una página fija por estado**: hoy la ficha de cada estado vive en una
     dirección con `#`, que Google no indexa por separado. Treinta y dos
     páginas («Jalisco: su dinero, su deuda, lo que no cuadra») responderían a
     lo que la gente escribe.
  3. **Notas «Al momento» de campaña**: cada promesa de gasto de una
     candidatura entra a la memoria de promesas, con su fecha.

---

## 1. Segmentos de clientes

1. **¿Para quién estamos creando valor?** ✅
   - Para dos lados que se necesitan.
   - Un lado es la ciudadanía, que consulta gratis y así seguirá.
   - El otro lado es quien trabaja con dinero público y paga por ahorrar tiempo o por un trabajo a la medida: periodistas, OSC, regidurías, universidades, despachos y gobiernos.
   - Los cuatro modos del Auditor ya son una segmentación.
   - *Dónde:* `MODOS` de `asistente.py`; `servicios.html`; la política de independencia.
2. **¿Quiénes son los clientes más importantes?** 🟡
   - No se ha elegido uno.
   - Para el libro, esto es una plataforma de dos lados.
   - Recomendación: periodistas y organizaciones civiles durante 90 días.
   - *Dónde:* `docs/LANZAMIENTO.md` §4.3.

## 2. Propuestas de valor

3. **¿Qué valor entregamos?** ✅ Pasar de no entender el presupuesto a verificar una cifra en un minuto, con su fuente, su estado y un dictamen sellado.
4. **¿Qué problemas resolvemos?** ✅ La información está regada entre DOF, SHCP, ASF e INEGI, las notas circulan sin cotejar, y lo que nadie publica se nombra en el Registro de pendientes.
5. **¿Qué necesidades satisfacemos?** ✅
   - Saber, verificar, vigilar y actuar.
   - Falta vigilar con aviso por correo.
6. **¿Qué paquetes ofrecemos a cada segmento?** 🟡
   - Gratis: la Enciclopedia, el Auditor (4 modos e IA), Noticias, los estados de cuenta y el dictamen.
   - De pago: cinco servicios escritos (`SERVICIOS`), sin precio ni canal.

## 3. Canales

7. **¿Por qué canales quieren ser alcanzados?** ✅ Celular, Google, redes y WhatsApp. El sitio está hecho para celular.
8. **¿Cómo los alcanzamos ahora?** 🟡
   - GitHub Pages, Search Console verificado, sitemap y las páginas «Al momento» como `NewsArticle`.
   - El candado deja a Google ver solo el canje.
   - En el repositorio no consta un canal propio en redes.
9. **¿Cómo se integran?** ✅ Todo lleva al Auditor: «Pregúntale al Auditor», «Volver al Auditor» y el cajón «Cuéntanos lo que viste».
10. **¿Cuáles funcionan mejor?** ❌ No se sabe: no hay analítica de visitas.
11. **¿Cuáles son más rentables?** ❌ Ninguno cobra.
12. **¿Cómo se integran con las rutinas del cliente?** 🟡
    - Ya existen la Mesa de redacción diaria, la Agenda del erario y el seguimiento de casos en el navegador.
    - Falta el aviso por correo.
13. **Fase 1 · Conciencia** 🟡 Google está listo, pero el candado lo frena.
14. **Fase 2 · Evaluación** ✅ Fuente a la vista, dictamen, pilares y fe de erratas.
15. **Fase 3 · Compra** ❌ No hay pasarela, y `CANAL_SOLICITUD` está vacío.
16. **Fase 4 · Entrega** 🟡 Hay un proceso de siete pasos, pero no existe «Mi Auditavisión».
17. **Fase 5 · Posventa** ✅ Fe de erratas, réplica con plazos de ley y folio de los reportes.

## 4. Relaciones con clientes

18. **¿Qué relación espera cada segmento?** ✅
    - La ciudadanía: autoservicio automatizado (el Auditor).
    - Periodistas y OSC: asistencia personal.
    - Instituciones: asistencia dedicada (licencia y capacitación).
    - Todos: co-creación (reportes y propuestas de nota).
19. **¿Cuáles hemos establecido?** 🟡
    - Ya funcionan la IA (encendida el 02-11-2026) y los formularios con Turnstile y folio.
    - La asistencia personal no tiene canal.
20. **¿Qué tan costosas son?** 🟡
    - La relación automática cuesta casi nada, salvo la IA: 10 preguntas por minuto y 100 al día, con el costo por pregunta aún por medir.
    - La personal cuesta horas del autor, sin tarifa.
21. **¿Cómo se integran con el resto del modelo?** ✅ Lo que el Auditor no sabe se vuelve ficha, y un reporte puede volverse columna de Verificado.

## 5. Flujos de ingresos

22. **¿Por qué valor pagarían?** 🟡
    - No por los datos, que nunca se cobran.
    - Sí por el trabajo, la memoria, el aviso y el cómputo.
    - Es una hipótesis que se valida con 3 a 5 encargos piloto.
23. **¿Por qué pagan hoy?** ❌ Por nada: no entra dinero.
24. **¿Cómo pagan hoy?** ❌ No pueden: `CANAL_DONACION` está vacío y la alcancía marca $0.
25. **¿Cómo preferirían pagar?** 🟡 Por confirmar. Las hipótesis:
    - Donativo, para la ciudadanía.
    - Cotización con CFDI, para organizaciones.
    - Créditos por uso, para la IA.
    - Suscripción, para las alertas.
    - Quedan fuera la publicidad, por la independencia, y la cripto, por la Ley Fintech.
26. **¿Cuánto aporta cada flujo?** ❌ 0 % cada uno. Ya está el compromiso de publicar un informe anual por vía.

## 6. Recursos clave

27. **¿Cuáles requiere la propuesta de valor?** ✅
    - Intelectuales: la base cotejada (295 páginas, 32 estados, 2,479 municipios), el método, la marca y el dominio.
    - Humanos: el autor y los agentes.
    - Tecnológicos: el repositorio, Supabase y la IA.
28. **¿Y los canales?** 🟡 Faltan el correo del dominio y las cuentas en redes.
29. **¿Y las relaciones?** ✅ El Auditor y su banco de pruebas, las funciones, los formularios y el responsable publicado.
30. **¿Y los ingresos?** ❌ Faltan:
    - la forma jurídica, el RFC y el régimen;
    - la pasarela y el contador;
    - la donataria autorizada, si se quiere dar recibo deducible.

## 7. Actividades clave

31. **¿Cuáles requiere la propuesta de valor?** ✅
    - Resolver problemas: cotejar, verificar y mantener los pendientes.
    - Cuidar la plataforma: `revision.py` en 8 de 8.
32. **¿Y los canales?** 🟡 Publicar y cuidar a Google. Falta quitar el candado y tener un calendario en redes.
33. **¿Y las relaciones?** 🟡 Formularios y réplica en 3 días hábiles. Falta la respuesta automática por correo.
34. **¿Y los ingresos?** ❌ Vender pilotos, cotizar, facturar y publicar el informe anual. No ha empezado.

## 8. Asociaciones clave

35. **¿Quiénes son los socios clave?** 🟡
    - No hay socios formales, y las fuentes oficiales no son socios.
    - Posibles: universidades, OSC, medios (que cooperan y compiten) y escuelas de diplomados, como canal de capacitación.
36. **¿Quiénes son los proveedores clave?** ✅
    - Hoy: GitHub, Supabase, Cloudflare Turnstile, Anthropic, Google y el registrador del dominio.
    - Al cobrar: Vercel Pro, Stripe y Resend.
37. **¿Qué recursos obtenemos de ellos?** ✅ Hospedaje, base, redacción con IA, antispam e indexación.
38. **¿Qué actividades hacen?** ✅
    - Servir el sitio, correr los flujos, redactar con las fichas (cotejado antes de mostrar) y filtrar bots.
    - Ninguno decide qué se publica.

## 9. Estructura de costos

39. **¿Cuáles son los costos más importantes?** 🟡
    - Hoy: el tiempo del autor, el dominio y la IA.
    - Al cobrar: US$45 al mes fijos (Vercel Pro y Supabase Pro), más $140 al mes de correo y el dominio al año.
    - Cada cobro con Stripe cuesta 3.6 % + $3.
    - Precios del 24-10-2026, por confirmar (`LANZAMIENTO.md` §5 bis).
    - Es un modelo impulsado por costos.
40. **¿Qué recursos son los más caros?** 🟡 El humano. Después, los planes de pago.
41. **¿Qué actividades son las más caras?** ❌
    - Cotejar, por las horas.
    - La IA, por el uso.
    - El costo por pregunta sale de `consultas_ia`.

---

## Los otros cuatro documentos

| Documento | Qué es | Qué aporta |
|---|---|---|
| ASF, «Documentar para sancionar» (julio de 2026) | Informe especial con 20 matrices | Ya integrado (`informes-documentar-para-sancionar.html`, `D.san`). Es materia prima de un taller de pago. |
| EBC, Diplomado en Auditoría y Control Interno | Temario de 80 h | Hay un mercado que paga por formarse. Guía de temas para la metodología. |
| Centro Certificador, Diplomado en Auditoría Forense | Temario de 6 módulos (nov 2026 a abr 2027) | Sus familias de fraude (compras, nómina, obra) son las de las matrices de la ASF. Vende comunidad y cobra la acreditación aparte. |
| GestionTech360, IA para la Auditoría | Curso de US$240, 8 chatbots | Competidor indirecto. Nuestra ventaja es una IA que no puede inventar y una base mexicana cotejada. |

**Los folletos no son fuente.** Sus cifras (PwC, UIF) quedan sin verificar.
Para la metodología solo sirvieron de guía de temas: cada concepto se cotejó
contra la ley o el documento oficial que lo sostiene. Es la misma regla de la
Enciclopedia antigua (AGENTS.md §0 bis).

## Puntos ciegos

1. **El valor está, el cobro no:** 3 de 5 preguntas de ingresos dicen ❌.
2. **El candado contradice a Google:** Search Console está listo, pero Google solo ve el canje.
3. **No se mide nada:** no sabemos qué canal funciona. La solución es una analítica sin cookies.
4. **Falta elegir el primer cliente.**
5. **No se conoce el costo de la IA:** sale de `consultas_ia` en unos días.

## Lo que decide el autor

1. La forma jurídica.
2. El primer cliente.
3. El primer producto de pago. Recomendación: el **taller «Documentar para sancionar»** y la **ficha de debida diligencia del proveedor**.
4. La fecha para quitar el candado.
5. La analítica sin cookies.
6. Si se vende a los auditados (municipios y tesorerías), y con qué límites.
7. La frase de la propuesta de valor.

## Metodología

Con los temarios como guía, la Enciclopedia suma la página
`aprende-auditoria.html`, «Cómo se audita». Explica en sencillo el control
interno, los riesgos, el fraude, la auditoría forense, la prevención de
lavado y la evidencia. Cada concepto lleva su ley o documento oficial, entra
al glosario y lo encuentra el Auditor.
