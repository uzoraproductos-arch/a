# Costo en vivo de las megaobras (módulo 2): documentos

Respaldo de la «Simulación en vivo» de la 2.2. Los datos los escriben
`herramientas/integrar_costo_vivo_megaobras.py` y `herramientas/integrar_cefedis.py`.

| Archivo | Qué sostiene | SHA-256 |
|---|---|---|
| `BIRMEX_NotasEstadosFinancieros_3T2024.pdf` · [original](https://datos.birmex.gob.mx/wp-content/uploads/2024/12/notas_estados_financieros.pdf) | Nota 14, pp. 42-45: clave de cartera **2312NEF0001** del CEFEDIS (Megafarmacia), registro 30-10-2023, autorización 6-11-2023, 425,389 m² de terreno y 90,000 posiciones | `fb3f36af96e0804a29b2c73a9207a58d21ff9d78270222375485c3da105f7e99` |
| `ASF_CP2024_0247_RefineriaOlmeca.pdf` · [original](https://www.asf.gob.mx/Trans/Informes/IR2024c/Documentos/Auditorias/2024_0247_a.pdf) | ASF, CP 2024, auditoría 247: aportaciones de Pemex a PTI-ID $42,696.7 mdp (pp. 1, 7); erogaciones $41,998.3 mdp sin IVA, 192 contratos (pp. 1, 11); servicios administrativos $15.6 mdp (p. 12); **obra en proceso de la refinería al 31-12-2024, $357,887.3 mdp** (p. 8); IVA devuelto $14,463.2 mdp (p. 13) | `0b517333d735160e535f43df7b25eba6a8b6211a1eeeefcc4756f484947319f3` |
| `PEMEX_EstadosFinancierosConsolidados2025.pdf` · [original](https://www.cuentapublica.hacienda.gob.mx/work/models/CP/2025/tomo/VIII/52TYY.05.DAR.pdf) | Pemex consolidado 2025: PTI ID se consolida sin estados propios (p. 35); primer tren de Olmeca en febrero de 2025 y segundo en mayo (p. 54); 263 mil barriles diarios en diciembre y pico de 313 mil (p. 55) | `0a6fe9e89e0d94714ea441134ac3c1ee7446c4c4713baaf9e62d8ebd554b86b2` |

Los integra `herramientas/integrar_olmeca_cefedis_bunker.py`, que además usa el Segundo Informe de Gobierno 2026 (p. 378: Olmeca procesó 188 mil barriles diarios en promedio de septiembre de 2025 a junio de 2026) y el dictamen de Birmex 2025 (`investigaciones/entregas/`, escaneo: denegación de opinión del 20-03-2026, pp. 3 y 5 del PDF).

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
