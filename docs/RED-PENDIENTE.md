# Dominios por permitir en la red de la sesión

Pedido del autor, 01-11-2026: «todos esos pendientes de enlace velos anotando».

Las sesiones de Claude Code en la nube salen a internet por la **política de red
del entorno**. Cuando un portal oficial no abre, el dato que vive ahí se queda
como `pendiente` (falta de la plataforma) aunque el documento exista. Esta es la
lista de lo que hay que permitir para cerrar esos pendientes. La política la
cambia el autor en la configuración del entorno (claude.ai/code → el entorno →
Acceso a la red: «Personalizado», con estos dominios); después de cambiarla, se
abre una sesión nueva.

**Prueba del 01-11-2026:** desde la sesión no abrió ninguno de los dominios de
abajo, ni siquiera INEGI o Banxico (`curl` devuelve 000). Solo funciona el
buscador, que da ligas pero no documentos.

Se actualiza cada vez que una nota deja un pendiente por un portal que no abre.

## Fiscalización y Congreso

| Dominio | Qué destraba | Notas que lo esperan |
|---|---|---|
| `asf.gob.mx`, `informe.asf.gob.mx` | Informes individuales y denuncias de la segunda entrega de la Cuenta Pública 2025; Matriz de Datos Básicos | `asf-segunda-entrega-cp2025`, `asf-nuevo-leon-triangulacion-cp2025` |
| `gaceta.diputados.gob.mx`, `www.diputados.gob.mx` | Dictámenes, reservas y votaciones; leyes vigentes (LeyesBiblio) | `lfd-2027-dnr-defensa-tren-maya-aifa`, `senado-ley-de-ingresos-2027` |
| `www.senado.gob.mx`, `comunicacion.senado.gob.mx` | Gaceta del Senado y votación de la Ley Federal de Derechos 2027 | `senado-ley-de-ingresos-2027`, `lfd-2027-dnr-defensa-tren-maya-aifa` |
| `www.canaldelcongreso.gob.mx` | Notas oficiales de las votaciones (ya se citan; hay que copiar su huella a la bóveda) | `senado-ley-de-ingresos-2027`, `lfd-2027-dnr-defensa-tren-maya-aifa` |
| `sil.gobernacion.gob.mx` | Perfiles legislativos (Sistema de Información Legislativa) | `garcia-luna-y-garcia-harfuch` |

## Hacienda, DOF y gobierno federal

| Dominio | Qué destraba | Notas que lo esperan |
|---|---|---|
| `dof.gob.mx`, `www.dof.gob.mx` | Decretos publicados: Ley Federal de Derechos 2027, acuerdos de la Sener | `lfd-2027-dnr-defensa-tren-maya-aifa`, `portacelis-permiso-diesel-sener` |
| `www.cuentapublica.hacienda.gob.mx` | Estados financieros de las empresas públicas (Tren Maya, AIFA); hoy falla por certificado | `lfd-2027-dnr-defensa-tren-maya-aifa` (anotado sin copia en la bóveda) |
| `www.ppef.hacienda.gob.mx` | Proyecto de Presupuesto 2027 por ramo y por empresa | `jalisco-gasto-federal-pef-2027`, `lfd-2027-dnr-defensa-tren-maya-aifa` |
| `www.transparenciapresupuestaria.gob.mx` | Datos abiertos del gasto | varias |
| `www.gob.mx` | Sener (permisos de importación), FGR, IPAB, Conagua y comunicados de Presidencia | `portacelis-permiso-diesel-sener`, `agua-guadalajara-14500-federal` |
| `stastdgv2portfgr032.blob.core.windows.net` | Estadísticas de la FEADLE (FGR) sobre agresiones a periodistas | pendiente `periodistas-feadle` |

## Empresas públicas

| Dominio | Qué destraba | Notas que lo esperan |
|---|---|---|
| `www.pemex.com` | Reporte de resultados trimestrales y saldo de la deuda | `pemex-3t-2026-perdida-neta`, pendiente `pemex-deuda` |
| `www.bmv.com.mx` | Reportes que Pemex entrega a la Bolsa | `pemex-3t-2026-perdida-neta` |

## Estados y municipios

| Dominio | Qué destraba | Notas que lo esperan |
|---|---|---|
| `www.ensenada.gob.mx` | Información financiera del Ayuntamiento y del IMCUDHE | `carnaval-ensenada-2026-imcudhe` |
| `www.asebc.gob.mx` | Auditoría Superior de Baja California | `carnaval-ensenada-2026-imcudhe` |
| `ssj.jalisco.gob.mx`, `www.jalisco.gob.mx` | Resultados de laboratorio del agua (Salud Jalisco) y comunicados del Gobierno de Jalisco | `agua-guadalajara-14500-federal` |

## Estadística oficial

| Dominio | Qué destraba |
|---|---|
| `www.inegi.org.mx` | Actualizar EFIPEM, PIB por entidad e INPC; balanza comercial por producto y valor agregado de exportación (`servidores-ia-exportaciones-contenido-nacional`) |
| `www.banxico.org.mx` | Tipo de cambio FIX (para cotejar conversiones a dólares) |
| `centralelectoral.ine.mx` | Comunicados del INE (`ine-contratos-desde-cordova`) |

## Prensa y organizaciones (punto de partida, no fuente)

Sirven para leer la nota completa que se coteja; nunca son fuente de cifras.

| Dominio | Para qué |
|---|---|
| `contralacorrupcion.mx` | Investigación de MCCI sobre Portacelis |
| `latinus.us` | Nota de los 18 mil millones de la Defensa |
| `www.jornada.com.mx` | Nota de la ASF y Nuevo León |
| `www.instagram.com` | Leer las publicaciones que pasa el autor |
| `www.justice.gov` | Sentencia de García Luna (Departamento de Justicia de EE. UU.) |
