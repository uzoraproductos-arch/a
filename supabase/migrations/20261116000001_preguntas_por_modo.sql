-- El registro por modo llega a la base (pedido del autor, 16-11-2026: «sí,
-- lleva el registro por modo a Supabase»). El Auditor trabaja en cuatro modos
-- y remite lo que le toca a otro: cada pregunta sin respuesta, o marcada «No
-- era lo que buscaba», guarda ahora en qué modo se hizo y a qué modo le
-- tocaba, para saber qué fichas le faltan a cada uno.
--
-- No se guarda nada más que antes: siguen llegando solo las preguntas que el
-- Auditor no supo contestar, sin nombre ni correo. El modo no es un dato
-- personal: es el botón que estaba elegido en el chat.
alter table public.preguntas_bot
  add column modo text check (modo is null or modo in ('inspector', 'periodista', 'ciudadano', 'ambientalista')),
  add column modo_toca text check (modo_toca is null or modo_toca in ('inspector', 'periodista', 'ciudadano', 'ambientalista'));

-- Qué le falta a cada modo: las preguntas por atender, repartidas.
create view public.preguntas_por_modo with (security_invoker = true) as
  select coalesce(modo_toca, modo, 'sin modo') as le_toca,
         coalesce(modo, 'sin modo') as se_pregunto_en,
         motivo, count(*) as veces, max(creado) as ultima
  from public.preguntas_bot
  where not atendida
  group by 1, 2, 3
  order by veces desc, ultima desc;
revoke all on public.preguntas_por_modo from anon;
grant select on public.preguntas_por_modo to authenticated;
