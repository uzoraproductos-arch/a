-- Auditavisión · Base de datos, paso 1: lo que escriben las personas.
-- Ninguna cifra fiscal vive aquí (docs/LANZAMIENTO.md, regla de arriba).
-- Se pega completo en Supabase > SQL Editor > Run. Se puede correr una vez.
--
-- Regla de seguridad: el público solo puede ESCRIBIR. Nadie puede leer
-- desde la página; solo la administración, desde el panel de Supabase.

-- 1. Formularios: solicitudes de Servicios, reportes, temas y errores.
create table public.mensajes (
  id        bigint generated always as identity primary key,
  creado    timestamptz not null default now(),
  tipo      text not null check (tipo in (
              'solicitud',   -- Servicios (servicios.html)
              'reporte',     -- Reporte ciudadano
              'tema',        -- Propuesta de tema
              'error',       -- Señalamiento de error / fe de erratas
              'otro')),
  campos    jsonb not null check (pg_column_size(campos) <= 16000),
  texto     text  not null check (char_length(texto) <= 8000),
  pagina    text  check (char_length(pagina) <= 300),
  estado    text not null default 'nuevo'
              check (estado in ('nuevo', 'en_revision', 'respondido', 'aprobado', 'descartado')),
  nota_admin text
);

comment on table public.mensajes is
  'Formularios de la plataforma. Escribe el público; lee solo la administración.';

-- 2. «Lo que aún no sé»: preguntas que el Auditor Virtual no supo contestar.
--    Sin datos personales: solo la pregunta y dónde se hizo.
create table public.preguntas_bot (
  id        bigint generated always as identity primary key,
  creado    timestamptz not null default now(),
  pregunta  text not null check (char_length(pregunta) between 2 and 500),
  motivo    text not null default 'sin_respuesta'
              check (motivo in ('sin_respuesta', 'no_era_lo_que_buscaba')),
  pagina    text check (char_length(pagina) <= 300),
  atendida  boolean not null default false
);

comment on table public.preguntas_bot is
  'Preguntas sin respuesta del Auditor Virtual. Se revisan cada mes para crear fichas.';

-- 3. Seguridad por renglón: sin política, nadie lee ni cambia nada.
alter table public.mensajes      enable row level security;
alter table public.preguntas_bot enable row level security;

-- El público (llave publicable) solo puede insertar, y solo estas columnas:
-- no puede ponerse estado «aprobado» ni cambiar la fecha.
revoke all on public.mensajes, public.preguntas_bot from anon, authenticated;
grant insert (tipo, campos, texto, pagina)     on public.mensajes      to anon;
grant insert (pregunta, motivo, pagina)        on public.preguntas_bot to anon;

create policy "El público puede enviar formularios"
  on public.mensajes for insert to anon
  with check (true);

create policy "El público puede anotar preguntas sin respuesta"
  on public.preguntas_bot for insert to anon
  with check (true);

-- No hay política de lectura: la administración ve todo desde el panel
-- (Table Editor), que usa la llave secreta y no pasa por estas reglas.
