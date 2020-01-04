CREATE TABLE param.countries
(
	"ID" integer NOT NULL,
	iso text COLLATE pg_catalog."default",
	name text COLLATE pg_catalog."default",
	CONSTRAINT countries_pkey PRIMARY KEY ("ID"),
	CONSTRAINT "unique" UNIQUE (iso)

)

TABLESPACE pg_default;

ALTER TABLE param.countries
	OWNER TO postgres;

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE param.countries TO db_tool_user;

GRANT ALL ON TABLE param.countries TO postgres;
