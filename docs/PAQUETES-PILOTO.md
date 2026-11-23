# Paquetes piloto — documento interno del autor

**Estado:** borrador para fijar tarifas piloto (Ronda 10, 23-11-2026). **No se publica ningún monto**
hasta que el autor cierre precios tras los primeros encargos (`AGENTS.md` §0 quater: «nunca un monto sin
pilotos»). Las casillas de precio van vacías a propósito.

Lo que ya está en el sitio, sin montos:

- `servicios-como-se-cobra.html#paquetes`: las tres tarjetas, con lo que incluye cada paquete, lo que se
  recibe, los servicios que junta y «Cotiza este paquete».
- `servicios-cotiza.html`: la fila «¿Te interesa un paquete piloto?» llena a un toque el servicio, el tema y la
  pregunta (que siguen libres); también con `?paquete=pyme|despacho|territorial`. **No agrega campos** a la
  solicitud, así que la validación del pase vigente y la función `recibir-formulario` no cambian.
- La fuente única es `PAQUETES` de `herramientas/apartados.py`: si un paquete nombra un servicio que no existe
  o trae un monto («$» seguido de un número), la generación se detiene.

## La línea entre lo gratis y lo que se cobra

| Gratis, siempre | Se cobra (por paquete) |
|---|---|
| Consultar cualquier dato público en el Auditor, el Planisferio y la Enciclopedia | Procesar **tus** datos: tu cartera de RFC, tus lotes de XML, tus recibos de nómina |
| Revisar un RFC suelto contra las listas | Vigilar tu cartera cada semana y avisarte cuando algo cambia (Vigía) |
| Leer los dictámenes y las fichas que genera el chat | Firmar el dictamen ejecutivo con folio y huella SHA-256, y darle seguimiento |
| Las aplicaciones que corren en tu navegador sin subir nada | El tiempo de revisión humana, la entrega y el taller |

## Tabla de alcances

| | **1. PyME y contrapartes** | **2. Despacho contable y cumplimiento PLD** | **3. Territorial e institucional** |
|---|---|---|---|
| Para quién | Empresas que pagan a proveedores o cobran a clientes | Despachos contables y áreas de cumplimiento con varios clientes | Redacciones, organizaciones civiles, cabildos, órganos de control, universidades |
| Servicios que junta | `contrapartes`, `seguimiento`, `diligencia` | `facturas`, `nomina`, `seguimiento`, `diligencia` | `radiografia`, `temporada`, `entrega`, `capacitacion`, `licencia` |
| Incluye | Vigía (69-B, sancionados, OFAC, ONU) + matriz de cartera + dictámenes ejecutivos | Vigía ampliado por cliente + lotes CFDI (XML) por proveedor + nómina + dictámenes de debida diligencia | Radiografía municipal o estatal + temporada electoral o kit de entrega-recepción + taller ASF o licencia |
| Entregables | Matriz CSV, avisos semanales, un dictamen por contraparte con señal | Resumen por lote y proveedor, señales de nómina, dictamen por cliente | Dictamen con expediente visual, kit o licencia, taller agendado |
| Límite sugerido (por fijar) | ___ RFC vigilados · ___ dictámenes al mes | ___ clientes · ___ XML por lote · ___ recibos por periodo | ___ municipios o estados · ___ talleres · ___ usuarios de licencia |
| Plazo del piloto (por fijar) | ___ meses | ___ meses | ___ meses o una temporada |
| **Precio piloto (MXN, más IVA)** | **$ ________** | **$ ________** | **$ ________** |
| Forma de cobro (de `COBRO`) | Suscripción mensual según RFC + precio fijo por ficha | Precio por lote y por periodo de nómina + suscripción | Precio fijo y público por documento; por temporada; por gobierno; por taller; convenio anual |

## Lo que nunca entra a un paquete

- Montos de multas ni promesas de que revisar libra de una sanción.
- Datos de personas físicas: sus RFC se cotejan por huella y nunca se publican.
- Decir que la plataforma cumple por el cliente, evita el fraude o emite un dictamen pericial.

## Antes de publicar precios

1. Cerrar los tres primeros encargos piloto (uno por paquete) y anotar horas, fuentes y entrega reales.
2. Llenar las casillas de arriba.
3. Pasar los precios a `monetizacion.py` (`PLANES`) y encender `MONETIZACION` solo con visto bueno del autor.
4. Cambiar el texto «Se cotiza; la tarifa sale de los pilotos» de `apartados.py` y regenerar.
