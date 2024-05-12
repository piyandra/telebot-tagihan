create table member
(
    id   bigint                   not null
        primary key,
    role enum ('admin', 'member') null,
    exp  bigint                   null
);

