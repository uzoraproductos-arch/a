-- Códigos de acceso (pedido del autor, 29-10-2026): «que funcionara un poquito
-- como lo hace este Nintendo Switch… cuatro casillas de un lado, espacio,
-- cuatro casillas de otro lado, y yo estar administrando tanto el número de
-- código como el tiempo de apertura… de un día, tres días, cinco días, una
-- semana, un mes, un año». Mientras la plataforma se perfecciona, todo es
-- gratis: el código solo abre la puerta de la versión de prueba.
--
-- Cómo funciona:
--   * La administración genera códigos de 8 caracteres (se muestran XXXX-XXXX)
--     con su duración, sus usos y, si quiere, una fecha límite para canjearlos.
--   * La persona canjea el código en canjea-tu-codigo.html. No hace falta
--     cuenta ni correo: el canje crea un «pase» (un número al azar que se
--     queda en su navegador). Sin datos personales.
--   * El tiempo corre desde el canje, no desde que se generó el código. Si el
--     mismo pase canjea otro código, su tiempo se suma al que le quedaba.
--   * Revocar un código le quita su tiempo a quien lo canjeó.
--   * El público no lee ninguna de estas tablas: canjea por la función
--     «codigo» (límite de intentos por IP) y la administración usa las
--     funciones de aquí, que revisan es_admin().

-- Sin 0/O ni 1/I/L, que se confunden al copiarlos: 31 caracteres, 31^8 ≈ 8.5e11.
create or replace function public.codigo_alfabeto() returns text
language sql immutable as $$ select '23456789ABCDEFGHJKMNPQRSTUVWXYZ'::text $$;

create table public.codigos (
  id            bigint generated always as identity primary key,
  codigo        text not null unique check (codigo ~ '^[23456789ABCDEFGHJKMNPQRSTUVWXYZ]{8}$'),
  -- De una hora a cinco años, o ilimitado: 100 años exactos (así lo lee el panel).
  duracion      interval not null check (duracion >= interval '1 hour' and (duracion <= interval '5 years' or duracion = interval '100 years')),
  usos_max      integer not null default 1 check (usos_max between 1 and 10000),
  usos          integer not null default 0 check (usos >= 0 and usos <= usos_max),
  canjear_antes timestamptz,
  nota          text check (nota is null or length(nota) <= 120),
  revocado      boolean not null default false,
  creado        timestamptz not null default now(),
  creado_por    uuid references auth.users (id) on delete set null
);
alter table public.codigos enable row level security;
create policy "administración ve los códigos" on public.codigos
  for select to authenticated using (public.es_admin());

-- El pase: lo que guarda el navegador de quien canjeó. Es solo un número al azar.
create table public.pases (
  id     uuid primary key default gen_random_uuid(),
  creado timestamptz not null default now()
);
alter table public.pases enable row level security;
create policy "administración ve los pases" on public.pases
  for select to authenticated using (public.es_admin());

create table public.canjes (
  id        bigint generated always as identity primary key,
  codigo_id bigint not null references public.codigos (id) on delete cascade,
  pase_id   uuid not null references public.pases (id) on delete cascade,
  en        timestamptz not null default now(),
  unique (codigo_id, pase_id)
);
alter table public.canjes enable row level security;
create policy "administración ve los canjes" on public.canjes
  for select to authenticated using (public.es_admin());

revoke all on public.codigos, public.pases, public.canjes from anon;
revoke insert, update, delete on public.codigos, public.pases, public.canjes from authenticated;
grant select on public.codigos, public.pases, public.canjes to authenticated;

-- Hasta cuándo abre un pase: cada canje de un código no revocado suma su
-- duración, a partir del canje o de donde iba el tiempo, lo que sea después.
create or replace function public.pase_hasta(p_pase uuid)
returns timestamptz
language plpgsql stable security definer set search_path = public
as $$
declare
  v_hasta timestamptz;
  r record;
begin
  for r in
    select c.en, k.duracion from public.canjes c join public.codigos k on k.id = c.codigo_id
    where c.pase_id = p_pase and not k.revocado order by c.en, c.id
  loop
    v_hasta := greatest(coalesce(v_hasta, r.en), r.en) + r.duracion;
  end loop;
  return v_hasta;
end;
$$;

-- El canje. Lo llama la función «codigo» con la llave de servicio, después de
-- revisar el límite de intentos. Devuelve {ok, pase, hasta} o {ok:false, motivo}.
create or replace function public.canjear_codigo(p_codigo text, p_pase uuid default null)
returns jsonb
language plpgsql security definer set search_path = public
as $$
declare
  v_cod text := upper(regexp_replace(coalesce(p_codigo, ''), '[^0-9A-Za-z]', '', 'g'));
  v_pase uuid := p_pase;
  k public.codigos;
begin
  if v_cod !~ '^[23456789ABCDEFGHJKMNPQRSTUVWXYZ]{8}$' then
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

-- Genera códigos nuevos (solo la administración). Cada carácter sale de
-- gen_random_bytes, descartando los bytes que harían más probable una letra.
create or replace function public.generar_codigos(
  p_cantidad integer, p_duracion interval, p_usos integer default 1,
  p_antes timestamptz default null, p_nota text default null)
returns setof public.codigos
language plpgsql security definer set search_path = public
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
      if v_b < 248 then  -- 248 = 31 × 8: así las 31 letras salen parejas
        v_cod := v_cod || substr(v_alfa, (v_b % 31) + 1, 1);
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

-- Revocar (o devolver) un código: solo la administración.
create or replace function public.revocar_codigo(p_id bigint, p_revocado boolean default true)
returns void
language plpgsql security definer set search_path = public
as $$
begin
  if not public.es_admin() then
    raise exception 'solo la administración revoca códigos';
  end if;
  update public.codigos set revocado = coalesce(p_revocado, true) where id = p_id;
end;
$$;

-- La lista del panel: cada código con su estado y hasta cuándo abre.
create or replace function public.codigos_lista()
returns table (id bigint, codigo text, duracion text, usos integer, usos_max integer, canjear_antes timestamptz,
               nota text, revocado boolean, creado timestamptz, hasta timestamptz, estado text)
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
         end
  from public.codigos k
  left join lateral (select max(public.pase_hasta(c.pase_id)) as hasta from public.canjes c where c.codigo_id = k.id) h on true
  order by k.creado desc, k.id desc;
end;
$$;

revoke all on function public.pase_hasta(uuid), public.canjear_codigo(text, uuid) from public, anon, authenticated;
revoke all on function public.generar_codigos(integer, interval, integer, timestamptz, text),
  public.revocar_codigo(bigint, boolean), public.codigos_lista() from public, anon;
grant execute on function public.generar_codigos(integer, interval, integer, timestamptz, text),
  public.revocar_codigo(bigint, boolean), public.codigos_lista() to authenticated;
grant execute on function public.pase_hasta(uuid), public.canjear_codigo(text, uuid) to service_role;
