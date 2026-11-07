-- La operación para cobrar, lista y apagada (pedido del autor, 07-11-2026:
-- «instalar toda la operación para que al momento en que te diga "ya"…
-- lancemos la monetización»). El interruptor y los planes viven en
-- herramientas/monetizacion.py, que se detiene si sus ids no son estos.
--
-- Reglas:
-- - Nada de esto es público, salvo los planes ya publicados (con precio).
-- - La cartera del Vigía guarda solo RFC de personas morales (12 caracteres):
--   el RFC de una persona física es un dato personal y no se guarda.
-- - Ninguna cifra fiscal vive aquí (AGENTS.md §5 ter): solo clientes,
--   contrataciones, la cartera, los avisos y los pagos.
-- - Lo de un cliente que cancela se borra 12 meses después (aviso de privacidad).

-- Los planes. publicado = se ve en la página; no se publica sin precio.
create table public.planes (
  id         text primary key check (id ~ '^[a-z]+$'),
  nombre     text not null,
  periodo    text not null check (periodo in ('gratis', 'mes', 'año', 'encargo')),
  precio_mxn numeric(12, 2) check (precio_mxn is null or precio_mxn >= 0),
  publicado  boolean not null default false,
  check (not publicado or precio_mxn is not null or periodo = 'encargo')
);
insert into public.planes (id, nombre, periodo, precio_mxn) values
  ('gratis', 'Gratis', 'gratis', 0),
  ('profesional', 'Profesional', 'mes', null),
  ('despacho', 'Despacho', 'mes', null),
  ('encargo', 'Por encargo', 'encargo', null),
  ('institucion', 'Institución', 'año', null);
alter table public.planes enable row level security;
create policy "el público ve los planes publicados" on public.planes
  for select to anon, authenticated using (publicado);
create policy "administración ve y cambia los planes" on public.planes
  for all to authenticated using (public.es_admin()) with check (public.es_admin());
revoke all on public.planes from anon;
grant select on public.planes to anon;
grant select, insert, update, delete on public.planes to authenticated;

-- Los clientes.
create table public.clientes (
  id           bigint generated always as identity primary key,
  tipo         text not null check (tipo in ('moral', 'fisica')),
  nombre       text not null check (length(nombre) between 2 and 200),
  correo       text not null check (length(correo) <= 254 and correo ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'),
  rfc          text check (rfc is null or rfc ~ '^[A-ZÑ&]{3,4}[0-9]{6}[A-Z0-9]{3}$'),
  acepta_aviso boolean not null check (acepta_aviso),
  creado       timestamptz not null default now(),
  baja         timestamptz
);

-- Lo que contrata cada cliente (plan o encargo). No es public.contrataciones,
-- que es de las cuentas personales (fase 5 de la primera migración).
create table public.contrataciones (
  id         bigint generated always as identity primary key,
  cliente_id bigint not null references public.clientes (id) on delete cascade,
  plan_id    text not null references public.planes (id),
  estado     text not null default 'prueba' check (estado in ('prueba', 'activa', 'vencida', 'cancelada')),
  inicio     date not null default current_date,
  fin        date check (fin is null or fin >= inicio),
  nota       text check (nota is null or length(nota) <= 500)
);
create index contrataciones_cliente on public.contrataciones (cliente_id, estado);

-- La cartera del Vigía: solo personas morales.
create table public.vigia_cartera (
  id         bigint generated always as identity primary key,
  cliente_id bigint not null references public.clientes (id) on delete cascade,
  rfc        text not null check (rfc ~ '^[A-ZÑ&]{3}[0-9]{6}[A-Z0-9]{3}$'),
  alias      text check (alias is null or length(alias) <= 120),
  creado     timestamptz not null default now(),
  unique (cliente_id, rfc)
);

-- Los avisos que el Vigía manda (o mandará): qué cambió y su documento.
create table public.avisos (
  id         bigint generated always as identity primary key,
  cliente_id bigint not null references public.clientes (id) on delete cascade,
  rfc        text not null,
  tipo       text not null check (tipo in ('alta_69b', 'cambio_69b', 'baja_69b', 'razon_social', 'otro')),
  detalle    text not null check (length(detalle) <= 1000),
  documento  text check (documento is null or documento ~ '^https://'),
  creado     timestamptz not null default now(),
  enviado    timestamptz
);
create index avisos_pendientes on public.avisos (enviado, creado);

-- Los pagos de servicios y planes, con su CFDI. Las donaciones siguen en
-- public.donaciones; el informe anual por vía junta las dos.
create table public.pagos (
  id              bigint generated always as identity primary key,
  cliente_id      bigint references public.clientes (id) on delete set null,
  contratacion_id bigint references public.contrataciones (id) on delete set null,
  via             text not null check (via in ('servicio', 'plan')),
  monto_mxn       numeric(12, 2) not null check (monto_mxn > 0),
  fecha           date not null default current_date,
  medio           text check (medio is null or length(medio) <= 60),
  cfdi_uuid       text check (cfdi_uuid is null or cfdi_uuid ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
);

-- Solo la administración ve y cambia clientes, contrataciones, cartera, avisos y pagos.
do $$
declare t text;
begin
  foreach t in array array['clientes', 'contrataciones', 'vigia_cartera', 'avisos', 'pagos'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('create policy "solo administración" on public.%I for all to authenticated using (public.es_admin()) with check (public.es_admin())', t);
    execute format('revoke all on public.%I from anon', t);
    execute format('grant select, insert, update, delete on public.%I to authenticated', t);
  end loop;
end $$;

-- El Vigía (herramientas/vigia_69b.py deja su bandeja) anota un aviso para
-- cada cliente que tiene ese RFC en su cartera. Lo llama la llave de servicio.
create or replace function public.anotar_aviso(p_rfc text, p_tipo text, p_detalle text, p_documento text default null)
returns integer
language plpgsql security definer set search_path = public
as $$
declare n integer;
begin
  insert into public.avisos (cliente_id, rfc, tipo, detalle, documento)
    select v.cliente_id, v.rfc, p_tipo, p_detalle, p_documento
      from public.vigia_cartera v
      join public.contrataciones s on s.cliente_id = v.cliente_id and s.estado in ('prueba', 'activa')
     where v.rfc = upper(trim(p_rfc))
     group by v.cliente_id, v.rfc;
  get diagnostics n = row_count;
  return n;
end;
$$;
revoke all on function public.anotar_aviso(text, text, text, text) from public, anon, authenticated;
grant execute on function public.anotar_aviso(text, text, text, text) to service_role;

-- La cuenta pública de lo que entró por vía y por año (el informe anual).
create or replace function public.ingresos_por_via(p_anio integer)
returns table (via text, pagos bigint, total_mxn numeric)
language sql security definer set search_path = public
as $$
  select via, count(*), sum(monto) from (
    select via, monto_mxn as monto, fecha from public.pagos
    union all
    select 'donacion', monto, fecha from public.donaciones where moneda = 'MXN'
  ) x where extract(year from fecha) = p_anio group by via order by via;
$$;
grant execute on function public.ingresos_por_via(integer) to anon, authenticated;

-- Borrar lo de los clientes que se dieron de baja hace más de 12 meses.
create or replace function public.depurar_clientes()
returns integer
language plpgsql security definer set search_path = public
as $$
declare n integer;
begin
  delete from public.clientes where baja is not null and baja < now() - interval '12 months';
  get diagnostics n = row_count;
  return n;
end;
$$;
revoke all on function public.depurar_clientes() from public, anon, authenticated;
grant execute on function public.depurar_clientes() to service_role;
