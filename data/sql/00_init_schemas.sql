CREATE SCHEMA data
	AUTHORIZATION db_tool_user;

CREATE SCHEMA entities
	AUTHORIZATION db_tool_user;

CREATE SCHEMA param
	AUTHORIZATION db_tool_user;

GRANT ALL ON SCHEMA data TO db_tool_user;
GRANT ALL ON SCHEMA entities TO db_tool_user;
GRANT ALL ON SCHEMA param TO db_tool_user;