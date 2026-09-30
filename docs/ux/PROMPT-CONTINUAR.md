# Cómo revisar los cambios y seguir con el plan (sin saber programar)

## Lo que tienes que hacer tú

No vas a escribir ningún comando. Tu asistente de IA hace la parte técnica.
Tú solo copias un mensaje, contestas sus preguntas y miras cómo quedó.

1. **Abre tu asistente de IA en la carpeta del proyecto.** Es el mismo programa
   que usas para trabajar en Auditavisión (Claude Code, Antigravity, Cursor u
   otro), abierto en la carpeta del proyecto.
2. **Copia el mensaje del recuadro de abajo, completo,** desde «Hola» hasta
   el final.
3. **Pégalo en el chat del asistente** y envíalo.
4. **Contesta lo que te pregunte.** Si no entiendes algo, escríbele
   «explícamelo más fácil».
5. **Cuando te diga que abras una página en tu navegador, ábrela** y mira
   cómo se ve.
6. **Para que algo se publique (que lo vea todo el mundo), el asistente te va
   a pedir permiso.** Solo contesta «sí, publícalo» cuando estés de acuerdo.

## Dos palabras que vas a leer

- **Rama:** una copia aparte del proyecto donde se prueban cambios sin que el
  público los vea. Los cambios nuevos están en la rama `ux/fase-1`.
- **Publicar:** pasar los cambios a la versión que ve todo el mundo en
  internet.

## El mensaje para copiar

```text
Hola. No sé programar, así que necesito que tú hagas toda la parte técnica y
me expliques cada cosa como si tuviera 5 años: frases cortas, sin palabras
técnicas, y un paso a la vez. Antes de cada paso dime qué vas a hacer y para
qué sirve. Si algo falla, arréglalo tú y cuéntame en palabras sencillas qué
pasó.

LO QUE NECESITO
Alguien preparó cambios para que la plataforma Auditavisión sea más fácil de
leer en el celular. Están guardados aparte, en una copia de prueba (la rama
ux/fase-1), y todavía no los ve el público. Quiero verlos, decidir si me
gustan y, si me gustan, seguir con el plan.

PASO 1 · Revisa que mi computadora tenga lo necesario
Comprueba que estén instalados git y python3. Si falta algo, dime qué es, para
qué sirve y cómo instalarlo, con instrucciones muy sencillas.

PASO 2 · Trae la versión más nueva y cámbiate a la copia de prueba
Descarga lo último del proyecto y cámbiate a la rama ux/fase-1. Si tengo
cambios sin guardar, avísame antes de hacer nada.

PASO 3 · Lee las instrucciones del proyecto
Lee AGENTS.md, CONTEXT.md, docs/ux/PLAN.md y docs/ux/fase-0-propuestas.md.
Luego explícame en 5 frases sencillas qué cambió y por qué.

PASO 4 · Enséñame cómo se ve
Prende la página en mi computadora (python3 -m http.server 8000) y dime
exactamente qué dirección abrir en el navegador: http://127.0.0.1:8000
Explícame cómo verla como si fuera un celular (en Chrome: clic derecho,
«Inspeccionar» y el botón del teléfono) y qué revisar, en una lista corta:
  - la portada nueva, con tres secciones: Lee, Explora y Consulta;
  - el botón «Menú»;
  - abrir un tema, por ejemplo «Busca tu municipio», y volver con «‹ Inicio»;
  - buscar «Zapopan» en el buscador;
  - cambiar a fondo claro.
Espera a que yo te diga qué me pareció.

PASO 5 · Comprueba que se lea bien
Corre la revisión automática de lectura:
  python3 herramientas/guardia_legibilidad.py --fase 1
Si hace falta, instala antes lo que necesita (pip install playwright y
python3 -m playwright install chromium) y dime qué estás instalando. Debe
decir «Fase 1: cumple». Explícame el resultado en palabras sencillas.

PASO 6 · Decisiones que me tocan a mí
Abre docs/ux/fase-0-propuestas.md y hazme las preguntas UNA POR UNA, en
palabras sencillas y con tu recomendación:
  1. las reglas para que el texto siempre se lea bien;
  2. el tamaño de la letra y el fondo;
  3. los nombres de las secciones (Lee, Explora, Consulta, Participa);
  4. comprar un dominio propio (una dirección de internet como
     auditavision.mx).
Cambia solo lo que yo apruebe y anótalo en ese mismo archivo.

PASO 7 · Publicar, SOLO si yo digo «sí, publícalo»
Si me gustó, pregúntame con estas palabras: «¿Quieres que lo publique para
que lo vea todo el mundo?». Si digo que sí:
  - trae primero lo último de la rama publicada
    (claude/funny-turing-imtm54) y júntalo con ux/fase-1;
  - si hay choques en los números de versión (?v=), deja uno solo y crea
    uno nuevo con: python3 herramientas/sello.py;
  - vuelve a correr la revisión de lectura del paso 5;
  - junta ux/fase-1 con claude/funny-turing-imtm54 y súbelo;
  - dime la dirección pública para que lo vea.
Si digo que no, no publiques nada.

PASO 8 · Seguir con el plan
Dime en qué parte del plan vamos (docs/ux/PLAN.md, sección 5 «Fases») y qué
sigue, en 3 frases. Lo que sigue es la fase 2: arreglar los temas uno por uno,
empezando por la calculadora de impuestos. Antes de empezar, pregúntame si
quiero seguir.
Si digo que sí:
  - trabaja en una copia aparte nueva (la rama ux/fase-2-calculadora), no en
    la que se publica;
  - sigue lo que dicen docs/ux/PLAN.md (sección 3, plantilla «herramienta») y
    AGENTS.md;
  - quita los emojis y los tamaños de letra fijos de ese tema directamente en
    los archivos;
  - cambia «Reiniciar a ceros» y «Contabilizar» por palabras más sencillas,
    como «Volver a cero» y «Ver la cuenta». Ajusta también el código que
    reconoce esos textos: BOTON_UNICO_REINICIO en audit-engine.js;
  - comprueba con:
      python3 herramientas/guardia_legibilidad.py --fase 2 --vistas calculadora
  - enséñame cómo quedó en el navegador y espera mi respuesta antes de
    publicar.

REGLAS QUE NUNCA SE ROMPEN
- Nunca inventes una cifra. Si no se puede comprobar, se marca «pendiente».
- No toques la Enciclopedia.
- No publiques nada sin que yo diga «sí, publícalo».
- Al terminar, actualiza docs/ux/PLAN.md y CONTEXT.md, y dime en 3 frases
  qué hiciste y qué falta.
```

## Si algo sale mal

- **El asistente no encuentra el proyecto:** dile «estoy en la carpeta del
  proyecto Auditavisión, búscala tú».
- **No entiendes lo que te dice:** escríbele «explícamelo más fácil, sin
  palabras técnicas».
- **La página no abre:** usa la dirección `http://127.0.0.1:8000`, no
  `localhost`.
- **Te pide una contraseña de GitHub:** es la de la cuenta con la que subes el
  proyecto. Si no la tienes, detente y pregúntale a quien te pasó esto.
