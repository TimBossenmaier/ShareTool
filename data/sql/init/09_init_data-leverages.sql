CREATE TABLE data.leverages
(
	"ID" SERIAL NOT NULL,
	share_ID integer NOT NULL,
	year integer NOT NULL,
	debt_to_equity_ratio double precision NOT NULL,
	valid_from timestamp(4) without time zone NOT NULL,
	valid_to timestamp(4) without time zone NOT NULL,
	CONSTRAINT leverages_pkey PRIMARY KEY ("ID"),
	CONSTRAINT leverages_share_fkey  FOREIGN KEY (share)
		REFERENCES entities.shares("ID") MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE data.leverages
	OWNER TO postgres;

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE data.leverages TO db_tool_user;

GRANT ALL ON TABLE data.leverages TO postgres;