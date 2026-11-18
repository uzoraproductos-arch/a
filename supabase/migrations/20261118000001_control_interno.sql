-- El control interno de la plataforma (pedido del autor, 18-11-2026: «tener
-- esta parte de control interno dentro de nuestra plataforma… editar o renovar
-- en vez de revocar… un historial… el tiempo que ha consumido los usuarios,
-- qué tema les ha interesado… dónde le da clic… gráficas de nuestros
-- consumos»). Tres piezas, todas solo para la administración:
--
--   1. Renovar un código: le devuelve la vida (quita la revocación y el
--      archivo), le suma personas o fecha para canjear y, si se pide, le da
--      más tiempo a quien ya lo canjeó, desde hoy si ya se le había acabado.
--   2. La bitácora: cada cosa que hace la administración con los códigos, las
--      solicitudes y su código maestro queda anotada sola, con quién y cuándo.
--      No se edita ni se borra desde el panel.
--   3. La medición de uso: qué páginas se abren, cuánto tiempo se quedan y
--      dónde se da clic, por navegador con pase (el número al azar de
--      av-pase), para saber qué temas interesan. NO se guarda: la IP, el
--      navegador, lo que la persona escribe (ni sus preguntas al chat: de
--      ellas solo el modo y la página a la que llevó la respuesta), ni nada
--      que diga quién es. Respeta «No rastrear» y el control global de
--      privacidad del navegador, y se apaga desde el aviso de privacidad. Se
--      borra sola a los 12 meses. La de la administración no se cuenta.

-- ---------------------------------------------------------------------------
-- 1. Renovar
-- ---------------------------------------------------------------------------
create table public.renovaciones (
  id        bigint generated always as identity primary key,
  codigo_id bigint not null references public.codigos (id) on delete cascade,
  pase_id   uuid not null references public.pases (id) on delete cascade,
  desde     timestamptz not null default now(),
  lapso     interval not null check (lapso > interval '0' and lapso <= interval '5 years')
);
create index renovaciones_pase on public.renovaciones (pase_id, desde);
alter table public.renovaciones enable row level security;
create policy "administración ve las renovaciones" on public.renovaciones
  for select to authenticated using (public.es_admin());
revoke all on public.renovaciones from anon;
revoke insert, update, delete on public.renovaciones from authenticated;

-- El tiempo de un pase, ahora con las renovaciones: canjes y renovaciones en
-- el orden en que pasaron; cada uno suma su lapso desde el final del anterior
-- o desde su propio momento, lo que sea más tarde. El semanal, como antes.
create or replace function public.pase_hasta(p_pase uuid)
returns timestamptz
language plpgsql stable security definer set search_path = public
as $$
declare
  v_hasta timestamptz;
  v_fin timestamptz;
  r record;
begin
  for r in
    select c.en, k.duracion, k.semanal, k.canjear_antes, c.id as orden from public.canjes c join public.codigos k on k.id = c.codigo_id
    where c.pase_id = p_pase and not k.revocado
    union all
    select x.desde, x.lapso, false, null::timestamptz, x.id from public.renovaciones x join public.codigos k on k.id = x.codigo_id
    where x.pase_id = p_pase and not k.revocado
    order by 1, 5
  loop
    if r.semanal then
      v_fin := least(r.en + r.duracion, r.canjear_antes);
      v_hasta := greatest(coalesce(v_hasta, v_fin), v_fin);
    else
      v_hasta := greatest(coalesce(v_hasta, r.en), r.en) + r.duracion;
    end if;
  end loop;
  return v_hasta;
end;
$$;
revoke all on function public.pase_hasta(uuid) from public, anon, authenticated;
grant execute on function public.pase_hasta(uuid) to service_role;

-- ---------------------------------------------------------------------------
-- 2. La bitácora
-- ---------------------------------------------------------------------------
create table public.bitacora_admin (
  id      bigint generated always as identity primary key,
  en      timestamptz not null default now(),
  quien   text not null,
  accion  text not null check (length(accion) <= 40),
  objeto  text check (length(objeto) <= 80),
  detalle jsonb not null default '{}'::jsonb
);
create index bitacora_admin_en on public.bitacora_admin (en desc);
alter table public.bitacora_admin enable row level security;
create policy "administración lee la bitácora" on public.bitacora_admin
  for select to authenticated using (public.es_admin());
