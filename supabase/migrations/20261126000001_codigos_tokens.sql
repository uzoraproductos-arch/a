-- Ronda 27A (26-11-2026, decisión del autor): códigos con tokens y temporalidad. La billetera de tokens vive en el
-- navegador (assets/auditor/js/tokens.js, localStorage av-tokens); un código puede, además de abrir los Servicios por su
-- duración como siempre, sumar tokens a esa billetera o dar tokens ilimitados durante su vigencia.
--
--   * tokens: cuántos suma al canjearse (de 1 a 100,000), o nada (null: el código solo abre, como antes).
--   * tokens_ilimitado: durante la vigencia del pase (pase_hasta) no gasta tokens. Va sin cantidad.
--   * El canje devuelve 'tokens', 'ilimitado' y 'codigo_id' (para que el navegador no sume dos veces el mismo código).
--     Un pase solo canjea un código una vez (canjes es único por código y pase), así que los tokens se dan una sola vez
--     por navegador; quien canjea el mismo código en otro navegador gasta otro de sus usos (usos_max).
--   * La billetera no es una cuenta: el saldo no está en la base. En la Ronda 27B se sincroniza con una cuenta por
--     correo y aquí nace su tabla. Nada de esto guarda datos personales.
--   * La Bitácora anota los tokens al crear y al editar.
--
-- La función «codigo» (supabase/functions/codigo) no cambia: devuelve lo que da canjear_codigo.

alter table public.codigos add column if not exists tokens integer check (tokens is null or tokens between 1 and 100000);
alter table public.codigos add column if not exists tokens_ilimitado boolean not null default false;
alter table public.codigos drop constraint if exists codigos_tokens_uno_u_otro;
alter table public.codigos add constraint codigos_tokens_uno_u_otro check (not (tokens_ilimitado and tokens is not null));

-- Generar y crear: los mismos de la Ronda 10 de códigos (20261030000010), con los tokens al final.
drop function if exists public.generar_codigos(integer, interval, integer, timestamptz, text);
create function public.generar_codigos(
  p_cantidad integer, p_duracion interval, p_usos integer default 1,
  p_antes timestamptz default null, p_nota text default null,
  p_tokens integer default null, p_ilimitado boolean default false)
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
  if coalesce(p_ilimitado, false) and p_tokens is not null then
    raise exception 'un código da tokens o tokens ilimitados, no los dos';
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
    insert into public.codigos (codigo, duracion, usos_max, canjear_antes, nota, creado_por, tokens, tokens_ilimitado)
      values (v_cod, p_duracion, coalesce(p_usos, 1), p_antes, nullif(trim(p_nota), ''), auth.uid(), p_tokens, coalesce(p_ilimitado, false))
      on conflict (codigo) do nothing
      returning * into v_fila;
    if found then
      v_hechos := v_hechos + 1;
      return next v_fila;
    end if;
  end loop;
end;
$$;

drop function if exists public.crear_codigo(text, interval, integer, timestamptz, text);
create function public.crear_codigo(
  p_codigo text, p_duracion interval, p_usos integer default 1,
  p_antes timestamptz default null, p_nota text default null,
  p_tokens integer default null, p_ilimitado boolean default false)
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
  if coalesce(p_ilimitado, false) and p_tokens is not null then
    raise exception 'un código da tokens o tokens ilimitados, no los dos';
  end if;
  insert into public.codigos (codigo, duracion, usos_max, canjear_antes, nota, creado_por, tokens, tokens_ilimitado)
    values (v_cod, p_duracion, coalesce(p_usos, 1), p_antes, nullif(trim(p_nota), ''), auth.uid(), p_tokens, coalesce(p_ilimitado, false))
    on conflict (codigo) do nothing
    returning * into v_fila;
  if not found then
    raise exception 'ese código ya existe: escribe otro';
  end if;
  return v_fila;
end;
$$;

-- Editar: p_tokens -1 (o sin mandarlo) lo deja como está; 0 le quita los tokens; de 1 en adelante, esa cantidad.
-- p_ilimitado null lo deja como está. Lo que ya se canjeó no cambia: los tokens se suman al canjear.
drop function if exists public.editar_codigo(bigint, text, integer, timestamptz, interval);
create function public.editar_codigo(p_id bigint, p_nota text, p_usos_max integer, p_antes timestamptz, p_duracion interval,
  p_tokens integer default -1, p_ilimitado boolean default null)
returns void
language plpgsql security definer set search_path = public
as $$
declare
  k public.codigos;
  v_tokens integer;
  v_ilim boolean;
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
  v_tokens := case when p_tokens is null or p_tokens < 0 then k.tokens when p_tokens = 0 then null else p_tokens end;
  v_ilim := coalesce(p_ilimitado, k.tokens_ilimitado);
  if v_ilim and v_tokens is not null then
    raise exception 'un código da tokens o tokens ilimitados, no los dos';
  end if;
  update public.codigos set
    nota = nullif(trim(p_nota), ''),
    usos_max = coalesce(p_usos_max, usos_max),
    canjear_antes = p_antes,
    duracion = coalesce(p_duracion, duracion),
    tokens = v_tokens,
    tokens_ilimitado = v_ilim
  where id = p_id;
