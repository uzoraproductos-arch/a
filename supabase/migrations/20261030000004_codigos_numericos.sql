-- Códigos de acceso, tercera entrega (pedido del autor, 30-10-2026): «los
-- códigos creo que van a ser únicamente con números». Desde aquí los códigos
-- son de 8 números, del 0 al 9 (sin letras ya no hay O ni I que confundir):
-- 10^8 = cien millones de combinaciones, con el límite de 10 intentos cada
-- 10 minutos por IP de la función «codigo». Los de letras que ya existieran
-- se siguen canjeando.

create or replace function public.codigo_alfabeto() returns text
language sql immutable as $$ select '0123456789'::text $$;

alter table public.codigos drop constraint if exists codigos_codigo_check;
alter table public.codigos add constraint codigos_codigo_check
  check (codigo ~ '^([0-9]{8}|[23456789ABCDEFGHJKMNPQRSTUVWXYZ]{8})$');

-- Cada número sale de gen_random_bytes, descartando los bytes de 250 en
-- adelante (250 = 10 × 25) para que los diez dígitos salgan parejos.
create or replace function public.generar_codigos(
  p_cantidad integer, p_duracion interval, p_usos integer default 1,
  p_antes timestamptz default null, p_nota text default null)
returns setof public.codigos
language plpgsql security definer set search_path = public, extensions
as $$
declare
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
      if v_b < 250 then
        v_cod := v_cod || (v_b % 10)::text;
      end if;
    end loop;
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

-- El código propio: 8 números. Se acepta con guion o espacios.
create or replace function public.crear_codigo(
  p_codigo text, p_duracion interval, p_usos integer default 1,
  p_antes timestamptz default null, p_nota text default null)
returns public.codigos
language plpgsql security definer set search_path = public
as $$
declare
  v_cod text := upper(regexp_replace(coalesce(p_codigo, ''), '[^0-9A-Za-z]', '', 'g'));
  v_fila public.codigos;
begin
  if not public.es_admin() then
    raise exception 'solo la administración crea códigos';
  end if;
  if v_cod !~ '^[0-9]{8}$' then
    raise exception 'el código lleva 8 números, del 0 al 9';
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

-- El canje acepta los de números y, para no dejar a nadie fuera, los de letras.
create or replace function public.canjear_codigo(p_codigo text, p_pase uuid default null)
returns jsonb
language plpgsql security definer set search_path = public
as $$
declare
  v_cod text := upper(regexp_replace(coalesce(p_codigo, ''), '[^0-9A-Za-z]', '', 'g'));
  v_pase uuid := p_pase;
  k public.codigos;
begin
  if v_cod !~ '^([0-9]{8}|[23456789ABCDEFGHJKMNPQRSTUVWXYZ]{8})$' then
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
