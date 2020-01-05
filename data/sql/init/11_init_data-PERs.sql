CREATE TABLE data."PERs"
(
	"ID" SERIAL NOT NULL,
	share_ID integer NOT NULL,
	"PE_ratio" double precision NOT NULL,
	year integer NOT NULL,
	valid_from timestamp(4) without time zone NOT NULL,
	valid_to timestamp(4) without time zone NOT NULL,
	CONSTRAINT per_pkey PRIMARY KEY ("ID"),
	CONSTRAINT per_share_fkey FOREIGN KEY (share)
		REFERENCES entities.shares("ID") MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
		NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE data."PERs"
	OWNER TO postgres;


GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE data."PERs" TO db_tool_user;

GRANT ALL ON TABLE data."PERs" TO postgres;