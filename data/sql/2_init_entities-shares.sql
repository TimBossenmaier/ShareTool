CREATE TABLE entities.shares
(
	"ID" integer NOT NULL DEFAULT nextval('entities."shares_ID_seq"'::regclass),
	company integer NOT NULL,
	isin text COLLATE pg_catalog."default" NOT NULL,
	category integer NOT NULL,
	comment text COLLATE pg_catalog."default",
	currency integer NOT NULL,
	CONSTRAINT shares_pkey PRIMARY KEY ("ID"),
	CONSTRAINT companies_isin_unique UNIQUE (isin),

	CONSTRAINT shares_category_fkey FOREIGN KEY (category)
		REFERENCES param.categories ("ID") MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
		NOT VALID,
	CONSTRAINT shares_company_fkey FOREIGN KEY (company)
		REFERENCES entities.companies ("ID") MATCH SIMPLE
		ON UPDATE NO ACTION			
		ON DELETE NO ACTION
		NOT VALID,
	CONSTRAINT shares_currency_fkey FOREIGN KEY (currency)
		REFERENCES param.currencies ("ID") MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
		NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE entities.shares
	OWNER TO postgres;

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE entities.share TO db_tool_user;

GRANT ALL ON TABLE entities.shares TO postgres;