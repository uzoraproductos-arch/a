-- Cuánto se guarda lo que la gente envía (decisión del autor, 30-10-2026:
-- 12 meses, igual que las solicitudes de código). El aviso de privacidad lo
-- dice (AVISO_CONSERVACION de herramientas/apartados.py) y esta migración lo
-- cumple: cada envío nuevo barre los que pasaron de un año. Una fe de
-- erratas publicada se queda, porque es pública, pero pierde el correo y la
-- huella de la conexión.
create or replace function public.envios_conservacion()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  delete from public.envios where creado < now() - interval '12 months' and estado <> 'publicado';
  update public.envios set correo = null, ip_huella = null
    where creado < now() - interval '12 months' and estado = 'publicado' and (correo is not null or ip_huella is not null);
  return null;
end;
$$;
revoke all on function public.envios_conservacion() from public, anon, authenticated;

create trigger envios_conservacion
  after insert on public.envios
  for each statement execute function public.envios_conservacion();
