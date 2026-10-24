-- Auditavisión · la base de datos (pedido del autor, 24-10-2026: «se necesita
-- construir la base de datos»). Plan completo en docs/LANZAMIENTO.md §3, fase 3,
-- y en docs/BASE-DE-DATOS.md.
--
-- Regla de la casa (AGENTS.md §2) llevada a la base:
--   * Ninguna cifra fiscal vive aquí. Las cifras siguen en los archivos que
--     genera Python, con su fuente y su huella. Esta base guarda solo lo que
--     escriben las personas, las bitácoras del Auditor y la copia de lo que se
--     consulta en los portales oficiales (con su dirección, su fecha y su
--     huella SHA-256, para que cualquiera compruebe que no se tocó).
--   * Seguridad por renglón en TODAS las tablas. El público (rol anon) no lee
--     nada privado ni escribe directo: escribe por las funciones, que validan,
--     ponen límite por minuto y usan la llave de servicio.
--   * Sin datos personales en las bitácoras: la dirección IP se guarda como
--     huella (SHA-256 con sal), nunca en claro.

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------------------
-- Administración: quién modera. Se da de alta a mano, con la llave de servicio.
-- ---------------------------------------------------------------------------
create table public.administradores (
  user_id   uuid primary key references auth.users (id) on delete cascade,
  nombre    text not null check (length(nombre) between 2 and 80),
  alta      timestamptz not null default now()
);
alter table public.administradores enable row level security;

create or replace function public.es_admin()
returns boolean
language sql stable security definer set search_path = public
as $$
  select exists (select 1 from public.administradores where user_id = auth.uid());
$$;

create policy "administración se ve a sí misma" on public.administradores
  for select to authenticated using (public.es_admin());

-- ---------------------------------------------------------------------------
-- Lo que escribe la gente: solicitudes de investigación (Servicios), fe de
-- erratas, temas, reportes ciudadanos y el cajón «Cuéntanos lo que viste».
-- Una sola tabla con su tipo, para moderar en un solo lugar.
-- ---------------------------------------------------------------------------
create type public.tipo_envio as enum ('solicitud', 'errata', 'tema', 'reporte', 'algo_raro', 'compartir');
create type public.estado_envio as enum ('nuevo', 'en_revision', 'aprobado', 'publicado', 'descartado');

