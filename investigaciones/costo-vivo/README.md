# Costo en vivo de las megaobras (módulo 2): documentos

Respaldo de la «Simulación en vivo» de la 2.2. Los datos los escriben
`herramientas/integrar_costo_vivo_megaobras.py` y `herramientas/integrar_cefedis.py`.

| Archivo | Qué sostiene | SHA-256 |
|---|---|---|
| `BIRMEX_NotasEstadosFinancieros_3T2024.pdf` · [original](https://datos.birmex.gob.mx/wp-content/uploads/2024/12/notas_estados_financieros.pdf) | Nota 14, pp. 42-45: clave de cartera **2312NEF0001** del CEFEDIS (Megafarmacia), registro 30-10-2023, autorización 6-11-2023, 425,389 m² de terreno y 90,000 posiciones | `fb3f36af96e0804a29b2c73a9207a58d21ff9d78270222375485c3da105f7e99` |

Otros documentos que usa el cálculo, ya en el repositorio:

- `investigaciones/entregas/PEMEX_TRI_EstadosFinancieros2024.pdf`: nota 12 (pp. 47-49 impresas): aportaciones de Pemex TRI a PTI Infraestructura de Desarrollo, $42,696,652 miles en 2024; resultados condensados de la filial (pérdida neta de $1,473,724 miles en 2024).
- `investigaciones/entregas/BIRMEX_EstadosFinancieros2024.pdf`: dictamen con denegación de opinión, párrafos III a V (el V sobre el CEFEDIS). Es un escaneo sin texto.
- Cartera de Hacienda, cortes de seguimiento 4T 2023 y 4T 2025 (Transparencia Presupuestaria, huellas en `herramientas/integrar_cefedis.py`): montos del CEFEDIS. No aparece en los cortes 4T 2024 ni 2T 2026.

## Lo que se revisó del reporte de Antigravity (28-09-2026) y no se usa

Cotejado contra los documentos: las cifras de PTI Infraestructura y la
clave del CEFEDIS son correctas. **No se integró**, por no tener documento
en mano: el costo de 20,959 millones de dólares del reporte 20-F, el crudo
procesado 2024-2026, la afirmación de que Pemex reservó el desglose de
Olmeca (hace falta la resolución y su folio), la baja de la ficha
2312NEF0001 del portal de cartera, los números de oficio, fechas,
superficies y condicionantes de los resolutivos ambientales, y los datos de
Fonadin. Cada uno entra cuando llegue su PDF.
