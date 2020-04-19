create table if not exists log_table
(
	id serial not null,
	date timestamp default now(),
	action text,
	description text,
	severity integer
);

alter table log_table owner to postgres;


create table magazine
(
	title text,
	date text,
	url text,
	id serial not null,
	date_inserted timestamp default now(),
	source text
);

alter table magazine owner to postgres;

create table sources
(
	id serial not null,
	source_name text,
	source_type text,
	url text,
	language text
);

comment on table sources is 'content sources';

alter table sources owner to postgres;



INSERT INTO public.sources (id, source_name, source_type, url, language) VALUES (8, 'CT24.cz', 'RSS', 'https://ct24.ceskatelevize.cz/rss/hlavni-zpravy?_ga=2.82432918.1891550398.1586297262-404706205.1586297262', 'CZ');
INSERT INTO public.sources (id, source_name, source_type, url, language) VALUES (1, 'Patria', 'RSS', 'https://www.patria.cz/rss.html', 'CZ');
INSERT INTO public.sources (id, source_name, source_type, url, language) VALUES (5, 'idnes.cz', 'RSS', 'https://servis.idnes.cz/rss.aspx?c=zpravodaj', 'CZ');
INSERT INTO public.sources (id, source_name, source_type, url, language) VALUES (6, 'ceskenoviny.cz', 'RSS', 'https://www.ceskenoviny.cz/sluzby/rss/zpravy.php', 'CZ');
INSERT INTO public.sources (id, source_name, source_type, url, language) VALUES (2, 'Kurzy.cz', 'RSS', 'https://www.kurzy.cz/zpravy/util/forext.dat?type=rss', 'CZ');
INSERT INTO public.sources (id, source_name, source_type, url, language) VALUES (7, 'irozhlas.cz', 'RSS', 'https://www.irozhlas.cz/rss/irozhlas', 'CZ');


