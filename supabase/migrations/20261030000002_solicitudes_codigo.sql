-- «¿No tienes código? Obtén uno» (pedido del autor, 29-10-2026): «se mandó
-- una solicitud de código al correo… y ya yo les mandaría el código… lo voy
-- a estar pasando a personas selectivas para que vayan probando poco a poco».
-- La persona deja su correo en canjea-tu-codigo.html; el autor ve la
-- solicitud en su panel, le asigna un código con la duración que elija y se
-- lo manda desde su propio correo. Quien ya usó su tiempo pide otro igual.
--
-- Datos personales: el correo (y, si quiere, su nombre y para qué lo quiere),
-- solo con el aviso de privacidad aceptado. Se borran solos 12 meses después
-- de atendida o descartada la solicitud.

create table public.solicitudes_codigo (
  id           bigint generated always as identity primary key,
  correo       text not null check (length(correo) <= 254 and correo ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'),
  nombre       text check (nombre is null or length(nombre) between 2 and 80),
  motivo       text check (motivo is null or length(motivo) <= 300),
  acepta_aviso boolean not null check (acepta_aviso),
  estado       text not null default 'nueva' check (estado in ('nueva', 'enviada', 'descartada')),
  codigo_id    bigint references public.codigos (id) on delete set null,
  ip_huella    text,
  creado       timestamptz not null default now(),
  atendida     timestamptz
);
create index solicitudes_codigo_estado on public.solicitudes_codigo (estado, creado desc);
alter table public.solicitudes_codigo enable row level security;
create policy "administración ve las solicitudes" on public.solicitudes_codigo
  for select to authenticated using (public.es_admin());
revoke all on public.solicitudes_codigo from anon;
revoke insert, update, delete on public.solicitudes_codigo from authenticated;
grant select on public.solicitudes_codigo to authenticated;

-- La solicitud. La llama la función «codigo» con la llave de servicio, después
-- del límite por IP. Si el mismo correo ya tiene una solicitud nueva, no se
-- duplica.
create or replace function public.solicitar_codigo(p_correo text, p_nombre text default null, p_motivo text default null,
                                                   p_acepta boolean default false, p_huella text default null)
returns jsonb
language plpgsql security definer set search_path = public
as $$
declare
  v_correo text := lower(trim(coalesce(p_correo, '')));
  v_id bigint;
begin
  if not coalesce(p_acepta, false) then
    return jsonb_build_object('ok', false, 'motivo', 'aviso');
  end if;
  if v_correo !~* '^[^@\s]+@[^@\s]+\.[^@\s]+$' or length(v_correo) > 254 then
    return jsonb_build_object('ok', false, 'motivo', 'correo');
  end if;
  -- Lo que ya se atendió hace más de un año se borra (aviso de privacidad).
  delete from public.solicitudes_codigo where estado <> 'nueva' and atendida < now() - interval '12 months';
  select id into v_id from public.solicitudes_codigo where correo = v_correo and estado = 'nueva' limit 1;
  if v_id is null then
    insert into public.solicitudes_codigo (correo, nombre, motivo, acepta_aviso, ip_huella)
      values (v_correo, nullif(left(trim(coalesce(p_nombre, '')), 80), ''), nullif(left(trim(coalesce(p_motivo, '')), 300), ''), true, p_huella)
      returning id into v_id;
  end if;
  return jsonb_build_object('ok', true, 'folio', 'SC-' || lpad(v_id::text, 5, '0'));
end;
$$;

-- Atender: genera un código de un uso con la duración elegida y marca la
-- solicitud como enviada. Devuelve el código para que el autor lo mande.
create or replace function public.atender_solicitud(p_id bigint, p_duracion interval)
returns jsonb
language plpgsql security definer set search_path = public
as $$
declare
  s public.solicitudes_codigo;
  k public.codigos;
begin
  if not public.es_admin() then
    raise exception 'solo la administración atiende solicitudes';
  end if;
  select * into s from public.solicitudes_codigo where id = p_id for update;
  if not found then
    raise exception 'no existe esa solicitud';
  end if;
  select * into k from public.generar_codigos(1, p_duracion, 1, null, 'Solicitud SC-' || lpad(p_id::text, 5, '0'));
  update public.solicitudes_codigo set estado = 'enviada', codigo_id = k.id, atendida = now() where id = p_id;
  return jsonb_build_object('codigo', k.codigo, 'correo', s.correo, 'nombre', s.nombre, 'duracion', k.duracion::text);
end;
$$;

create or replace function public.descartar_solicitud(p_id bigint)
returns void
language plpgsql security definer set search_path = public
as $$
begin
  if not public.es_admin() then
    raise exception 'solo la administración descarta solicitudes';
  end if;
  update public.solicitudes_codigo set estado = 'descartada', atendida = now() where id = p_id;
end;
$$;

-- La lista del panel, con el código que se mandó y cuántas veces ha pedido
-- ese correo (para ver quién vuelve).
create or replace function public.solicitudes_lista()
returns table (id bigint, correo text, nombre text, motivo text, estado text, creado timestamptz, atendida timestamptz,
               codigo text, duracion text, veces bigint)
language plpgsql stable security definer set search_path = public
as $$
begin
  if not public.es_admin() then
    raise exception 'solo la administración ve las solicitudes';
  end if;
  return query
  select s.id, s.correo, s.nombre, s.motivo, s.estado, s.creado, s.atendida, k.codigo, k.duracion::text,
         (select count(*) from public.solicitudes_codigo t where t.correo = s.correo)
  from public.solicitudes_codigo s left join public.codigos k on k.id = s.codigo_id
  order by (s.estado = 'nueva') desc, s.creado desc;
end;
$$;

revoke all on function public.solicitar_codigo(text, text, text, boolean, text) from public, anon, authenticated;
grant execute on function public.solicitar_codigo(text, text, text, boolean, text) to service_role;
revoke all on function public.atender_solicitud(bigint, interval), public.descartar_solicitud(bigint), public.solicitudes_lista() from public, anon;
grant execute on function public.atender_solicitud(bigint, interval), public.descartar_solicitud(bigint), public.solicitudes_lista() to authenticated;
