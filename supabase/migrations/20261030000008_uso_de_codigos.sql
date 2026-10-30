-- El registro de uso de cada código (pedido del autor, 30-10-2026: «tener un
-- registro del tiempo que lo está usando cada usuario… del código que le
-- pasé»). Por cada canje la administración ve cuándo se canjeó, hasta cuándo
-- abre, la última vez que se usó y en cuántos días distintos.
--
-- Qué se guarda y qué no: solo la FECHA de cada día en que el navegador abrió
-- la plataforma (una vez al día, cuando acceso.js confirma el pase). No se
-- guardan horas, páginas, IP ni nada que diga quién es. El nombre y el correo
-- solo aparecen si el código salió de una solicitud que la persona hizo con su
-- correo (y con el aviso de privacidad aceptado). Los días se borran solos a
-- los 12 meses.
create table public.pase_dias (
  pase_id uuid not null references public.pases (id) on delete cascade,
  dia     date not null,
  primary key (pase_id, dia)
);
alter table public.pase_dias enable row level security;
create policy "administración ve los días de uso" on public.pase_dias
  for select to authenticated using (public.es_admin());
revoke all on public.pase_dias from anon;
revoke insert, update, delete on public.pase_dias from authenticated;

-- La consulta diaria del pase (función «codigo», acción consultar): anota el
-- día y devuelve hasta cuándo abre, como pase_hasta.
create or replace function public.pase_consulta(p_pase uuid)
returns timestamptz
language plpgsql security definer set search_path = public
as $$
declare
  v_hoy date := (now() at time zone 'America/Mexico_City')::date;
begin
  if exists (select 1 from public.pases where id = p_pase) then
    insert into public.pase_dias (pase_id, dia) values (p_pase, v_hoy) on conflict do nothing;
    delete from public.pase_dias where dia < v_hoy - interval '12 months';
  end if;
  return public.pase_hasta(p_pase);
end;
$$;

-- El día del canje también cuenta como día de uso.
create or replace function public.canje_cuenta_dia() returns trigger
language plpgsql security definer set search_path = public
as $$
begin
  insert into public.pase_dias (pase_id, dia)
    values (new.pase_id, (new.en at time zone 'America/Mexico_City')::date) on conflict do nothing;
  return new;
end;
$$;
create trigger canjes_cuenta_dia after insert on public.canjes
  for each row execute function public.canje_cuenta_dia();

-- El registro de un código: un renglón por persona que lo canjeó (numeradas
-- por orden de canje), o el de todos los códigos si p_id es null.
create or replace function public.codigo_uso(p_id bigint default null)
returns table (codigo_id bigint, codigo text, persona integer, canjeado timestamptz, hasta timestamptz,
               ultimo date, dias integer, nombre text, correo text)
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
         s.nombre, s.correo
  from public.canjes c
  join public.codigos k on k.id = c.codigo_id
  left join lateral (select x.nombre, x.correo from public.solicitudes_codigo x where x.codigo_id = k.id order by x.id limit 1) s on true
  where p_id is null or k.id = p_id
  order by c.en desc, c.id desc;
end;
$$;

revoke all on function public.pase_consulta(uuid), public.canje_cuenta_dia() from public, anon, authenticated;
grant execute on function public.pase_consulta(uuid) to service_role;
revoke all on function public.codigo_uso(bigint) from public, anon;
grant execute on function public.codigo_uso(bigint) to authenticated;
