-- Prueba de permisos de la migración: cada renglón dice qué se espera y
-- detiene todo si no se cumple. Corre con herramientas/prueba_base_datos.py.
\set ON_ERROR_STOP on

-- Dos personas y una administradora.
insert into auth.users values
  ('00000000-0000-0000-0000-00000000000a', 'a@ejemplo.mx'),
  ('00000000-0000-0000-0000-00000000000b', 'b@ejemplo.mx'),
  ('00000000-0000-0000-0000-0000000000ad', 'admin@ejemplo.mx');
insert into public.administradores values ('00000000-0000-0000-0000-0000000000ad', 'Moderación');

create function pg_temp.debe_fallar(sql text, que text) returns void language plpgsql as $$
begin
  begin
    execute sql;
  exception when others then
    raise notice 'OK  (rechazado) %', que;
    return;
  end;
  raise exception 'FALLA: se permitió %', que;
end $$;
create function pg_temp.igual(v bigint, esperado bigint, que text) returns void language plpgsql as $$
begin
  if v is distinct from esperado then raise exception 'FALLA: % = %, se esperaba %', que, v, esperado; end if;
  raise notice 'OK  % = %', que, v;
end $$;
grant execute on function pg_temp.debe_fallar(text, text), pg_temp.igual(bigint, bigint, text) to anon, authenticated;

-- 1. La función (llave de servicio) guarda envíos y preguntas.
set role service_role;
insert into public.envios (tipo, asunto, texto, pagina, estado) values
  ('errata', 'Cifra del PEF', 'La cifra del anexo no coincide con el DOF.', 'numeros-gasto-publico.html', 'publicado'),
  ('solicitud', 'Investigar contrato', 'Quiero que revisen el contrato de la obra.', null, 'nuevo');
insert into public.preguntas_bot (pregunta, motivo, version) values ('¿cuánto costó la barda?', 'sin', '20261024r'), ('¿Cuánto  costó la barda?', 'sin', '20261024r');
select pg_temp.debe_fallar($$insert into public.envios (tipo, asunto, texto, correo) values ('tema','Hola','Texto suficiente aquí','x@y.mx')$$, 'un correo sin aceptar el aviso de privacidad');
select pg_temp.debe_fallar($$insert into public.envios (tipo, asunto, texto, pagina) values ('tema','Hola','Texto suficiente aquí','https://otro.sitio/x')$$, 'una página que no es de la plataforma');
select pg_temp.debe_fallar($$insert into public.consultas_ia (pregunta, fichas, version, verificada, rechazo) values ('x?', '{1}', '20261024r', true, 'formato')$$, 'una consulta verificada y rechazada a la vez');
insert into public.busquedas_web (clave, nombre, enlaces, vence) values ('fulana perez', 'Fulana Pérez', '[]', now() + interval '1 day');
select pg_temp.debe_fallar($$insert into public.busquedas_web (clave, nombre, enlaces, vence) values ('<script>', 'Fulana Pérez', '[]', now())$$, 'una búsqueda con la clave mal escrita');
select pg_temp.debe_fallar($$insert into public.busquedas_web (clave, nombre, enlaces, vence) values ('fulana perez', 'Fulana Pérez', '{"texto": "redactado"}', now())$$, 'una búsqueda que guarda texto en vez de enlaces');
reset role;

