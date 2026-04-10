-- 遗境焕活 MVP 数据模型（PostgreSQL）

create table users (
  id bigserial primary key,
  role varchar(20) not null default 'visitor',
  nickname varchar(80),
  email varchar(120),
  phone varchar(32),
  password_hash varchar(255),
  preferences jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table heritage_items (
  id bigserial primary key,
  name varchar(120) not null,
  category varchar(64) not null,
  city varchar(64) not null,
  history_background text,
  craft_process text,
  cultural_meaning text,
  representative_works text,
  inheritor_info text,
  experience_method text,
  status varchar(20) not null default 'draft',
  created_by bigint,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table heritage_contents (
  id bigserial primary key,
  item_id bigint not null references heritage_items(id) on delete cascade,
  content_type varchar(32) not null,
  title varchar(200) not null,
  body text not null,
  tags jsonb not null default '[]'::jsonb,
  media_assets jsonb not null default '[]'::jsonb,
  version int not null default 1,
  status varchar(20) not null default 'draft',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table guide_scripts (
  id bigserial primary key,
  item_id bigint not null references heritage_items(id) on delete cascade,
  style varchar(32) not null,
  script_schema jsonb not null,
  fallback_text text not null,
  status varchar(20) not null default 'draft',
  version int not null default 1,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table routes (
  id bigserial primary key,
  user_id bigint references users(id) on delete set null,
  item_id bigint references heritage_items(id) on delete set null,
  duration_minutes int not null,
  interests jsonb not null default '[]'::jsonb,
  travel_type varchar(20) not null,
  first_time boolean not null default true,
  preference varchar(32),
  reasoning text,
  status varchar(20) not null default 'active',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table route_nodes (
  id bigserial primary key,
  route_id bigint not null references routes(id) on delete cascade,
  node_order int not null,
  node_title varchar(120) not null,
  stay_minutes int not null,
  highlight text,
  skippable boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(route_id, node_order)
);

create table user_behaviors (
  id bigserial primary key,
  user_id bigint references users(id) on delete set null,
  session_id varchar(120),
  behavior_type varchar(40) not null,
  target_type varchar(40),
  target_id bigint,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table generated_contents (
  id bigserial primary key,
  user_id bigint references users(id) on delete set null,
  route_id bigint references routes(id) on delete set null,
  content_type varchar(40) not null,
  template_id varchar(80) not null,
  input_payload jsonb not null default '{}'::jsonb,
  output_payload jsonb not null default '{}'::jsonb,
  preview_url text,
  download_url text,
  share_url text,
  status varchar(20) not null default 'ready',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table feedbacks (
  id bigserial primary key,
  user_id bigint references users(id) on delete set null,
  item_id bigint references heritage_items(id) on delete set null,
  rating int,
  comment text,
  source varchar(32) not null default 'app',
  created_at timestamptz not null default now()
);

create table admins (
  id bigserial primary key,
  username varchar(80) not null unique,
  password_hash varchar(255) not null,
  role varchar(32) not null default 'operator',
  is_active boolean not null default true,
  last_login_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table audit_logs (
  id bigserial primary key,
  admin_id bigint references admins(id) on delete set null,
  action varchar(120) not null,
  target_type varchar(80),
  target_id varchar(80),
  request_id varchar(120),
  ip varchar(64),
  detail jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index idx_heritage_items_city on heritage_items(city);
create index idx_heritage_items_status on heritage_items(status);
create index idx_heritage_contents_item_id on heritage_contents(item_id);
create index idx_guide_scripts_item_style on guide_scripts(item_id, style);
create index idx_routes_user_id on routes(user_id);
create index idx_route_nodes_route_id on route_nodes(route_id);
create index idx_user_behaviors_user_time on user_behaviors(user_id, created_at desc);
create index idx_generated_contents_user_id on generated_contents(user_id);
create index idx_feedbacks_item_id on feedbacks(item_id);
create index idx_audit_logs_admin_time on audit_logs(admin_id, created_at desc);


create table conversation_history (
  id bigserial primary key,
  user_id bigint references users(id) on delete set null,
  session_id varchar(120) not null,
  heritage_id bigint references heritage_items(id) on delete cascade,
  role varchar(20) not null,
  user_text text not null default '',
  summary_text text not null default '',
  vector jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index idx_conversation_session_time on conversation_history(session_id, created_at desc);


create table user_profiles (
  id bigserial primary key,
  user_id bigint not null references users(id) on delete cascade unique,
  level int not null default 1,
  exp int not null default 0,
  title varchar(40) not null default '见习',
  badges jsonb not null default '[]'::jsonb,
  completed_items jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table team_sessions (
  id bigserial primary key,
  team_code varchar(16) not null unique,
  leader_user_id bigint not null references users(id) on delete cascade,
  member_user_id bigint references users(id) on delete set null,
  heritage_id bigint not null references heritage_items(id) on delete cascade,
  latest_step jsonb not null default '{}'::jsonb,
  status varchar(20) not null default 'active',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index idx_team_sessions_code on team_sessions(team_code);
