CREATE TABLE entities.companies
(
	company_name text COLLATE pg_catalog."default" NOT NULL,
	country_ID integer NOT NULL,
	"ID" SERIAL NOT NULL,
	sector_ID integer NOT NULL,
	CONSTRAINT companies_pkey PRIMARY KEY ("ID"),
	CONSTRAINT companies_country_fkey FOREIGN KEY (country)
		REFERENCES param.countries("ID") MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
		NOT VALID,
	CONSTRAINT companies_sector_fkey FOREIGN KEY (sector)
		REFERENCES param.sectors("ID") MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
		NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE entities.companies
	OWNER to postgres;

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE entities.companies TO db_tool_user;

GRANT ALL ON TABLE entities.companies TO postgres;