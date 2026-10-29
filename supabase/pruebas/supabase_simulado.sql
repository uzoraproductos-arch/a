-- Lo mínimo de Supabase para probar la migración en un PostgreSQL local:
-- los roles anon, authenticated y service_role, el esquema auth con su tabla
-- de usuarios y auth.uid(), y los permisos que Supabase da por omisión en el
-- esquema public (todo a anon y authenticated: la seguridad por renglón es la
-- que cierra). Solo para pruebas; en Supabase esto ya existe.
create role anon nologin;
create role authenticated nologin;
create role service_role nologin bypassrls;
grant usage on schema public to anon, authenticated, service_role;
alter default privileges in schema public grant all on tables to anon, authenticated, service_role;
alter default privileges in schema public grant all on sequences to anon, authenticated, service_role;
alter default privileges in schema public grant all on functions to anon, authenticated, service_role;

create schema auth;
grant usage on schema auth to anon, authenticated, service_role;
create table auth.users (id uuid primary key, email text);
create function auth.uid() returns uuid language sql stable as $$
  select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid;
$$;
grant execute on function auth.uid() to anon, authenticated, service_role;

-- Como en Supabase: pgcrypto vive en el esquema «extensions», fuera de public.
-- Así una función con search_path = public que la use falla aquí también
-- (30-10-2026: generar_codigos falló en el proyecto real por eso).
create schema extensions;
grant usage on schema extensions to anon, authenticated, service_role;
create extension pgcrypto with schema extensions;

-- El almacenamiento de archivos (Storage): sus dos tablas, con la seguridad
-- por renglón encendida como en Supabase.
create schema storage;
grant usage on schema storage to anon, authenticated, service_role;
create table storage.buckets (id text primary key, name text not null, public boolean default false);
create table storage.objects (id uuid primary key default gen_random_uuid(), bucket_id text references storage.buckets (id), name text not null, owner uuid);
alter table storage.objects enable row level security;
grant select, insert, update, delete on storage.buckets, storage.objects to anon, authenticated, service_role;
