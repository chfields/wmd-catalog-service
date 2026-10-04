create table products (
    id text primary key,
    name text not null,
    description text not null default '',
    price_cents integer not null check (price_cents >= 0),
    stock integer not null check (stock >= 0),
    created_at timestamptz not null default now()
);

create table reservations (
    id uuid primary key default gen_random_uuid(),
    order_ref text not null,
    lines jsonb not null,
    created_at timestamptz not null default now()
);

create index reservations_order_ref on reservations (order_ref);
