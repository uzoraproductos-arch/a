-- El código de la administración (pedido del autor, 30-10-2026: «un código
-- que será exclusivo del administrador y que por seguridad cambia cada semana
-- en automático»). Cambia cada lunes a las 0:00 de la Ciudad de México: el
-- código de una semana solo se canjea esa semana y el acceso que da termina
-- el lunes siguiente, aunque nadie abra el panel (lo calcula pase_hasta, sin
-- tareas programadas). El panel lo muestra a quien entra con su correo de
-- administración, y puede cambiarlo antes si se filtró.
alter table public.codigos add column if not exists semanal boolean not null default false;

-- El tiempo de un pase: el código semanal no suma, abre hasta su lunes.
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
    select c.en, k.duracion, k.semanal, k.canjear_antes from public.canjes c join public.codigos k on k.id = c.codigo_id
    where c.pase_id = p_pase and not k.revocado order by c.en, c.id
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

-- El código de esta semana: lo crea si falta, retira los de semanas pasadas
-- y, con p_cambiar, lo reemplaza por uno nuevo en ese momento.
create or replace function public.codigo_admin_semana(p_cambiar boolean default false)
returns jsonb
language plpgsql security definer set search_path = public, extensions
as $$
declare
  v_ini timestamptz := date_trunc('week', now() at time zone 'America/Mexico_City') at time zone 'America/Mexico_City';
  v_fin timestamptz := v_ini + interval '7 days';
  k public.codigos;
begin
  if not public.es_admin() then
    raise exception 'solo la administración ve su código';
  end if;
  update public.codigos set revocado = true
    where semanal and not revocado and (canjear_antes <= v_ini or (coalesce(p_cambiar, false) and canjear_antes = v_fin));
  select * into k from public.codigos where semanal and not revocado and canjear_antes = v_fin order by id desc limit 1;
  if not found then
    select * into k from public.generar_codigos(1, interval '7 days', 50, v_fin, 'Administración: código de la semana');
    update public.codigos set semanal = true where id = k.id;
  end if;
  return jsonb_build_object('codigo', k.codigo, 'desde', v_ini, 'hasta', v_fin, 'usos', k.usos);
end;
$$;
revoke all on function public.codigo_admin_semana(boolean) from public, anon;
grant execute on function public.codigo_admin_semana(boolean) to authenticated;
