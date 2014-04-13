drop table if exists tl_videos;
create table tl_videos (
    id integer primary key autoincrement,
    title text,
    filename text not null,
    fullpath text not null,
    interval text not null,
    datetimestamp datetime,
    notable boolean,
    usable boolean,
    size integer
);
