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
3. El primer producto de pago. Recomendación: el **taller «Documentar para sancionar»**.
4. La fecha para quitar el candado.
5. La analítica sin cookies.

## Metodología

Con los temarios como guía, la Enciclopedia suma la página
`aprende-auditoria.html`, «Cómo se audita». Explica en sencillo el control
interno, los riesgos, el fraude, la auditoría forense, la prevención de
lavado y la evidencia. Cada concepto lleva su ley o documento oficial, entra
al glosario y lo encuentra el Auditor.