-- 2. El público (anon): no lee lo privado ni escribe directo.
set role anon;
select pg_temp.igual((select count(*) from public.envios), 0, 'envíos que ve el público');
select pg_temp.igual((select count(*) from public.envios_publicos), 1, 'erratas publicadas que ve el público');
select pg_temp.igual((select count(*) from public.preguntas_bot), 0, 'preguntas del bot que ve el público');
select pg_temp.igual((select count(*) from public.donaciones), 0, 'donaciones (públicas, aún vacías)');
select pg_temp.debe_fallar($$insert into public.envios (tipo, asunto, texto) values ('tema','Directo','Sin pasar por la función')$$, 'que el público escriba directo en envíos');
select pg_temp.debe_fallar($$insert into public.donaciones (monto, comprobante) values (100, 'falso')$$, 'que el público invente una donación');
select pg_temp.debe_fallar($$insert into public.portales_cache (fuente, url, clave, sha256, cuerpo, bytes, vence) values ('banxico-sie','https://x','k',repeat('a',64),'{}',2,now())$$, 'que el público altere la copia de un portal');
select pg_temp.debe_fallar($$select public.limite_ok('h','r',1,60)$$, 'que el público use el límite por minuto');
select pg_temp.igual((select count(*) from public.busquedas_web), 1, 'búsquedas en internet que ve el público');
select pg_temp.debe_fallar($$insert into public.busquedas_web (clave, nombre, enlaces, vence) values ('falsa busca', 'Falsa Busca', '[]', now())$$, 'que el público plante una búsqueda');
select pg_temp.debe_fallar($$insert into public.foro_hilos (titulo) values ('Sin cuenta no se puede')$$, 'abrir un hilo sin cuenta');
reset role;

-- 3. Una persona con cuenta: su perfil, sus alertas, el foro.
set role authenticated;
set request.jwt.claim.sub = '00000000-0000-0000-0000-00000000000a';
insert into public.perfiles (user_id, seudonimo, entidad) values ('00000000-0000-0000-0000-00000000000a', 'Vecina de Puebla', 'PUE');
insert into public.alertas (ente) values ('estado:pue'), ('federal:pemex');
insert into public.foro_hilos (titulo) values ('¿Alguien revisó el Ramo 33 de mi municipio?');
select pg_temp.debe_fallar($$insert into public.foro_hilos (titulo, aprobado) values ('Me apruebo sola', true)$$, 'que alguien apruebe su propio hilo');
select pg_temp.debe_fallar($$insert into public.perfiles (user_id, seudonimo) values ('00000000-0000-0000-0000-00000000000b', 'Suplantación')$$, 'crear el perfil de otra persona');
select pg_temp.debe_fallar($$insert into public.alertas (ente) values ('estado:<script>')$$, 'una alerta con un ente mal escrito');
select pg_temp.igual((select count(*) from public.foro_hilos), 1, 'hilos que ve su autora (sin aprobar)');
select pg_temp.igual((select count(*) from public.envios), 0, 'envíos que ve una persona común');
select pg_temp.igual((select count(*) from public.consultas_ia), 0, 'consultas de IA que ve una persona común');

set request.jwt.claim.sub = '00000000-0000-0000-0000-00000000000b';
select pg_temp.igual((select count(*) from public.perfiles), 0, 'perfiles ajenos que ve otra persona');
select pg_temp.igual((select count(*) from public.alertas), 0, 'alertas ajenas que ve otra persona');
select pg_temp.igual((select count(*) from public.foro_hilos), 0, 'hilos sin aprobar que ve otra persona');
update public.envios set estado = 'publicado';
select pg_temp.igual((select count(*) from public.envios_publicos), 1, 'erratas publicadas tras un intento de publicar sin permiso');

-- 4. La administradora modera.
set request.jwt.claim.sub = '00000000-0000-0000-0000-0000000000ad';
select pg_temp.igual((select count(*) from public.envios), 2, 'envíos que ve la administración');
update public.foro_hilos set aprobado = true;
update public.envios set estado = 'en_revision', respuesta = 'Lo revisamos' where tipo = 'solicitud';
select pg_temp.igual((select veces from public.preguntas_por_atender limit 1), 2, 'veces de la pregunta más repetida (sin importar mayúsculas ni espacios)');
reset role;

set role anon;
reset request.jwt.claim.sub;
select pg_temp.igual((select count(*) from public.foro_hilos), 1, 'hilos aprobados que ve el público');
reset role;

-- 5. El límite por minuto.
set role service_role;
select pg_temp.igual((select count(*) from generate_series(1, 5) g where public.limite_ok('huella', 'ia', 3, 60)), 3, 'consultas que deja pasar un límite de 3 por minuto');
reset role;