end;
$$;

-- La lista suma sus tokens (cambia de forma: se rehace).
drop function if exists public.codigos_lista();
create function public.codigos_lista()
returns table (id bigint, codigo text, duracion text, usos integer, usos_max integer, canjear_antes timestamptz,
               nota text, revocado boolean, creado timestamptz, hasta timestamptz, estado text,
               semanal boolean, archivado boolean, tokens integer, tokens_ilimitado boolean)
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
         k.semanal, k.archivado, k.tokens, k.tokens_ilimitado
  from public.codigos k
  left join lateral (select max(public.pase_hasta(c.pase_id)) as hasta from public.canjes c where c.codigo_id = k.id) h on true
  order by k.creado desc, k.id desc;
end;
$$;

-- El canje: el mismo de 20261030000010, y al canjear dice los tokens del código. Un código ya canjeado en este pase no
-- los vuelve a dar.
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
    return jsonb_build_object('ok', false, 'motivo', 'ya_canjeado', 'pase', v_pase, 'hasta', public.pase_hasta(v_pase), 'codigo_id', k.id);
  end if;
  if k.usos >= k.usos_max then
    return jsonb_build_object('ok', false, 'motivo', 'agotado');
  end if;
  if v_pase is null then
    insert into public.pases default values returning id into v_pase;
  end if;
  insert into public.canjes (codigo_id, pase_id) values (k.id, v_pase);
  update public.codigos set usos = usos + 1 where id = k.id;
  return jsonb_build_object('ok', true, 'pase', v_pase, 'hasta', public.pase_hasta(v_pase), 'duracion', k.duracion::text,
                            'codigo_id', k.id, 'tokens', k.tokens, 'ilimitado', k.tokens_ilimitado);
end;
$$;

-- La Bitácora: la misma de 20261118000001, con los tokens.
create or replace function public.codigos_a_bitacora() returns trigger
language plpgsql security definer set search_path = public
as $$
declare
  d jsonb := '{}'::jsonb;
begin
  if tg_op = 'INSERT' then
    perform public.anota_bitacora(case when new.semanal then 'código de la semana' else 'creó' end, new.codigo,
      jsonb_strip_nulls(jsonb_build_object('duracion', new.duracion::text, 'personas', new.usos_max, 'canjear_antes', new.canjear_antes, 'nota', new.nota,
        'tokens', case when new.tokens_ilimitado then 'ilimitados' else new.tokens::text end)));
    return new;
  end if;
  if tg_op = 'DELETE' then
    perform public.anota_bitacora('eliminó', old.codigo, jsonb_build_object('lo_habian_usado', old.usos));
    return old;
  end if;
  if new.revocado is distinct from old.revocado then
    perform public.anota_bitacora(case when new.revocado then 'revocó' else 'devolvió' end, new.codigo, '{}'::jsonb);
  end if;
  if new.archivado is distinct from old.archivado then
    perform public.anota_bitacora(case when new.archivado then 'archivó' else 'desarchivó' end, new.codigo, '{}'::jsonb);
  end if;
  if new.duracion is distinct from old.duracion then d := d || jsonb_build_object('duracion', jsonb_build_array(old.duracion::text, new.duracion::text)); end if;
  if new.usos_max is distinct from old.usos_max then d := d || jsonb_build_object('personas', jsonb_build_array(old.usos_max, new.usos_max)); end if;
  if new.canjear_antes is distinct from old.canjear_antes then d := d || jsonb_build_object('canjear_antes', jsonb_build_array(old.canjear_antes, new.canjear_antes)); end if;
  if new.nota is distinct from old.nota then d := d || jsonb_build_object('nota', jsonb_build_array(old.nota, new.nota)); end if;
  if new.tokens is distinct from old.tokens or new.tokens_ilimitado is distinct from old.tokens_ilimitado then
    d := d || jsonb_build_object('tokens', jsonb_build_array(
      case when old.tokens_ilimitado then 'ilimitados' else old.tokens::text end,
      case when new.tokens_ilimitado then 'ilimitados' else new.tokens::text end));
  end if;
  -- renovar_codigo deja su propio renglón, con todo lo que cambió.
  if d <> '{}'::jsonb and current_setting('av.renovando', true) is distinct from 'si' then
    perform public.anota_bitacora('editó', new.codigo, d);
  end if;
  return new;
end;
$$;

revoke all on function public.canjear_codigo(text, uuid) from public, anon, authenticated;
grant execute on function public.canjear_codigo(text, uuid) to service_role;
revoke all on function public.generar_codigos(integer, interval, integer, timestamptz, text, integer, boolean),
  public.crear_codigo(text, interval, integer, timestamptz, text, integer, boolean),
  public.editar_codigo(bigint, text, integer, timestamptz, interval, integer, boolean), public.codigos_lista() from public, anon;
grant execute on function public.generar_codigos(integer, interval, integer, timestamptz, text, integer, boolean),
  public.crear_codigo(text, interval, integer, timestamptz, text, integer, boolean),
  public.editar_codigo(bigint, text, integer, timestamptz, interval, integer, boolean), public.codigos_lista() to authenticated;
