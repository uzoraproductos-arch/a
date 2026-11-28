-- Ronda 42 · el agente lector de auditor-ia (Ola 4, entrega B).
-- consultas_ia anota además si la consulta fue en modo agente, qué
-- herramientas usó (solo sus nombres, nunca lo que el modelo les escribió),
-- cuántas rondas hizo y qué datos de la base fiscal leyó. En modo agente una
-- consulta puede no haber leído ninguna ficha (solo datos fiscales) o haber
-- leído más de doce, así que el tope de «fichas» se ensancha.
-- Desde esta ronda la pregunta se guarda sin correo, CURP, RFC, teléfono ni
-- montos (lo hace la función, con _comun/anonimo.ts).
alter table public.consultas_ia drop constraint if exists consultas_ia_fichas_check;
alter table public.consultas_ia add constraint consultas_ia_fichas_check check (cardinality(fichas) <= 60);
alter table public.consultas_ia alter column fichas set default '{}';
alter table public.consultas_ia
  add column if not exists agente       boolean  not null default false,
  add column if not exists herramientas text[]   not null default '{}',
  add column if not exists datos        text[]   not null default '{}',
  add column if not exists rondas       smallint;
alter table public.consultas_ia
  add constraint consultas_ia_herramientas check (
    cardinality(herramientas) <= 12
    and herramientas <@ array['buscar_fichas', 'consultar_dato_fiscal', 'consultar_pendientes']::text[]),
  add constraint consultas_ia_datos check (cardinality(datos) <= 60),
  add constraint consultas_ia_rondas check (rondas is null or rondas between 0 and 3),
  -- El modo de siempre lee al menos una ficha; solo el agente puede no leer ninguna.
  add constraint consultas_ia_modo check (agente or (cardinality(fichas) >= 1 and cardinality(herramientas) = 0 and rondas is null));
comment on column public.consultas_ia.agente is 'true: el modelo buscó con herramientas de solo lectura (agente lector, Ronda 42)';
comment on column public.consultas_ia.herramientas is 'Nombres de las herramientas que llamó, en orden; nunca sus consultas';
comment on column public.consultas_ia.datos is 'id de los datos de docs/fiscal-2027/ que leyó';
