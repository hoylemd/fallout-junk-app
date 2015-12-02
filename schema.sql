drop table if exists components;
create table components {
  id integer primary key autoincrement,
  slug varchar[32] not null,
  name varchar[64] not null,
  int value default 0,
  decimal weight default 0
}
