CREATE TABLE param.currencies
(
	"ID" integer NOT NULL DEFAULT nextval('param."currencies_ID_seq"'::regclass),
	currency_code text COLLATE pg_catalog."default" NOT NULL,
	currency_name text COLLATE pg_catalog."default" NOT NULL,
	CONSTRAINT currencies_pkey PRIMARY KEY ("ID")
)

TABLESPACE pg_default;

ALTER TABLE param.currencies
	OWNER TO postgres;

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE param.currencies TO db_tool_user;

GRANT ALL ON TABLE param.currencies TO postgres;