-- 6. La bóveda de evidencias: pública para leer, inalterable para todos.
set role service_role;
insert into public.evidencias (url, sha256, bytes, tipo, copiado, ruta, usos) values
  ('https://www.dof.gob.mx/ejemplo.pdf', repeat('a', 64), 1024, 'application/pdf', '2026-10-26', repeat('a', 64) || '.pdf', '{cotejo:ejemplo:0}'),
  ('https://www.dof.gob.mx/ejemplo.pdf', repeat('b', 64), 2048, 'application/pdf', '2026-10-27', null, '{cotejo:ejemplo:0}');
insert into storage.objects (bucket_id, name) values ('boveda', repeat('a', 64) || '.pdf');
select pg_temp.debe_fallar($$insert into public.evidencias (url, sha256, bytes, copiado) values ('https://x.mx/a', 'no-es-huella', 1, '2026-10-27')$$, 'una huella que no es SHA-256');
select pg_temp.debe_fallar($$insert into public.evidencias (url, sha256, bytes, copiado) values ('javascript:alert(1)', repeat('c', 64), 1, '2026-10-27')$$, 'una dirección que no es http');
select pg_temp.debe_fallar($$insert into public.evidencias (url, sha256, bytes, copiado) values ('https://www.dof.gob.mx/ejemplo.pdf', repeat('a', 64), 1024, '2026-10-28')$$, 'la misma huella dos veces');
select pg_temp.debe_fallar($$update public.evidencias set sha256 = repeat('d', 64)$$, 'corregir una huella, ni con la llave de servicio');
select pg_temp.debe_fallar($$delete from public.evidencias$$, 'borrar una evidencia, ni con la llave de servicio');
reset role;

set role anon;
select pg_temp.igual((select count(*) from public.evidencias), 2, 'evidencias que ve el público');
select pg_temp.igual((select cambios from public.evidencias_vigentes where url = 'https://www.dof.gob.mx/ejemplo.pdf'), 1, 'veces que cambió el documento de ejemplo');
select pg_temp.igual((select count(*) from storage.objects where bucket_id = 'boveda'), 1, 'archivos de la bóveda que ve el público');
select pg_temp.debe_fallar($$insert into public.evidencias (url, sha256, bytes, copiado) values ('https://falsa.mx/x', repeat('e', 64), 1, '2026-10-27')$$, 'que el público plante una evidencia');
select pg_temp.debe_fallar($$insert into storage.objects (bucket_id, name) values ('boveda', 'falso.pdf')$$, 'que el público suba un archivo a la bóveda');
reset role;

set role authenticated;
set request.jwt.claim.sub = '00000000-0000-0000-0000-0000000000ad';
select pg_temp.debe_fallar($$insert into public.evidencias (url, sha256, bytes, copiado) values ('https://falsa.mx/y', repeat('f', 64), 1, '2026-10-27')$$, 'que la administración escriba evidencias sin la llave de servicio');
delete from storage.objects where bucket_id = 'boveda';
select pg_temp.igual((select count(*) from storage.objects where bucket_id = 'boveda'), 1, 'archivos de la bóveda tras un intento de borrarlos sin la llave de servicio');
reset role;
reset request.jwt.claim.sub;

-- 7. Los códigos de acceso (29-10-2026): solo la administración los genera y
-- los ve; el público canjea por la función (llave de servicio).
set role anon;
select pg_temp.debe_fallar($$select count(*) from public.codigos$$, 'que el público lea los códigos');
select pg_temp.debe_fallar($$select public.canjear_codigo('ABCD2345')$$, 'que el público canjee sin pasar por la función');
select pg_temp.debe_fallar($$select public.generar_codigos(1, interval '1 day')$$, 'que el público genere códigos');
reset role;

