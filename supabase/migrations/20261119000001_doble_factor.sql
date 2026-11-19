-- El doble factor de la administración (19-11-2026, pedido del autor: «la forma
-- de proteger la información»; LFPDPPP, DOF 20-03-2025, art. 18: medidas de
-- seguridad técnicas según el riesgo).
--
-- Hasta hoy bastaba con abrir el enlace del correo (o el código maestro) para
-- ser la administración. Desde aquí, la base solo la reconoce con la sesión de
-- dos factores de Supabase (aal2: correo o código maestro + el código de seis
-- números de una aplicación de autenticación, TOTP). Toda regla que pregunta
-- es_admin() (los códigos, las solicitudes, la bitácora, el tablero de uso, la
-- moderación) queda detrás del segundo factor sin tocar cada una.
--
-- El panel (acceso-paginas.js) da de alta la aplicación la primera vez. Si se
-- pierde, se borra el factor con la llave de servicio (auth.mfa_factors) y se
-- vuelve a dar de alta.

create or replace function public.es_admin()
returns boolean
language sql stable security definer set search_path = public
as $$
  select exists (select 1 from public.administradores where user_id = auth.uid())
     and coalesce(auth.jwt() ->> 'aal', 'aal1') = 'aal2';
$$;

comment on function public.es_admin() is
  'Administración con sesión de dos factores (aal2). Ver 20261119000001_doble_factor.sql.';
