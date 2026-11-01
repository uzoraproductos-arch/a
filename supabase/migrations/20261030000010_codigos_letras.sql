-- Códigos de acceso, cuarta entrega (pedido del autor, 30-10-2026: «sí va a
-- ser necesario meterle también letras… aquellos que únicamente sean números
-- es porque yo los otorgué… o viceversa, puras letras»).
--   * Los que salen al azar (generar_codigos, y con él el código de la
--     semana) llevan letras y números revueltos, siempre al menos uno de cada
--     uno, y sin los que se confunden (0, 1, O, I, L): 31 caracteres, 31^8 ≈
--     852 mil millones de combinaciones.
--   * Un código de puros números o de puras letras solo lo escribe a mano la
--     administración (crear_codigo): así se sabe que lo dio ella. A mano
--     también se vale revolverlos, con cualquier letra de la A a la Z.
--   * El código maestro también acepta letras.
--   * Los de puros números generados al azar antes de hoy se siguen canjeando.

create or replace function public.codigo_alfabeto() returns text
language sql immutable as $$ select '23456789ABCDEFGHJKMNPQRSTUVWXYZ'::text $$;

alter table public.codigos drop constraint if exists codigos_codigo_check;
alter table public.codigos add constraint codigos_codigo_check check (codigo ~ '^[0-9A-Z]{8}$');

-- Cada carácter sale de gen_random_bytes, descartando los bytes de 248 en
-- adelante (248 = 31 × 8) para que los 31 salgan parejos. Se descarta el que
-- quede de puros números o de puras letras: esos son de la administración.
create or replace function public.generar_codigos(
  p_cantidad integer, p_duracion interval, p_usos integer default 1,
  p_antes timestamptz default null, p_nota text default null)
returns setof public.codigos
language plpgsql security definer set search_path = public, extensions
as $$
declare
  v_alfa text := public.codigo_alfabeto();
  v_cod text;
  v_b integer;
  v_hechos integer := 0;
  v_intentos integer := 0;
  v_fila public.codigos;
begin
  if not public.es_admin() then
    raise exception 'solo la administración genera códigos';
  end if;
  if p_cantidad is null or p_cantidad < 1 or p_cantidad > 500 then
    raise exception 'la cantidad va de 1 a 500';
  end if;
  while v_hechos < p_cantidad loop
    v_intentos := v_intentos + 1;
    if v_intentos > p_cantidad * 20 then
      raise exception 'no se pudieron generar códigos únicos';
    end if;
    v_cod := '';
    while length(v_cod) < 8 loop
      v_b := get_byte(gen_random_bytes(1), 0);
      if v_b < 248 then
        v_cod := v_cod || substr(v_alfa, (v_b % 31) + 1, 1);
      end if;
    end loop;
    continue when v_cod !~ '[0-9]' or v_cod !~ '[A-Z]';
    insert into public.codigos (codigo, duracion, usos_max, canjear_antes, nota, creado_por)
      values (v_cod, p_duracion, coalesce(p_usos, 1), p_antes, nullif(trim(p_nota), ''), auth.uid())
      on conflict (codigo) do nothing
      returning * into v_fila;
    if found then
      v_hechos := v_hechos + 1;
      return next v_fila;
    end if;
  end loop;
end;
$$;

-- El código propio: 8 caracteres, números y letras de la A a la Z, como la
-- administración quiera (puros números, puras letras o revueltos).
create or replace function public.crear_codigo(
  p_codigo text, p_duracion interval, p_usos integer default 1,
  p_antes timestamptz default null, p_nota text default null)
returns public.codigos
language plpgsql security definer set search_path = public
as $$
declare
  v_cod text := upper(regexp_replace(coalesce(p_codigo, ''), '[\s-]', '', 'g'));
  v_fila public.codigos;
begin
  if not public.es_admin() then
    raise exception 'solo la administración crea códigos';
  end if;
  if v_cod !~ '^[0-9A-Z]{8}$' then
    raise exception 'el código lleva 8 caracteres: números y letras de la A a la Z, sin acentos ni Ñ';
  end if;
  insert into public.codigos (codigo, duracion, usos_max, canjear_antes, nota, creado_por)
    values (v_cod, p_duracion, coalesce(p_usos, 1), p_antes, nullif(trim(p_nota), ''), auth.uid())
    on conflict (codigo) do nothing
    returning * into v_fila;
  if not found then
    raise exception 'ese código ya existe: escribe otro';
  end if;
  return v_fila;
