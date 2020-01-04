CREATE TABLE data."sharePrices"
(
	"ID" SERIAL NOT NULL,
	share integer NOT NULL,
	share_price double precision NOT NULL,
	valid_from timestamp(4) without time zone NOT NULL,
	valid_to timestamp(4) without time zone NOT NULL,
	CONSTRAINT "sharePrices_pkey" PRIMARY KEY ("ID"),
	CONSTRAINT "sharePrices_share_fkey" FOREIGN KEY (share)
		REFERENCES entities.shares ("ID") MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
		NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE data."sharePrices"
	OWNER TO postgres;

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE data."sharePrices" TO db_tool_user;

GRANT ALL ON TABLE  data."sharePrices" TO postgres;