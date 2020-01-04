CREATE TABLE data."assetTurnovers"
(
	"ID" integer NOT NULL DEFAULT nextval('data."assetTurnovers_ID_seq"'::regclass),
	share integer NOT NULL,
	year integer NOT NULL,
	asset_turnover double precision NOT NULL,
	valid_from timestamp(4) without time zone NOT NULL,
	valid_to_timestamp(4) without time zone NOT NULL,
	CONSTRAINT "assetTurnovers_pkey" PRIMARY KEY ("ID"),
	CONSTRAINT "assetTurnovers_share_fkey" FOREIGN KEY (share)
		REFERENCES entities.shares("ID") MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
		NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE data."assetTurnovers"
	OWNER TO postgres;

GRANT INSERT, SELECT, UPDATE, DELET ON TABLE data."assetTurnovers" TO db_tool_user;

GRANT ALL ON TABLE data."assetTurnovers" TO postgres;