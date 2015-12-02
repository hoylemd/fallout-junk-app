drop table if exists components;
create table components (
  id integer primary key autoincrement,
  slug varchar[64] not null unique,
  name varchar[64] not null,
  value int default 0,
  weight decimal default 0
);

drop table if exists junk;
create table junk (
  id integer primary key autoincrement,
  slug varchar[64] not null unique,
  name varchar[64] not null,
  value int default 0,
  weight decimal default 0,
  components_value int,
  components_weight decimal,
  craftable integer default 0,
  used_for_crafting integer default 0
);

drop table if exists junk_compositions;
create table junk_compositions (
  junk_id integer not null,
  component_id integer not null,
  count integer default 1,
  foreign key(junk_id) references junk(id),
  foreign key(component_id) references components(id)
  primary key(junk_id, component_id)
)
