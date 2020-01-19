SELECT
	share."ID",
	companie.company_name

FROM
	entities.shares share
JOIN
	 entities.companies companie on companie."ID" = share."company_ID"