set role authenticated;
set request.jwt.claim.sub = '00000000-0000-0000-0000-00000000000a';
select pg_temp.debe_fallar($$select public.generar_codigos(1, interval '1 day')$$, 'que una cuenta común genere códigos');
select pg_temp.debe_fallar($$select * from public.codigos_lista()$$, 'que una cuenta común vea la lista de códigos');
select pg_temp.debe_fallar($$insert into public.codigos (codigo, duracion) values ('ABCD2345', interval '1 day')$$, 'que una cuenta común escriba un código');
set request.jwt.claim.sub = '00000000-0000-0000-0000-0000000000ad';
select count(*) as n from public.generar_codigos(3, interval '7 days', 1, null, 'Prueba semana') \gset
select pg_temp.igual(:n, 3, 'códigos de una semana generados');
select count(*) as n from public.generar_codigos(1, interval '1 day', 2, null, 'Grupo') \gset
select pg_temp.igual((select count(*) from public.generar_codigos(1, interval '100 years', 1, null, 'Ilimitado')), 1, 'un código ilimitado');
select count(*) as n from public.generar_codigos(1, interval '1 day', 1, now() - interval '1 hour', 'Ya vencido') \gset
select pg_temp.debe_fallar($$select public.generar_codigos(501, interval '1 day')$$, 'generar más de 500 códigos de una vez');
select pg_temp.debe_fallar($$select public.generar_codigos(1, interval '10 years')$$, 'un código de más de cinco años');
select pg_temp.igual((select count(*) from public.codigos where codigo ~ '^[0-9]{8}$'), 6, 'códigos de 8 números');
select codigo as c1 from public.codigos where nota = 'Prueba semana' order by id limit 1 \gset
select codigo as c2 from public.codigos where nota = 'Prueba semana' order by id offset 1 limit 1 \gset
select codigo as cg from public.codigos where nota = 'Grupo' \gset
select codigo as cv from public.codigos where nota = 'Ya vencido' \gset
reset role;
reset request.jwt.claim.sub;

set role service_role;
select (public.canjear_codigo(:'c1'))->>'pase' as pase \gset
select pg_temp.igual((select count(*) from public.pases where id = :'pase'), 1, 'pase creado al canjear');
select pg_temp.igual(abs(extract(epoch from public.pase_hasta(:'pase') - (now() + interval '7 days')))::bigint / 60, 0, 'minutos de diferencia con una semana desde el canje');
select pg_temp.igual(((public.canjear_codigo(:'c1')) ->> 'motivo' = 'agotado')::int, 1, 'un código de un uso, canjeado otra vez');
select pg_temp.igual(((public.canjear_codigo(:'c1', :'pase')) ->> 'motivo' = 'ya_canjeado')::int, 1, 'el mismo pase con el mismo código');
select pg_temp.igual(((public.canjear_codigo(:'cg', :'pase')) ->> 'ok')::boolean::int, 1, 'un segundo código en el mismo pase');
select pg_temp.igual(abs(extract(epoch from public.pase_hasta(:'pase') - (now() + interval '8 days')))::bigint / 60, 0, 'minutos de diferencia con ocho días (el tiempo se suma)');
select pg_temp.igual(((public.canjear_codigo(lower(substr(:'c2', 1, 4)) || ' - ' || lower(substr(:'c2', 5)))) ->> 'ok')::boolean::int, 1, 'un código escrito en minúsculas y con guion');
select pg_temp.igual(((public.canjear_codigo(:'cv')) ->> 'motivo' = 'vencido')::int, 1, 'un código que ya no se podía canjear');
select pg_temp.igual(((public.canjear_codigo('ABC')) ->> 'motivo' = 'formato')::int, 1, 'un código mal escrito');
select pg_temp.igual(((public.canjear_codigo('ZZZZ2222')) ->> 'motivo' = 'no_valido')::int, 1, 'un código que no existe');
select pg_temp.igual(((public.canjear_codigo('OOOO1111')) ->> 'motivo' = 'formato')::int, 1, 'un código con O y 1, que no se usan');
reset role;

