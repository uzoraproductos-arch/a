# Auditavisión

Sistema cívico de fiscalización y geopolítica del gasto público en México.

**Versión:** 3.3 — Golden Master (estado aprobado)

## Qué es

Plataforma web de consulta ciudadana sobre el ejercicio del gasto público
federal y federalizado, organizada en nueve módulos:

| Módulo | Contenido |
|---|---|
| Presupuesto | Desglose del PEF y gasto federalizado por entidad |
| Políticos | Fichas de servidores públicos |
| Judicial | Resoluciones SCJN y marco constitucional |
| Legislativo | Iniciativas y Gaceta Parlamentaria |
| Acción financiera | Simuladores y comparativos de ahorro |
| Verificador | Validación de cifras contra fuente oficial |
| Comunidad | Participación ciudadana |
| Referencias | Fuentes: ASF, SHCP, Banxico, DOF, INE |
| FAQ | Preguntas frecuentes |

## Estructura

```
index.html                       Estructura, 9 pestañas y contenido editorial
assets/css/auditavision.css      Estilos maestros
assets/js/mexico-states-geo.js   Geometría vectorial de los 32 estados
assets/js/audit-database.js      Base de datos fiscal
assets/js/audit-engine.js        Motor de la aplicación
```

Dependencias externas por CDN: Leaflet 1.9.4 (mapas) y Google Fonts
(Playfair Display, Source Serif 4, JetBrains Mono, Inter).

## Estado de la migración

Este repositorio se creó al migrar el proyecto desde su entorno de
desarrollo anterior. Por ahora **solo contiene `index.html`**; los cuatro
archivos de `assets/` están pendientes de subir. Sin ellos la página carga
sin estilos y sin funcionalidad, ya que el HTML invoca `AuditEngine` en más
de 300 puntos.

## Ejecución local

Requiere un servidor HTTP: al abrir el archivo directamente con `file://`
el navegador bloquea la carga de los scripts.

```bash
python3 -m http.server 8000
# luego abrir http://localhost:8000
```

## Fuentes de datos

Transparencia Presupuestaria (SHCP), Auditoría Superior de la Federación,
Banco de México, Diario Oficial de la Federación, Cartografía INE y Gaceta
Parlamentaria de la Cámara de Diputados.
