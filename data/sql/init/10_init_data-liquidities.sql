CREATE TABLE data.liquidities
(
	"ID" SERIAL NOT NULL,
	share_ID integer NOT NULL,
	year integer NOT NULL,
	current_ratio double precision NOT NULL,
	valid_from timestamp(4) without time zone NOT NULL,
	valid_to timestamp(4) without time zone NOT NULL,
	CONSTRAINT liquidities_pkey PRIMARY KEY ("ID"),
	CONSTRAINT liquidities_share_fkey FOREIGN KEY (share)
		REFERENCES entities.shares ("ID") MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE data.liquidities
	OWNER TO postgres;

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE data.liquidities TO db_tool_user;

GRANT ALL ON TABLE data.liquidities TO postgres;