set role authenticated;
set request.jwt.claim.sub = '00000000-0000-0000-0000-0000000000ad';
select public.revocar_codigo((select id from public.codigos where codigo = :'cg'));
select pg_temp.igual((select count(*) from public.codigos_lista() where estado = 'revocado'), 1, 'códigos revocados en la lista');
select pg_temp.igual((select count(*) from public.codigos_lista() where estado = 'en_uso'), 2, 'códigos en uso en la lista');
select pg_temp.igual((select count(*) from public.codigos_lista() where estado = 'sin_usar'), 2, 'códigos sin usar en la lista');
select pg_temp.igual((select count(*) from public.codigos_lista() where estado = 'vencido'), 1, 'códigos vencidos en la lista');
reset role;
reset request.jwt.claim.sub;
set role service_role;
select pg_temp.igual(abs(extract(epoch from public.pase_hasta(:'pase') - (now() + interval '7 days')))::bigint / 60, 0, 'minutos de diferencia con una semana tras revocar el segundo código');
select pg_temp.igual(((public.canjear_codigo(:'cg')) ->> 'motivo' = 'no_valido')::int, 1, 'un código revocado');
reset role;

-- 7 bis. Los códigos propios (30-10-2026): los escribe la administración.
set role anon;
select pg_temp.debe_fallar($$select public.crear_codigo('23456789', interval '1 day')$$, 'que el público cree un código propio');
reset role;
set role authenticated;
set request.jwt.claim.sub = '00000000-0000-0000-0000-00000000000a';
select pg_temp.debe_fallar($$select public.crear_codigo('23456789', interval '1 day')$$, 'que una cuenta común cree un código propio');
set request.jwt.claim.sub = '00000000-0000-0000-0000-0000000000ad';
select pg_temp.igual((select count(*) from public.crear_codigo('2345-6789', interval '3 days', 5, null, 'Taller')), 1, 'un código propio, escrito con guion');
select pg_temp.igual((select count(*) from public.codigos where codigo = '23456789' and usos_max = 5), 1, 'el código propio se guarda sin guion');
select pg_temp.debe_fallar($$select public.crear_codigo('2345 6789', interval '1 day')$$, 'un código propio repetido');
select pg_temp.debe_fallar($$select public.crear_codigo('PASE2345', interval '1 day')$$, 'un código propio con letras');
select pg_temp.igual((select count(*) from public.crear_codigo('1000 0001', interval '1 day', 1, null, null)), 1, 'un código propio con ceros y unos, sin nota');
select pg_temp.debe_fallar($$select public.crear_codigo('234567', interval '1 day')$$, 'un código propio de menos de 8 números');
reset role;
reset request.jwt.claim.sub;
set role service_role;
select pg_temp.igual(((public.canjear_codigo('2345-6789')) ->> 'ok')::boolean::int, 1, 'el código propio se canjea');
select pg_temp.igual(((public.canjear_codigo('1000-0001')) ->> 'ok')::boolean::int, 1, 'un código con ceros y unos se canjea');
reset role;

-- 8. «Obtén uno»: las solicitudes de código (29-10-2026).
set role anon;
select pg_temp.debe_fallar($$select count(*) from public.solicitudes_codigo$$, 'que el público lea las solicitudes de código');
select pg_temp.debe_fallar($$select public.solicitar_codigo('x@y.mx', null, null, true)$$, 'que el público pida un código sin pasar por la función');
reset role;
set role service_role;
select pg_temp.igual(((public.solicitar_codigo('Ana@Ejemplo.mx', 'Ana', 'Soy contadora', true, 'h1')) ->> 'ok')::boolean::int, 1, 'una solicitud de código');
select pg_temp.igual(((public.solicitar_codigo('ana@ejemplo.mx', null, null, true)) ->> 'ok')::boolean::int, 1, 'la misma persona pide otra vez');
select pg_temp.igual(((public.solicitar_codigo('b@ejemplo.mx', null, null, false)) ->> 'motivo' = 'aviso')::int, 1, 'una solicitud sin aceptar el aviso');
select pg_temp.igual(((public.solicitar_codigo('no-es-correo', null, null, true)) ->> 'motivo' = 'correo')::int, 1, 'una solicitud sin correo válido');
select pg_temp.igual((select count(*) from public.solicitudes_codigo), 1, 'solicitudes guardadas (sin duplicar el mismo correo)');
reset role;
set role authenticated;
set request.jwt.claim.sub = '00000000-0000-0000-0000-00000000000a';
select pg_temp.debe_fallar($$select * from public.solicitudes_lista()$$, 'que una cuenta común vea las solicitudes');
select pg_temp.debe_fallar($$select public.atender_solicitud(1, interval '1 day')$$, 'que una cuenta común atienda una solicitud');
set request.jwt.claim.sub = '00000000-0000-0000-0000-0000000000ad';
select (public.atender_solicitud((select id from public.solicitudes_codigo limit 1), interval '3 days')) ->> 'codigo' as cs \gset
select pg_temp.igual((select count(*) from public.solicitudes_lista() where estado = 'enviada' and codigo = :'cs' and duracion = '3 days'), 1, 'solicitud atendida con su código de 3 días');
reset role;
reset request.jwt.claim.sub;
set role service_role;
select pg_temp.igual(((public.canjear_codigo(:'cs')) ->> 'ok')::boolean::int, 1, 'el código de la solicitud se canjea');
select pg_temp.igual(((public.solicitar_codigo('ana@ejemplo.mx', null, 'Se me acabó el tiempo', true)) ->> 'ok')::boolean::int, 1, 'pedir más tiempo después de usarlo');
select pg_temp.igual((select count(*) from public.solicitudes_codigo where correo = 'ana@ejemplo.mx'), 2, 'solicitudes del mismo correo tras usar su código');
reset role;