revoke all on public.bitacora_admin from anon;
revoke insert, update, delete on public.bitacora_admin from authenticated;

-- Quién lo hizo: el correo de la cuenta de la administración, o «sistema»
-- cuando lo hace la plataforma sola (el canje, el código de la semana).
create or replace function public.quien_admin()
returns text
language sql stable security definer set search_path = public, auth
as $$
  select coalesce((select u.email from auth.users u where u.id = auth.uid() and public.es_admin()), 'sistema');
$$;
revoke all on function public.quien_admin() from public, anon, authenticated;

create or replace function public.anota_bitacora(p_accion text, p_objeto text, p_detalle jsonb default '{}'::jsonb)
returns void
language plpgsql security definer set search_path = public
as $$
begin
  insert into public.bitacora_admin (quien, accion, objeto, detalle)
    values (public.quien_admin(), p_accion, left(p_objeto, 80), coalesce(p_detalle, '{}'::jsonb));
end;
$$;
revoke all on function public.anota_bitacora(text, text, jsonb) from public, anon, authenticated;

-- Los códigos: se anota cada alta, cambio y baja. Que se use (usos + 1 en el
-- canje) no es un acto de la administración: no se anota aquí.
create or replace function public.codigos_a_bitacora() returns trigger
language plpgsql security definer set search_path = public
as $$
declare
  d jsonb := '{}'::jsonb;
begin
  if tg_op = 'INSERT' then
    perform public.anota_bitacora(case when new.semanal then 'código de la semana' else 'creó' end, new.codigo,
      jsonb_strip_nulls(jsonb_build_object('duracion', new.duracion::text, 'personas', new.usos_max, 'canjear_antes', new.canjear_antes, 'nota', new.nota)));
    return new;
  end if;
  if tg_op = 'DELETE' then
    perform public.anota_bitacora('eliminó', old.codigo, jsonb_build_object('lo_habian_usado', old.usos));
    return old;
  end if;
  if new.revocado is distinct from old.revocado then
    perform public.anota_bitacora(case when new.revocado then 'revocó' else 'devolvió' end, new.codigo, '{}'::jsonb);
  end if;
  if new.archivado is distinct from old.archivado then
    perform public.anota_bitacora(case when new.archivado then 'archivó' else 'desarchivó' end, new.codigo, '{}'::jsonb);
  end if;
  if new.duracion is distinct from old.duracion then d := d || jsonb_build_object('duracion', jsonb_build_array(old.duracion::text, new.duracion::text)); end if;
  if new.usos_max is distinct from old.usos_max then d := d || jsonb_build_object('personas', jsonb_build_array(old.usos_max, new.usos_max)); end if;
  if new.canjear_antes is distinct from old.canjear_antes then d := d || jsonb_build_object('canjear_antes', jsonb_build_array(old.canjear_antes, new.canjear_antes)); end if;
  if new.nota is distinct from old.nota then d := d || jsonb_build_object('nota', jsonb_build_array(old.nota, new.nota)); end if;
  -- renovar_codigo deja su propio renglón, con todo lo que cambió.
  if d <> '{}'::jsonb and current_setting('av.renovando', true) is distinct from 'si' then
    perform public.anota_bitacora('editó', new.codigo, d);
  end if;
  return new;
end;
$$;
create trigger codigos_bitacora after insert or update or delete on public.codigos
  for each row execute function public.codigos_a_bitacora();

create or replace function public.solicitudes_a_bitacora() returns trigger
language plpgsql security definer set search_path = public
as $$
begin
  if new.estado is distinct from old.estado then
    perform public.anota_bitacora(case new.estado when 'enviada' then 'atendió solicitud' when 'descartada' then 'descartó solicitud' else 'solicitud ' || new.estado end,
      'solicitud ' || new.id, jsonb_strip_nulls(jsonb_build_object('codigo', (select k.codigo from public.codigos k where k.id = new.codigo_id))));
  end if;
  return new;
