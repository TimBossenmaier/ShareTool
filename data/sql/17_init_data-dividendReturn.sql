CREATE TABLE data."dividendReturns"
(
	"ID" SERIAL NOT NULL,
	year integer NOT NULL,
	dividend_return double precision NOT NULL,
	valid_from timestamp(4) without time zone NOT NULL,
	valid_to timestamp(4) without time zone NOT NULL,
	share integer NOT NULL,
	CONSTRAINT "dividendReturns_pkey" PRIMARY KEY ("ID"),
	CONSTRAINT "dividendReturns_share_fkey" FOREIGN KEY (share)
		REFERENCES entities.shares("ID") MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE data."dividendReturns"
	OWNER TO postgres;

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE data."dividendReturns" TO db_tool_user;

GRANT ALL ON TABLE data."dividendReturns" TO postgres;