CREATE TABLE data.profits
(
	"ID" SERIAL NOT NULL,
	year integer NOT NULL,
	share integer NOT NULL,
	profit double precision NOT NULL,
	valid_from timestamp(4) without time zone NOT NULL,
	valid_to timestamp(4) without time zone NOT NULL,
	CONSTRAINT profits_pkey PRIMARY KEY ("ID"),
	CONSTRAINT profits_share_fkey FOREIGN KEY (share)
		REFERENCES entities.shares ("ID") MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE data.profits
	OWNER TO postgres;

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE data.profits TO db_tool_user;

GRANT ALL ON TABLE data.profits TO postgres;