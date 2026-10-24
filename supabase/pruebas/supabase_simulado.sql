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