end;
$$;
create trigger solicitudes_bitacora after update on public.solicitudes_codigo
  for each row execute function public.solicitudes_a_bitacora();

-- El código maestro: se anota que cambió, nunca cuál es.
create or replace function public.maestro_a_bitacora() returns trigger
language plpgsql security definer set search_path = public
as $$
begin
  perform public.anota_bitacora('cambió su código maestro', null, '{}'::jsonb);
  return new;
end;
$$;
create trigger admin_codigo_bitacora after insert or update on public.admin_codigo
  for each row execute function public.maestro_a_bitacora();

create or replace function public.bitacora_lista(p_limite integer default 300)
returns setof public.bitacora_admin
language plpgsql stable security definer set search_path = public
as $$
begin
  if not public.es_admin() then
    raise exception 'solo la administración lee la bitácora';
  end if;
  return query select * from public.bitacora_admin order by en desc, id desc limit least(greatest(coalesce(p_limite, 300), 1), 5000);
end;
$$;

-- Renovar: devuelve cuántas personas recibieron más tiempo. Marca que está
-- renovando para que el cambio no se anote dos veces («editó» y «renovó»).
create or replace function public.renovar_codigo(p_id bigint, p_lapso interval default null,
                                                 p_usos_mas integer default 0, p_antes timestamptz default null)
returns integer
language plpgsql security definer set search_path = public
as $$
declare
  k public.codigos;
  n integer := 0;
begin
  if not public.es_admin() then
    raise exception 'solo la administración renueva códigos';
  end if;
  select * into k from public.codigos where id = p_id;
  if not found then
    raise exception 'ese código ya no existe';
  end if;
  if k.semanal then
    raise exception 'el código de la semana no se renueva: cámbialo con «Cambiarlo ahora»';
  end if;
  if p_lapso is not null and (p_lapso <= interval '0' or p_lapso > interval '5 years') then
    raise exception 'el tiempo extra va de un día a cinco años';
  end if;
  if coalesce(p_usos_mas, 0) < 0 or coalesce(p_usos_mas, 0) > 10000 then
    raise exception 'las personas extra van de 0 a 10,000';
  end if;
  if p_antes is not null and p_antes <= now() then
    raise exception 'la nueva fecha para canjear tiene que ser después de hoy';
  end if;
  perform set_config('av.renovando', 'si', true);
  update public.codigos set
    revocado = false,
    archivado = false,
    usos_max = usos_max + coalesce(p_usos_mas, 0),
    canjear_antes = case when p_antes is not null then p_antes
                         when canjear_antes is not null and canjear_antes <= now() then null
                         else canjear_antes end
  where id = p_id;
  perform set_config('av.renovando', '', true);
  if p_lapso is not null then
    insert into public.renovaciones (codigo_id, pase_id, lapso)
      select distinct k.id, c.pase_id, p_lapso from public.canjes c where c.codigo_id = k.id;
    get diagnostics n = row_count;
  end if;
  perform public.anota_bitacora('renovó', k.codigo, jsonb_strip_nulls(jsonb_build_object(
    'tiempo_extra', p_lapso::text, 'personas_con_mas_tiempo', case when p_lapso is null then null else n end,
    'personas_mas', nullif(coalesce(p_usos_mas, 0), 0), 'canjear_antes', p_antes,
    'estaba', case when k.revocado then 'revocado' when k.archivado then 'archivado' end)));
  return n;
end;
$$;
revoke all on function public.renovar_codigo(bigint, interval, integer, timestamptz), public.bitacora_lista(integer) from public, anon;
grant execute on function public.renovar_codigo(bigint, interval, integer, timestamptz), public.bitacora_lista(integer) to authenticated;

