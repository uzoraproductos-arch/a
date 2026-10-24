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

\echo 'Todas las pruebas de permisos pasaron.'
