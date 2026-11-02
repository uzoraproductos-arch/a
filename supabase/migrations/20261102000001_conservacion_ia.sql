-- Cuánto se guardan las preguntas a la IA (02-11-2026, al encenderla). Igual
-- que los envíos: 12 meses. El aviso de privacidad lo dice y esta migración
-- lo cumple: cada consulta nueva barre las que pasaron de un año. Las
-- búsquedas en internet (busquedas_web) no guardan nada de quien pregunta.
create or replace function public.consultas_ia_conservacion()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  delete from public.consultas_ia where creado < now() - interval '12 months';
  return null;
end;
$$;
revoke all on function public.consultas_ia_conservacion() from public, anon, authenticated;

create trigger consultas_ia_conservacion
  after insert on public.consultas_ia
  for each statement execute function public.consultas_ia_conservacion();
