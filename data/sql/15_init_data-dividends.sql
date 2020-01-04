CREATE TABLE data.dividends
(
	"ID" SERIAL NOT NULL,
	share integer NOT NULL,
	year integer NOT NULL,
	dividend double precision NOT NULL,
	valid_from timestamp(4) without time zone NOT NULL,
	valid_to timestamp(4) without time zone NOT NULL,
	CONSTRAINT dividends_pkey PRIMARY KEY ("ID"),
	CONSTRAINT dividends_share_fkey FOREIGN KEY (share)
		REFERENCES entities.shares ("ID") MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE data.dividends
	OWNER TO postgres;

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE data.dividends TO db_tool_user;

GRANT ALL ON TABLE data.dividends TO postgres;