-- ---------------------------------------------------------------------------
-- 3. La medición de uso
-- ---------------------------------------------------------------------------
-- A qué parte de la plataforma pertenece una página: una sola regla, que usan
-- el registro y el tablero.
create or replace function public.uso_seccion(p_pagina text)
returns text
language sql immutable
as $$
  select case
    when p_pagina = 'index.html' then 'Portada'
    when p_pagina in ('herramienta-inspector-pregunta.html', 'herramienta-inspector-dictamen.html') then 'Auditor (chat)'
    when p_pagina ~ '^planisferio' then 'Planisferio'
    when p_pagina ~ '^(noticias|periodismo-en-riesgo)' then 'Noticiero'
    when p_pagina ~ '^servicios' then 'Servicios'
    when p_pagina ~ '^(herramienta|numeros-herramientas)' then 'Herramientas'
    when p_pagina ~ '^auditoria' then 'Auditoría en imágenes'
    when p_pagina ~ '^expediente' then 'Expedientes'
    when p_pagina ~ '^informes' then 'Informes oficiales'
    when p_pagina ~ '^(numeros|sigue-el-dinero|estado-de-cuenta)' then 'Enciclopedia: Números'
    when p_pagina ~ '^(datos|descarga-los-datos)' then 'Enciclopedia: Datos'
    when p_pagina ~ '^(aprende|glosario|marco-legal)' then 'Enciclopedia: Aprende'
    when p_pagina ~ '^enciclopedia' then 'Enciclopedia'
    when p_pagina ~ '^(participa|agora|garantias|donaciones|comunidad|pilares)' then 'Comunidad'
    when p_pagina ~ '^(canjea-tu-codigo|administracion-codigos)' then 'Entrada'
    when p_pagina ~ '^(aviso-de-privacidad|derecho-de-replica|pendientes|fe-de-erratas)' then 'Transparencia y avisos'
    else 'Otras páginas'
  end;
$$;

create table public.uso_eventos (
  id       bigint generated always as identity primary key,
  en       timestamptz not null default now(),
  dia      date not null default (now() at time zone 'America/Mexico_City')::date,
  hora     smallint not null default extract(hour from now() at time zone 'America/Mexico_City')::smallint,
  pase_id  uuid references public.pases (id) on delete set null,
  sesion   text not null check (sesion ~ '^[0-9a-z]{8,24}$'),
  tipo     text not null check (tipo in ('vista', 'tiempo', 'clic', 'pregunta')),
  pagina   text not null check (pagina ~ '^[a-z0-9._-]{1,120}\.html$'),
  seccion  text not null,
  destino  text check (length(destino) <= 160),
  etiqueta text check (length(etiqueta) <= 80),
  segundos integer check (segundos between 0 and 7200),
  modo     text check (modo in ('inspector', 'periodista', 'ciudadano', 'ambientalista'))
);
create index uso_eventos_dia on public.uso_eventos (dia, tipo);
create index uso_eventos_pase on public.uso_eventos (pase_id) where pase_id is not null;
alter table public.uso_eventos enable row level security;
create policy "administración ve el uso" on public.uso_eventos
  for select to authenticated using (public.es_admin());
revoke all on public.uso_eventos from anon;
revoke insert, update, delete on public.uso_eventos from authenticated;

-- Lo llama la función «codigo» (acción uso) con la llave de servicio, después
-- de su límite por IP. Recibe hasta 40 eventos; los que no cumplen la forma se
-- descartan sin error. El navegador de la administración no se cuenta.
create or replace function public.registrar_uso(p_pase uuid, p_sesion text, p_eventos jsonb)
returns integer
language plpgsql security definer set search_path = public
as $$
declare
  e jsonb;
  v_pase uuid;
  v_pag text;
  v_tipo text;
  n integer := 0;