-- 9. Los envíos se guardan 12 meses (30-10-2026).
insert into public.envios (tipo, asunto, texto, correo, acepta_aviso, creado) values
  ('tema', 'Viejo', 'Un envío de hace más de un año', 'v@ejemplo.mx', true, now() - interval '13 months');
insert into public.envios (tipo, asunto, texto, estado, correo, acepta_aviso, creado) values
  ('errata', 'Errata vieja', 'Una fe de erratas publicada hace más de un año', 'publicado', 'e@ejemplo.mx', true, now() - interval '13 months');
insert into public.envios (tipo, asunto, texto) values ('tema', 'Nuevo', 'Un envío de hoy, que barre los viejos');
select pg_temp.igual((select count(*) from public.envios where asunto = 'Viejo'), 0, 'un envío de hace más de 12 meses se borra');
select pg_temp.igual((select count(*) from public.envios where asunto = 'Errata vieja' and correo is null), 1, 'una errata publicada vieja se queda sin correo');
select pg_temp.igual((select count(*) from public.envios where asunto = 'Nuevo'), 1, 'el envío nuevo se guarda');

-- 10. El código semanal de la administración (30-10-2026).
set role authenticated;
set request.jwt.claim.sub = '00000000-0000-0000-0000-00000000000a';
select pg_temp.debe_fallar($$select public.codigo_admin_semana()$$, 'que una cuenta común vea el código de la administración');
set request.jwt.claim.sub = '00000000-0000-0000-0000-0000000000ad';
select (public.codigo_admin_semana()) ->> 'codigo' as ca \gset
select pg_temp.igual(((public.codigo_admin_semana()) ->> 'codigo' = :'ca')::int, 1, 'el código de la semana es el mismo al pedirlo otra vez');
select (public.codigo_admin_semana(true)) ->> 'codigo' as cb \gset
select pg_temp.igual((:'ca' <> :'cb')::int, 1, 'cambiarlo antes da un código nuevo');
reset role;
reset request.jwt.claim.sub;
select pg_temp.igual((select count(*) from public.codigos where codigo = :'ca' and revocado), 1, 'el código anterior queda revocado');
set role service_role;
select pg_temp.igual(((public.canjear_codigo(:'ca')) ->> 'ok' = 'true')::int, 0, 'el código anterior ya no abre');
select (public.canjear_codigo(:'cb')) ->> 'hasta' as hb \gset
select pg_temp.igual((:'hb'::timestamptz <= date_trunc('week', now() at time zone 'America/Mexico_City') at time zone 'America/Mexico_City' + interval '7 days')::int, 1,
  'el acceso de la administración termina el lunes');
reset role;

\echo 'Todas las pruebas de permisos pasaron.'
