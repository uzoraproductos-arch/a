-- Orden en la tabla de códigos (pedido del autor, 30-10-2026: «un control…
-- de la tabla del registro de los códigos, de editar y eliminar, así como de
-- archivar, como para mantener un orden»).
--   * Editar: la nota, cuántas personas lo pueden usar, hasta cuándo se
--     canjea y su duración. Cambiar la duración cambia también el tiempo de
--     quien ya lo canjeó (pase_hasta lo calcula al momento).
--   * Archivar: lo quita de la lista principal sin borrarlo ni cambiar lo que
--     abre. Un código archivado que sigue en uso sigue abriendo.
--   * Eliminar: lo borra para siempre con sus canjes; quien lo canjeó pierde
--     ese tiempo. Una solicitud atendida con él se queda, sin su código.
--   * El código semanal de la administración no se edita ni se elimina: se
--     cambia con «Cambiarlo ahora» (codigo_admin_semana).
alter table public.codigos add column if not exists archivado boolean not null default false;

-- La lista cambia de forma (trae semanal, archivado y canjes): se rehace.
drop function if exists public.codigos_lista();
create function public.codigos_lista()
returns table (id bigint, codigo text, duracion text, usos integer, usos_max integer, canjear_antes timestamptz,
               nota text, revocado boolean, creado timestamptz, hasta timestamptz, estado text,
               semanal boolean, archivado boolean)
language plpgsql stable security definer set search_path = public
as $$
begin
  if not public.es_admin() then
    raise exception 'solo la administración ve los códigos';
  end if;
  return query
  select k.id, k.codigo, k.duracion::text, k.usos, k.usos_max, k.canjear_antes, k.nota, k.revocado, k.creado, h.hasta,
         case
           when k.revocado then 'revocado'
           when h.hasta > now() then 'en_uso'
           when k.usos > 0 and k.usos >= k.usos_max then 'terminado'
           when k.canjear_antes is not null and now() > k.canjear_antes then 'vencido'
           when k.usos > 0 then 'terminado'
           else 'sin_usar'
         end,
         k.semanal, k.archivado
  from public.codigos k
  left join lateral (select max(public.pase_hasta(c.pase_id)) as hasta from public.canjes c where c.codigo_id = k.id) h on true
  order by k.creado desc, k.id desc;
end;
$$;

create or replace function public.editar_codigo(p_id bigint, p_nota text, p_usos_max integer, p_antes timestamptz, p_duracion interval)
returns void
language plpgsql security definer set search_path = public
as $$
declare
  k public.codigos;
begin
  if not public.es_admin() then
    raise exception 'solo la administración edita códigos';
  end if;
  select * into k from public.codigos where id = p_id;
  if not found then
    raise exception 'ese código ya no existe';
  end if;
  if k.semanal then
    raise exception 'el código de la semana no se edita: cámbialo con «Cambiarlo ahora»';
  end if;
  if coalesce(p_usos_max, k.usos_max) < k.usos then
    raise exception 'ya lo usaron % personas: no puede bajar de ahí', k.usos;
  end if;
  update public.codigos set
    nota = nullif(trim(p_nota), ''),
    usos_max = coalesce(p_usos_max, usos_max),
    canjear_antes = p_antes,
    duracion = coalesce(p_duracion, duracion)
  where id = p_id;
end;
$$;

create or replace function public.archivar_codigo(p_id bigint, p_archivado boolean default true)
returns void
language plpgsql security definer set search_path = public
as $$
begin
  if not public.es_admin() then
    raise exception 'solo la administración archiva códigos';
  end if;
  update public.codigos set archivado = coalesce(p_archivado, true) where id = p_id;
end;
$$;

-- Archiva de una vez los que ya no abren a nadie: revocados, terminados y
-- vencidos. Devuelve cuántos archivó.
create or replace function public.archivar_inactivos()
returns integer
language plpgsql security definer set search_path = public
as $$
declare
  n integer;
begin
  if not public.es_admin() then
    raise exception 'solo la administración archiva códigos';
  end if;
  update public.codigos set archivado = true
  where not archivado
    and id in (select l.id from public.codigos_lista() l where l.estado in ('revocado', 'terminado', 'vencido'));
  get diagnostics n = row_count;
  return n;
end;
$$;

create or replace function public.eliminar_codigo(p_id bigint)
returns void
language plpgsql security definer set search_path = public
as $$
begin
  if not public.es_admin() then
    raise exception 'solo la administración elimina códigos';
  end if;
  if exists (select 1 from public.codigos where id = p_id and semanal) then
    raise exception 'el código de la semana no se elimina: cámbialo con «Cambiarlo ahora»';
  end if;
  delete from public.codigos where id = p_id;
end;
$$;

revoke all on function public.codigos_lista(), public.editar_codigo(bigint, text, integer, timestamptz, interval),
  public.archivar_codigo(bigint, boolean), public.archivar_inactivos(), public.eliminar_codigo(bigint) from public, anon;
grant execute on function public.codigos_lista(), public.editar_codigo(bigint, text, integer, timestamptz, interval),
  public.archivar_codigo(bigint, boolean), public.archivar_inactivos(), public.eliminar_codigo(bigint) to authenticated;
