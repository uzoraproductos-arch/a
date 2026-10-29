-- Auditavisión · bóveda de evidencias (paso 2.4 del plan v2, 27-10-2026).
-- Cada documento oficial que respalda un dato de la plataforma, con su huella
-- SHA-256: la prueba de qué decía y cuándo, aunque el gobierno lo cambie de
-- dirección o lo retire. La fuente de verdad sigue en el repositorio
-- (docs/boveda/evidencias.json, que escribe herramientas/boveda.py); esta
-- tabla es su espejo público y el almacenamiento «boveda» guarda el archivo.
--
-- Reglas:
--   * Una huella no se corrige: si el documento cambió, entra otro renglón
--     con la huella nueva y el anterior se queda. Nadie actualiza ni borra.
--   * Solo la llave de servicio (herramientas/boveda.py --subir) escribe.
--   * Todo es público: son documentos oficiales y sus huellas.
create table public.evidencias (
  id          bigint generated always as identity primary key,
  url         text not null check (url ~ '^https?://' and length(url) <= 2000),
  sha256      text not null check (sha256 ~ '^[0-9a-f]{64}$'),
  bytes       bigint not null check (bytes > 0),
  tipo        text check (tipo is null or length(tipo) <= 120),
  copiado     date not null,
  ruta        text check (ruta is null or ruta ~ '^[0-9a-f]{64}(\.[a-z0-9]{1,5})?$'),
  archive_org text check (archive_org is null or archive_org ~ '^https://web\.archive\.org/'),
  usos        text[] not null default '{}',
  alta        timestamptz not null default now(),
  unique (url, sha256)
);
create index evidencias_url on public.evidencias (url, copiado desc);
alter table public.evidencias enable row level security;
create policy "las evidencias son públicas" on public.evidencias
  for select to anon, authenticated using (true);
revoke insert, update, delete on public.evidencias from anon, authenticated;
grant select on public.evidencias to anon, authenticated;

-- La huella es inalterable, también para la llave de servicio.
create or replace function public.evidencias_inalterables()
returns trigger language plpgsql as $$
begin
  raise exception 'una evidencia no se modifica ni se borra: si el documento cambió, entra con su huella nueva';
end $$;
create trigger evidencias_inalterables before update or delete on public.evidencias
  for each row execute function public.evidencias_inalterables();

-- La versión más reciente de cada documento, y si cambió desde la primera.
create view public.evidencias_vigentes with (security_invoker = true) as
  select distinct on (url) url, sha256, bytes, tipo, copiado, ruta, archive_org,
         (select count(*) from public.evidencias h where h.url = e.url) - 1 as cambios
  from public.evidencias e
  order by url, copiado desc, id desc;
grant select on public.evidencias_vigentes to anon, authenticated;

-- El almacenamiento: los archivos, nombrados por su huella. Lectura pública,
-- escritura solo con la llave de servicio (que no pasa por estas reglas).
insert into storage.buckets (id, name, public) values ('boveda', 'boveda', true)
  on conflict (id) do nothing;
create policy "la bóveda se lee en público" on storage.objects
  for select to anon, authenticated using (bucket_id = 'boveda');
