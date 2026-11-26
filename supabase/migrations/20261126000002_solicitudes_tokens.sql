-- Ronda 28B (26-11-2026, pedido del autor): al atender una solicitud se elige también cuántos tokens da su código.
--
--   * atender_solicitud suma p_tokens y p_ilimitado, con las mismas reglas de generar_codigos (20261126000001): una
--     cantidad de 1 a 100,000, o ilimitados durante la vigencia, nunca los dos. Sin ellos, el código solo abre, como antes.
--   * Devuelve además 'tokens' e 'ilimitado', para que el correo que arma el panel lo diga.
--   * La Bitácora ya anota los tokens al crear el código (codigos_a_bitacora): aquí no hace falta nada más.
--   * renovar_codigo no cambia: un código renovado conserva los tokens que tenía (se cambian con editar_codigo).

drop function if exists public.atender_solicitud(bigint, interval);
create function public.atender_solicitud(p_id bigint, p_duracion interval,
  p_tokens integer default null, p_ilimitado boolean default false)
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
  select * into k from public.generar_codigos(1, p_duracion, 1, null, 'Solicitud SC-' || lpad(p_id::text, 5, '0'), p_tokens, p_ilimitado);
  update public.solicitudes_codigo set estado = 'enviada', codigo_id = k.id, atendida = now() where id = p_id;
  return jsonb_build_object('codigo', k.codigo, 'correo', s.correo, 'nombre', s.nombre, 'duracion', k.duracion::text,
                            'tokens', k.tokens, 'ilimitado', k.tokens_ilimitado);
end;
$$;

revoke all on function public.atender_solicitud(bigint, interval, integer, boolean) from public, anon;
grant execute on function public.atender_solicitud(bigint, interval, integer, boolean) to authenticated;