end;
$$;

-- El canje: cualquier código de 8 números y letras.
create or replace function public.canjear_codigo(p_codigo text, p_pase uuid default null)
returns jsonb
language plpgsql security definer set search_path = public
as $$
declare
  v_cod text := upper(regexp_replace(coalesce(p_codigo, ''), '[^0-9A-Za-z]', '', 'g'));
  v_pase uuid := p_pase;
  k public.codigos;
begin
  if v_cod !~ '^[0-9A-Z]{8}$' then
    return jsonb_build_object('ok', false, 'motivo', 'formato');
  end if;
  select * into k from public.codigos where codigo = v_cod for update;
  if not found or k.revocado then
    return jsonb_build_object('ok', false, 'motivo', 'no_valido');
  end if;
  if k.canjear_antes is not null and now() > k.canjear_antes then
    return jsonb_build_object('ok', false, 'motivo', 'vencido');
  end if;
  if v_pase is not null and not exists (select 1 from public.pases where id = v_pase) then
    v_pase := null;
  end if;
  if v_pase is not null and exists (select 1 from public.canjes where codigo_id = k.id and pase_id = v_pase) then
    return jsonb_build_object('ok', false, 'motivo', 'ya_canjeado', 'pase', v_pase, 'hasta', public.pase_hasta(v_pase));
  end if;
  if k.usos >= k.usos_max then
    return jsonb_build_object('ok', false, 'motivo', 'agotado');
  end if;
  if v_pase is null then
    insert into public.pases default values returning id into v_pase;
  end if;
  insert into public.canjes (codigo_id, pase_id) values (k.id, v_pase);
  update public.codigos set usos = usos + 1 where id = k.id;
  return jsonb_build_object('ok', true, 'pase', v_pase, 'hasta', public.pase_hasta(v_pase), 'duracion', k.duracion::text);
end;
$$;

-- El código maestro, con letras también.
create or replace function public.fijar_codigo_admin(p_codigo text)
returns void
language plpgsql security definer set search_path = public, extensions
as $$
declare
  v_cod text := upper(regexp_replace(coalesce(p_codigo, ''), '[\s-]', '', 'g'));
begin
  if not public.es_admin() then
    raise exception 'solo la administración pone su código';
  end if;
  if v_cod !~ '^[0-9A-Z]{8}$' then
    raise exception 'el código lleva 8 caracteres: números y letras de la A a la Z';
  end if;
  if v_cod ~ '^(.)\1{7}$' or v_cod in ('12345678', '87654321', '01234567', 'ABCDEFGH', 'QWERTYUI') then
    raise exception 'ese código es demasiado fácil de adivinar: escribe otro';
  end if;
  if exists (select 1 from public.codigos where codigo = v_cod) then
    raise exception 'ese código ya es un código de acceso común: escribe otro';
  end if;
  insert into public.admin_codigo (id, huella, user_id, cambiado)
    values (1, crypt(v_cod, gen_salt('bf', 10)), auth.uid(), now())
    on conflict (id) do update set huella = excluded.huella, user_id = excluded.user_id, cambiado = excluded.cambiado;
end;
$$;

create or replace function public.revisar_codigo_admin(p_codigo text)
returns uuid
language plpgsql security definer set search_path = public, extensions
as $$
declare
  v_cod text := upper(regexp_replace(coalesce(p_codigo, ''), '[^0-9A-Za-z]', '', 'g'));
  a public.admin_codigo;
begin
  if v_cod !~ '^[0-9A-Z]{8}$' then
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

-- create or replace conserva los permisos; se repiten por claridad.
revoke all on function public.canjear_codigo(text, uuid), public.revisar_codigo_admin(text) from public, anon, authenticated;
grant execute on function public.canjear_codigo(text, uuid), public.revisar_codigo_admin(text) to service_role;
revoke all on function public.generar_codigos(integer, interval, integer, timestamptz, text), public.crear_codigo(text, interval, integer, timestamptz, text),
  public.fijar_codigo_admin(text) from public, anon;
grant execute on function public.generar_codigos(integer, interval, integer, timestamptz, text), public.crear_codigo(text, interval, integer, timestamptz, text),
  public.fijar_codigo_admin(text) to authenticated;