begin
  if p_sesion is null or p_sesion !~ '^[0-9a-z]{8,24}$' or jsonb_typeof(p_eventos) is distinct from 'array' then
    return 0;
  end if;
  select id into v_pase from public.pases where id = p_pase;
  if v_pase is not null and exists (select 1 from public.canjes c join public.codigos k on k.id = c.codigo_id
                                    where c.pase_id = v_pase and k.semanal) then
    return 0;
  end if;
  for e in select * from jsonb_array_elements(p_eventos) limit 40 loop
    if jsonb_typeof(e) <> 'object' then continue; end if;
    v_tipo := e ->> 'tipo';
    v_pag := lower(coalesce(e ->> 'pagina', ''));
    if v_tipo not in ('vista', 'tiempo', 'clic', 'pregunta') or v_pag !~ '^[a-z0-9._-]{1,120}\.html$' then continue; end if;
    insert into public.uso_eventos (pase_id, sesion, tipo, pagina, seccion, destino, etiqueta, segundos, modo)
    values (v_pase, p_sesion, v_tipo, v_pag, public.uso_seccion(v_pag),
            nullif(left(regexp_replace(coalesce(e ->> 'destino', ''), '[[:cntrl:]]', '', 'g'), 160), ''),
            nullif(left(regexp_replace(coalesce(e ->> 'etiqueta', ''), '\s+', ' ', 'g'), 80), ''),
            case when v_tipo = 'tiempo' and (e ->> 'segundos') ~ '^\d{1,5}$' then least((e ->> 'segundos')::integer, 7200) end,
            case when e ->> 'modo' in ('inspector', 'periodista', 'ciudadano', 'ambientalista') then e ->> 'modo' end);
    n := n + 1;
  end loop;
  delete from public.uso_eventos where dia < (now() at time zone 'America/Mexico_City')::date - interval '12 months';
  return n;
end;
$$;
revoke all on function public.registrar_uso(uuid, text, jsonb) from public, anon, authenticated;
grant execute on function public.registrar_uso(uuid, text, jsonb) to service_role;

-- El tablero: todo lo que pintan las gráficas del panel, de los últimos
-- p_dias días (de 1 a 365). Solo cuentas: ningún renglón suelto.
create or replace function public.uso_tablero(p_dias integer default 30)
returns jsonb
language plpgsql stable security definer set search_path = public
as $$
declare
  v_dias integer := least(greatest(coalesce(p_dias, 30), 1), 365);
  v_desde date := (now() at time zone 'America/Mexico_City')::date - (v_dias - 1);
  v jsonb;
begin
  if not public.es_admin() then
    raise exception 'solo la administración ve el uso';
  end if;
  with ev as (select * from public.uso_eventos where dia >= v_desde),
  ultimo_codigo as (
    select distinct on (c.pase_id) c.pase_id, k.codigo, k.nota
    from public.canjes c join public.codigos k on k.id = c.codigo_id
    where not k.semanal order by c.pase_id, c.en desc, c.id desc)
  select jsonb_build_object(
    'dias', v_dias, 'desde', v_desde,
    'resumen', (select jsonb_build_object(
        'vistas', count(*) filter (where tipo = 'vista'),
        'sesiones', count(distinct sesion),
        'personas', count(distinct pase_id),
        'minutos', round(coalesce(sum(segundos) filter (where tipo = 'tiempo'), 0) / 60.0),
        'clics', count(*) filter (where tipo = 'clic'),
        'preguntas', count(*) filter (where tipo = 'pregunta')) from ev),
    'canjes', (select count(*) from public.canjes c join public.codigos k on k.id = c.codigo_id
               where not k.semanal and (c.en at time zone 'America/Mexico_City')::date >= v_desde),
    'sin_respuesta', (select count(*) from public.preguntas_bot where (creado at time zone 'America/Mexico_City')::date >= v_desde),
    'por_dia', coalesce((select jsonb_agg(x order by x.dia) from (
        select g.dia::date as dia,
               count(e.id) filter (where e.tipo = 'vista') as vistas,
               count(distinct e.sesion) as sesiones,
               count(distinct e.pase_id) as personas,
               round(coalesce(sum(e.segundos) filter (where e.tipo = 'tiempo'), 0) / 60.0) as minutos
        from generate_series(v_desde, (now() at time zone 'America/Mexico_City')::date, interval '1 day') g(dia)
        left join ev e on e.dia = g.dia::date
        group by 1) x), '[]'::jsonb),
    'secciones', coalesce((select jsonb_agg(x order by x.minutos desc, x.vistas desc) from (
        select seccion, count(*) filter (where tipo = 'vista') as vistas,
               round(coalesce(sum(segundos) filter (where tipo = 'tiempo'), 0) / 60.0) as minutos,
               count(distinct sesion) as sesiones
        from ev group by 1) x), '[]'::jsonb),
    'paginas', coalesce((select jsonb_agg(x order by x.vistas desc, x.minutos desc) from (
        select pagina, seccion, count(*) filter (where tipo = 'vista') as vistas,
               round(coalesce(sum(segundos) filter (where tipo = 'tiempo'), 0) / 60.0) as minutos
        from ev group by 1, 2 order by 3 desc, 4 desc limit 20) x), '[]'::jsonb),
    'clics', coalesce((select jsonb_agg(x order by x.n desc) from (
        select destino, max(etiqueta) as etiqueta, count(*) as n
        from ev where tipo = 'clic' and destino is not null group by 1 order by 3 desc limit 20) x), '[]'::jsonb),
    'modos', coalesce((select jsonb_agg(x order by x.n desc) from (
        select coalesce(modo, 'sin modo') as modo, count(*) as n from ev where tipo = 'pregunta' group by 1) x), '[]'::jsonb),
    'destinos_chat', coalesce((select jsonb_agg(x order by x.n desc) from (
        select destino, count(*) as n from ev where tipo = 'pregunta' and destino is not null group by 1 order by 2 desc limit 15) x), '[]'::jsonb),
    'horas', coalesce((select jsonb_agg(x order by x.hora) from (
        select g.h as hora, count(e.id) as vistas
        from generate_series(0, 23) g(h) left join ev e on e.hora = g.h and e.tipo = 'vista' group by 1) x), '[]'::jsonb),
    'codigos', coalesce((select jsonb_agg(x order by x.minutos desc, x.vistas desc) from (
        select u.codigo, u.nota, count(distinct e.pase_id) as personas, count(*) filter (where e.tipo = 'vista') as vistas,
               round(coalesce(sum(e.segundos) filter (where e.tipo = 'tiempo'), 0) / 60.0) as minutos
        from ev e join ultimo_codigo u on u.pase_id = e.pase_id
        group by 1, 2 order by 5 desc limit 15) x), '[]'::jsonb)
  ) into v;
  return v;
