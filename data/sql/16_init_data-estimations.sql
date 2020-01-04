CREATE TABLE data.estimations
(
	"ID" SERIAL NOT NULL,
	share integer NOT NULL,
	year integer NOT NULL,
	profit_per_share double precision NOT NULL,
	dividend double precision NOT NULL,
	valid_from timestamp(4) without time zone NOT NULL,
	valid_to timestamp(4) without time zone NOT NULL,
	CONSTRAINT estimations_pkey PRIMARY KEY ("ID"),
	CONSTRAINT estimations_share_fkey FOREIGN KEY (share)
		REFERENCES entities.shares ("ID") MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE data.estimations
	OWNER TO postgres;

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE data.estimations TO db_tool_user;

GRANT ALL ON TABLE data.estimations TO postgres;