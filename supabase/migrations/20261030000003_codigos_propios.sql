-- Códigos de acceso, segunda entrega (pedido del autor, 30-10-2026):
--   1. Arreglo: en Supabase, pgcrypto (gen_random_bytes) vive en el esquema
--      «extensions», y generar_codigos solo buscaba en public: el panel decía
--      «function gen_random_bytes(integer) does not exist». Ahora busca en los dos.
--   2. Códigos propios: «unos que sí se generaran en automático y otros que yo
--      pudiera designar». crear_codigo da de alta uno escrito por la
--      administración, con las mismas reglas que los de al azar.

alter function public.generar_codigos(integer, interval, integer, timestamptz, text)
  set search_path = public, extensions;

-- Un código escrito a mano. Se acepta en minúsculas, con guion o espacios
-- (igual que al canjearlo), y se guarda en mayúsculas y sin guion.
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
  if v_cod !~ '^[23456789ABCDEFGHJKMNPQRSTUVWXYZ]{8}$' then
    raise exception 'el código lleva 8 caracteres: números del 2 al 9 y letras sin I, L ni O';
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

revoke all on function public.crear_codigo(text, interval, integer, timestamptz, text) from public, anon;
grant execute on function public.crear_codigo(text, interval, integer, timestamptz, text) to authenticated;