end;
$$;
revoke all on function public.uso_tablero(integer) from public, anon;
grant execute on function public.uso_tablero(integer) to authenticated;

-- El registro de un código, ahora con lo que cada persona usó la plataforma:
-- minutos y páginas vistas (de lo medido, los últimos 12 meses).
drop function if exists public.codigo_uso(bigint);
create function public.codigo_uso(p_id bigint default null)
returns table (codigo_id bigint, codigo text, persona integer, canjeado timestamptz, hasta timestamptz,
               ultimo date, dias integer, nombre text, correo text, minutos integer, vistas integer, renovado boolean)
language plpgsql stable security definer set search_path = public
as $$
begin
  if not public.es_admin() then
    raise exception 'solo la administración ve el uso de los códigos';
  end if;
  return query
  select k.id, k.codigo,
         (row_number() over (partition by k.id order by c.en, c.id))::integer,
         c.en, public.pase_hasta(c.pase_id),
         (select max(d.dia) from public.pase_dias d where d.pase_id = c.pase_id),
         (select count(*) from public.pase_dias d where d.pase_id = c.pase_id)::integer,
         s.nombre, s.correo,
         (select round(coalesce(sum(e.segundos), 0) / 60.0) from public.uso_eventos e where e.pase_id = c.pase_id and e.tipo = 'tiempo')::integer,
         (select count(*) from public.uso_eventos e where e.pase_id = c.pase_id and e.tipo = 'vista')::integer,
         exists (select 1 from public.renovaciones r where r.pase_id = c.pase_id and r.codigo_id = k.id)
  from public.canjes c
  join public.codigos k on k.id = c.codigo_id
  left join lateral (select x.nombre, x.correo from public.solicitudes_codigo x where x.codigo_id = k.id order by x.id limit 1) s on true
  where p_id is null or k.id = p_id
  order by c.en desc, c.id desc;
end;
$$;
revoke all on function public.codigo_uso(bigint) from public, anon;
grant execute on function public.codigo_uso(bigint) to authenticated;
