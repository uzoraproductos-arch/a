# Inspector ciudadano: primera entrega local

Fecha: 23 de septiembre de 2026. Diseño orientado por Taste / Redesign Skill, conservando HTML, CSS y JavaScript nativos.

## Alcance implementado

- Tres espacios conectados: examinar notas, seguimiento manual de dependencias y mesa ciudadana por expediente.
- Casos iniciales: captura del titular de Tlaxcala, captura con dieciséis asuntos y publicación de X aportadas por el usuario. Todos pendientes de verificación. X se pudo leer directamente en el navegador tras fallar la consulta web: cinco afirmaciones sobre inversión ferroviaria, empleos, kilómetros e inauguraciones previstas. El video no se pudo reproducir.
- Registro de afirmaciones, capturas, fuentes con ubicación y periodo, propuestas personales e historial. No hay porcentajes de veracidad ni decisiones automáticas. Añadir una URL o rellenar campos no autentica un documento.
- Comentarios, preguntas, fuentes y réplicas por caso. No se inventan participantes ni actividad social.
- Persistencia local, exportación JSON y ficha copiable con fuentes y límites. Si falla el almacenamiento, aparece un aviso y la sesión sigue exportable.
- Se retira de la interfaz el antiguo índice financiero alimentado por cifras sin respaldo. El catálogo y funciones heredadas se conservan en el código para una futura migración de datos; no sustentan conclusiones en el nuevo Inspector.
- Se retiran el total que sumaba deuda, intereses, pérdidas y observaciones, y su equivalencia en días de ingreso personal. Las magnitudes separadas aún requieren la conciliación documental registrada en CONTEXT.md.
- Corrección de la inserción HTML de la consulta sin resultados en el buscador global.

## Lo que todavía no hace

No descarga ni extrae publicaciones de X automáticamente, no hace OCR, no analiza PDF, no consulta cuentas públicas en segundo plano y no emite dictámenes oficiales. Los enlaces a los portales son puntos de búsqueda, no evidencia del caso. Esta entrega no afirma que las notas adjuntas sean verdaderas o falsas.

La mesa es un cuaderno local, no una red social en funcionamiento. Para la siguiente fase hacen falta una base compartida, autenticación, permisos por expediente, almacenamiento de archivos, moderación, reportes, bloqueo de abuso, mecanismos de rectificación e historial de revisiones independiente de los comentarios. Las credenciales del servidor nunca deberán estar en el JavaScript público. Ninguna publicación comunitaria debe convertir votos o popularidad en veracidad.

El seguimiento requiere cargar series con ejercicio, unidad, fuente exacta, fecha de corte y estado de fiscalización. La existencia de una observación no basta para imputar un delito a una persona.

## Procedencia de imágenes

Las dos capturas son material aportado por el usuario para revisión local. No se consideran fotografías editoriales propias ni se asume una licencia para una futura redistribución pública. Los originales se conservan. La incorporación local no publica el sitio.

## Referencias de metodología

- https://www.asf.gob.mx/Section/52_Que_hacemos_y_como_lo_hacemos
- https://www.asf.gob.mx/Trans/Informes/IR2023b/Documentos/Matriz/IR2023_Entrega_a.pdf
- https://github.com/Leonxlnx/taste-skill/blob/main/skills/redesign-skill/SKILL.md

## Respaldo y publicación

Respaldo anterior del HTML y motor: backups/20260923-inspector-previo/. El script herramientas/integrar_inspector.py es una migración única, no un comando de arranque. El sello administra ahora ocho recursos locales.

Esta carpeta no contiene .git. No se ejecutó pull, commit ni push; la rama remota no fue modificada y el sitio no se publicó. Antes de integrar en la rama documentada se deben cotejar estas modificaciones con el estado remoto y conservar cualquier avance externo.
