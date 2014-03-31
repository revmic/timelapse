drop table if exists tl_videos;
create table tl_videos (
    id integer primary key autoincrement,
    filename text not null,
    fullpath text not null,
    title text,
    datetimestamp datetime,
    notable boolean,
    size integer
);
