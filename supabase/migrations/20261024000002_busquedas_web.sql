-- Auditavisión · búsquedas en internet del Auditor Virtual (24-10-2026).
-- Pedido del autor: que el chat, al escribir el nombre de un personaje, ofrezca
-- también «cuestiones que se puedan localizar en internet». La función
-- buscar-web guarda aquí lo que encontró: SOLO enlaces (título, dirección,
-- sitio, tipo y fecha de la página), nunca un texto redactado sobre la persona.
-- La copia dura un día, para no pagar dos veces la misma búsqueda.
create table public.busquedas_web (
  id         bigint generated always as identity primary key,
  clave      text not null check (clave ~ '^[a-z0-9ñ ]{4,70}$'),
  nombre     text not null check (length(nombre) between 5 and 70),
  enlaces    jsonb not null check (jsonb_typeof(enlaces) = 'array'),
  modelo     text,
  tokens_in  integer check (tokens_in is null or tokens_in >= 0),
  tokens_out integer check (tokens_out is null or tokens_out >= 0),
  busquedas  integer check (busquedas is null or busquedas >= 0),
  obtenido   timestamptz not null default now(),
  vence      timestamptz not null
);
create index busquedas_web_vigente on public.busquedas_web (clave, obtenido desc);
alter table public.busquedas_web enable row level security;
-- Son enlaces públicos: cualquiera puede ver qué se encontró y cuándo.
create policy "las búsquedas en internet son públicas" on public.busquedas_web
  for select to anon, authenticated using (true);
revoke insert, update, delete on public.busquedas_web from anon, authenticated;
grant select on public.busquedas_web to anon, authenticated;
