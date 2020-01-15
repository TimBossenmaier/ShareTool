import psycopg2
import json
import pandas as pd
"""
    This python file is used to implement the connection to the database.
    The credentials for the database are read from a JSON file, found in : ./data/db_config.json
    JSON File is structured as follows:
        {
            "db_name": w,
            "user": x,
            "host": y,
            "password": z
}
"""

# dictionary containing the relation of a table to its schema
table_schema_relation = {
    "PERs" : "data",
    "ROAs" : "data",
    "assetTurnovers": "data",
    "cashflows": "data",
    "dividendReturns": "data",
    "dividends": "data",
    "estimations": "data",
    "grossMargins": "data",
    "leverages" : "data",
    "liquidities": "data",
    "profits" : "data",
    "sharePrices": "data",
    "companies" : "entities",
    "shares" : "entities",
    "categories" : "param",
    "countries" : "param",
    "currencies" : "param",
    "sectors" : "param"
}


def connect_to_db():
    """
    Establish the connection to the  PostgreSQL data base specified in the json file
    :return: in case of a successful connection, the connection to the database otherwise None
    """

    dict_db_params = None

    # read the cofig JSON and load it as JSON
    with open('./data/db_config.json', encoding='utf-8') as F:
        dict_db_params = json.load(F)

    try:

        conn = psycopg2.connect("dbname='" + dict_db_params["db_name"] + "' user='" + dict_db_params["user"]
                                + "' host='" + dict_db_params["host"] + "' password='" +  dict_db_params["password"] + "'")

        return conn
    except:
        return None


def connect_to_db_with_params(db_name, host, user, password):
    """
    Same as connect_to_db() but uses given parameters instead of ththe config file
    :param db_name: name of database
    :param host: name of host
    :param user: name of user
    :param password: password
    :return: in case of a successful connection, the connection to the database otherwise None
    """

    try:

        conn = psycopg2.connect("dbname='" + db_name + "' user='" + user + "' host='"
                                + host + "' password='" + password + "'")
        conn.set_client_encoding('UTF-8')
        return conn
    except:
        return None


def get_db_name():
    """
    :return: name of the currently used db
    """
    # read the cofig JSON and load it as JSON
    with open('./data/db_config.json', encoding='utf-8') as F:
        dict_db_params = json.load(F)

    return dict_db_params["db_name"]


def get_column_names_from_db_table(sql_cursor, table_name):
    """
    Scrape the column names from a database to a list
    :param sql_cursor: psycopg cursor
    :param table_name: name of table to get the column names from
    :return: a list with table column names
    """

    # read the required sql statement from the corresponding file
    sql_query_table_names = open('./data/sql/get_column_names_for_table.sql', 'r').read()

    # append the table tame
    sql_query_table_names += " '" + table_name + "'"

    # execute sql query and fetch the results
    sql_cursor.execute(sql_query_table_names)
    table_column_names = sql_cursor.fetchall()

    column_names = list()

    # append each result to the list
    for each_name in table_column_names:
        column_names.append(each_name[0])

    return column_names


def create_insert_into_statement_for_df(df, table_name):


    """
    Creates the special form of a INSERT statement required by psycopg2
    :param df: dataframe to be inserted
    :param table_name: name of table which receives inserts
    :return: sql statement as a string
    """

    query_string = "INSERT INTO " + table_schema_relation[table_name] + "." + table_name + " ("

    # iterate over the columns
    for column, i in zip(df.columns, range(1, df.shape[1] + 1)):

        # append column name in quotes
        query_string += '"' + column + '"'

        # append closing bracket after last column, else append a comma
        if i == df.shape[1]:
            query_string += ")"

        else:
            query_string += ", "

    # append series placeholder for each column
    query_string += " VALUES(" + "%s, " * (df.shape[1] - 1) + "%s)"

    return query_string


def get_total_number_of_shares(sql_cursor):

    sql_query = open('./data/sql/get_total_number_of_shares.sql','r').read()

    sql_cursor.execute(sql_query)

    number_of_shares = sql_cursor.fetchall()[0][0]

    return number_of_shares


def get_all_sectors(sql_cursor):

    sql_query = 'SELECT * FROM param.sectors ORDER BY sector_name ASC'

    sql_cursor.execute(sql_query)

    df_sectors = pd.DataFrame(columns=['ID', 'sector_name'])
    for each_line in sql_cursor.fetchall():

        key, value = each_line

        df_sectors = df_sectors.append({'ID':key, 'sector_name': value}, ignore_index=True)

    return df_sectors


def get_all_countries(sql_cursor):

    sql_query = 'SELECT "ID", country_name FROM param.countries ORDER BY country_name ASC'

    sql_cursor.execute(sql_query)

    df_countries = pd.DataFrame(columns=['ID', 'country_name'])
    for each_line in sql_cursor.fetchall():

        key, value = each_line

        df_countries = df_countries.append({'ID': key, 'country_name': value}, ignore_index=True)

    return df_countries


def create_insert_into_statement(table_name, column_names, returning=False):


    """
    s.o.
    """

    query_string = "INSERT INTO " + table_schema_relation[table_name] + "." + table_name + " ("

    # iterate over the columns
    for column, i in zip(column_names, range(1, len(column_names) + 1 )):

        # append column name in quotes
        query_string += '"' + column + '"'

        # append closing bracket after last column, else append a comma
        if i == len(column_names):
            query_string += ")"

        else:
            query_string += ", "

    # append series placeholder for each column
    query_string += " VALUES(" + "%s, " * (len(column_names) - 1) + "%s)"

    if returning:
        query_string += ' RETURNING "ID"'

    return query_string


def insert_company(db_connection, company_name, country, sector):
    """

    :param db_connection:
    :param company_name:
    :param country:
    :param sector:
    :return:
    """
    # TODO Handling of UniqueViolation (throw error and catch on GUI) -> see comment
    sql_cursor = db_connection.cursor()
    column_names = get_column_names_from_db_table(sql_cursor, "companies")
    column_names.remove("ID")
    query = create_insert_into_statement("companies", column_names, returning=True)
    sql_cursor.execute(query, (company_name, country, sector))
    db_connection.commit()
    idx_new_row = sql_cursor.fetchone()[0]
    return idx_new_row


"""
try:
    sql_cursor.execute(query, (company_name, country, sector))
except psycopg2.errors.UniqueViolation:
    print("Hallo")
    
"""





