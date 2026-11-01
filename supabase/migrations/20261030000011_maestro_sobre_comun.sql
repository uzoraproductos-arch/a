-- El código maestro puede ser uno que ya exista como código común (pedido del
-- autor, 30-10-2026: «otra vez ingresé con el código y no me salió la pestaña
-- de administración»). Si el autor ya había dado de alta ese número como
-- código propio, la entrada lo canjeaba como código común (sin reconocerlo como
-- administración) y fijar_codigo_admin lo rechazaba. Ahora el maestro se queda
-- con ese número: el código común se archiva con su nota, y como la entrada
-- revisa primero el maestro, ya nadie lo vuelve a canjear como común. Quien ya
-- lo hubiera canjeado conserva su tiempo (no se revoca).
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
  update public.codigos set archivado = true,
    nota = left(coalesce(nullif(nota, '') || ' · ', '') || 'ahora es el código maestro', 120)
    where codigo = v_cod;
  insert into public.admin_codigo (id, huella, user_id, cambiado)
    values (1, crypt(v_cod, gen_salt('bf', 10)), auth.uid(), now())
    on conflict (id) do update set huella = excluded.huella, user_id = excluded.user_id, cambiado = excluded.cambiado;
end;
$$;
revoke all on function public.fijar_codigo_admin(text) from public, anon;
grant execute on function public.fijar_codigo_admin(text) to authenticated;
