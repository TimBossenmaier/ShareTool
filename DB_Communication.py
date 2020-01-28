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
    "PERs": "data",
    "ROAs": "data",
    "assetTurnovers": "data",
    "cashflows": "data",
    "dividendReturns": "data",
    "dividends": "data",
    "estimations": "data",
    "grossMargins": "data",
    "leverages": "data",
    "liquidities": "data",
    "profits": "data",
    "sharePrices": "data",
    "companies": "entities",
    "shares": "entities",
    "categories": "param",
    "countries": "param",
    "currencies": "param",
    "sectors": "param"
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

    except BaseException:
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
    except BaseException:
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

    list_column_names = list()

    # append each result to the list
    for each_name in table_column_names:
        list_column_names.append(each_name[0])

    return list_column_names


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
    """
    returns the total number of shares in the database
    :param sql_cursor: current database cursor
    :return: number of shares in db
    """

    # read in query string from corresponding file
    sql_query = open('./data/sql/get_total_number_of_shares.sql', 'r').read()

    # execute query
    sql_cursor.execute(sql_query)

    # get first entry of response
    number_of_shares = sql_cursor.fetchall()[0][0]

    return number_of_shares


def get_all_sectors(sql_cursor):
    """
    query all sectors and their ID
    :param sql_cursor: current database cursor
    :return: returns all sectors and their ID as data frame
    """
    # TODO: get all zu einer Funktion zusammenfassen

    sql_query = 'SELECT * FROM param.sectors ORDER BY sector_name ASC'

    sql_cursor.execute(sql_query)

    df_sectors = pd.DataFrame(columns=['ID', 'sector_name'])

    # loop over all entries of the response
    for each_line in sql_cursor.fetchall():

        # separate into ID and name
        key, value = each_line

        # create row in data frame for each value pair
        df_sectors = df_sectors.append({'ID':key, 'sector_name': value}, ignore_index=True)

    return df_sectors


def get_all_countries(sql_cursor):
    """
    query all countries and their ID
    :param sql_cursor: current database cursor
    :return: returns all countries and their ID as data frame
    """
    # TODO: get_all_* zu einer Funktion zusammenfassen

    sql_query = 'SELECT "ID", country_name FROM param.countries ORDER BY country_name ASC'

    sql_cursor.execute(sql_query)

    df_countries = pd.DataFrame(columns=['ID', 'country_name'])

    # loop over all entries of the response
    for each_line in sql_cursor.fetchall():

        # separate into ID and name
        key, value = each_line

        # create row in data frame for each value pair
        df_countries = df_countries.append({'ID': key, 'country_name': value}, ignore_index=True)

    return df_countries


def get_all_categories(sql_cursor):
    """
    query all categories and their ID
    :param sql_cursor: current database cursor
    :return: returns all categories and their ID as data frame
    """
    # TODO: get_all_* zu einer Funktion zusammenfassen

    sql_query = 'SELECT "ID", category_name FROM param.categories ORDER BY category_name ASC'

    sql_cursor.execute(sql_query)

    df_categories = pd.DataFrame(columns=['ID', 'category_name'])

    # loop over all entries of the response
    for each_line in sql_cursor.fetchall():

        # separate into ID and name
        key, value = each_line

        # create row in data frame for each value pair
        df_categories = df_categories.append({'ID': key,'category_name': value}, ignore_index=True)

    return df_categories


def get_all_currencies(sql_cursor):
    """
    query all currencies and their ID
    :param sql_cursor: current database cursor
    :return: returns all currencies and their ID as data frame
    """
    # TODO: get_all_* zu einer Funktion zusammenfassen

    sql_query = 'SELECT "ID", currency_name FROM param.currencies ORDER BY currency_name ASC'

    sql_cursor.execute(sql_query)

    df_currencies = pd.DataFrame(columns=['ID', 'currency_name'])

    # loop over all entries of the response
    for each_line in sql_cursor.fetchall():

        # separate into ID and name
        key, value = each_line

        # create row in data frame for each value pair
        df_currencies = df_currencies.append({'ID': key, 'currency_name': value}, ignore_index=True)

    return df_currencies


def get_all_isin(sql_cursor):
    """
    query all isin
    :param sql_cursor: current database cursor
    :return: returns all isin as list
    """
    # TODO: get_all_* zu einer Funktion zusammenfassen

    sql_query = 'SELECT shares FROM entities.shares'

    sql_cursor.execute(sql_query)

    list_isin = []

    for each_line in sql_cursor.fetchall():

        # append each entry to list
        list_isin.append(each_line[0])

    return list_isin


def get_all_shares(sql_cursor):
    """
    query all shares
    :param sql_cursor: current database cursor
    :return: returns all shares and their ID as data frame
    """
    # TODO: get_all_* zu einer Funktion zusammenfassen

    sql_query = open('./data/sql/get_all_shares.sql', 'r').read()

    sql_cursor.execute(sql_query)

    df_shares = pd.DataFrame(columns=['ID', 'company_name'])

    for each_line in sql_cursor.fetchall():

        key, value = each_line

        df_shares = df_shares.append({'ID': key, 'company_name': value}, ignore_index=True)

    return df_shares


def get_years_for_specific_share(sql_cursor, table, share_id):
    """

    :param sql_cursor:
    :param table:
    :param share_id:
    :return:
    """

    sql_query = 'SELECT tab.year FROM entities.shares share ' \
                'INNER JOIN data.' + table + ' tab on tab."share_ID" = share."ID" ' \
                'WHERE share."ID" = ' + str(share_id)

    sql_cursor.execute(sql_query)

    list_years = []

    for each_line in sql_cursor.fetchall():

        list_years.append(each_line[0])

    return list_years


def create_insert_into_statement(table_name, column_names, returning=False):
    """
    Creates the special form of a INSERT statement required by psycopg2
    :param table_name: name of table which receives inserts
    :param column_names: list of all column names integrated in the query
    :param returning: indicates whether a returning clause should be included
    :return: sql statement as a string
    """

    query_string = "INSERT INTO " + table_schema_relation[table_name] + "." + table_name + " ("

    # iterate over the columns
    for column, i in zip(column_names, range(1, len(column_names) + 1)):

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
    Performs INSERT statement for a company
    :param db_connection: psycopg2 connection to database
    :param company_name: name of the company as string
    :param country: id of country (serves as foreign key)
    :param sector: id of sector (serves as foreign key)
    :return: id of the created company entry
    """

    sql_cursor = db_connection.cursor()

    column_names = get_column_names_from_db_table(sql_cursor, "companies")

    # remove ID as this is generated automatically by the database
    column_names.remove("ID")

    # create insert statement with returning clause
    query = create_insert_into_statement("companies", column_names, returning=True)

    sql_cursor.execute(query, (company_name, country, sector))
    db_connection.commit()

    # process returned key
    idx_new_row = sql_cursor.fetchone()[0]

    return idx_new_row


def insert_share(db_connection, values):
    """
    Performs insert statement of a share
    :param db_connection: psycopg2 connection to database
    :param values: dictionary of values to be integrated in the statement
    :return: error message
    """

    error_message = None
    try:
        sql_cursor = db_connection.cursor()

        column_names = get_column_names_from_db_table(sql_cursor, "shares")

        # remove ID as this is generated automatically by the database
        column_names.remove("ID")

        query = create_insert_into_statement("shares", column_names)
        sql_cursor.execute(query, (values["company_id"], values["isin"], values["category_id"],
                                   values["comment"], values["currency_id"]))

        db_connection.commit()

    except BaseException as e:
        error_message = e

    return error_message
