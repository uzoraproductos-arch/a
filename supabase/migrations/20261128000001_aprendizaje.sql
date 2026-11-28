-- Ronda 41 (28-11-2026, Ola 4, entrega A): el buzón de aprendizaje verificado.
--
-- Bajo cada respuesta del Auditor, quien quiere manda su duda para que la administración la investigue. Es voluntario
-- y la pregunta sale del navegador ya anonimizada (FiscalCalc.anonimiza de assets/auditor/js/fiscal-calculo.js): sin
-- RFC, CURP, correos ni teléfonos, y con cada monto cambiado por [MONTO]. Aquí no se guarda nombre, correo ni la huella
-- de la conexión.
--
--   * preguntas_aprendizaje: la pregunta anonimizada, el modo del chat, si quedó sin respuesta, cuántas veces llegó,
--     su estado (nueva, en_revision, integrada, descartada) y la nota de la administración.
--   * Un candado en la tabla rechaza lo que traiga una arroba, un signo de pesos con cifra o cinco dígitos seguidos:
--     si el navegador no anonimizó, la base no lo guarda.
--   * anotar_aprendizaje (solo la llave de servicio, desde la función «aprendizaje»): si la misma pregunta ya está
--     como nueva, suma una vez; si no, la guarda.
--   * aprendizaje_lista y aprendizaje_marca: solo la administración con dos factores (es_admin()). Cada cambio de
--     estado o de nota queda en la Bitácora.
--   * El público nunca lee, cambia ni borra: sin políticas para anon, y sin permisos de escritura directa para nadie.
--   * Conservación: lo descartado se borra a los 12 meses de su última actualización.

create table public.preguntas_aprendizaje (
  id               bigint generated always as identity primary key,
  pregunta_anonima text not null check (char_length(pregunta_anonima) between 4 and 400),
  modo             text check (modo is null or modo in ('inspector', 'periodista', 'ciudadano', 'ambientalista')),
  sin_respuesta    boolean not null default false,
  veces            integer not null default 1 check (veces >= 1),
  estado           text not null default 'nueva' check (estado in ('nueva', 'en_revision', 'integrada', 'descartada')),
  nota_admin       text check (nota_admin is null or char_length(nota_admin) <= 600),
  version          text check (version is null or version ~ '^\d{8}[a-z]{0,2}$'),
  creada_en        timestamptz not null default now(),
  actualizada_en   timestamptz not null default now(),
  constraint aprendizaje_anonima check (pregunta_anonima !~ '@' and pregunta_anonima !~ '\d{5,}' and pregunta_anonima !~ '\$\s?\d')
);
create index preguntas_aprendizaje_estado on public.preguntas_aprendizaje (estado, veces desc, actualizada_en desc);
create unique index preguntas_aprendizaje_nueva on public.preguntas_aprendizaje (lower(pregunta_anonima)) where estado = 'nueva';

alter table public.preguntas_aprendizaje enable row level security;
create policy "administración lee el aprendizaje" on public.preguntas_aprendizaje
  for select to authenticated using (public.es_admin());
create policy "administración actualiza el aprendizaje" on public.preguntas_aprendizaje
  for update to authenticated using (public.es_admin()) with check (public.es_admin());
revoke all on public.preguntas_aprendizaje from anon, authenticated;
grant select on public.preguntas_aprendizaje to authenticated;
grant update (estado, nota_admin) on public.preguntas_aprendizaje to authenticated;

-- La función «aprendizaje» guarda con esto: devuelve true si la pregunta es nueva y false si ya estaba y solo sumó.
create or replace function public.anotar_aprendizaje(p_pregunta text, p_modo text default null, p_sin boolean default false, p_version text default null)
returns boolean
language plpgsql security definer set search_path = public
as $$
declare
  v_p text := btrim(regexp_replace(coalesce(p_pregunta, ''), '\s+', ' ', 'g'));
  v_id bigint;
begin
  update public.preguntas_aprendizaje
     set veces = veces + 1, sin_respuesta = sin_respuesta or coalesce(p_sin, false), actualizada_en = now()
   where estado = 'nueva' and lower(pregunta_anonima) = lower(v_p)
  returning id into v_id;
  if v_id is not null then
    return false;
  end if;
  insert into public.preguntas_aprendizaje (pregunta_anonima, modo, sin_respuesta, version)
  values (v_p, p_modo, coalesce(p_sin, false), p_version);
  return true;
end;
$$;
revoke all on function public.anotar_aprendizaje(text, text, boolean, text) from public, anon, authenticated;
grant execute on function public.anotar_aprendizaje(text, text, boolean, text) to service_role;

-- La hoja «Aprendizaje» del panel.
create or replace function public.aprendizaje_lista()
returns setof public.preguntas_aprendizaje
language plpgsql stable security definer set search_path = public
as $$
begin
  if not public.es_admin() then
    raise exception 'solo la administración ve el buzón de aprendizaje';
  end if;
  return query select * from public.preguntas_aprendizaje order by (estado = 'nueva') desc, veces desc, actualizada_en desc limit 2000;
end;
$$;

create or replace function public.aprendizaje_marca(p_id bigint, p_estado text, p_nota text default null)
returns public.preguntas_aprendizaje
language plpgsql security definer set search_path = public
as $$
declare
  f public.preguntas_aprendizaje;
begin
  if not public.es_admin() then
    raise exception 'solo la administración cambia el buzón de aprendizaje';
  end if;
  update public.preguntas_aprendizaje
     set estado = p_estado, nota_admin = nullif(btrim(coalesce(p_nota, '')), ''), actualizada_en = now()
   where id = p_id
  returning * into f;
  if not found then
    raise exception 'no existe esa pregunta';
  end if;
  return f;
end;
$$;
revoke all on function public.aprendizaje_lista(), public.aprendizaje_marca(bigint, text, text) from public, anon;
grant execute on function public.aprendizaje_lista(), public.aprendizaje_marca(bigint, text, text) to authenticated;

-- El control interno: cada cambio de estado o de nota queda anotado solo.
create or replace function public.aprendizaje_a_bitacora() returns trigger
language plpgsql security definer set search_path = public
as $$
begin
  if new.estado is distinct from old.estado or new.nota_admin is distinct from old.nota_admin then
    perform public.anota_bitacora('aprendizaje: ' || new.estado, 'AP-' || lpad(new.id::text, 5, '0'),
      jsonb_strip_nulls(jsonb_build_object('antes', case when new.estado is distinct from old.estado then old.estado end,
                                           'con_nota', case when new.nota_admin is not null then true end)));
  end if;
  return new;
end;
$$;
revoke all on function public.aprendizaje_a_bitacora() from public, anon, authenticated;
create trigger aprendizaje_bitacora after update on public.preguntas_aprendizaje
  for each row execute function public.aprendizaje_a_bitacora();

-- Conservación: lo descartado no se queda para siempre.
create or replace function public.aprendizaje_conservacion() returns trigger
language plpgsql security definer set search_path = public
as $$
begin
  delete from public.preguntas_aprendizaje where estado = 'descartada' and actualizada_en < now() - interval '12 months';
  return null;
end;
$$;
revoke all on function public.aprendizaje_conservacion() from public, anon, authenticated;
create trigger aprendizaje_conservacion after insert on public.preguntas_aprendizaje
  for each statement execute function public.aprendizaje_conservacion();
