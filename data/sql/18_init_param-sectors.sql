CREATE TABLE param.sectors
(
	"ID" integer NOT NULL DEFAULT nextval('param."segment_ID_seq"'::regclass),
	name text COLLATE pg_catalog."default" NOT NULL,
	CONSTRAINT segment_pkey PRIMARY KEY ("ID")
)

TABLESPACE pg_default;

ALTER TABLE param.sectors
	OWNER TO postgres;

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE param.sectors TO db_tool_user;

GRANT ALL ON TABLE param.sectors TO postgres;