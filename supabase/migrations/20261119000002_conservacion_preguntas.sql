-- Cuánto se guardan las preguntas que el Auditor no supo contestar (19-11-2026).
-- Llegaban a preguntas_bot sin plazo de borrado, con la huella de la conexión.
-- Igual que los envíos y las consultas a la IA: 12 meses. El aviso de
-- privacidad lo dice («Qué datos tratamos») y esta migración lo cumple: cada
-- pregunta nueva barre las que pasaron de un año.
create or replace function public.preguntas_bot_conservacion()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  delete from public.preguntas_bot where creado < now() - interval '12 months';
  return null;
end;
$$;
revoke all on function public.preguntas_bot_conservacion() from public, anon, authenticated;

create trigger preguntas_bot_conservacion
  after insert on public.preguntas_bot
  for each statement execute function public.preguntas_bot_conservacion();
