drop table if exists users;
drop table if exists income;
drop table if exists expenses;
drop table if exists subscriptions;
drop table if exists savings;
drop table if exists budget;

create table users (
  id integer primary key autoincrement,
  admin integer not null DEFAULT 0,
  username text not null unique,
  password text not null,
  balance float default 0.0 not null,
  savings_goal float,
  savings_name text
);
create table income (
  id integer primary key autoincrement,
  user_id integer not null,
  amount float default 0.0 not null,
  category text not null,
  description text not null,
  date date not null
);
create table expenses (
  id integer primary key autoincrement,
  user_id integer not null,
  amount float default 0.0 not null,
  category text not null,
  date date not null,
  description text not null
);
create table subscriptions (
  id integer primary key autoincrement,
  user_id integer not null,
  amount float default 0.0 not null,
  date date not null,
  months date not null,
  description text not null
);
create table savings (
  id integer primary key autoincrement,
  user_id integer not null,
  amount float default 0.0 not null
);
create table budget (
  id integer primary key autoincrement,
  user_id integer not null,
  amount float default 0.0 not null,
  category text not null,
  month integer not null
);