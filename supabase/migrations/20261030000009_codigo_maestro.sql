-- El código maestro de la administración (pedido del autor, 30-10-2026: «que
-- nomás a través del código que yo ingreso se reconozca que yo soy el
-- administrador»; «únicamente va a estar cambiando si yo te lo digo»).
--   * Son 8 números, como los demás códigos, y se escribe en la misma entrada
--     (canjea-tu-codigo.html). Si coincide, la entrada abre la sesión de la
--     administración, sin correo, y lleva al panel.
--   * No cambia solo: lo pone y lo cambia la administración desde su panel.
--     Nunca vive en el repositorio (que es público) ni en el chat: aquí solo se
--     guarda su huella (bcrypt), que no se puede leer de vuelta.
--   * Cada entrada con el código queda anotada (fecha y hora, sin IP) y el
--     panel la muestra, para darse cuenta si alguien más lo usó.
--   * El límite de intentos por IP lo pone la función «codigo».
create table public.admin_codigo (
  id        integer primary key default 1 check (id = 1),
  huella    text not null,
  user_id   uuid not null references public.administradores (user_id) on delete cascade,
  cambiado  timestamptz not null default now()
);
alter table public.admin_codigo enable row level security;
revoke all on public.admin_codigo from anon, authenticated;

create table public.admin_entradas (
  id  bigserial primary key,
  en  timestamptz not null default now()
);
alter table public.admin_entradas enable row level security;
revoke all on public.admin_entradas from anon, authenticated;

-- Pone o cambia el código (solo la administración, ya dentro con su correo o
-- con el código anterior). No puede ser uno que ya exista como código común.
create or replace function public.fijar_codigo_admin(p_codigo text)
returns void
language plpgsql security definer set search_path = public, extensions
as $$
declare
  v_cod text := regexp_replace(coalesce(p_codigo, ''), '[^0-9]', '', 'g');
begin
  if not public.es_admin() then
    raise exception 'solo la administración pone su código';
  end if;
  if v_cod !~ '^[0-9]{8}$' or length(regexp_replace(coalesce(p_codigo, ''), '[\s-]', '', 'g')) <> 8 then
    raise exception 'el código lleva 8 números, del 0 al 9';
  end if;
  if v_cod ~ '^(.)\1{7}$' or v_cod in ('12345678', '87654321', '01234567') then
    raise exception 'ese código es demasiado fácil de adivinar: escribe otro';
  end if;
  if exists (select 1 from public.codigos where codigo = v_cod) then
    raise exception 'ese número ya es un código de acceso común: escribe otro';
  end if;
  insert into public.admin_codigo (id, huella, user_id, cambiado)
    values (1, crypt(v_cod, gen_salt('bf', 10)), auth.uid(), now())
    on conflict (id) do update set huella = excluded.huella, user_id = excluded.user_id, cambiado = excluded.cambiado;
end;
$$;

-- Lo que el panel muestra: si hay código, cuándo cambió y las últimas entradas.
create or replace function public.codigo_admin_info()
returns jsonb
language plpgsql stable security definer set search_path = public
as $$
begin
  if not public.es_admin() then
    raise exception 'solo la administración ve su código';
  end if;
  return jsonb_build_object(
    'puesto', exists (select 1 from public.admin_codigo),
    'cambiado', (select cambiado from public.admin_codigo),
    'entradas', coalesce((select jsonb_agg(e.en order by e.en desc)
                          from (select en from public.admin_entradas order by en desc limit 20) e), '[]'::jsonb));
end;
$$;

-- La revisión (solo la función «codigo», con la llave de servicio): si el
-- código coincide, anota la entrada y devuelve a quién pertenece; si no, null.
create or replace function public.revisar_codigo_admin(p_codigo text)
returns uuid
language plpgsql security definer set search_path = public, extensions
as $$
declare
  v_cod text := regexp_replace(coalesce(p_codigo, ''), '[^0-9]', '', 'g');
  a public.admin_codigo;
begin
  if v_cod !~ '^[0-9]{8}$' then
    return null;
  end if;
  select * into a from public.admin_codigo where id = 1;
  if not found or crypt(v_cod, a.huella) <> a.huella then
    return null;
  end if;
  insert into public.admin_entradas default values;
  delete from public.admin_entradas where en < now() - interval '12 months';
  return a.user_id;
end;
$$;

revoke all on function public.fijar_codigo_admin(text), public.codigo_admin_info(), public.revisar_codigo_admin(text) from public, anon, authenticated;
grant execute on function public.fijar_codigo_admin(text), public.codigo_admin_info() to authenticated;
grant execute on function public.revisar_codigo_admin(text) to service_role;
