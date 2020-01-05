CREATE TABLE data."assetTurnovers"
(
	"ID" SERIAL NOT NULL,
	share_ID integer NOT NULL,
	year integer NOT NULL,
	asset_turnover double precision NOT NULL,
	valid_from timestamp(4) without time zone NOT NULL,
	valid_to timestamp(4) without time zone NOT NULL,
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

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE data."assetTurnovers" TO db_tool_user;

GRANT ALL ON TABLE data."assetTurnovers" TO postgres;