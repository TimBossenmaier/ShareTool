CREATE TABLE data."ROAs"
(
	"ID" integer NOT NULL DEFAULT nextval('data.ROAs_ID_seq"'::regclass),
	share integer NOT NULL,
	year integer NOT NULL,
	roa double precision NOT NULL,
	valid_from timestamp(4) without time zone NOT NULL,
	valid_to timestamp(4) without time zone NOT NULL,
	CONSTRAINT "ROAs_pkey" PRIMARY KEY ("ID"),
	CONSTRAINT "ROAs_share_fkey" FOREIGN KEY (share)
		REFERENCES entities.shares ("ID") MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE data."ROAs"
	OWNER TO postgres;

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE data."ROAs" TO db_tool_user;

GRANT ALL ON TABLE data."ROAs" TO postgres;