create table public.envios (
  id          bigint generated always as identity primary key,
  tipo        public.tipo_envio not null,
  estado      public.estado_envio not null default 'nuevo',
  pagina      text check (pagina is null or pagina ~ '^[a-z0-9-]+\.html([?#].*)?$'),
  asunto      text not null check (length(asunto) between 3 and 200),
  texto       text not null check (length(texto) between 10 and 8000),
  documento   text check (documento is null or documento ~ '^https?://'),
  -- Correo solo si la persona quiere respuesta (aviso de privacidad, fase 2).
  correo      text check (correo is null or correo ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'),
  acepta_aviso boolean not null default false,
  ip_huella   text,
  respuesta   text,
  respondio   uuid references auth.users (id),
  creado      timestamptz not null default now(),
  actualizado timestamptz not null default now(),
  -- Sin aceptar el aviso de privacidad no se guarda un correo.
  constraint correo_con_aviso check (correo is null or acepta_aviso)
);
create index envios_estado on public.envios (estado, creado desc);
alter table public.envios enable row level security;

create policy "administración modera los envíos" on public.envios
  for all to authenticated using (public.es_admin()) with check (public.es_admin());

-- Lo aprobado de la fe de erratas, los temas y los reportes es público, sin el
-- correo ni la huella de quien lo mandó.
create view public.envios_publicos with (security_invoker = false) as
  select id, tipo, pagina, asunto, texto, documento, respuesta, creado
  from public.envios
  where estado = 'publicado' and tipo in ('errata', 'tema', 'reporte');
grant select on public.envios_publicos to anon, authenticated;

-- ---------------------------------------------------------------------------
-- El foro de Comunidad (hoy vive en localStorage): escriben personas con
-- cuenta; se publica lo aprobado.
-- ---------------------------------------------------------------------------
create table public.perfiles (
  user_id    uuid primary key references auth.users (id) on delete cascade,
  seudonimo  text not null unique check (seudonimo ~ '^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9 _.-]{3,30}$'),
  entidad    text check (entidad is null or entidad ~ '^[A-Z]{2,5}$'),
  municipio  text check (municipio is null or municipio ~ '^\d{5}$'),
  creado     timestamptz not null default now()
);
alter table public.perfiles enable row level security;
create policy "cada quien ve su perfil" on public.perfiles
  for select to authenticated using (user_id = auth.uid() or public.es_admin());
create policy "cada quien crea su perfil" on public.perfiles
  for insert to authenticated with check (user_id = auth.uid());
create policy "cada quien cambia su perfil" on public.perfiles
  for update to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy "cada quien borra su perfil" on public.perfiles
  for delete to authenticated using (user_id = auth.uid());

create table public.foro_hilos (
  id        bigint generated always as identity primary key,
  autor     uuid not null default auth.uid() references auth.users (id) on delete cascade,
  titulo    text not null check (length(titulo) between 5 and 160),
  pagina    text check (pagina is null or pagina ~ '^[a-z0-9-]+\.html([?#].*)?$'),
  aprobado  boolean not null default false,
  creado    timestamptz not null default now()
);
create table public.foro_mensajes (
  id        bigint generated always as identity primary key,
  hilo      bigint not null references public.foro_hilos (id) on delete cascade,
  autor     uuid not null default auth.uid() references auth.users (id) on delete cascade,
  texto     text not null check (length(texto) between 2 and 4000),
  aprobado  boolean not null default false,
  creado    timestamptz not null default now()
);
create index foro_mensajes_hilo on public.foro_mensajes (hilo, creado);
alter table public.foro_hilos enable row level security;
alter table public.foro_mensajes enable row level security;

create policy "se lee lo aprobado y lo propio" on public.foro_hilos
  for select to anon, authenticated using (aprobado or autor = auth.uid() or public.es_admin());
create policy "con cuenta se abre un hilo, sin aprobar" on public.foro_hilos
  for insert to authenticated with check (autor = auth.uid() and not aprobado);
create policy "administración aprueba hilos" on public.foro_hilos
  for update to authenticated using (public.es_admin()) with check (public.es_admin());
create policy "administración borra hilos" on public.foro_hilos
  for delete to authenticated using (public.es_admin() or autor = auth.uid());

create policy "se lee lo aprobado y lo propio" on public.foro_mensajes
  for select to anon, authenticated using (aprobado or autor = auth.uid() or public.es_admin());
create policy "con cuenta se contesta un hilo visible, sin aprobar" on public.foro_mensajes
  for insert to authenticated with check (
    autor = auth.uid() and not aprobado
    and exists (select 1 from public.foro_hilos h where h.id = hilo and (h.aprobado or h.autor = auth.uid())));
create policy "administración aprueba mensajes" on public.foro_mensajes
  for update to authenticated using (public.es_admin()) with check (public.es_admin());
create policy "administración borra mensajes" on public.foro_mensajes
  for delete to authenticated using (public.es_admin() or autor = auth.uid());

-- ---------------------------------------------------------------------------
-- Alertas: qué entes sigue cada persona (la función de avisos las lee).
-- ---------------------------------------------------------------------------
create table public.alertas (
  id        bigint generated always as identity primary key,
  user_id   uuid not null default auth.uid() references auth.users (id) on delete cascade,
  ente      text not null check (ente ~ '^(federal|estado|municipio):[a-z0-9-]{1,40}$'),
  creado    timestamptz not null default now(),
  unique (user_id, ente)
);
alter table public.alertas enable row level security;
create policy "cada quien ve sus alertas" on public.alertas
  for select to authenticated using (user_id = auth.uid());
create policy "cada quien agrega sus alertas" on public.alertas
  for insert to authenticated with check (user_id = auth.uid());
create policy "cada quien quita sus alertas" on public.alertas
  for delete to authenticated using (user_id = auth.uid());

-- ---------------------------------------------------------------------------
-- Pagos (fase 5): solo los escribe el webhook de la pasarela, con la llave de
-- servicio. Las donaciones son públicas: la alcancía de cuentas claras.
-- ---------------------------------------------------------------------------
create table public.suscripciones (
  id          bigint generated always as identity primary key,
  user_id     uuid not null references auth.users (id) on delete cascade,
  plan        text not null check (length(plan) between 2 and 40),
  estado      text not null check (estado in ('activa', 'vencida', 'cancelada', 'pendiente')),
  vence       date,
  referencia  text unique,
  creado      timestamptz not null default now()
);
alter table public.suscripciones enable row level security;
create policy "cada quien ve su suscripción" on public.suscripciones
  for select to authenticated using (user_id = auth.uid() or public.es_admin());

create table public.donaciones (
  id          bigint generated always as identity primary key,
  monto       numeric(12, 2) not null check (monto > 0),
  moneda      text not null default 'MXN' check (moneda ~ '^[A-Z]{3}$'),
  fecha       date not null default current_date,
  comprobante text not null unique,
  -- Nombre público solo si quien dona lo pide; si no, «Anónima».
  nombre_publico text check (nombre_publico is null or length(nombre_publico) between 2 and 80),
  creado      timestamptz not null default now()
);
alter table public.donaciones enable row level security;
create policy "las donaciones son públicas" on public.donaciones
  for select to anon, authenticated using (true);

-- ---------------------------------------------------------------------------
-- El Auditor Virtual
-- ---------------------------------------------------------------------------
-- «Lo que aún no sé» (hoy en el navegador de cada quien): las preguntas sin
-- respuesta y las que se marcaron «No era lo que buscaba». Dicen qué fichas
-- agregar primero. Sin datos personales: solo la pregunta.
create table public.preguntas_bot (
  id        bigint generated always as identity primary key,
  pregunta  text not null check (length(pregunta) between 2 and 600),
  motivo    text not null check (motivo in ('sin', 'noera', 'ia_rechazada')),
  ficha     text check (ficha is null or length(ficha) <= 300),
  version   text not null check (version ~ '^\d{8}[a-z]{0,2}$'),
  ip_huella text,
  atendida  boolean not null default false,
  creado    timestamptz not null default now()
);
create index preguntas_bot_pendientes on public.preguntas_bot (atendida, creado desc);
alter table public.preguntas_bot enable row level security;
create policy "administración lee y atiende las preguntas" on public.preguntas_bot
  for all to authenticated using (public.es_admin()) with check (public.es_admin());

-- Las más repetidas primero: el tablero de qué fichas faltan.
create view public.preguntas_por_atender with (security_invoker = true) as
  select lower(regexp_replace(pregunta, '\s+', ' ', 'g')) as pregunta, motivo,
         count(*) as veces, max(creado) as ultima
  from public.preguntas_bot
  where not atendida
  group by 1, 2
  order by veces desc, ultima desc;

-- Fase 2 · los portales oficiales. La copia de cada respuesta, con su
-- dirección exacta, la fecha en que se consultó y su huella. Es caché: el
-- dato se cita siempre al portal, nunca a esta tabla.
create table public.portales_cache (
  id         bigint generated always as identity primary key,
  fuente     text not null check (fuente ~ '^[a-z0-9-]{3,40}$'),
  url        text not null check (url ~ '^https://'),
  clave      text not null,
  sha256     text not null check (sha256 ~ '^[0-9a-f]{64}$'),
  cuerpo     jsonb not null,
  bytes      integer not null check (bytes >= 0),
  obtenido   timestamptz not null default now(),
  vence      timestamptz not null,
  unique (fuente, clave, sha256)
);
create index portales_cache_vigente on public.portales_cache (fuente, clave, obtenido desc);
alter table public.portales_cache enable row level security;
-- La copia es pública: cualquiera puede comparar la huella con el portal.
create policy "la copia de los portales es pública" on public.portales_cache
  for select to anon, authenticated using (true);

-- Fase 3 · la capa de inteligencia artificial. Cada consulta queda anotada con
-- las fichas que recibió, lo que contestó, el modelo, los tokens y si pasó la
-- verificación de cifras: así se audita a la IA como a cualquier otra fuente.
create table public.consultas_ia (
  id           bigint generated always as identity primary key,
  pregunta     text not null check (length(pregunta) between 2 and 600),
  fichas       integer[] not null check (cardinality(fichas) between 1 and 12),
  version      text not null check (version ~ '^\d{8}[a-z]{0,2}$'),
  respuesta    text,
  verificada   boolean not null default false,
  rechazo      text check (rechazo is null or rechazo in ('cifra_no_respaldada', 'ficha_no_citada', 'negativa_modelo', 'error_api', 'formato')),
  modelo       text,
  tokens_in    integer check (tokens_in is null or tokens_in >= 0),
  tokens_out   integer check (tokens_out is null or tokens_out >= 0),
  ip_huella    text,
  creado       timestamptz not null default now(),
  constraint verificada_sin_rechazo check (not (verificada and rechazo is not null))
);
create index consultas_ia_fecha on public.consultas_ia (creado desc);
alter table public.consultas_ia enable row level security;
create policy "administración audita a la IA" on public.consultas_ia
  for select to authenticated using (public.es_admin());

-- ---------------------------------------------------------------------------
-- Límite por minuto (antispam y tope de costo de la IA). Lo llaman las
-- funciones con la llave de servicio; el público no lo toca.
-- ---------------------------------------------------------------------------
create table public.limites (
  ip_huella text not null,
  ruta      text not null,
  ventana   timestamptz not null,
  n         integer not null default 1,
  primary key (ip_huella, ruta, ventana)
);
alter table public.limites enable row level security;

create or replace function public.limite_ok(p_huella text, p_ruta text, p_max integer, p_segundos integer)
returns boolean
language plpgsql security definer set search_path = public
as $$
declare
  v_ventana timestamptz := to_timestamp(floor(extract(epoch from now()) / p_segundos) * p_segundos);
  v_n integer;
begin
  if p_max < 1 or p_segundos < 1 then
    raise exception 'límite inválido';
  end if;
  insert into public.limites as l (ip_huella, ruta, ventana) values (p_huella, p_ruta, v_ventana)
    on conflict (ip_huella, ruta, ventana) do update set n = l.n + 1
    returning n into v_n;
  -- Limpieza de ventanas viejas (más de un día), de paso.
  delete from public.limites where ventana < now() - interval '1 day';
  return v_n <= p_max;
end;
$$;
revoke all on function public.limite_ok(text, text, integer, integer) from public, anon, authenticated;

-- Ni el público ni las cuentas comunes escriben directo en lo que solo
-- escriben las funciones.
revoke insert, update, delete on public.envios, public.preguntas_bot, public.portales_cache,
  public.consultas_ia, public.limites, public.suscripciones, public.donaciones, public.administradores
  from anon, authenticated;
-- Los moderadores sí cambian el estado de envíos y preguntas (su política lo exige).
grant select, update on public.envios, public.preguntas_bot to authenticated;
grant select on public.consultas_ia, public.suscripciones, public.administradores to authenticated;
grant select on public.donaciones, public.portales_cache to anon, authenticated;
grant select on public.preguntas_por_atender to authenticated;

-- Fecha de actualización de los envíos.
create or replace function public.toca_actualizado()
returns trigger language plpgsql as $$
begin
  new.actualizado := now();
  return new;
end;
$$;
create trigger envios_actualizado before update on public.envios
  for each row execute function public.toca_actualizado();
