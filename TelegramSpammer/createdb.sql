create table if NOT EXISTS links(
    id integer primary key,
    link text
);

create table if not EXISTS messages(
    id integer primary key,
    message_text text
);