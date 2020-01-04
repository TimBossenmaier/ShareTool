CREATE TABLE data.cashflows
(
	"ID" SERIAL NOT NULL,
	share integer NOT NULL,
	year integer NOT NULL,
	cashflow double precision NOT NULL,
	valid_from timestamp(4) without time zone NOT NULL,
	valid_to timestamp(4) without time zone NOT NULL,
	CONSTRAINT cashflows_pkey PRIMARY KEY ("ID"),
	CONSTRAINT cashflows_share_fkey  FOREIGN KEY (share)
		REFERENCES entities.shares ("ID") MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE data.cashflows
	OWNER TO postgres;

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE data.cashflows TO db_tool_user;

GRANT ALL ON TABLE data.cashflows TO postgres;