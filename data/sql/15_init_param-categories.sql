CREATE TABLE param.categories
(
	"ID" integer NOT NULL,
	name text COLLATE pg_catalog."default" NOT NULL,
	CONSTRAINT categories_pkey PRIMARY KEY ("ID")
)

TABLESPACE pg_default;

ALTER TABLE param.categories
	OWNER TO postgres;

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE param.categories TO db_tool_user;

GRANT ALL ON TABLE param.categories TO postgres;
