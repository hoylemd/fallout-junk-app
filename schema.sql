drop table if exists components;
create table components (
  id integer primary key autoincrement,
  slug varchar[64] not null,
  name varchar[64] not null,
  value int default 0,
  weight decimal default 0
);
