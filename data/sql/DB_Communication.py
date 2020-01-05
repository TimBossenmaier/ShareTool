import psycopg2
import json
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

    #read the cofig JSON and load it as JSON
    with open('./data/db_config.json', encoding='utf-8') as F:
        dict_db_params = json.load(F)

    try:

        conn = psycopg2.connect("dbname='" + dict_db_params["db_name"] + "' user='" + dict_db_params["user"]
                                + "' host='" + dict_db_params["host"] + "' password='" +  dict_db_params["password"] + "'")

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