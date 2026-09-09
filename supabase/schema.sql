-- FOUNTAIN website · Supabase schema
-- Run once in Supabase SQL editor (Project → SQL → New query).

create extension if not exists pgcrypto;

create table if not exists public.contact_requests (
  id          uuid primary key default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  audience    text,                       -- lab | robot | hardware | supplier | investor | other
  needs       text[] default '{}',        -- data | supply | prod | motion | compliance | invest | other
  name        text not null,
  company     text,
  email       text not null,
  role        text,
  website     text,
  linkedin    text,
  brief       text,
  timeline    text,
  budget      text,
  page        text,
  user_agent  text,
  ip          inet,
  status      text not null default 'new' -- new | replied | closed
);

create table if not exists public.applications (
  id          uuid primary key default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  name        text not null,
  email       text not null,
  linkedin    text,
  location    text,
  company     text,
  website     text,
  one_liner   text,
  pitch       text,
  deck_link   text,
  demo_link   text,
  why         text,
  source      text,
  stage       text,                       -- idea | proto | users | shipped
  page        text,
  user_agent  text,
  ip          inet,
  status      text not null default 'new' -- new | screening | call | pass | accepted
);

create index if not exists contact_requests_created_idx on public.contact_requests (created_at desc);
create index if not exists applications_created_idx on public.applications (created_at desc);

-- Lock down: no anon/authenticated access. Only the service role (used by Vercel functions) can write/read.
alter table public.contact_requests enable row level security;
alter table public.applications enable row level security;
revoke all on public.contact_requests from anon, authenticated;
revoke all on public.applications from anon, authenticated;
