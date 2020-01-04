CREATE TABLE data."grossMargins"
(
	"ID" integer NOT NULL DEFAULT nextval('data.gross_margins_ID_seq"'::regclass),
	share integer NOT NULL,
	year integer NOT NULL,
	gross_margin double precision NOT NULL,
	valid_from timestamp(4) without time zone NOT NULL,
	valid_to timestamp(4) without time zone NOT NULL,
	CONSTRAINT "grossMargins_pkey" PRIMARY KEY ("ID"),
	CONSTRAINT grossMargins_share_fkey FOREIGN KEY (share)
		REFERENCES entities.shares ("ID") MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE data."grossMargins"
	OWNER TO postgres;

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE data."grossMargins" TO db_tool_user;

GRANT ALL ON TABLE data."grossMargins" TO postgres;